"""Shared fixtures and hooks for the test suite."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# CLI options
# ---------------------------------------------------------------------------


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the running Fluently API (default: http://localhost:8000)",
    )


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url").rstrip("/")


# ---------------------------------------------------------------------------
# Translation test cases
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def translation_cases():
    path = FIXTURES_DIR / "translation_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Quality report dataclass & collection
# ---------------------------------------------------------------------------


@dataclass
class QualityResult:
    id: str
    pair: str
    source: str
    hypothesis: str
    bleu: float
    chrf: float
    passed: bool


@dataclass
class QualityReport:
    results: list[QualityResult] = field(default_factory=list)

    def add(self, result: QualityResult):
        self.results.append(result)


def pytest_configure(config):
    config._quality_report = QualityReport()


@pytest.fixture(scope="session")
def quality_report(request):
    return request.config._quality_report


# ---------------------------------------------------------------------------
# Terminal summary hook — prints the quality table after the test run
# ---------------------------------------------------------------------------


def _truncate(text: str, width: int = 30) -> str:
    return text[: width - 3] + "..." if len(text) > width else text


def pytest_terminal_summary(terminalreporter, config):
    report: QualityReport = config._quality_report
    if not report.results:
        return

    terminalreporter.section("Translation Quality Results")

    # Per-case table
    header = f"{'ID':<8} {'Pair':<8} {'Source':<32} {'Hypothesis':<32} {'BLEU':>6} {'chrF':>6} {'Status':<6}"
    terminalreporter.write_line(header)
    terminalreporter.write_line("-" * len(header))

    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        line = (
            f"{r.id:<8} "
            f"{r.pair:<8} "
            f"{_truncate(r.source, 30):<32} "
            f"{_truncate(r.hypothesis, 30):<32} "
            f"{r.bleu:>6.1f} "
            f"{r.chrf:>6.1f} "
            f"{status:<6}"
        )
        terminalreporter.write_line(line)

    terminalreporter.write_line("")

    # Per-pair averages
    from collections import defaultdict

    pair_stats = defaultdict(lambda: {"bleu": [], "chrf": []})
    for r in report.results:
        pair_stats[r.pair]["bleu"].append(r.bleu)
        pair_stats[r.pair]["chrf"].append(r.chrf)

    avg_header = f"{'Language Pair':<16} {'Cases':>5} {'Avg BLEU':>10} {'Avg chrF':>10}"
    terminalreporter.write_line(avg_header)
    terminalreporter.write_line("-" * len(avg_header))

    for pair in sorted(pair_stats):
        stats = pair_stats[pair]
        n = len(stats["bleu"])
        avg_bleu = sum(stats["bleu"]) / n
        avg_chrf = sum(stats["chrf"]) / n
        terminalreporter.write_line(
            f"{pair:<16} {n:>5} {avg_bleu:>10.1f} {avg_chrf:>10.1f}"
        )
