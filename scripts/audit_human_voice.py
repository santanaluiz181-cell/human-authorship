"""
Deterministic Anti-AI-Slop & Human Voice Metric Gate (`audit_human_voice.py`).
Measures burstiness (sentence length stdev), vocabulary slop markers (PT-BR & EN),
zero-width watermarks, em/en dashes, and Paragraph uniformity WITHOUT rewriting user text.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

SLOP_PATTERNS_PT = [
    r"\bal[eé]m disso\b",
    r"\bvale ressaltar\b",
    r"\bcabe destacar\b",
    r"\bna era digital\b",
    r"\bem suma\b",
    r"\bpor um lado\b",
    r"\bpor outro lado\b",
    r"\btape[cç]aria\b",
    r"\bdiante desse cen[aá]rio\b",
    r"\bnessa perspectiva\b",
    r"\b[eé] imperativo que\b",
    r"\becossistema\b",
    r"\bfarol de esperan[cç]a\b",
    r"\bmergulhar fundo\b",
    r"\bconstruir um futuro melhor\b",
    r"\bno cen[aá]rio contempor[aâ]neo\b",
]

SLOP_PATTERNS_EN = [
    r"\bdelve(?:s|d|ing)?\b",
    r"\btapestry\b",
    r"\bmoreover\b",
    r"\bfurthermore\b",
    r"\btestament to\b",
    r"\bin conclusion\b",
    r"\bin today'?s digital world\b",
    r"\bnavigating the complexities\b",
    r"\bunderscores the importance\b",
    r"\bseamless(?:ly)?\b",
]

ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\uFEFF]")
DASH_RE = re.compile(r"[\u2013\u2014]")
SENTENCE_SPLIT_RE = re.compile(r"[.!?]+(?:\s+|$)")
WORD_RE = re.compile(r"\b[\wÀ-ÖØ-öø-ÿ-]+\b", re.UNICODE)


def _split_sentences(text):
    clean = re.sub(r"```[\s\S]*?```", " ", text)
    clean = re.sub(r"^#+\s+.*$", " ", clean, flags=re.MULTILINE)
    raw_parts = [s.strip() for s in SENTENCE_SPLIT_RE.split(clean) if s.strip()]
    lengths = []
    for part in raw_parts:
        words = WORD_RE.findall(part)
        if len(words) >= 2:
            lengths.append((part, len(words)))
    return lengths


def audit_text(text):
    if text and text.startswith("\ufeff"):
        text = text[1:]
    if not text or not text.strip():
        return {
            "status": "EMPTY_INPUT",
            "verdict": "EMPTY_INPUT",
            "authorship_gate_score": 0,
            "word_count": 0,
            "sentence_count": 0,
            "mean_sentence_words": 0.0,
            "burstiness_stdev": 0.0,
            "short_sentences_le8": 0,
            "long_sentences_ge28": 0,
            "em_en_dash_count": 0,
            "zero_width_count": 0,
            "slop_hits": [],
            "warnings": ["Input text is empty."],
        }

    words = WORD_RE.findall(text)
    sentences = _split_sentences(text)
    lengths = [item[1] for item in sentences]

    if lengths:
        mean_len = sum(lengths) / len(lengths)
        variance = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
        stdev_len = math.sqrt(variance)
        short_sentences = sum(1 for x in lengths if x <= 8)
        long_sentences = sum(1 for x in lengths if x >= 28)
    else:
        mean_len = 0.0
        stdev_len = 0.0
        short_sentences = 0
        long_sentences = 0

    zero_width_hits = len(ZERO_WIDTH_RE.findall(text))
    dash_hits = len(DASH_RE.findall(text))

    slop_hits = []
    for pat in SLOP_PATTERNS_PT + SLOP_PATTERNS_EN:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        if matches:
            slop_hits.append({"pattern": pat, "count": len(matches), "sample": matches[0]})

    warnings = []
    if len(sentences) >= 5 and stdev_len < 6.0:
        warnings.append(
            f"Low burstiness (stdev={stdev_len:.2f} < 6.0): sentences look rhythmically uniform like LLM cadence. Vary short (<8w) and dense (>24w) sentences manually."
        )
    if len(sentences) >= 5 and short_sentences == 0:
        warnings.append("Zero punchy short sentences (<= 8 words). Human prose breathes with abrupt transitions.")
    if dash_hits > 0:
        warnings.append(f"Detected {dash_hits} em/en dashes (U+2014/U+2013), a strong synthetic cadence marker.")
    if zero_width_hits > 0:
        warnings.append(f"Detected {zero_width_hits} hidden zero-width characters.")
    if slop_hits:
        warnings.append(f"Detected {len(slop_hits)} AI-slop lexical cliches.")

    score = 100
    score -= min(35, len(slop_hits) * 10)
    score -= min(20, dash_hits * 4)
    score -= min(25, 25 if zero_width_hits > 0 else 0)
    if len(sentences) >= 5 and stdev_len < 6.0:
        score -= 20
    if len(sentences) >= 5 and short_sentences == 0:
        score -= 10
    score = max(0, score)

    verdict = "PASS_HUMAN_RHYTHM" if score >= 80 and not warnings else ("REVIEW_NEEDED" if score >= 55 else "HIGH_SLOP_RISK")

    return {
        "verdict": verdict,
        "authorship_gate_score": score,
        "word_count": len(words),
        "sentence_count": len(sentences),
        "mean_sentence_words": round(mean_len, 2),
        "burstiness_stdev": round(stdev_len, 2),
        "short_sentences_le8": short_sentences,
        "long_sentences_ge28": long_sentences,
        "em_en_dash_count": dash_hits,
        "zero_width_count": zero_width_hits,
        "slop_hits": slop_hits,
        "warnings": warnings,
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Deterministic Human Authorship & Anti-AI-Slop Voice Gate")
    parser.add_argument("file", help="Path to Markdown or text draft written by the human author")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    target = Path(args.file)
    if not target.exists():
        print(f"ERROR: file not found: {target}", file=sys.stderr)
        sys.exit(2)

    report = audit_text(target.read_text(encoding="utf-8", errors="replace"))
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"=== HUMAN AUTHORSHIP GATE: {report['verdict']} (Score {report['authorship_gate_score']}/100) ===")
        print(
            f"Words: {report['word_count']} | Sentences: {report['sentence_count']} | "
            f"Mean Len: {report['mean_sentence_words']}w | Burstiness (stdev): {report['burstiness_stdev']}w"
        )
        print(
            f"Short (<=8w): {report['short_sentences_le8']} | Long (>=28w): {report['long_sentences_ge28']} | "
            f"Em/En Dashes: {report['em_en_dash_count']} | Zero-Width: {report['zero_width_count']}"
        )
        if report["slop_hits"]:
            print("Slop Phrases:")
            for hit in report["slop_hits"]:
                print(f"  - '{hit['sample']}' ({hit['count']}x)")
        if report["warnings"]:
            print("Diagnostic Questions / Warnings:")
            for w in report["warnings"]:
                print(f"  * {w}")
        else:
            print("No robotic slop markers detected. Keep reviewing primary facts manually.")


if __name__ == "__main__":
    main()
