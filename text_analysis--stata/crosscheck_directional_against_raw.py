"""Cross-check every directional transcript message against raw oTree chats."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


CHANNEL_RE = re.compile(r"^.+-bargaining_tdl_main-(\d+)_(\d+)_(\d+)$")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def readable_utc(value: str) -> str:
    return datetime.fromtimestamp(float(value), tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S.%f UTC"
    )


def key(
    session: str, group: str, sender: int | str, receiver: int | str,
    body: str, timestamp: str,
) -> tuple[str, str, str, str, str, str]:
    return session, group, str(sender), str(receiver), body, timestamp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wide", required=True, type=Path)
    parser.add_argument("--chat", required=True, type=Path)
    parser.add_argument("--final", required=True, type=Path)
    args = parser.parse_args()

    wide = rows(args.wide)
    chat = rows(args.chat)
    final = rows(args.final)
    participants: dict[tuple[str, str], tuple[str, str]] = {}
    for row in wide:
        participant_key = (row.get("session.code", ""), row.get("participant.code", ""))
        participant_value = (
            row.get("bargaining_tdl_main.1.player.id_in_group", ""),
            row.get("participant.part1_group_id", ""),
        )
        if participant_key in participants:
            raise ValueError(f"Duplicate participant key: {participant_key}")
        participants[participant_key] = participant_value

    expected: Counter[tuple[str, str, str, str, str, str]] = Counter()
    for csv_row, row in enumerate(chat, start=2):
        match = CHANNEL_RE.match(row.get("channel", ""))
        if not match:
            raise ValueError(f"Malformed chat channel at raw row {csv_row}")
        group, id_a, id_b = match.groups()
        participant_key = (row.get("session_code", ""), row.get("participant_code", ""))
        sender, canonical_group = participants[participant_key]
        if canonical_group != group or sender not in {id_a, id_b}:
            raise ValueError(f"Raw sender/group mismatch at chat row {csv_row}")
        receiver = id_b if sender == id_a else id_a
        expected[key(
            row.get("session_code", ""), group, sender, receiver,
            row.get("body", ""), readable_utc(row.get("timestamp", "")),
        )] += 1

    actual: Counter[tuple[str, str, str, str, str, str]] = Counter()
    count_errors = 0
    direction_errors = 0
    participant_row_counts: Counter[tuple[str, str]] = Counter()
    group_row_counts: Counter[tuple[str, str]] = Counter()
    for row in final:
        participant_row_counts[(row.get("session.code", ""), row.get("code", ""))] += 1
        if row.get("group_id", ""):
            group_row_counts[(row.get("session.code", ""), row.get("group_id", ""))] += 1
        transcript = json.loads(row.get("chat_transcript") or "[]")
        focal = row.get("focal_player_id", "")
        partner = row.get("partner_id", "")
        if row.get("number_of_messages") != str(len(transcript)):
            count_errors += 1
        words = sum(len(str(message.get("body", "")).split()) for message in transcript)
        if row.get("number_of_words") != str(words):
            count_errors += 1
        for message in transcript:
            if str(message.get("from_id", "")) != focal or str(message.get("to_id", "")) != partner:
                direction_errors += 1
            actual[key(
                row.get("session.code", ""), row.get("group_id", ""),
                message.get("from_id", ""), message.get("to_id", ""),
                str(message.get("body", "")), str(message.get("timestamp_utc", "")),
            )] += 1

    participant_topology_errors = sum(value != 2 for value in participant_row_counts.values())
    group_topology_errors = sum(value != 6 for value in group_row_counts.values())
    missing_from_final = expected - actual
    extra_in_final = actual - expected
    report = {
        "raw_chat_rows": len(chat),
        "final_rows": len(final),
        "final_directional_message_occurrences": sum(actual.values()),
        "distinct_expected_message_records": len(expected),
        "distinct_final_message_records": len(actual),
        "missing_raw_messages_in_final": sum(missing_from_final.values()),
        "extra_final_messages_not_in_raw": sum(extra_in_final.values()),
        "direction_errors": direction_errors,
        "count_errors": count_errors,
        "participants_not_having_exactly_two_rows": participant_topology_errors,
        "populated_groups": len(group_row_counts),
        "populated_groups_not_having_exactly_six_rows": group_topology_errors,
    }
    report["status"] = "PASS" if not any(
        report[field] for field in (
            "missing_raw_messages_in_final", "extra_final_messages_not_in_raw",
            "direction_errors", "count_errors",
            "participants_not_having_exactly_two_rows",
            "populated_groups_not_having_exactly_six_rows",
        )
    ) else "FAIL"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
