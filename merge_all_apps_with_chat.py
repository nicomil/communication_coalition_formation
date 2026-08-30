"""Merge the official oTree wide export with the official chat export.

Outputs one participant-level file and one participant-by-partner file.
Only the Python standard library is used so the script is portable and auditable.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WIDE = Path("docs/all_apps_wide_2026-08-17.csv")
DEFAULT_CHAT = Path("docs/ChatMessages-2026-08-17.csv")
DEFAULT_AGGREGATED = Path("docs/all_apps_wide_2026-08-17_chat_aggregated.csv")
DEFAULT_BY_PARTNER = Path("docs/all_apps_wide_2026-08-17_chat_by_partner.csv")
DEFAULT_AUDIT = Path("docs/all_apps_wide-2026-08-17_chat_audit.md")

TOPOLOGY = {1: {"left": 3, "right": 2}, 2: {"left": 1, "right": 3}, 3: {"left": 2, "right": 1}}
COLORS = {1: "Yellow", 2: "Orange", 3: "Purple"}
CHANNEL_RE = re.compile(r"^.+-bargaining_tdl_main-(\d+)_(\d+)_(\d+)$")


@dataclass(frozen=True)
class Message:
    session_code: str
    group_id: str
    id_a: int
    id_b: int
    sender_id: int | None
    receiver_id: int | None
    nickname: str
    body: str
    timestamp: str
    participant_code: str
    channel: str
    parse_status: str


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def required(row: dict[str, str], *names: str) -> str:
    for name in names:
        if name in row:
            return (row.get(name) or "").strip()
    return ""


def parse_int(value: str) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_channel(channel: str, nickname: str) -> tuple[str, int | None, int | None, int | None, str]:
    match = CHANNEL_RE.match(channel or "")
    if not match:
        return "", None, None, None, "malformed_channel"
    group_id, id_a, id_b = match.groups()
    id_a_i, id_b_i = int(id_a), int(id_b)
    if id_a_i not in COLORS or id_b_i not in COLORS or id_a_i >= id_b_i:
        return group_id, id_a_i, id_b_i, None, "invalid_player_pair"

    # This is the established oTree chat convention in process_chat.py.
    pair_map = {
        (1, 2, "LeftPartner"): 1,
        (1, 2, "RightPartner"): 2,
        (2, 3, "LeftPartner"): 2,
        (2, 3, "RightPartner"): 3,
        (1, 3, "LeftPartner"): 3,
        (1, 3, "RightPartner"): 1,
    }
    sender = pair_map.get((id_a_i, id_b_i, nickname))
    if sender is None:
        return group_id, id_a_i, id_b_i, None, "unknown_nickname_for_pair"
    receiver = id_b_i if sender == id_a_i else id_a_i
    return group_id, id_a_i, id_b_i, (sender * 10 + receiver), "ok"


def load_messages(path: Path) -> tuple[list[Message], Counter[str]]:
    headers, rows = read_csv(path)
    required_headers = {"session_code", "channel", "nickname", "body", "timestamp", "participant_code"}
    missing = required_headers - set(headers)
    if missing:
        raise ValueError(f"Chat file missing required columns: {sorted(missing)}")
    statuses: Counter[str] = Counter()
    messages: list[Message] = []
    for row in rows:
        session = (row.get("session_code") or "").strip()
        nickname = (row.get("nickname") or "").strip()
        channel = (row.get("channel") or "").strip()
        group_id, id_a, id_b, packed_ids, status = parse_channel(channel, nickname)
        sender = receiver = None
        if packed_ids is not None:
            sender, receiver = divmod(packed_ids, 10)
        statuses[status] += 1
        messages.append(Message(session, group_id, id_a or 0, id_b or 0, sender, receiver,
                                nickname, row.get("body") or "", row.get("timestamp") or "",
                                row.get("participant_code") or "", channel, status))
    return messages, statuses


def group_key(session: str, group_id: str) -> tuple[str, str]:
    return session, str(group_id or "").strip()


def safe_timestamp(value: str) -> tuple[int, float | str]:
    try:
        return 0, float(value)
    except (TypeError, ValueError):
        return 1, str(value)


def message_record(message: Message) -> dict[str, object]:
    sender = COLORS.get(message.sender_id, "Unknown")
    receiver = COLORS.get(message.receiver_id, "Unknown")
    return {
        "timestamp": message.timestamp,
        "from_id": message.sender_id,
        "from_color": sender,
        "to_id": message.receiver_id,
        "to_color": receiver,
        "nickname": message.nickname,
        "participant_code": message.participant_code,
        "body": message.body,
        "channel": message.channel,
        "parse_status": message.parse_status,
    }


def transcript_json(messages: list[Message]) -> str:
    """Serialize every message in one valid, single-line JSON array."""
    return json.dumps(
        [message_record(message) for message in messages],
        ensure_ascii=False,
        separators=(",", ":"),
    )


def target_from_choice(choice: str, focal_id: int, side: str) -> tuple[str, str]:
    if choice not in {"Left", "Right"} or focal_id not in TOPOLOGY:
        return ("NoOne", "NoOne") if choice == "NoOne" else ("", "")
    target_id = TOPOLOGY[focal_id][choice.lower()]
    return str(target_id), COLORS[target_id]


def target_from_guess(choice: str, focal_id: int, guessed_partner_side: str) -> tuple[str, str]:
    if choice == "NoOne":
        return "NoOne", "NoOne"
    if focal_id not in TOPOLOGY or guessed_partner_side not in {"left", "right"}:
        return "", ""
    partner_id = TOPOLOGY[focal_id][guessed_partner_side]
    # The guess is expressed from the guessed partner's point of view.
    # Left partner: Right means focal, Left means focal's right partner.
    # Right partner: Left means focal, Right means focal's left partner.
    if (guessed_partner_side == "left" and choice == "Right") or (
        guessed_partner_side == "right" and choice == "Left"
    ):
        target_id = focal_id
    else:
        other_side = "right" if guessed_partner_side == "left" else "left"
        target_id = TOPOLOGY[focal_id][other_side]
    return str(target_id), COLORS[target_id]


def target_from_signal(signal: str, focal_id: int, recipient_side: str, received: bool = False) -> tuple[str, str]:
    if signal == "support_none":
        return "NoOne", "NoOne"
    if focal_id not in TOPOLOGY or recipient_side not in {"left", "right"}:
        return "", ""
    if not received:
        target_side = recipient_side if signal == "split_you" else ("right" if recipient_side == "left" else "left")
    else:
        # For a received signal, split_you means the focal player; split_other
        # means the other player from the sender's perspective.
        target_side = None if signal == "split_you" else ("right" if recipient_side == "left" else "left")
    if target_side is None:
        return str(focal_id), COLORS[focal_id]
    target_id = TOPOLOGY[focal_id][target_side]
    return str(target_id), COLORS[target_id]


def add_choice_columns(row: dict[str, str]) -> None:
    focal_id = parse_int(row.get("bargaining_tdl_main.1.player.id_in_group", ""))
    if focal_id not in TOPOLOGY:
        for name in ("decision_target_id", "decision_target_color", "guess_left_target_id", "guess_left_target_color",
                     "guess_right_target_id", "guess_right_target_color", "signal_left_target_id",
                     "signal_left_target_color", "signal_right_target_id", "signal_right_target_color",
                     "received_signal_left_target_id", "received_signal_left_target_color",
                     "received_signal_right_target_id", "received_signal_right_target_color"):
            row[name] = ""
        return
    decision_id, decision_color = target_from_choice(row.get("bargaining_tdl_main.1.player.decision_choice", ""), focal_id, "")
    gl_id, gl_color = target_from_guess(row.get("bargaining_tdl_main.1.player.guess_left_choice", ""), focal_id, "left")
    gr_id, gr_color = target_from_guess(row.get("bargaining_tdl_main.1.player.guess_right_choice", ""), focal_id, "right")
    sl_id, sl_color = target_from_signal(row.get("bargaining_tdl_main.1.player.signal_left", ""), focal_id, "left")
    sr_id, sr_color = target_from_signal(row.get("bargaining_tdl_main.1.player.signal_right", ""), focal_id, "right")
    rsl_id, rsl_color = target_from_signal(row.get("bargaining_tdl_main.1.player.received_signal_left", ""), focal_id, "left", True)
    rsr_id, rsr_color = target_from_signal(row.get("bargaining_tdl_main.1.player.received_signal_right", ""), focal_id, "right", True)
    row.update({
        "focal_player_id": str(focal_id), "focal_player_color": COLORS[focal_id],
        "decision_target_id": decision_id, "decision_target_color": decision_color,
        "guess_left_target_id": gl_id, "guess_left_target_color": gl_color,
        "guess_right_target_id": gr_id, "guess_right_target_color": gr_color,
        "signal_left_target_id": sl_id, "signal_left_target_color": sl_color,
        "signal_right_target_id": sr_id, "signal_right_target_color": sr_color,
        "received_signal_left_target_id": rsl_id, "received_signal_left_target_color": rsl_color,
        "received_signal_right_target_id": rsr_id, "received_signal_right_target_color": rsr_color,
    })


def build_outputs(wide_rows: list[dict[str, str]], messages: list[Message]) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int], list[str]]:
    participant_to_group = {
        (required(row, "session.code"), required(row, "participant.code")): required(
            row, "bargaining_tdl_main.1.group.id_in_subsession"
        )
        for row in wide_rows
        if required(row, "session.code") and required(row, "participant.code")
    }
    by_group: defaultdict[tuple[str, str], list[Message]] = defaultdict(list)
    by_dyad: defaultdict[tuple[str, str, int, int], list[Message]] = defaultdict(list)
    unmatched: list[str] = []
    group_members: defaultdict[tuple[str, str], dict[int, str]] = defaultdict(dict)
    for row in wide_rows:
        session = required(row, "session.code")
        group = required(row, "bargaining_tdl_main.1.group.id_in_subsession")
        player_id = parse_int(row.get("bargaining_tdl_main.1.player.id_in_group", ""))
        code = required(row, "participant.code")
        if session and group and player_id in TOPOLOGY and code:
            group_members[group_key(session, group)][player_id] = code
    for message in messages:
        if message.parse_status != "ok":
            unmatched.append(f"message channel={message.channel!r}: {message.parse_status}")
            continue
        canonical_group = participant_to_group.get((message.session_code, message.participant_code), "")
        if not canonical_group:
            unmatched.append(f"message participant={message.participant_code!r}, session={message.session_code!r}: sender not found in wide export")
            continue
        members = group_members.get(group_key(message.session_code, canonical_group), {})
        expected_sender_code = members.get(message.sender_id or -1, "")
        if expected_sender_code != message.participant_code:
            unmatched.append(
                f"message channel={message.channel!r}: channel sender id {message.sender_id} "
                f"does not match participant {message.participant_code!r} in canonical group {canonical_group!r}"
            )
            continue
        if message.receiver_id not in members:
            unmatched.append(
                f"message channel={message.channel!r}: receiver id {message.receiver_id} "
                f"not present in canonical group {canonical_group!r}"
            )
            continue
        by_group[group_key(message.session_code, canonical_group)].append(message)
        by_dyad[(message.session_code, canonical_group, message.id_a, message.id_b)].append(message)
    for group_messages in by_group.values():
        group_messages.sort(key=lambda m: safe_timestamp(m.timestamp))
    for dyad_messages in by_dyad.values():
        dyad_messages.sort(key=lambda m: safe_timestamp(m.timestamp))

    agg_rows: list[dict[str, str]] = []
    long_rows: list[dict[str, str]] = []
    wide_codes: set[tuple[str, str]] = set()
    for original in wide_rows:
        row = dict(original)
        session = required(row, "session.code")
        group_id = required(row, "bargaining_tdl_main.1.group.id_in_subsession")
        participant_code = required(row, "participant.code")
        focal_id = parse_int(row.get("bargaining_tdl_main.1.player.id_in_group", ""))
        wide_codes.add((session, participant_code))
        add_choice_columns(row)
        group_messages = by_group.get(group_key(session, group_id), [])
        sent = [m for m in group_messages if m.participant_code == participant_code or m.sender_id == focal_id]
        received = [m for m in group_messages if m.receiver_id == focal_id]
        row.update({
            "chat_group_key": f"{session}|{group_id}" if session and group_id else "",
            "chat_group_status": "matched" if group_messages else ("no_group" if not group_id else "no_messages"),
            "chat_message_count_group": str(len(group_messages)),
            "chat_message_count_sent": str(len(sent)),
            "chat_message_count_received": str(len(received)),
            "chat_first_timestamp": group_messages[0].timestamp if group_messages else "",
            "chat_last_timestamp": group_messages[-1].timestamp if group_messages else "",
            "chat_transcript_group": transcript_json(group_messages),
        })
        agg_rows.append(row)

        if focal_id not in TOPOLOGY:
            sides = [("left", "", "", "", ""), ("right", "", "", "", "")]
        else:
            sides = []
            for side in ("left", "right"):
                partner_id = TOPOLOGY[focal_id][side]
                pair = tuple(sorted((focal_id, partner_id)))
                dyad_messages = by_dyad.get((session, group_id, pair[0], pair[1]), [])
                focal_messages = [m for m in dyad_messages if m.sender_id == focal_id or m.participant_code == participant_code]
                partner_messages = [m for m in dyad_messages if m.receiver_id == focal_id]
                sides.append((side, str(partner_id), COLORS[partner_id], dyad_messages, focal_messages, partner_messages))
        for item in sides:
            side, partner_id, partner_color, *rest = item
            dyad_messages = rest[0] if rest and isinstance(rest[0], list) else []
            focal_messages = rest[1] if len(rest) > 1 else []
            partner_messages = rest[2] if len(rest) > 2 else []
            out = dict(original)
            add_choice_columns(out)
            out.update({
                "chat_side": side,
                "partner_id": partner_id,
                "partner_color": partner_color,
                "chat_group_key": f"{session}|{group_id}" if session and group_id else "",
                "chat_status": "matched" if dyad_messages else ("no_group" if not group_id else "no_messages"),
                "chat_channel": dyad_messages[0].channel if dyad_messages else "",
                "chat_message_count": str(len(dyad_messages)),
                "chat_message_count_focal_sent": str(len(focal_messages)),
                "chat_message_count_partner_sent": str(len(partner_messages)),
                "chat_first_timestamp": dyad_messages[0].timestamp if dyad_messages else "",
                "chat_last_timestamp": dyad_messages[-1].timestamp if dyad_messages else "",
                "chat_transcript": transcript_json(dyad_messages),
            })
            long_rows.append(out)
    metrics = {
        "wide_rows": len(wide_rows), "aggregated_rows": len(agg_rows), "long_rows": len(long_rows),
        "expected_long_rows": len(wide_rows) * 2, "groups_with_messages": len(by_group),
        "dyads_with_messages": len(by_dyad), "wide_participants": len(wide_codes),
    }
    return agg_rows, long_rows, metrics, unmatched


def message_fingerprint(record: dict[str, object]) -> tuple[str, str, str, str, str, str]:
    return (
        str(record.get("channel", "")),
        str(record.get("participant_code", "")),
        str(record.get("timestamp", "")),
        str(record.get("nickname", "")),
        str(record.get("body", "")),
        str(record.get("parse_status", "")),
    )


def validate_complete_outputs(
    wide_headers: list[str],
    wide_rows: list[dict[str, str]],
    messages: list[Message],
    agg_rows: list[dict[str, str]],
    long_rows: list[dict[str, str]],
) -> list[str]:
    """Triple-check source coverage, source-column preservation and row shape."""
    failures: list[str] = []
    source_fps = {message_fingerprint(message_record(m)) for m in messages if m.parse_status == "ok"}
    agg_fps: set[tuple[str, str, str, str, str, str]] = set()
    long_fps: set[tuple[str, str, str, str, str, str]] = set()
    try:
        for row in agg_rows:
            payload = json.loads(row.get("chat_transcript_group", "[]"))
            if not isinstance(payload, list):
                failures.append("aggregate transcript is not a JSON list")
            agg_fps.update(message_fingerprint(item) for item in payload)
        for row in long_rows:
            payload = json.loads(row.get("chat_transcript", "[]"))
            if not isinstance(payload, list):
                failures.append("left/right transcript is not a JSON list")
            long_fps.update(message_fingerprint(item) for item in payload)
    except (json.JSONDecodeError, TypeError) as exc:
        failures.append(f"invalid transcript JSON: {exc}")
    if agg_fps != source_fps:
        failures.append(f"aggregate message coverage mismatch: source={len(source_fps)} output={len(agg_fps)}")
    if long_fps != source_fps:
        failures.append(f"left/right message coverage mismatch: source={len(source_fps)} output={len(long_fps)}")

    original_by_key = {(required(r, "session.code"), required(r, "participant.code")): r for r in wide_rows}
    agg_by_key = {(required(r, "session.code"), required(r, "participant.code")): r for r in agg_rows}
    if set(original_by_key) != set(agg_by_key):
        failures.append("aggregate participant key set differs from original wide file")
    else:
        for key, original in original_by_key.items():
            if any(agg_by_key[key].get(column, "") != original.get(column, "") for column in wide_headers):
                failures.append(f"original column value changed in aggregate row {key}")
                break
    long_counts = Counter((required(r, "session.code"), required(r, "participant.code")) for r in long_rows)
    if any(count != 2 for count in long_counts.values()) or set(long_counts) != set(original_by_key):
        failures.append("left/right output does not contain exactly two rows per original participant")
    for row in long_rows:
        key = (required(row, "session.code"), required(row, "participant.code"))
        original = original_by_key.get(key)
        if original and any(row.get(column, "") != original.get(column, "") for column in wide_headers):
            failures.append(f"original column value changed in left/right row {key}")
            break
    return failures


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_audit(path: Path, metrics: dict[str, int], statuses: Counter[str], unmatched: list[str], wide_headers: list[str], validation_failures: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Audit merge all_apps_wide + ChatMessages", "", "## Conteggi", ""]
    for key, value in metrics.items(): lines.append(f"- `{key}`: **{value}**")
    lines += ["", "## Stato parsing dei messaggi", ""]
    for key, value in sorted(statuses.items()): lines.append(f"- `{key}`: **{value}**")
    lines += ["", "## Controlli", "", f"- Output aggregato con una riga per partecipante: **{'PASS' if metrics['aggregated_rows'] == metrics['wide_rows'] else 'FAIL'}**", f"- Output left/right con due righe per partecipante: **{'PASS' if metrics['long_rows'] == metrics['expected_long_rows'] else 'FAIL'}**", f"- Colonne originali all_apps_wide preservate: **{len(wide_headers)}** colonne di base", "", "## Triple check", "", f"- Copertura messaggi nell’aggregato: **{'PASS' if not any('aggregate message coverage' in x for x in validation_failures) else 'FAIL'}**", f"- Copertura messaggi nel file left/right: **{'PASS' if not any('left/right message coverage' in x for x in validation_failures) else 'FAIL'}**", f"- Conservazione valori originali: **{'PASS' if not any('original column value changed' in x or 'participant key set' in x for x in validation_failures) else 'FAIL'}**", f"- JSON transcript valido: **{'PASS' if not any('JSON' in x for x in validation_failures) else 'FAIL'}**"]
    if validation_failures:
        lines.append("- Dettagli: " + " | ".join(validation_failures))
    lines += ["", "## Messaggi non abbinati", ""]
    lines.extend(f"- {item}" for item in unmatched) if unmatched else lines.append("Nessun messaggio non abbinato rilevato.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wide", type=Path, default=DEFAULT_WIDE)
    parser.add_argument("--chat", type=Path, default=DEFAULT_CHAT)
    parser.add_argument("--aggregated-output", type=Path, default=DEFAULT_AGGREGATED)
    parser.add_argument("--by-partner-output", type=Path, default=DEFAULT_BY_PARTNER)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--strict", action="store_true", help="fail if parsing or row-count checks fail")
    args = parser.parse_args()

    wide_headers, wide_rows = read_csv(args.wide)
    required_wide = {"participant.code", "session.code", "bargaining_tdl_main.1.group.id_in_subsession", "bargaining_tdl_main.1.player.id_in_group"}
    missing = required_wide - set(wide_headers)
    if missing:
        raise ValueError(f"Wide file missing required columns: {sorted(missing)}")
    messages, statuses = load_messages(args.chat)
    agg_rows, long_rows, metrics, unmatched = build_outputs(wide_rows, messages)
    added_agg = list(agg_rows[0].keys()) if agg_rows else []
    added_long = list(long_rows[0].keys()) if long_rows else []
    validation_failures = validate_complete_outputs(wide_headers, wide_rows, messages, agg_rows, long_rows)
    write_csv(args.aggregated_output, agg_rows, list(dict.fromkeys(wide_headers + added_agg)))
    write_csv(args.by_partner_output, long_rows, list(dict.fromkeys(wide_headers + added_long)))

    write_audit(args.audit, metrics, statuses, unmatched, wide_headers, validation_failures)

    failures = [name for name, ok in {
        "aggregated_row_count": metrics["aggregated_rows"] == metrics["wide_rows"],
        "by_partner_row_count": metrics["long_rows"] == metrics["expected_long_rows"],
        "message_parsing": statuses.get("malformed_channel", 0) == 0 and statuses.get("invalid_player_pair", 0) == 0 and statuses.get("unknown_nickname_for_pair", 0) == 0,
        "message_participant_matching": not unmatched,
        "triple_check_source_coverage_and_preservation": not validation_failures,
    }.items() if not ok]
    failures.extend(validation_failures)
    print(json.dumps({"metrics": metrics, "parse_statuses": dict(statuses), "failures": failures,
                      "aggregated_output": str(args.aggregated_output), "by_partner_output": str(args.by_partner_output),
                      "audit": str(args.audit)}, ensure_ascii=False, indent=2))
    if args.strict and failures:
        raise SystemExit("Strict validation failed: " + ", ".join(failures))


if __name__ == "__main__":
    main()
