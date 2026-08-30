"""Inspect the raw and final order for one distinctive chat phrase."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
FINAL = HERE / "all_apps_wide_2026-08-26_chat_by_partner_goodshape_FINAL.csv"
RAW_CHAT = HERE / "ChatMessages-2026-08-26 (3).csv"
PHRASE = "sry i already agreed to spt purple"


def utc(value: str) -> str:
    return datetime.fromtimestamp(float(value), tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S.%f UTC"
    )


final_rows = list(csv.DictReader(FINAL.open(encoding="utf-8-sig", newline="")))
chat_rows = list(csv.DictReader(RAW_CHAT.open(encoding="utf-8-sig", newline="")))
hits = [
    (index, row) for index, row in enumerate(final_rows, start=2)
    if PHRASE in row.get("chat_transcript", "")
]
for index, row in hits:
    print("FINAL_ROW", index)
    print(json.dumps({k: row.get(k, "") for k in (
        "session.code", "group_id", "code", "id_in_session",
        "focal_player_id", "partner_id", "chat_channel",
    )}, ensure_ascii=False))
    print(json.dumps(json.loads(row["chat_transcript"]), ensure_ascii=False, indent=2))
    session = row["session.code"]
    group = row["group_id"]
    focal = int(row["focal_player_id"])
    partner = int(row["partner_id"])
    channel_suffix = f"-bargaining_tdl_main-{group}_{min(focal, partner)}_{max(focal, partner)}"
    raw_pair = [
        (raw_index, raw) for raw_index, raw in enumerate(chat_rows, start=2)
        if raw.get("session_code") == session
        and raw.get("channel", "").endswith(channel_suffix)
    ]
    for title, values in (
        ("RAW_FILE_ORDER", raw_pair),
        ("RAW_TIMESTAMP_ORDER", sorted(raw_pair, key=lambda item: float(item[1]["timestamp"]))),
    ):
        print(title)
        for raw_index, raw in values:
            print(json.dumps({
                "raw_row": raw_index,
                "timestamp_raw": raw["timestamp"],
                "timestamp_utc": utc(raw["timestamp"]),
                "participant_code": raw["participant_code"],
                "body": raw["body"],
            }, ensure_ascii=False))
