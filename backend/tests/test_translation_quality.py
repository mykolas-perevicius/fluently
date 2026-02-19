"""
Translation quality evaluation tests.

Run with:  uv run pytest -m quality -v --tb=short
Requires:  Docker stack running (Ollama + Fluently API)
"""

import json
from pathlib import Path

import httpx
import pytest
import sacrebleu

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Thresholds per language pair (conservative floors)
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "en-es": {"bleu": 25, "chrf": 50},
    "en-fr": {"bleu": 25, "chrf": 50},
    "en-de": {"bleu": 20, "chrf": 45},
    "en-ja": {"bleu": 10, "chrf": 25},
    "en-pt": {"bleu": 25, "chrf": 50},
}

# Target language code extracted from pair string (e.g. "en-es" → "es")
TARGET_LANG = {
    "en-es": "es",
    "en-fr": "fr",
    "en-de": "de",
    "en-ja": "ja",
    "en-pt": "pt",
}

# ---------------------------------------------------------------------------
# Load test cases for parametrization
# ---------------------------------------------------------------------------


def _load_cases():
    path = FIXTURES_DIR / "translation_cases.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    return [(c["id"], c) for c in cases]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.quality
@pytest.mark.parametrize("case_id,case", _load_cases(), ids=[c[0] for c in _load_cases()])
def test_translation_quality(case_id, case, base_url, quality_report):
    """Translate via live API and score against reference translations."""
    pair = case["pair"]
    source = case["source"]
    references = case["references"]
    target_lang = TARGET_LANG[pair]

    # Call the live API
    with httpx.Client(timeout=120.0) as client:
        response = client.post(
            f"{base_url}/translate/",
            json={"contents": [source], "targetLanguageCode": target_lang},
        )

    assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
    data = response.json()
    hypothesis = data[0].strip()

    # Compute BLEU — use 'intl' tokenizer for Japanese, '13a' for Latin-script
    tokenize = "intl" if target_lang == "ja" else "13a"
    bleu = sacrebleu.sentence_bleu(
        hypothesis,
        references,
        tokenize=tokenize,
    ).score

    # Compute chrF
    chrf = sacrebleu.sentence_chrf(
        hypothesis,
        references,
    ).score

    # Record result for the summary report
    thresholds = THRESHOLDS[pair]
    passed = bleu >= thresholds["bleu"] and chrf >= thresholds["chrf"]

    from tests.conftest import QualityResult

    quality_report.add(
        QualityResult(
            id=case_id,
            pair=pair,
            source=source,
            hypothesis=hypothesis,
            bleu=bleu,
            chrf=chrf,
            passed=passed,
        )
    )

    # Assert thresholds
    assert bleu >= thresholds["bleu"], (
        f"[{case_id}] BLEU {bleu:.1f} < {thresholds['bleu']} threshold "
        f"(hypothesis: {hypothesis!r})"
    )
    assert chrf >= thresholds["chrf"], (
        f"[{case_id}] chrF {chrf:.1f} < {thresholds['chrf']} threshold "
        f"(hypothesis: {hypothesis!r})"
    )
