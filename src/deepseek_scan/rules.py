"""Rule loading. Rules are data (JSON), not code.

The canonical rules file lives at ``rules/deepseek.rules.json`` in the
repository. A byte-identical copy is bundled inside the package so
installed copies work from any directory; a test keeps the two in sync.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    severity: str  # critical | high | medium | low
    evidence_type: str
    component_type: str
    patterns: tuple[str, ...] = ()
    file_globs: tuple[str, ...] = ()
    case_insensitive: bool = False
    fascsa_note: str = ""
    remediation: str = ""
    # Artifact rules match on filename instead of file content.
    filename_contains: str | None = None
    filename_suffixes: tuple[str, ...] = ()

    @property
    def is_artifact_rule(self) -> bool:
        return self.filename_contains is not None


@dataclass
class RuleSet:
    rules_version: str
    vendor: str
    rules: list[Rule] = field(default_factory=list)


def _parse(data: dict) -> RuleSet:
    rules = []
    for raw in data.get("rules", []):
        rules.append(
            Rule(
                id=raw["id"],
                name=raw["name"],
                severity=raw["severity"],
                evidence_type=raw["evidence_type"],
                component_type=raw["component_type"],
                patterns=tuple(raw.get("patterns", [])),
                file_globs=tuple(raw.get("file_globs", [])),
                case_insensitive=bool(raw.get("case_insensitive", False)),
                fascsa_note=raw.get("fascsa_note", ""),
                remediation=raw.get("remediation", ""),
                filename_contains=raw.get("filename_contains"),
                filename_suffixes=tuple(raw.get("filename_suffixes", [])),
            )
        )
    return RuleSet(
        rules_version=data.get("rules_version", "unknown"),
        vendor=data.get("vendor", ""),
        rules=rules,
    )


def _candidate_paths(explicit: str | None) -> list[Path]:
    paths: list[Path] = []
    if explicit:
        paths.append(Path(explicit))
    env = os.environ.get("DEEPSEEK_SCAN_RULES")
    if env:
        paths.append(Path(env))
    # Repository checkout layout: <root>/rules/deepseek.rules.json where
    # this file is <root>/src/deepseek_scan/rules.py
    paths.append(Path(__file__).resolve().parents[2] / "rules" / "deepseek.rules.json")
    paths.append(Path.cwd() / "rules" / "deepseek.rules.json")
    return paths


def load_rules(explicit: str | None = None) -> RuleSet:
    """Load the rule set from an explicit path, the repo checkout, or the
    copy bundled with the package (in that order)."""
    for path in _candidate_paths(explicit):
        try:
            if path.is_file():
                return _parse(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    bundled = resources.files("deepseek_scan").joinpath("rules", "deepseek.rules.json")
    return _parse(json.loads(bundled.read_text(encoding="utf-8")))
