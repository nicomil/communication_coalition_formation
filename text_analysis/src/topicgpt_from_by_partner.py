"""TopicGPT pipeline driven only by the final directional by-partner CSV.

Each non-empty focal-to-partner transcript is one TopicGPT document. The same
set of documents is used for topic induction and topic assignment. The oTree
wide and ChatMessages exports are neither required nor read.
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from . import config, topicgpt


REQUIRED = {
    "session.code", "group_id", "treatment", "focal_player_id",
    "partner_id", "focal_player_color", "partner_color", "chat_transcript",
    "number_of_messages", "number_of_words",
}
TOPIC_COLUMNS = (
    "nlp_sent_topics", "nlp_sent_topic_primary", "nlp_sent_n_topics",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV without header: {path}")
        missing = sorted(REQUIRED - set(reader.fieldnames))
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return list(reader.fieldnames), list(reader)


def write_csv_atomic(path: Path, headers: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8-sig", newline="", dir=path.parent,
        delete=False, suffix=".tmp",
    ) as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def document_id(row: dict[str, str]) -> str:
    return "|".join((
        row.get("session.code", "").strip(),
        row.get("group_id", "").strip(),
        row.get("focal_player_id", "").strip(),
        row.get("partner_id", "").strip(),
    ))


def parse_messages(row: dict[str, str], csv_row: int) -> list[dict[str, object]]:
    payload = json.loads(row.get("chat_transcript") or "[]")
    if not isinstance(payload, list) or any(not isinstance(message, dict) for message in payload):
        raise ValueError(f"Invalid transcript at CSV row {csv_row}")
    focal = row.get("focal_player_id", "").strip()
    partner = row.get("partner_id", "").strip()
    focal_color = row.get("focal_player_color", "").strip()
    partner_color = row.get("partner_color", "").strip()
    previous_timestamp = None
    for message in payload:
        if str(message.get("from_id", "")) != focal or str(message.get("to_id", "")) != partner:
            raise ValueError(
                f"Non-directional message at CSV row {csv_row}: "
                f"{message.get('from_id')}->{message.get('to_id')}, expected {focal}->{partner}"
            )
        if focal_color and str(message.get("from_color", "")).strip() != focal_color:
            raise ValueError(f"Sender-color mismatch at CSV row {csv_row}")
        if partner_color and str(message.get("to_color", "")).strip() != partner_color:
            raise ValueError(f"Receiver-color mismatch at CSV row {csv_row}")
        timestamp = str(message.get("timestamp_utc", "")).strip()
        if timestamp:
            try:
                parsed_timestamp = datetime.fromisoformat(
                    timestamp.removesuffix(" UTC").replace("Z", "+00:00")
                )
            except ValueError as exc:
                raise ValueError(
                    f"Invalid timestamp at CSV row {csv_row}: {timestamp}"
                ) from exc
            if previous_timestamp is not None and parsed_timestamp < previous_timestamp:
                raise ValueError(f"Non-chronological transcript at CSV row {csv_row}")
            previous_timestamp = parsed_timestamp
    if row.get("number_of_messages") != str(len(payload)):
        raise ValueError(f"number_of_messages mismatch at CSV row {csv_row}")
    words = sum(len(str(message.get("body", "")).split()) for message in payload)
    if row.get("number_of_words") != str(words):
        raise ValueError(f"number_of_words mismatch at CSV row {csv_row}")
    return payload


def build_documents(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    documents: list[dict[str, object]] = []
    populated_groups: Counter[tuple[str, str]] = Counter()
    participants: Counter[tuple[str, str]] = Counter()
    identified_participants: Counter[tuple[str, str, str]] = Counter()
    group_pairs: defaultdict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    group_treatments: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    source_messages = 0

    for csv_row, row in enumerate(rows, start=2):
        session = row.get("session.code", "").strip()
        group = row.get("group_id", "").strip()
        focal = row.get("focal_player_id", "").strip()
        partner = row.get("partner_id", "").strip()
        participants[(session, row.get("code", ""))] += 1
        messages = parse_messages(row, csv_row)
        if not (session and group and focal and partner):
            if messages:
                raise ValueError(f"Messages found on an unidentified row {csv_row}")
            continue
        if focal == partner:
            raise ValueError(f"Self-directed row at CSV row {csv_row}")
        populated_groups[(session, group)] += 1
        identified_participants[(session, group, focal)] += 1
        group_pairs[(session, group)].append((focal, partner))
        group_treatments[(session, group)].add(row.get("treatment", "").strip())
        source_messages += len(messages)
        if not messages:
            continue

        doc_id = document_id(row)
        text = "\n".join(
            f"{message.get('from_color', '?')} to {message.get('to_color', '?')}: "
            f"{message.get('body', '')}"
            for message in messages
        ).strip()
        documents.append({
            "id": doc_id,
            "text": text,
            "unit": "dyad_directed",
            "group_uid": f"{session}|{group}",
            "sender_id_in_group": focal,
            "receiver_id_in_group": partner,
            "treatment": row.get("treatment", ""),
            "n_messages": len(messages),
        })

    ids = [str(document["id"]) for document in documents]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate TopicGPT document IDs")
    participant_errors = sum(count != 2 for count in participants.values())
    identified_participant_errors = sum(
        count != 2 for count in identified_participants.values()
    )
    group_errors = 0
    for group_key, pairs in group_pairs.items():
        players = {player for pair in pairs for player in pair}
        expected = {
            (sender, receiver) for sender in players for receiver in players
            if sender != receiver
        }
        if (len(players) != 3 or len(pairs) != 6 or len(set(pairs)) != 6
                or set(pairs) != expected or len(group_treatments[group_key]) != 1):
            group_errors += 1
    if participant_errors or identified_participant_errors or group_errors:
        raise ValueError(
            f"Topology validation failed: {participant_errors} participants do not have "
            f"two rows overall; {identified_participant_errors} identified participants "
            f"do not have two partner rows; {group_errors} identified groups do not "
            f"contain the six unique directed pairs and one treatment"
        )
    if sum(int(document["n_messages"]) for document in documents) != source_messages:
        raise AssertionError("TopicGPT documents do not cover every source message exactly once")

    report = {
        "source_rows": len(rows),
        "participants": len(participants),
        "identified_participants": len(identified_participants),
        "populated_groups": len(populated_groups),
        "populated_groups_with_six_rows": len(populated_groups),
        "identified_directional_rows": sum(populated_groups.values()),
        "source_directional_messages": source_messages,
        "topicgpt_documents": len(documents),
        "topicgpt_document_messages": sum(int(d["n_messages"]) for d in documents),
        "identified_empty_directional_texts": sum(populated_groups.values()) - len(documents),
        "rows_outside_identified_triads": len(rows) - sum(populated_groups.values()),
        "structural_texts_per_identified_group": 6,
        "induction_unit": "dyad_directed",
        "assignment_unit": "dyad_directed",
        "status": "PASS",
    }
    return documents, report


def merge_assignments(
    headers: list[str], rows: list[dict[str, str]], assignments: dict[str, dict[str, object]],
) -> tuple[list[str], list[dict[str, object]]]:
    output_headers = [column for column in headers if column not in TOPIC_COLUMNS] + list(TOPIC_COLUMNS)
    output_rows: list[dict[str, object]] = []
    expected_ids = set()
    for row in rows:
        output: dict[str, object] = {
            column: row.get(column, "") for column in headers if column not in TOPIC_COLUMNS
        }
        messages = json.loads(row.get("chat_transcript") or "[]")
        if messages:
            doc_id = document_id(row)
            expected_ids.add(doc_id)
            result = assignments.get(doc_id)
            if result is None:
                raise ValueError(f"TopicGPT assignment missing for document {doc_id}")
            output["nlp_sent_topics"] = result.get("topics", "")
            output["nlp_sent_topic_primary"] = result.get("topic_primary", "")
            output["nlp_sent_n_topics"] = result.get("n_topics", 0)
        else:
            output["nlp_sent_topics"] = ""
            output["nlp_sent_topic_primary"] = ""
            output["nlp_sent_n_topics"] = ""
        output_rows.append(output)
    extras = set(assignments) - expected_ids
    if extras:
        raise ValueError(f"TopicGPT returned {len(extras)} unknown document IDs")
    return output_headers, output_rows


def prepare(
    input_path: Path, outdir: Path,
) -> tuple[list[str], list[dict[str, str]], list[dict[str, object]], dict[str, object]]:
    headers, rows = read_csv(input_path)
    documents, validation = build_documents(rows)
    outdir.mkdir(parents=True, exist_ok=True)
    topicgpt.write_jsonl(outdir / "topicgpt_input.jsonl", documents)
    manifest = {
        "input": str(input_path.resolve()),
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "method": {
            "source": "final directional by-partner CSV only",
            "induction_unit": "dyad_directed",
            "assignment_unit": "dyad_directed",
            "same_documents_for_induction_and_assignment": True,
            "empty_transcripts": (
                "the six-row group structure is retained in the final CSV; empty texts "
                "are excluded from model calls and receive blank topic fields"
            ),
        },
        "validation": validation,
    }
    (outdir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return headers, rows, documents, manifest


def run(args) -> dict[str, object]:
    input_path = Path(args.by_partner_input).resolve()
    if not input_path.is_file():
        raise SystemExit(f"Input CSV not found: {input_path}")
    outdir = Path(args.outdir) / "topicgpt_by_partner"
    headers, rows, documents, manifest = prepare(input_path, outdir)
    print(f"Input CSV: {input_path}")
    print(f"TopicGPT documents: {len(documents)} (directed focal-to-partner texts)")
    print(f"Messages represented: {manifest['validation']['source_directional_messages']}")
    print(f"JSONL: {outdir / 'topicgpt_input.jsonl'}")

    if args.topicgpt_dry_run:
        print("Dry run: no API call made.")
        return {"input_jsonl": outdir / "topicgpt_input.jsonl", "manifest": outdir / "manifest.json"}

    if args.topicgpt_api == "openai":
        config.require_key("OPENAI_API_KEY")
        topicgpt.check_model_compatibility(args.topicgpt_api, args.topicgpt_model)
    repo = Path(args.topicgpt_repo).expanduser().resolve()
    corrected = topicgpt.run_topicgpt(
        documents=documents,
        outdir=outdir,
        repo_path=repo,
        api=args.topicgpt_api,
        model=args.topicgpt_model,
        refine=not args.topicgpt_no_refine,
        verbose=args.verbose,
        seed_file=Path(args.topicgpt_seed).expanduser() if args.topicgpt_seed else None,
        assignment_documents=None,
    )
    assignments = topicgpt.parse_assignments(corrected)
    output_headers, output_rows = merge_assignments(headers, rows, assignments)
    output_path = Path(args.outdir) / "datasets" / f"{input_path.stem}_topicgpt.csv"
    write_csv_atomic(output_path, output_headers, output_rows)
    manifest["result"] = {
        "assignments": len(assignments),
        "output_csv": str(output_path.resolve()),
        "output_rows": len(output_rows),
    }
    (outdir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Topic-enriched CSV: {output_path}")
    return {
        "input_jsonl": outdir / "topicgpt_input.jsonl",
        "manifest": outdir / "manifest.json",
        "dataset": output_path,
    }
