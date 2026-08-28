"""Merge an oTree wide export with ChatMessages using an explicit column whitelist.

The script writes:
1. one row per input participant, with the full group conversation;
2. two rows per input participant (left/right partner), with dyadic conversation.

Only the Python standard library is required.  Validation is strict by default:
no output is committed unless every chat row can be assigned unambiguously.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


BASE_COLUMNS = [
    "participant.id_in_session",
    "participant.code",
    "participant.label",
    "participant._index_in_pages",
    "participant.payoff",
    "participant.inactive_excluded",
    "participant.inactive_excluded_reason",
    "participant.group_dropped",
    "participant.part1_payoff_eligible",
    "participant.group_outcome",
    "participant.part1_group_id",
    "session.code",
    "bargaining_tdl_intro.1.player.time_welcome",
    "bargaining_tdl_intro.1.player.time_instructions_part1",
    "bargaining_tdl_intro.1.player.time_control_questions",
    "bargaining_tdl_main.1.player.id_in_group",
    "bargaining_tdl_main.1.player.payoff",
    "bargaining_tdl_main.1.player.player_color",
    "bargaining_tdl_main.1.player.treatment",
    "bargaining_tdl_main.1.player.part1_calculated_payoff",
    "bargaining_tdl_main.1.player.signal_left",
    "bargaining_tdl_main.1.player.signal_right",
    "bargaining_tdl_main.1.player.first_intention_selected",
    "bargaining_tdl_main.1.player.guess_left_confidence",
    "bargaining_tdl_main.1.player.guess_right_confidence",
    "bargaining_tdl_main.1.player.time_welcome",
    "bargaining_tdl_main.1.player.time_chat",
    "bargaining_tdl_main.1.player.time_signals",
    "bargaining_tdl_main.1.player.decision_choice",
    "bargaining_tdl_main.1.player.decision_option_1",
    "bargaining_tdl_main.1.player.decision_option_2",
    "bargaining_tdl_main.1.player.decision_option_3",
    "bargaining_tdl_main.1.player.received_signal_left",
    "bargaining_tdl_main.1.player.received_signal_right",
    "bargaining_tdl_main.1.player.id_player_on_the_left",
    "bargaining_tdl_main.1.player.id_player_on_the_right",
    "bargaining_tdl_main.1.player.id_player_visualized_on_the_left",
    "bargaining_tdl_main.1.player.id_player_visualized_on_the_right",
    "bargaining_tdl_main.1.player.time_decision",
    "bargaining_tdl_main.1.player.time_post_decision_confidence",
    "bargaining_tdl_main.1.player.chat_interrupted",
    "bargaining_tdl_main.1.player.part1_payoff_eligible",
    "bargaining_tdl_main.1.player.decision_inactive",
    "bargaining_tdl_main.1.player.signal_inactive",
    "bargaining_tdl_main.1.player.received_signal_left_inactive",
    "bargaining_tdl_main.1.player.received_signal_right_inactive",
    "bargaining_tdl_main.1.player.guess_left_choice",
    "bargaining_tdl_main.1.player.guess_right_choice",
    "bargaining_tdl_main.1.group.id_in_subsession",
    "bargaining_tdl_main.1.group.grp_coordinate",
    "bargaining_tdl_main.1.group.group_outcome",
    "bargaining_tdl_main.1.group.chat_left_p1",
    "bargaining_tdl_main.1.group.chat_left_p2",
    "bargaining_tdl_main.1.group.chat_left_p3",
    "bargaining_tdl_main.1.group.group_dropped",
    "bargaining_tdl_survey.1.player.gender",
    "bargaining_tdl_survey.1.player.birth_year",
    "bargaining_tdl_survey.1.player.field_of_study",
    "bargaining_tdl_survey.1.player.university_years",
    "bargaining_tdl_survey.1.player.main_situation",
    "bargaining_tdl_survey.1.player.job_type",
    "bargaining_tdl_survey.1.player.sd3_mach_01",
    "bargaining_tdl_survey.1.player.sd3_mach_02",
    "bargaining_tdl_survey.1.player.sd3_mach_03",
    "bargaining_tdl_survey.1.player.sd3_mach_04",
    "bargaining_tdl_survey.1.player.sd3_mach_05",
    "bargaining_tdl_survey.1.player.sd3_mach_06",
    "bargaining_tdl_survey.1.player.sd3_mach_07",
    "bargaining_tdl_survey.1.player.sd3_mach_08",
    "bargaining_tdl_survey.1.player.sd3_mach_09",
    "bargaining_tdl_survey.1.player.sd3_narc_01",
    "bargaining_tdl_survey.1.player.sd3_narc_02",
    "bargaining_tdl_survey.1.player.sd3_narc_03",
    "bargaining_tdl_survey.1.player.sd3_narc_04",
    "bargaining_tdl_survey.1.player.sd3_narc_05",
    "bargaining_tdl_survey.1.player.sd3_narc_06",
    "bargaining_tdl_survey.1.player.sd3_narc_07",
    "bargaining_tdl_survey.1.player.sd3_narc_08",
    "bargaining_tdl_survey.1.player.sd3_narc_09",
    "bargaining_tdl_survey.1.player.sd3_psych_01",
    "bargaining_tdl_survey.1.player.sd3_psych_02",
    "bargaining_tdl_survey.1.player.sd3_psych_03",
    "bargaining_tdl_survey.1.player.sd3_psych_04",
    "bargaining_tdl_survey.1.player.sd3_psych_05",
    "bargaining_tdl_survey.1.player.sd3_psych_06",
    "bargaining_tdl_survey.1.player.sd3_psych_07",
    "bargaining_tdl_survey.1.player.sd3_psych_08",
    "bargaining_tdl_survey.1.player.sd3_psych_09",
    "bargaining_tdl_survey.1.player.willingness_future",
    "bargaining_tdl_survey.1.player.willingness_risk",
    "bargaining_tdl_survey.1.player.reciprocity_positive",
    "bargaining_tdl_survey.1.player.reciprocity_negative",
    "bargaining_tdl_survey.1.player.willingness_donate",
    "bargaining_tdl_survey.1.player.trust_general",
    "bargaining_tdl_survey.1.player.beauty_contest_guess",
    "bargaining_tdl_survey.1.player.instructions_clarity",
    "bargaining_tdl_survey.1.player.general_comment",
    "bargaining_tdl_survey.1.player.time_survey_questions",
    "bargaining_tdl_survey.1.player.time_survey_sd3_mach",
    "bargaining_tdl_survey.1.player.time_survey_sd3_narc",
    "bargaining_tdl_survey.1.player.time_survey_sd3_psych",
    "bargaining_tdl_survey.1.player.time_survey_page4",
    "bargaining_tdl_survey.1.player.time_survey_page10",
    "bargaining_tdl_survey.1.player.time_survey_feedback",
]

CHOICE_COLUMNS = [
    "focal_player_id", "focal_player_color",
    "decision_target_id", "decision_target_color",
    "guess_left_target_id", "guess_left_target_color",
    "guess_right_target_id", "guess_right_target_color",
    "signal_left_target_id", "signal_left_target_color",
    "signal_right_target_id", "signal_right_target_color",
    "received_signal_left_target_id", "received_signal_left_target_color",
    "received_signal_right_target_id", "received_signal_right_target_color",
]

AGGREGATE_COLUMNS = [
    "chat_group_key", "chat_group_status", "chat_message_count_group",
    "chat_message_count_sent", "chat_message_count_received",
    "chat_first_timestamp", "chat_last_timestamp", "chat_transcript_group",
]

PARTNER_COLUMNS = [
    "chat_side", "partner_id", "partner_color", "chat_group_key",
    "chat_status", "chat_channel", "chat_message_count",
    "chat_message_count_focal_sent", "chat_message_count_partner_sent",
    "chat_first_timestamp", "chat_last_timestamp", "chat_transcript",
]

TOPOLOGY = {1: {"left": 3, "right": 2}, 2: {"left": 1, "right": 3}, 3: {"left": 2, "right": 1}}
COLORS = {1: "Yellow", 2: "Orange", 3: "Purple"}
CHANNEL_RE = re.compile(r"^.+-bargaining_tdl_main-(\d+)_(\d+)_(\d+)$")


@dataclass(frozen=True)
class Message:
    sequence: int
    session_code: str
    group_id: str
    id_a: int
    id_b: int
    sender_id: int
    receiver_id: int
    nickname: str
    body: str
    timestamp: str
    participant_code: str
    channel: str


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV without a header: {path}")
        return list(reader.fieldnames), list(reader)


def parse_int(value: str) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def chat_group_id(row: dict[str, str]) -> str:
    """Use the immutable Part-1 group, falling back only for legacy exports."""
    return (row.get("participant.part1_group_id") or row.get("bargaining_tdl_main.1.group.id_in_subsession") or "").strip()


def sort_key(message: Message) -> tuple[int, float | str, int]:
    try:
        return 0, float(message.timestamp), message.sequence
    except ValueError:
        return 1, message.timestamp, message.sequence


def resolve_messages(chat_path: Path, wide_rows: list[dict[str, str]]) -> tuple[list[Message], dict[str, int]]:
    headers, chat_rows = read_csv(chat_path)
    required = {"session_code", "participant_code", "channel", "nickname", "body", "timestamp"}
    missing = sorted(required - set(headers))
    if missing:
        raise ValueError(f"Chat file missing columns: {missing}")

    participant = {}
    for row in wide_rows:
        key = ((row.get("session.code") or "").strip(), (row.get("participant.code") or "").strip())
        if key in participant:
            raise ValueError(f"Duplicate participant key in wide export: {key}")
        participant[key] = (parse_int(row.get("bargaining_tdl_main.1.player.id_in_group", "")), chat_group_id(row))

    messages: list[Message] = []
    errors: list[str] = []
    for sequence, row in enumerate(chat_rows):
        session = (row.get("session_code") or "").strip()
        code = (row.get("participant_code") or "").strip()
        channel = (row.get("channel") or "").strip()
        match = CHANNEL_RE.match(channel)
        if not match:
            errors.append(f"row {sequence + 2}: malformed channel {channel!r}")
            continue
        group_id, id_a_s, id_b_s = match.groups()
        id_a, id_b = int(id_a_s), int(id_b_s)
        if id_a not in COLORS or id_b not in COLORS or id_a >= id_b:
            errors.append(f"row {sequence + 2}: invalid player pair in {channel!r}")
            continue
        sender_info = participant.get((session, code))
        if sender_info is None:
            errors.append(f"row {sequence + 2}: participant {(session, code)!r} absent from wide export")
            continue
        sender_id, canonical_group = sender_info
        if canonical_group != group_id:
            errors.append(f"row {sequence + 2}: channel group {group_id!r} != Part-1 group {canonical_group!r}")
            continue
        if sender_id not in (id_a, id_b):
            errors.append(f"row {sequence + 2}: sender id {sender_id!r} is not in channel pair {(id_a, id_b)!r}")
            continue
        receiver_id = id_b if sender_id == id_a else id_a
        messages.append(Message(
            sequence, session, group_id, id_a, id_b, sender_id, receiver_id,
            row.get("nickname") or "", row.get("body") or "", row.get("timestamp") or "", code, channel,
        ))
    if errors:
        preview = "\n".join(errors[:20])
        raise ValueError(f"Could not resolve {len(errors)} chat rows. First errors:\n{preview}")
    return messages, {"chat_rows": len(chat_rows), "chat_rows_resolved": len(messages)}


def message_record(message: Message) -> dict[str, object]:
    return {
        "timestamp": message.timestamp,
        "from_id": message.sender_id,
        "from_color": COLORS[message.sender_id],
        "to_id": message.receiver_id,
        "to_color": COLORS[message.receiver_id],
        "nickname": message.nickname,
        "participant_code": message.participant_code,
        "body": message.body,
        "channel": message.channel,
        "parse_status": "ok",
    }


def transcript(messages: list[Message]) -> str:
    return json.dumps([message_record(m) for m in messages], ensure_ascii=False, separators=(",", ":"))


def target_from_choice(choice: str, focal_id: int) -> tuple[str, str]:
    if choice == "NoOne":
        return "NoOne", "NoOne"
    if choice not in {"Left", "Right"} or focal_id not in TOPOLOGY:
        return "", ""
    target = TOPOLOGY[focal_id][choice.lower()]
    return str(target), COLORS[target]


def target_from_guess(choice: str, focal_id: int, partner_side: str) -> tuple[str, str]:
    if choice == "NoOne":
        return "NoOne", "NoOne"
    if choice not in {"Left", "Right"} or focal_id not in TOPOLOGY:
        return "", ""
    if (partner_side == "left" and choice == "Right") or (partner_side == "right" and choice == "Left"):
        target = focal_id
    else:
        target = TOPOLOGY[focal_id]["right" if partner_side == "left" else "left"]
    return str(target), COLORS[target]


def target_from_signal(signal: str, focal_id: int, recipient_side: str, received: bool = False) -> tuple[str, str]:
    if signal == "support_none":
        return "NoOne", "NoOne"
    if signal not in {"split_you", "split_other"} or focal_id not in TOPOLOGY:
        return "", ""
    if received and signal == "split_you":
        target = focal_id
    else:
        side = recipient_side if signal == "split_you" else ("right" if recipient_side == "left" else "left")
        target = TOPOLOGY[focal_id][side]
    return str(target), COLORS[target]


def choice_values(row: dict[str, str]) -> dict[str, str]:
    focal = parse_int(row.get("bargaining_tdl_main.1.player.id_in_group", ""))
    values = {column: "" for column in CHOICE_COLUMNS}
    if focal not in TOPOLOGY:
        return values
    decision = target_from_choice(row.get("bargaining_tdl_main.1.player.decision_choice", ""), focal)
    guess_left = target_from_guess(row.get("bargaining_tdl_main.1.player.guess_left_choice", ""), focal, "left")
    guess_right = target_from_guess(row.get("bargaining_tdl_main.1.player.guess_right_choice", ""), focal, "right")
    signal_left = target_from_signal(row.get("bargaining_tdl_main.1.player.signal_left", ""), focal, "left")
    signal_right = target_from_signal(row.get("bargaining_tdl_main.1.player.signal_right", ""), focal, "right")
    received_left = target_from_signal(row.get("bargaining_tdl_main.1.player.received_signal_left", ""), focal, "left", True)
    received_right = target_from_signal(row.get("bargaining_tdl_main.1.player.received_signal_right", ""), focal, "right", True)
    pairs = [
        ("focal_player", (str(focal), COLORS[focal])), ("decision_target", decision),
        ("guess_left_target", guess_left), ("guess_right_target", guess_right),
        ("signal_left_target", signal_left), ("signal_right_target", signal_right),
        ("received_signal_left_target", received_left), ("received_signal_right_target", received_right),
    ]
    for stem, (target_id, color) in pairs:
        values[f"{stem}_id"] = target_id
        values[f"{stem}_color"] = color
    return values


def build_outputs(wide_rows: list[dict[str, str]], messages: list[Message]) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int]]:
    by_group: defaultdict[tuple[str, str], list[Message]] = defaultdict(list)
    by_dyad: defaultdict[tuple[str, str, int, int], list[Message]] = defaultdict(list)
    for message in messages:
        by_group[(message.session_code, message.group_id)].append(message)
        by_dyad[(message.session_code, message.group_id, message.id_a, message.id_b)].append(message)
    for values in by_group.values():
        values.sort(key=sort_key)
    for values in by_dyad.values():
        values.sort(key=sort_key)

    aggregated: list[dict[str, str]] = []
    by_partner: list[dict[str, str]] = []
    for source in wide_rows:
        session = (source.get("session.code") or "").strip()
        group = chat_group_id(source)
        focal = parse_int(source.get("bargaining_tdl_main.1.player.id_in_group", ""))
        base = {column: source.get(column, "") for column in BASE_COLUMNS}
        base.update(choice_values(source))
        group_messages = by_group.get((session, group), [])
        agg = dict(base)
        agg.update({
            "chat_group_key": f"{session}|{group}" if session and group else "",
            "chat_group_status": "matched" if group_messages else ("no_group" if not group else "no_messages"),
            "chat_message_count_group": str(len(group_messages)),
            "chat_message_count_sent": str(sum(m.sender_id == focal for m in group_messages)),
            "chat_message_count_received": str(sum(m.receiver_id == focal for m in group_messages)),
            "chat_first_timestamp": group_messages[0].timestamp if group_messages else "",
            "chat_last_timestamp": group_messages[-1].timestamp if group_messages else "",
            "chat_transcript_group": transcript(group_messages),
        })
        aggregated.append(agg)

        for side in ("left", "right"):
            partner_id = TOPOLOGY[focal][side] if focal in TOPOLOGY else None
            pair = tuple(sorted((focal, partner_id))) if partner_id is not None else None
            dyad = by_dyad.get((session, group, pair[0], pair[1]), []) if pair else []
            partner = dict(base)
            partner.update({
                "chat_side": side,
                "partner_id": str(partner_id) if partner_id is not None else "",
                "partner_color": COLORS[partner_id] if partner_id is not None else "",
                "chat_group_key": f"{session}|{group}" if session and group else "",
                "chat_status": "matched" if dyad else ("no_group" if not group else "no_messages"),
                "chat_channel": dyad[0].channel if dyad else "",
                "chat_message_count": str(len(dyad)),
                "chat_message_count_focal_sent": str(sum(m.sender_id == focal for m in dyad)),
                "chat_message_count_partner_sent": str(sum(m.sender_id == partner_id for m in dyad)),
                "chat_first_timestamp": dyad[0].timestamp if dyad else "",
                "chat_last_timestamp": dyad[-1].timestamp if dyad else "",
                "chat_transcript": transcript(dyad),
            })
            by_partner.append(partner)

    metrics = {
        "wide_rows": len(wide_rows),
        "aggregated_rows": len(aggregated),
        "by_partner_rows": len(by_partner),
        "expected_by_partner_rows": 2 * len(wide_rows),
        "messages": len(messages),
        "groups_with_messages": len(by_group),
        "dyads_with_messages": len(by_dyad),
    }
    return aggregated, by_partner, metrics


def write_csv_atomic(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", dir=path.parent, delete=False, suffix=".tmp") as handle:
        temp_path = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    temp_path.replace(path)


def validate(
    wide_rows: list[dict[str, str]], messages: list[Message],
    aggregated: list[dict[str, str]], by_partner: list[dict[str, str]],
) -> dict[str, object]:
    failures: list[str] = []
    if len(aggregated) != len(wide_rows):
        failures.append("aggregated row count differs from wide input")
    if len(by_partner) != 2 * len(wide_rows):
        failures.append("by-partner output does not have exactly two rows per wide row")
    if any(list(row) != BASE_COLUMNS + CHOICE_COLUMNS + AGGREGATE_COLUMNS for row in aggregated):
        failures.append("aggregated output schema/order mismatch")
    if any(list(row) != BASE_COLUMNS + CHOICE_COLUMNS + PARTNER_COLUMNS for row in by_partner):
        failures.append("by-partner output schema/order mismatch")

    source_keys = [(row.get("session.code", ""), row.get("participant.code", "")) for row in wide_rows]
    aggregate_keys = [(row.get("session.code", ""), row.get("participant.code", "")) for row in aggregated]
    if source_keys != aggregate_keys:
        failures.append("participant order/key mismatch in aggregated output")
    partner_keys = [(row.get("session.code", ""), row.get("participant.code", ""), row.get("chat_side", "")) for row in by_partner]
    expected_partner_keys = [(session, code, side) for session, code in source_keys for side in ("left", "right")]
    if partner_keys != expected_partner_keys:
        failures.append("participant/side order mismatch in by-partner output")

    for source, output in zip(wide_rows, aggregated):
        if any(output[column] != source.get(column, "") for column in BASE_COLUMNS):
            failures.append(f"whitelisted source value changed for participant {source.get('participant.code', '')!r}")
            break
    for index, source in enumerate(wide_rows):
        for output in by_partner[index * 2:index * 2 + 2]:
            if any(output[column] != source.get(column, "") for column in BASE_COLUMNS):
                failures.append(f"whitelisted source value changed in by-partner rows for participant {source.get('participant.code', '')!r}")
                break
        if failures and failures[-1].startswith("whitelisted source value changed in by-partner"):
            break

    expected_group: defaultdict[tuple[str, str], list[Message]] = defaultdict(list)
    expected_dyad: defaultdict[tuple[str, str, int, int], list[Message]] = defaultdict(list)
    for message in messages:
        expected_group[(message.session_code, message.group_id)].append(message)
        expected_dyad[(message.session_code, message.group_id, message.id_a, message.id_b)].append(message)
    for values in expected_group.values():
        values.sort(key=sort_key)
    for values in expected_dyad.values():
        values.sort(key=sort_key)
    if sum(map(len, expected_group.values())) != len(messages) or sum(map(len, expected_dyad.values())) != len(messages):
        failures.append("message assignment coverage mismatch")

    for row in aggregated:
        try:
            payload = json.loads(row["chat_transcript_group"])
            focal = parse_int(row.get("bargaining_tdl_main.1.player.id_in_group", ""))
            expected_messages = expected_group.get(((row.get("session.code") or "").strip(), chat_group_id(row)), [])
            expected_payload = [message_record(message) for message in expected_messages]
            if payload != expected_payload:
                failures.append("aggregate transcript differs from resolved source messages")
                break
            expected_counts = (
                len(expected_messages),
                sum(message.sender_id == focal for message in expected_messages),
                sum(message.receiver_id == focal for message in expected_messages),
            )
            actual_counts = (
                int(row["chat_message_count_group"]),
                int(row["chat_message_count_sent"]),
                int(row["chat_message_count_received"]),
            )
            if actual_counts != expected_counts:
                failures.append("invalid aggregate chat counts")
                break
        except (ValueError, TypeError, json.JSONDecodeError):
            failures.append("invalid aggregate transcript JSON")
            break
    for row in by_partner:
        try:
            payload = json.loads(row["chat_transcript"])
            session = (row.get("session.code") or "").strip()
            group = chat_group_id(row)
            focal = parse_int(row.get("bargaining_tdl_main.1.player.id_in_group", ""))
            partner = parse_int(row.get("partner_id", ""))
            pair = tuple(sorted((focal, partner))) if focal is not None and partner is not None else None
            expected_messages = expected_dyad.get((session, group, pair[0], pair[1]), []) if pair else []
            expected_payload = [message_record(message) for message in expected_messages]
            if payload != expected_payload:
                failures.append("by-partner transcript differs from resolved source messages")
                break
            expected_counts = (
                len(expected_messages),
                sum(message.sender_id == focal for message in expected_messages),
                sum(message.sender_id == partner for message in expected_messages),
            )
            actual_counts = (
                int(row["chat_message_count"]),
                int(row["chat_message_count_focal_sent"]),
                int(row["chat_message_count_partner_sent"]),
            )
            if actual_counts != expected_counts:
                failures.append("invalid by-partner chat counts")
                break
        except (ValueError, TypeError, json.JSONDecodeError):
            failures.append("invalid by-partner transcript JSON")
            break
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "base_columns_requested": len(BASE_COLUMNS),
        "aggregated_columns": len(BASE_COLUMNS + CHOICE_COLUMNS + AGGREGATE_COLUMNS),
        "by_partner_columns": len(BASE_COLUMNS + CHOICE_COLUMNS + PARTNER_COLUMNS),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wide", type=Path, required=True)
    parser.add_argument("--chat", type=Path, required=True)
    parser.add_argument("--aggregated-output", type=Path, required=True)
    parser.add_argument("--by-partner-output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()

    wide_headers, wide_rows = read_csv(args.wide)
    missing = [column for column in BASE_COLUMNS if column not in wide_headers]
    if missing:
        raise ValueError(f"Wide file missing {len(missing)} requested columns: {missing}")
    messages, chat_metrics = resolve_messages(args.chat, wide_rows)
    aggregated, by_partner, metrics = build_outputs(wide_rows, messages)
    checks = validate(wide_rows, messages, aggregated, by_partner)
    audit = {
        "inputs": {"wide": str(args.wide.resolve()), "chat": str(args.chat.resolve())},
        "outputs": {"aggregated": str(args.aggregated_output.resolve()), "by_partner": str(args.by_partner_output.resolve())},
        "metrics": {**chat_metrics, **metrics},
        "validation": checks,
    }
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if checks["status"] != "PASS":
        raise SystemExit("Strict validation failed: " + "; ".join(checks["failures"]))
    write_csv_atomic(args.aggregated_output, aggregated, BASE_COLUMNS + CHOICE_COLUMNS + AGGREGATE_COLUMNS)
    write_csv_atomic(args.by_partner_output, by_partner, BASE_COLUMNS + CHOICE_COLUMNS + PARTNER_COLUMNS)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
