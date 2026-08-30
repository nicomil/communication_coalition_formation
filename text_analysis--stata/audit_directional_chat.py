"""Audit a by-partner CSV whose chat transcripts should be directional.

This script is read-only. It validates JSON structure, endpoint attribution,
directionality, message/word counts, and the six-row topology of complete triads.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV without headers: {path}")
        return list(reader.fieldnames), list(reader)


def word_count(messages: list[dict[str, object]]) -> int:
    """Count Unicode whitespace-delimited tokens across message bodies."""
    return sum(len(str(message.get("body", "")).split()) for message in messages)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--expect-directional", action="store_true")
    args = parser.parse_args()

    headers, rows = read_rows(args.csv_path)
    required = {
        "session.code", "group_id", "focal_player_id", "partner_id",
        "chat_transcript",
    }
    missing = sorted(required - set(headers))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    endpoint_errors: list[dict[str, object]] = []
    direction_errors: list[dict[str, object]] = []
    count_errors: list[dict[str, object]] = []
    total_occurrences = 0
    forward_occurrences = 0
    nonempty_key_counts: Counter[tuple[str, str]] = Counter()

    for csv_row, row in enumerate(rows, start=2):
        messages = json.loads(row.get("chat_transcript") or "[]")
        if not isinstance(messages, list):
            raise ValueError(f"Transcript is not a JSON array at CSV row {csv_row}")
        focal = row.get("focal_player_id", "")
        partner = row.get("partner_id", "")
        if focal and partner and row.get("group_id", ""):
            nonempty_key_counts[(row.get("session.code", ""), row.get("group_id", ""))] += 1

        total_occurrences += len(messages)
        for message in messages:
            sender = str(message.get("from_id", ""))
            receiver = str(message.get("to_id", ""))
            if {sender, receiver} != {focal, partner}:
                endpoint_errors.append({
                    "csv_row": csv_row, "focal": focal, "partner": partner,
                    "from_id": sender, "to_id": receiver,
                })
            if sender == focal and receiver == partner:
                forward_occurrences += 1
            elif args.expect_directional:
                direction_errors.append({
                    "csv_row": csv_row, "focal": focal, "partner": partner,
                    "from_id": sender, "to_id": receiver,
                })

        if args.expect_directional:
            expected_messages = len(messages)
            expected_words = word_count(messages)
            if row.get("number_of_messages") != str(expected_messages):
                count_errors.append({
                    "csv_row": csv_row,
                    "field": "number_of_messages",
                    "actual": row.get("number_of_messages"),
                    "expected": expected_messages,
                })
            if row.get("number_of_words") != str(expected_words):
                count_errors.append({
                    "csv_row": csv_row,
                    "field": "number_of_words",
                    "actual": row.get("number_of_words"),
                    "expected": expected_words,
                })

    topology_distribution = Counter(nonempty_key_counts.values())
    report = {
        "file": str(args.csv_path.resolve()),
        "rows": len(rows),
        "columns": len(headers),
        "total_transcript_message_occurrences": total_occurrences,
        "forward_message_occurrences": forward_occurrences,
        "endpoint_errors": len(endpoint_errors),
        "direction_errors": len(direction_errors),
        "count_errors": len(count_errors),
        "nonempty_group_row_count_distribution": dict(sorted(topology_distribution.items())),
        "complete_six_row_groups": topology_distribution[6],
        "status": "PASS" if not endpoint_errors and not direction_errors and not count_errors else "FAIL",
        "first_errors": (endpoint_errors + direction_errors + count_errors)[:10],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
