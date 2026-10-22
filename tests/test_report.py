import json
from pathlib import Path

from deepseek_scan.report import render_json, render_markdown
from deepseek_scan.rules import load_rules
from deepseek_scan.scanner import scan_path

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]

# Words that must never appear in anything this tool emits: the tool
# collects evidence; it does not certify anything.
BANNED = ("certif", "guarantee")


def _positive():
    ruleset = load_rules()
    return scan_path(FIXTURES / "positive", ruleset), ruleset


def _negative():
    ruleset = load_rules()
    return scan_path(FIXTURES / "negative", ruleset), ruleset


def test_markdown_report_structure():
    result, ruleset = _positive()
    md = render_markdown(result, ruleset)
    assert "# DeepSeek Exposure Scan - Evidence Report" in md
    assert "## Summary by severity" in md
    assert "## Findings" in md
    assert "## Detection limits" in md
    assert "app.py:" in md  # file:line evidence
    assert ruleset.rules_version in md


def test_markdown_report_for_clean_scan_states_limits():
    result, ruleset = _negative()
    md = render_markdown(result, ruleset)
    assert "No indicators from the current rule set were found" in md
    assert "Detection limits" in md
    assert "not proof" in md


def test_json_report_is_ai_bom_shaped():
    result, ruleset = _positive()
    data = json.loads(render_json(result, ruleset))
    assert data["tool"]["name"] == "deepseek-exposure-scan"
    assert data["rules_version"] == ruleset.rules_version
    assert data["summary"]["total_findings"] == len(result.findings)
    first = data["findings"][0]
    assert first["component"]["vendor"] == "DeepSeek"
    assert first["component"]["name"]
    assert first["component"]["type"]
    assert first["evidence"]["source_file"]
    assert "snippet" in first["evidence"]
    assert "limitations" in data and "cannot detect" in data["limitations"]


def test_reports_contain_no_certification_language():
    for result, ruleset in (_positive(), _negative()):
        for text in (render_markdown(result, ruleset), render_json(result, ruleset)):
            low = text.lower()
            for word in BANNED:
                assert word not in low
            assert "compliant" not in low


def test_readme_contains_no_certification_language():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    for word in BANNED:
        assert word not in readme
