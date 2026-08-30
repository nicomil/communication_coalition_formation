"""Generate rigorous session-specific payoff comparison TXT files."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


DEFAULT_SESSION_CODES = ("yv2jggqe", "wvbg5of9", "lz09lc4v")
PAGE_NAME = "FinalResults"
PART1_FIELD = "bargaining_tdl_main.1.player.part1_calculated_payoff"
BEAUTY_FIELD = "bargaining_tdl_survey.1.player.beauty_contest_guess"
PROLIFIC_FIELD = "participant.prolific_id"
SESSION_FIELD = "session.code"
PAGE_FIELD = "participant._current_page_name"


def money(value: str, field: str, row_number: int) -> Decimal:
    try:
        return Decimal((value or "").strip()).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid numeric value in {field!r} at CSV row {row_number}: {value!r}")


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        required = {SESSION_FIELD, PAGE_FIELD, PROLIFIC_FIELD, PART1_FIELD, BEAUTY_FIELD}
        missing = required - set(headers)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        return headers, list(reader)


def participant_label(row: dict[str, str], row_number: int) -> str:
    prolific = (row.get(PROLIFIC_FIELD) or "").strip()
    return prolific or f"[MISSING_PROLIFIC_ID|csv_row_{row_number}]"


def format_record(record: dict[str, object], show_11_20_bonus: bool = False) -> str:
    text = (
        f"{record['prolific_id']},{record['total']:.2f}"
        f"(Part1 {record['part1']:.2f}+BeautyContest {record['beauty']:.2f})"
    )
    if show_11_20_bonus and record.get("winner_11_20"):
        text += "+3 11-20 game"
    return text


def generate(
    rows: list[dict[str, str]],
    output_dir: Path,
    seed: int,
    session_codes: tuple[str, ...] = DEFAULT_SESSION_CODES,
) -> tuple[list[str], dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    eligible = [
        (index + 2, row)
        for index, row in enumerate(rows)
        if (row.get(PAGE_FIELD) or "").strip() == PAGE_NAME
        and (row.get(SESSION_FIELD) or "").strip() in session_codes
    ]
    by_session: dict[str, list[dict[str, object]]] = {code: [] for code in session_codes}
    for csv_row, row in eligible:
        session = (row.get(SESSION_FIELD) or "").strip()
        part1 = money(row.get(PART1_FIELD, ""), PART1_FIELD, csv_row)
        beauty = money(row.get(BEAUTY_FIELD, ""), BEAUTY_FIELD, csv_row)
        by_session[session].append({
            "csv_row": csv_row,
            "prolific_id": participant_label(row, csv_row),
            "part1": part1,
            "beauty": beauty,
            "total": part1 + beauty,
        })

    audit: list[str] = []
    failures: list[str] = []
    all_output_paths: list[str] = []
    for session in session_codes:
        records = by_session[session]
        ids = [str(r["prolific_id"]) for r in records]
        if len(ids) != len(set(ids)):
            failures.append(f"{session}: duplicate prolific_id among eligible records")
        rng = random.Random(f"{seed}:{session}")
        shuffled = list(records)
        rng.shuffle(shuffled)
        if len(shuffled) % 2:
            # Keep the exceptional group explicitly at the end.
            groups = [shuffled[i:i + 2] for i in range(0, len(shuffled) - 3, 2)]
            groups.append(shuffled[-3:])
        else:
            groups = [shuffled[i:i + 2] for i in range(0, len(shuffled), 2)]
        expected_sizes = ([2] * ((len(records) - 3) // 2) + [3]) if len(records) % 2 else [2] * (len(records) // 2)
        if [len(group) for group in groups] != expected_sizes:
            failures.append(
                f"{session}: unexpected group sizes; expected {expected_sizes}, "
                f"got {[len(group) for group in groups]}"
            )
        paired_ids = [str(item["prolific_id"]) for group in groups for item in group]
        if Counter(paired_ids) != Counter(ids):
            failures.append(f"{session}: pairing does not cover eligible participants exactly once")

        # In each random group, a participant wins the additional $3 whenever
        # their request is exactly $0.10 below at least one other group member.
        for group in groups:
            for record in group:
                record["winner_11_20"] = any(
                    record["beauty"] == other["beauty"] - Decimal("0.10")
                    for other in group
                    if other is not record
                )
                record["payment_bonus"] = (
                    record["part1"]
                    + record["beauty"]
                    - Decimal("1.10")
                    + (Decimal("3.00") if record["winner_11_20"] else Decimal("0.00"))
                ).quantize(Decimal("0.01"))

        output_path = output_dir / f"{session}_comparison.txt"
        lines = [
            f"Session: {session}",
            f"Filter: {PAGE_FIELD} == {PAGE_NAME}",
            "Total = Part1 payoff + Beauty Contest guess; show-up fee excluded.",
            f"Eligible participants: {len(records)}",
            f"Random seed: {seed}:{session}",
            "",
            "ELIGIBLE PARTICIPANTS",
        ]
        lines.extend(
            format_record(record, show_11_20_bonus=True)
            for record in sorted(records, key=lambda x: str(x["prolific_id"]))
        )
        lines += ["", "RANDOM GROUPS"]
        for number, group in enumerate(groups, start=1):
            label = "PAIR" if len(group) == 2 else "TRIPLE (odd session; necessary to include everyone)"
            lines.append(f"{number}. {label}")
            lines.extend(f"   {format_record(record)}" for record in group)
            lines.append("")
        lines.extend(
            f"{record['prolific_id']},{record['payment_bonus']:.2f}"
            for record in sorted(records, key=lambda x: str(x["prolific_id"]))
            if record["payment_bonus"] > 0
        )
        output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        all_output_paths.append(str(output_path))
        audit.extend([
            f"{session}: eligible={len(records)}, groups={len(groups)}, sizes={[len(g) for g in groups]}, output={output_path}",
            f"{session}: unique_ids={len(set(ids))}, paired_ids={len(set(paired_ids))}, exact_coverage={Counter(paired_ids) == Counter(ids)}",
        ])

    audit_path = output_dir / "comparison_audit.txt"
    audit_lines = [
        "Session payoff comparison audit",
        "",
        f"Input filter: {PAGE_FIELD} == {PAGE_NAME}",
        f"Sessions: {', '.join(session_codes)}",
        f"Seed: {seed}",
        "",
        *audit,
        "",
        "Validation failures:",
        *(failures or ["NONE"]),
        "",
        "PASS" if not failures else "FAIL",
    ]
    audit_path.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")
    if failures:
        raise RuntimeError("Validation failed; see comparison_audit.txt: " + " | ".join(failures))
    return all_output_paths, {"eligible_total": len(eligible), "audit": str(audit_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("docs/all_apps_wide_2026-08-18.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs/session_payoff_comparisons"))
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--sessions", nargs="+", default=list(DEFAULT_SESSION_CODES))
    args = parser.parse_args()
    _, rows = read_rows(args.input)
    _, metadata = generate(rows, args.output_dir, args.seed, tuple(args.sessions))
    print(metadata)


if __name__ == "__main__":
    main()
