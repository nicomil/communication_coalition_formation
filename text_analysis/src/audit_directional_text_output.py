from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "text_analysis/output/datasets/all_apps_wide_2026-08-26_chat_by_partner_goodshape_FINAL_topicgpt_with_indicators.csv"
OUTPUT = ROOT / "text_analysis/output/datasets/all_apps_wide_2026-08-26_chat_by_partner_goodshape_FINAL_topicgpt_with_indicators_text_analysis.csv"
SCORES = Path(r"C:\Users\Donat\.codex\visualizations\2026\08\26\01a03e60-ea52-7b91-867d-bd9308c7a2c9\topic_indicators\directional_text_scores.json")

ADDED = [
    "volume_continuous_words",
    "emotional_tone_continuous_0_100",
    "sentiment_continuous_neg1_pos1",
    "analytical_thinking_continuous_0_100",
    "clout_continuous_0_100",
    "authenticity_continuous_0_100",
    "volume",
    "emotional_tone",
    "sentiment",
    "analytical_thinking",
    "clout",
    "authenticity",
]


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader), list(reader)


source_header, source_rows = read_csv(SOURCE)
output_header, output_rows = read_csv(OUTPUT)
scores_document = json.loads(SCORES.read_text(encoding="utf-8"))
assert scores_document["columns"] == ADDED
scores = scores_document["rows"]

assert len(source_rows) == len(output_rows) == len(scores) == 6180
assert len(source_header) == 116
assert len(output_header) == 128
assert output_header[:116] == source_header
assert output_header[116:] == ADDED

for row_number, (source, output, expected) in enumerate(
    zip(source_rows, output_rows, scores, strict=True), start=2
):
    assert output[:116] == source, f"Source columns changed at CSV row {row_number}"
    for offset, name in enumerate(ADDED, start=116):
        actual = output[offset]
        wanted = expected[name]
        if wanted in (None, ""):
            assert actual == "", (row_number, name, actual, wanted)
        elif name in ADDED[:6]:
            assert float(actual) == float(wanted), (row_number, name, actual, wanted)
        else:
            assert actual == str(wanted), (row_number, name, actual, wanted)

for name in ADDED[6:]:
    index = output_header.index(name)
    assert {row[index] for row in output_rows} <= {"", "1", "2", "3", "4"}

continuous_ordinal_pairs = list(zip(ADDED[:6], ADDED[6:], strict=True))
for continuous, ordinal in continuous_ordinal_pairs:
    ci = output_header.index(continuous)
    oi = output_header.index(ordinal)
    assert all((row[ci] == "") == (row[oi] == "") for row in output_rows)

distributions = {}
for name in ADDED[6:]:
    idx = output_header.index(name)
    counts = Counter(row[idx] or "blank" for row in output_rows)
    distributions[name] = {key: counts.get(key, 0) for key in ["blank", "1", "2", "3", "4"]}

digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
print(json.dumps({
    "status": "PASS",
    "rows": len(output_rows),
    "columns": len(output_header),
    "source_columns_preserved": len(source_header),
    "distributions": distributions,
    "sha256": digest,
}, indent=2))
