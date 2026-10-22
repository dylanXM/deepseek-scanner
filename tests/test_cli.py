import json
from pathlib import Path

from deepseek_scan.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]


def test_cli_scan_positive_exit_zero_by_default(capsys):
    code = main(["scan", str(FIXTURES / "positive")])
    out = capsys.readouterr().out
    assert code == 0
    assert "Evidence Report" in out


def test_cli_fail_on_high_exits_one_for_positive():
    code = main(["scan", str(FIXTURES / "positive"), "--fail-on", "high"])
    assert code == 1


def test_cli_fail_on_high_exits_zero_for_negative():
    code = main(["scan", str(FIXTURES / "negative"), "--fail-on", "high"])
    assert code == 0


def test_cli_json_format(capsys):
    code = main(["scan", str(FIXTURES / "positive"), "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0
    data = json.loads(out)
    assert data["summary"]["total_findings"] > 0


def test_cli_out_writes_file(tmp_path):
    target = tmp_path / "report.md"
    code = main(["scan", str(FIXTURES / "positive"), "--out", str(target)])
    assert code == 0
    assert "Evidence Report" in target.read_text(encoding="utf-8")


def test_cli_missing_dir_errors():
    assert main(["scan", str(FIXTURES / "does-not-exist")]) == 2


def test_rules_file_sync_and_version():
    root_rules = ROOT / "rules" / "deepseek.rules.json"
    bundled = ROOT / "src" / "deepseek_scan" / "rules" / "deepseek.rules.json"
    if root_rules.is_file() and bundled.is_file():
        assert root_rules.read_bytes() == bundled.read_bytes()
    data = json.loads(bundled.read_text(encoding="utf-8"))
    assert data["rules_version"] == "2026.10.22.1"
    assert len(data["rules"]) >= 10
    ids = [r["id"] for r in data["rules"]]
    assert len(ids) == len(set(ids))
    for r in data["rules"]:
        assert r["severity"] in ("critical", "high", "medium", "low")
        assert r["fascsa_note"] and r["remediation"]
