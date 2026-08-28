"""Apply the renames/drops in goodshape_data.txt to the two final chat CSVs.

The originals are read-only inputs. Outputs use the suffix ``_goodshape.csv``.
Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_SPEC = HERE / "goodshape_data.txt"
DEFAULT_AGGREGATED = HERE / "all_apps_wide_2026-08-26_chat_aggregated_final.csv"
DEFAULT_BY_PARTNER = HERE / "all_apps_wide_2026-08-26_chat_by_partner_final.csv"

PAYOFF_PARTICIPANT = "participant.payoff"
PAYOFF_MAIN = "bargaining_tdl_main.1.player.payoff"
OUTCOME_PARTICIPANT = "participant.group_outcome"
OUTCOME_GROUP = "bargaining_tdl_main.1.group.group_outcome"
TRANSCRIPTS = {"chat_transcript_group", "chat_transcript"}
COMPACT_MESSAGE_FIELDS = (
    "from_id", "from_color", "to_id", "to_color", "body", "timestamp_utc"
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV senza header: {path}")
        return list(reader.fieldnames), list(reader)


def parse_spec(path: Path) -> tuple[dict[str, str], set[str]]:
    renames: dict[str, str] = {}
    drops: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("-->"):
            continue
        drop_match = re.fullmatch(r"([^\s]+)\s+drop", line)
        if drop_match:
            drops.add(drop_match.group(1))
            continue
        rename_match = re.match(r"^([^\s]+)\s+-->\s+([^\s]+)", line)
        if rename_match:
            source, target = rename_match.groups()
            renames[source] = target

    # The specification asks to compare these two fields before retaining one
    # payoff. Equality is enforced separately; the main-app duplicate is then
    # removed so the participant-level field alone becomes ``payoff``.
    renames[PAYOFF_PARTICIPANT] = "payoff"
    renames.pop(PAYOFF_MAIN, None)
    drops.add(PAYOFF_MAIN)

    # The participant copy is empty outside the experimental groups, whereas
    # the group-level field correctly contains ``pending``. Retain the latter.
    drops.add(OUTCOME_PARTICIPANT)
    return renames, drops


def readable_utc(value: object) -> str:
    try:
        timestamp = float(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Timestamp chat non numerico: {value!r}") from exc
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S.%f UTC"
    )


def compact_transcript(value: str) -> str:
    payload = json.loads(value or "[]")
    if not isinstance(payload, list):
        raise ValueError("Il transcript non è un array JSON")
    compact = []
    for message in payload:
        if not isinstance(message, dict):
            raise ValueError("Un elemento del transcript non è un oggetto JSON")
        compact.append({
            "from_id": message.get("from_id"),
            "from_color": message.get("from_color", ""),
            "to_id": message.get("to_id"),
            "to_color": message.get("to_color", ""),
            "body": message.get("body", ""),
            "timestamp_utc": readable_utc(message.get("timestamp")),
        })
    return json.dumps(compact, ensure_ascii=False, separators=(",", ":"))


def output_schema(headers: list[str], renames: dict[str, str], drops: set[str]) -> list[str]:
    result = [renames.get(column, column) for column in headers if column not in drops]
    duplicates = sorted({name for name in result if result.count(name) > 1})
    if duplicates:
        raise ValueError(f"Collisioni dopo la rinomina: {duplicates}")
    return result


def transform(
    headers: list[str], rows: list[dict[str, str]],
    renames: dict[str, str], drops: set[str],
) -> tuple[list[str], list[dict[str, str]]]:
    new_headers = output_schema(headers, renames, drops)
    transformed = []
    for source_row in rows:
        output_row: dict[str, str] = {}
        for column in headers:
            if column in drops:
                continue
            target = renames.get(column, column)
            value = source_row.get(column, "")
            output_row[target] = compact_transcript(value) if column in TRANSCRIPTS else value
        transformed.append(output_row)
    return new_headers, transformed


def write_csv_atomic(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8-sig", newline="", dir=path.parent,
        delete=False, suffix=".tmp"
    ) as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def validate_source(
    all_headers: set[str], all_rows: list[dict[str, str]],
    renames: dict[str, str], drops: set[str],
) -> dict[str, object]:
    referenced = set(renames) | drops
    missing_spec_columns = sorted(referenced - all_headers)
    if missing_spec_columns:
        raise ValueError(f"Colonne della specifica assenti dagli input: {missing_spec_columns}")

    payoff_differences = sum(
        row.get(PAYOFF_PARTICIPANT, "") != row.get(PAYOFF_MAIN, "")
        for row in all_rows
    )
    if payoff_differences:
        raise ValueError(
            f"I due payoff differiscono in {payoff_differences} righe: impossibile consolidare"
        )

    outcome_conflicts = sum(
        bool(row.get(OUTCOME_PARTICIPANT, ""))
        and row.get(OUTCOME_PARTICIPANT, "") != row.get(OUTCOME_GROUP, "")
        for row in all_rows
    )
    if outcome_conflicts:
        raise ValueError(
            f"Le due copie dell'outcome confliggono in {outcome_conflicts} righe"
        )
    return {
        "payoff_rows_compared": len(all_rows),
        "payoff_differences": payoff_differences,
        "nonempty_outcome_conflicts": outcome_conflicts,
    }


def validate_output(
    source_headers: list[str], source_rows: list[dict[str, str]],
    output_headers: list[str], output_rows: list[dict[str, str]],
    renames: dict[str, str], drops: set[str], transcript_column: str,
) -> dict[str, object]:
    failures: list[str] = []
    expected_headers = output_schema(source_headers, renames, drops)
    if output_headers != expected_headers:
        failures.append("ordine/schema delle colonne non coincide con la specifica")
    if len(output_rows) != len(source_rows):
        failures.append("numero di righe modificato")

    source_keys = [
        (row.get("session.code", ""), row.get("participant.code", ""), row.get("chat_side", ""))
        for row in source_rows
    ]
    output_keys = [
        (row.get("session.code", ""), row.get("code", ""), row.get("topology_side", ""))
        for row in output_rows
    ]
    if source_keys != output_keys:
        failures.append("chiavi o ordine delle righe modificati")

    transcript_occurrences = 0
    for source_row, output_row in zip(source_rows, output_rows):
        for source_column in source_headers:
            if source_column in drops or source_column in TRANSCRIPTS:
                continue
            target = renames.get(source_column, source_column)
            if output_row.get(target, "") != source_row.get(source_column, ""):
                failures.append(f"valore modificato nella colonna {source_column}")
                break
        source_messages = json.loads(source_row.get(transcript_column) or "[]")
        output_messages = json.loads(output_row.get(transcript_column) or "[]")
        if len(source_messages) != len(output_messages):
            failures.append("numero di messaggi modificato in un transcript")
            break
        transcript_occurrences += len(output_messages)
        for old, new in zip(source_messages, output_messages):
            if tuple(new) != COMPACT_MESSAGE_FIELDS:
                failures.append("schema di un messaggio JSON non conforme")
                break
            if (
                new["from_id"] != old.get("from_id")
                or new["from_color"] != old.get("from_color", "")
                or new["to_id"] != old.get("to_id")
                or new["to_color"] != old.get("to_color", "")
                or new["body"] != old.get("body", "")
                or new["timestamp_utc"] != readable_utc(old.get("timestamp"))
            ):
                failures.append("contenuto di un messaggio JSON modificato")
                break
        if failures:
            break

    forbidden = set(drops) | set(renames)
    remaining_old_names = sorted(forbidden & set(output_headers))
    if remaining_old_names:
        failures.append(f"nomi originali/drop ancora presenti: {remaining_old_names}")
    if "chat_first_timestamp" in output_headers or "chat_last_timestamp" in output_headers:
        failures.append("timestamp first/last non rimossi")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "rows": len(output_rows),
        "columns": len(output_headers),
        "transcript_message_occurrences": transcript_occurrences,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--aggregated", type=Path, default=DEFAULT_AGGREGATED)
    parser.add_argument("--by-partner", type=Path, default=DEFAULT_BY_PARTNER)
    parser.add_argument(
        "--aggregated-output", type=Path,
        default=HERE / "all_apps_wide_2026-08-26_chat_aggregated_goodshape.csv"
    )
    parser.add_argument(
        "--by-partner-output", type=Path,
        default=HERE / "all_apps_wide_2026-08-26_chat_by_partner_goodshape.csv"
    )
    parser.add_argument(
        "--audit", type=Path,
        default=HERE / "all_apps_wide_2026-08-26_chat_goodshape_audit.json"
    )
    args = parser.parse_args()

    renames, drops = parse_spec(args.spec)
    agg_headers, agg_rows = read_csv(args.aggregated)
    partner_headers, partner_rows = read_csv(args.by_partner)
    source_checks = validate_source(
        set(agg_headers) | set(partner_headers), agg_rows + partner_rows,
        renames, drops,
    )

    agg_out_headers, agg_out_rows = transform(agg_headers, agg_rows, renames, drops)
    partner_out_headers, partner_out_rows = transform(
        partner_headers, partner_rows, renames, drops
    )
    agg_check = validate_output(
        agg_headers, agg_rows, agg_out_headers, agg_out_rows,
        renames, drops, "chat_transcript_group",
    )
    partner_check = validate_output(
        partner_headers, partner_rows, partner_out_headers, partner_out_rows,
        renames, drops, "chat_transcript",
    )
    audit = {
        "inputs": {
            "spec": str(args.spec.resolve()),
            "aggregated": str(args.aggregated.resolve()),
            "by_partner": str(args.by_partner.resolve()),
        },
        "outputs": {
            "aggregated": str(args.aggregated_output.resolve()),
            "by_partner": str(args.by_partner_output.resolve()),
        },
        "rules": {
            "renamed_columns": len(renames),
            "dropped_columns": len(drops),
            "message_fields": list(COMPACT_MESSAGE_FIELDS),
            "timestamp_format": "YYYY-MM-DD HH:MM:SS.ffffff UTC",
        },
        "source_checks": source_checks,
        "aggregated_validation": agg_check,
        "by_partner_validation": partner_check,
    }
    args.audit.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    failures = agg_check["failures"] + partner_check["failures"]
    if failures:
        raise SystemExit("Validazione strict fallita: " + "; ".join(failures))
    write_csv_atomic(args.aggregated_output, agg_out_headers, agg_out_rows)
    write_csv_atomic(args.by_partner_output, partner_out_headers, partner_out_rows)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
