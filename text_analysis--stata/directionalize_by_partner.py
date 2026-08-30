"""Convert by-partner chat transcripts from bidirectional to focal-to-partner.

All non-chat values and row order are preserved. The operation is atomic and
strictly validated before the output replaces the requested destination.
"""

from __future__ import annotations

import argparse
import csv
import json
import tempfile
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = {
    "session.code", "group_id", "focal_player_id", "partner_id",
    "chat_message_count", "chat_message_count_focal_sent",
    "chat_message_count_partner_sent", "chat_transcript",
}
NEW_COLUMNS = ("number_of_words", "number_of_messages")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV without headers: {path}")
        return list(reader.fieldnames), list(reader)


def message_key(message: dict[str, object]) -> tuple[object, ...]:
    return (
        message.get("from_id"), message.get("from_color", ""),
        message.get("to_id"), message.get("to_color", ""),
        message.get("body", ""), message.get("timestamp_utc", ""),
    )


def word_count(messages: list[dict[str, object]]) -> int:
    """Count Unicode whitespace-delimited tokens across message bodies."""
    return sum(len(str(message.get("body", "")).split()) for message in messages)


def transform(
    headers: list[str], rows: list[dict[str, str]],
) -> tuple[list[str], list[dict[str, str]], dict[str, object]]:
    missing = sorted(REQUIRED_COLUMNS - set(headers))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    output_headers = [column for column in headers if column not in NEW_COLUMNS]
    transcript_index = output_headers.index("chat_transcript")
    output_headers[transcript_index:transcript_index] = list(NEW_COLUMNS)

    output_rows: list[dict[str, str]] = []
    original_occurrences: Counter[tuple[object, ...]] = Counter()
    directed_occurrences: Counter[tuple[object, ...]] = Counter()
    empty_directed_rows = 0

    for csv_row, source in enumerate(rows, start=2):
        payload = json.loads(source.get("chat_transcript") or "[]")
        if not isinstance(payload, list) or any(not isinstance(m, dict) for m in payload):
            raise ValueError(f"Invalid transcript JSON array at CSV row {csv_row}")
        focal = source.get("focal_player_id", "")
        partner = source.get("partner_id", "")

        forward: list[dict[str, object]] = []
        reverse_count = 0
        for message in payload:
            sender = str(message.get("from_id", ""))
            receiver = str(message.get("to_id", ""))
            if {sender, receiver} != {focal, partner}:
                raise ValueError(
                    f"Message endpoints do not match focal/partner at CSV row {csv_row}: "
                    f"{sender}->{receiver}, expected {focal}<->{partner}"
                )
            original_occurrences[message_key(message)] += 1
            if sender == focal and receiver == partner:
                forward.append(message)
                directed_occurrences[message_key(message)] += 1
            else:
                reverse_count += 1

        expected_total = int(source.get("chat_message_count") or 0)
        expected_forward = int(source.get("chat_message_count_focal_sent") or 0)
        expected_reverse = int(source.get("chat_message_count_partner_sent") or 0)
        if (len(payload), len(forward), reverse_count) != (
            expected_total, expected_forward, expected_reverse
        ):
            raise ValueError(
                f"Existing chat counts conflict with transcript at CSV row {csv_row}"
            )

        output = {column: source.get(column, "") for column in output_headers}
        output["chat_transcript"] = json.dumps(
            forward, ensure_ascii=False, separators=(",", ":")
        )
        output["number_of_words"] = str(word_count(forward))
        output["number_of_messages"] = str(len(forward))
        output_rows.append(output)
        if not forward:
            empty_directed_rows += 1

    # Each source message must occur twice in the old symmetric layout and
    # exactly once after direction filtering.
    multiplicity_errors = [
        key for key, occurrences in original_occurrences.items()
        if occurrences != 2 or directed_occurrences[key] != 1
    ]
    if multiplicity_errors:
        raise ValueError(
            f"Symmetric-to-directional coverage failed for {len(multiplicity_errors)} messages"
        )

    report = {
        "rows": len(output_rows),
        "columns_before": len(headers),
        "columns_after": len(output_headers),
        "source_transcript_occurrences": sum(original_occurrences.values()),
        "unique_directional_messages": len(directed_occurrences),
        "output_transcript_occurrences": sum(directed_occurrences.values()),
        "empty_directional_rows": empty_directed_rows,
        "word_definition": "Unicode whitespace-delimited tokens in message body",
        "coverage_status": "PASS",
    }
    return output_headers, output_rows, report


def write_csv_atomic(
    path: Path, headers: list[str], rows: list[dict[str, str]],
) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--audit", type=Path)
    args = parser.parse_args()

    headers, rows = read_csv(args.input)
    output_headers, output_rows, report = transform(headers, rows)
    write_csv_atomic(args.output, output_headers, output_rows)
    report.update({
        "input": str(args.input.resolve()),
        "output": str(args.output.resolve()),
    })
    if args.audit:
        args.audit.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
