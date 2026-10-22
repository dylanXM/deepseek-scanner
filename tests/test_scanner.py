from pathlib import Path

from deepseek_scan.rules import load_rules
from deepseek_scan.scanner import scan_path

FIXTURES = Path(__file__).parent / "fixtures"


def _rule_ids(result):
    return {f.rule_id for f in result.findings}


def test_positive_fixture_triggers_every_rule():
    ruleset = load_rules()
    result = scan_path(FIXTURES / "positive", ruleset)
    expected = {
        "DS-001",  # api.deepseek.com endpoint
        "DS-002",  # DEEPSEEK_API_KEY
        "DS-003",  # deepseek-chat / deepseek-reasoner model ids
        "DS-004",  # deepseek-ai/ hub namespace
        "DS-005",  # import deepseek
        "DS-006",  # direct dependency manifests
        "DS-007",  # lockfile reference
        "DS-008",  # Dockerfile / compose
        "DS-009",  # .gguf weight file by name
        "DS-010",  # model config.json architecture
    }
    assert expected <= _rule_ids(result)


def test_positive_findings_have_file_and_line_evidence():
    ruleset = load_rules()
    result = scan_path(FIXTURES / "positive", ruleset)
    content_findings = [f for f in result.findings if f.line is not None]
    assert content_findings, "expected line-level evidence"
    for f in content_findings:
        assert f.file and f.line >= 1 and f.snippet
    endpoint = [f for f in result.findings if f.rule_id == "DS-001"]
    assert endpoint and endpoint[0].file == "app.py"


def test_positive_findings_sorted_by_severity():
    ruleset = load_rules()
    result = scan_path(FIXTURES / "positive", ruleset)
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ranks = [order[f.severity] for f in result.findings]
    assert ranks == sorted(ranks)
    assert result.findings[0].severity == "critical"


def test_negative_fixture_is_clean():
    ruleset = load_rules()
    result = scan_path(FIXTURES / "negative", ruleset)
    assert result.findings == []
    assert result.files_scanned >= 4


def test_secrets_are_redacted_from_snippets():
    ruleset = load_rules()
    result = scan_path(FIXTURES / "positive", ruleset)
    for f in result.findings:
        assert "sk-fakeexamplekey123456" not in f.snippet
