"""Score final focal-to-partner transcripts with the project's text measures.

The six user-facing variables are ordinal (1--4). Empty strings mean that the
text contains no usable evidence for that construct. Continuous source scores
are retained beside the ordinal variables so every transformation is auditable.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .text_metrics import count_categories, score_counts, sentiment, standardize, sum_counts


CONTINUOUS_COLUMNS = (
    "volume_continuous_words",
    "emotional_tone_continuous_0_100",
    "sentiment_continuous_neg1_pos1",
    "analytical_thinking_continuous_0_100",
    "clout_continuous_0_100",
    "authenticity_continuous_0_100",
)
ORDINAL_COLUMNS = (
    "volume",
    "emotional_tone",
    "sentiment",
    "analytical_thinking",
    "clout",
    "authenticity",
)
OUTPUT_COLUMNS = CONTINUOUS_COLUMNS + ORDINAL_COLUMNS

ANALYTIC_EVIDENCE = (
    "article", "prep", "ppron", "ipron", "auxverb", "conj", "adverb", "negate",
)
CLOUT_EVIDENCE = ("we", "you", "social", "i", "negate", "swear")
AUTHENTICITY_EVIDENCE = ("i", "exclusive", "negemo", "motion")


def _quantile(values: list[int], proportion: float) -> float:
    """Linear empirical quantile, equivalent to NumPy's default method."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot calculate a quantile of an empty sequence")
    position = (len(ordered) - 1) * proportion
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _quartile_score(value: float, cutpoints: tuple[float, float, float]) -> int:
    if value <= cutpoints[0]:
        return 1
    if value <= cutpoints[1]:
        return 2
    if value <= cutpoints[2]:
        return 3
    return 4


def _score_0_100(value: float) -> int:
    return _quartile_score(value, (25.0, 50.0, 75.0))


def _score_sentiment(value: float) -> int:
    """Four equal-width bands: very negative through very positive."""
    if value < -0.5:
        return 1
    if value < 0.0:
        return 2
    if value < 0.5:
        return 3
    return 4


def _parse_transcript(row: dict[str, str], csv_row: int) -> list[dict]:
    try:
        messages = json.loads(row.get("chat_transcript") or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid chat_transcript at CSV row {csv_row}") from exc
    if not isinstance(messages, list) or any(not isinstance(message, dict) for message in messages):
        raise ValueError(f"Invalid chat_transcript at CSV row {csv_row}")
    focal = str(row.get("focal_player_id", "")).strip()
    partner = str(row.get("partner_id", "")).strip()
    for message in messages:
        if str(message.get("from_id", "")) != focal or str(message.get("to_id", "")) != partner:
            raise ValueError(f"Non-directional transcript at CSV row {csv_row}")
    return messages


def score_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict]:
    working: list[dict[str, object]] = []
    evidence_counts = {
        "volume": 0, "emotional_tone": 0, "sentiment": 0,
        "analytical_thinking": 0, "clout": 0, "authenticity": 0,
    }

    for csv_row, row in enumerate(rows, start=2):
        messages = _parse_transcript(row, csv_row)
        bodies = [str(message.get("body", "")) for message in messages]
        message_counts = [count_categories(body) for body in bodies]
        counts = sum_counts(message_counts)
        scores = score_counts(counts)
        sentiment_scores = [sentiment(body) for body in bodies]
        compounds = [float(item["sentiment_compound"]) for item in sentiment_scores]
        compound_mean = sum(compounds) / len(compounds) if compounds else 0.0
        sentiment_present = any(
            float(item["sentiment_pos"]) > 0 or float(item["sentiment_neg"]) > 0
            for item in sentiment_scores
        )
        stored_messages = row.get("number_of_messages", "")
        if stored_messages not in ("", str(len(messages))):
            raise ValueError(f"number_of_messages mismatch at CSV row {csv_row}")
        try:
            volume_words = int(row.get("number_of_words", "") or 0)
        except ValueError as exc:
            raise ValueError(f"Invalid number_of_words at CSV row {csv_row}") from exc

        record: dict[str, object] = dict(scores)
        record["sentiment_compound_mean"] = compound_mean
        record["volume_words"] = volume_words
        record["evidence_volume"] = volume_words > 0
        record["evidence_emotional_tone"] = bool(scores["has_emotion_words"])
        record["evidence_sentiment"] = sentiment_present
        record["evidence_analytical_thinking"] = any(counts[key] > 0 for key in ANALYTIC_EVIDENCE)
        record["evidence_clout"] = any(counts[key] > 0 for key in CLOUT_EVIDENCE)
        record["evidence_authenticity"] = any(counts[key] > 0 for key in AUTHENTICITY_EVIDENCE)
        working.append(record)

    standardize(working)
    positive_words = [
        int(record["volume_words"]) for record in working
        if int(record["volume_words"]) > 0
    ]
    volume_cutpoints = (
        tuple(_quantile(positive_words, p) for p in (0.25, 0.5, 0.75))
        if positive_words else (0.0, 0.0, 0.0)
    )

    output: list[dict[str, object]] = []
    for record in working:
        result: dict[str, object] = {column: "" for column in OUTPUT_COLUMNS}
        if record["evidence_volume"]:
            result["volume_continuous_words"] = int(record["volume_words"])
            result["volume"] = _quartile_score(
                float(record["volume_words"]), volume_cutpoints
            )
            evidence_counts["volume"] += 1
        if record["evidence_emotional_tone"]:
            result["emotional_tone_continuous_0_100"] = record["tone_100"]
            result["emotional_tone"] = _score_0_100(float(record["tone_100"]))
            evidence_counts["emotional_tone"] += 1
        if record["evidence_sentiment"]:
            result["sentiment_continuous_neg1_pos1"] = round(
                float(record["sentiment_compound_mean"]), 6
            )
            result["sentiment"] = _score_sentiment(
                float(record["sentiment_compound_mean"])
            )
            evidence_counts["sentiment"] += 1
        if record["evidence_analytical_thinking"]:
            result["analytical_thinking_continuous_0_100"] = record["analytic_100"]
            result["analytical_thinking"] = _score_0_100(float(record["analytic_100"]))
            evidence_counts["analytical_thinking"] += 1
        if record["evidence_clout"]:
            result["clout_continuous_0_100"] = record["clout_100"]
            result["clout"] = _score_0_100(float(record["clout_100"]))
            evidence_counts["clout"] += 1
        if record["evidence_authenticity"]:
            result["authenticity_continuous_0_100"] = record["authenticity_100"]
            result["authenticity"] = _score_0_100(float(record["authenticity_100"]))
            evidence_counts["authenticity"] += 1
        output.append(result)

    report = {
        "rows": len(rows),
        "nonempty_texts": len(positive_words),
        "volume_word_quartiles": list(volume_cutpoints),
        "ordinal_rules": {
            "volume": "empirical word-count quartiles among nonempty texts",
            "emotional_tone_analytical_clout_authenticity": "0-25=1; >25-50=2; >50-75=3; >75-100=4",
            "sentiment": "[-1,-0.5)=1; [-0.5,0)=2; [0,0.5)=3; [0.5,1]=4",
            "missing": "blank when the construct has no lexical/sentiment evidence",
        },
        "evidence_counts": evidence_counts,
    }
    return output, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--report-json", type=Path, required=True)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    scores, report = score_rows(rows)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps({"columns": list(OUTPUT_COLUMNS), "rows": scores}, ensure_ascii=False),
        encoding="utf-8",
    )
    args.report_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
