"""Split a payoff-comparison report into two independently randomized studies."""

from __future__ import annotations

import argparse
import random
import re
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader


RECORD_RE = re.compile(
    r"^([0-9a-f]{24}),(\d+\.\d{2})"
    r"\(Part1 (\d+\.\d{2})\+BeautyContest (\d+\.\d{2})\)"
    r"(?:\+3 11-20 game)?$"
)


def parse_source(path: Path) -> tuple[str, list[dict[str, object]]]:
    text = path.read_text(encoding="utf-8")
    session_match = re.search(r"(?m)^Session: (\S+)$", text)
    if not session_match:
        raise ValueError("Source report has no Session header")
    try:
        block = text.split("ELIGIBLE PARTICIPANTS\n", 1)[1].split(
            "\n\nRANDOM GROUPS", 1
        )[0]
    except IndexError as exc:
        raise ValueError("Source report has no eligible-participant block") from exc

    records: list[dict[str, object]] = []
    for line in block.splitlines():
        match = RECORD_RE.fullmatch(line.strip())
        if not match:
            raise ValueError(f"Unexpected eligible-participant line: {line!r}")
        prolific_id, total, part1, beauty = match.groups()
        record = {
            "prolific_id": prolific_id,
            "total": Decimal(total),
            "part1": Decimal(part1),
            "beauty": Decimal(beauty),
        }
        if record["total"] != record["part1"] + record["beauty"]:
            raise ValueError(f"Inconsistent total for {prolific_id}")
        records.append(record)
    ids = [str(record["prolific_id"]) for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate Prolific IDs in source report")
    return session_match.group(1), records


def ids_from_pdfs(paths: list[Path]) -> set[str]:
    ids: set[str] = set()
    for path in paths:
        reader = PdfReader(path)
        for page in reader.pages:
            # Some browser-generated PDFs concatenate the date immediately
            # after the 24-character ID, so no trailing whitespace is required.
            ids.update(re.findall(r"(?m)^([0-9a-f]{24})", page.extract_text() or ""))
    return ids


def make_groups(records: list[dict[str, object]], seed: str):
    shuffled = [dict(record) for record in records]
    random.Random(seed).shuffle(shuffled)
    if len(shuffled) % 2:
        groups = [shuffled[i:i + 2] for i in range(0, len(shuffled) - 3, 2)]
        groups.append(shuffled[-3:])
    else:
        groups = [shuffled[i:i + 2] for i in range(0, len(shuffled), 2)]

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
    return groups


def format_record(record: dict[str, object], annotate: bool = False) -> str:
    text = (
        f"{record['prolific_id']},{record['total']:.2f}"
        f"(Part1 {record['part1']:.2f}+BeautyContest {record['beauty']:.2f})"
    )
    if annotate and record["winner_11_20"]:
        text += "+3 11-20 game"
    return text


def write_report(
    path: Path,
    session: str,
    study_number: int,
    records: list[dict[str, object]],
    seed: str,
    source: Path,
) -> dict[str, int]:
    groups = make_groups(records, seed)
    flattened = [record for group in groups for record in group]
    if {str(r["prolific_id"]) for r in flattened} != {
        str(r["prolific_id"]) for r in records
    }:
        raise ValueError(f"Study {study_number} grouping coverage failed")

    lines = [
        f"Session: {session}",
        f"Prolific study subset: {study_number}",
        f"Source report: {source}",
        "Total = Part1 payoff + Beauty Contest guess; show-up fee excluded.",
        f"Eligible participants: {len(records)}",
        f"Random seed: {seed}",
        "",
        "ELIGIBLE PARTICIPANTS",
    ]
    lines.extend(
        format_record(record, annotate=True)
        for record in sorted(flattened, key=lambda r: str(r["prolific_id"]))
    )
    lines += ["", "RANDOM GROUPS"]
    for number, group in enumerate(groups, start=1):
        label = "PAIR" if len(group) == 2 else "TRIPLE (odd study; necessary to include everyone)"
        lines.append(f"{number}. {label}")
        lines.extend(f"   {format_record(record)}" for record in group)
        lines.append("")
    lines.extend(
        f"{record['prolific_id']},{record['payment_bonus']:.2f}"
        for record in sorted(flattened, key=lambda r: str(r["prolific_id"]))
        if record["payment_bonus"] > 0
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "participants": len(records),
        "groups": len(groups),
        "pairs": sum(len(group) == 2 for group in groups),
        "triples": sum(len(group) == 3 for group in groups),
        "winners": sum(bool(record["winner_11_20"]) for record in flattened),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--study1-pdf", type=Path, action="append", default=[])
    parser.add_argument("--study1-id", action="append", default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260820)
    args = parser.parse_args()

    session, records = parse_source(args.source)
    source_ids = {str(record["prolific_id"]) for record in records}
    study1_ids = ids_from_pdfs(args.study1_pdf) | set(args.study1_id)
    missing = study1_ids - source_ids
    if missing:
        raise ValueError(f"Study 1 IDs absent from source: {sorted(missing)}")
    study2_ids = source_ids - study1_ids
    if study1_ids & study2_ids or study1_ids | study2_ids != source_ids:
        raise ValueError("Study split is not disjoint and exhaustive")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for number, ids in ((1, study1_ids), (2, study2_ids)):
        subset = [record for record in records if record["prolific_id"] in ids]
        output = args.output_dir / f"{session}_study{number}_comparison.txt"
        seed = f"{args.seed}:{session}:study{number}"
        results[f"study{number}"] = write_report(
            output, session, number, subset, seed, args.source
        )
        results[f"study{number}"]["output"] = str(output)
    print(results)


if __name__ == "__main__":
    main()
