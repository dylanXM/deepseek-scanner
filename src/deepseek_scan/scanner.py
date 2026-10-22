"""Static scanner: walks a tree, applies data-driven rules, returns
findings with file:line evidence. Detection is evidence of presence
only - see LIMITATIONS in the reports."""

from __future__ import annotations

import fnmatch
import os
import re
from dataclasses import dataclass
from pathlib import Path

from .rules import Rule, RuleSet

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    ".mypy_cache", ".pytest_cache", ".tox", "dist", "build", ".idea",
    ".next", "target", "vendor",
}
MAX_TEXT_BYTES = 5 * 1024 * 1024  # skip text scanning of very large files
MAX_SNIPPET = 200

# Redact anything that looks like a live credential before it can land
# in a report that gets shared with third parties.
_SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{6,}|ghp_[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{12,})")


def _redact(text: str) -> str:
    return _SECRET_RE.sub(lambda m: m.group(0)[:3] + "-***REDACTED***", text)


@dataclass
class Finding:
    rule_id: str
    rule_name: str
    severity: str
    evidence_type: str
    component_type: str
    component_name: str
    file: str  # path relative to scan root, posix separators
    line: int | None
    snippet: str
    fascsa_note: str
    remediation: str

    def key(self) -> tuple:
        return (self.rule_id, self.file, self.line, self.snippet)


@dataclass
class ScanResult:
    target: str
    files_scanned: int
    findings: list[Finding]

    def counts_by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts


def _glob_match(rel_posix: str, basename: str, globs: tuple[str, ...]) -> bool:
    if not globs:
        return True
    for g in globs:
        if fnmatch.fnmatch(rel_posix, g) or fnmatch.fnmatch(basename, g):
            return True
    return False


def _looks_binary(chunk: bytes) -> bool:
    return b"\x00" in chunk


def _compile(rule: Rule) -> list[re.Pattern]:
    flags = re.IGNORECASE if rule.case_insensitive else 0
    return [re.compile(p, flags) for p in rule.patterns]


def scan_path(root: Path, ruleset: RuleSet) -> ScanResult:
    root = root.resolve()
    text_rules = [r for r in ruleset.rules if not r.is_artifact_rule]
    artifact_rules = [r for r in ruleset.rules if r.is_artifact_rule]
    compiled = {r.id: _compile(r) for r in text_rules}

    findings: list[Finding] = []
    seen: set[tuple] = set()
    files_scanned = 0

    def add(finding: Finding) -> None:
        k = finding.key()
        if k not in seen:
            seen.add(k)
            findings.append(finding)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            fpath = Path(dirpath) / name
            rel = fpath.relative_to(root).as_posix()

            # --- artifact (filename-based) rules ---------------------
            for rule in artifact_rules:
                suffix_ok = not rule.filename_suffixes or any(
                    name.lower().endswith(s) for s in rule.filename_suffixes
                )
                if suffix_ok and rule.filename_contains.lower() in name.lower():
                    add(Finding(
                        rule_id=rule.id, rule_name=rule.name,
                        severity=rule.severity,
                        evidence_type=rule.evidence_type,
                        component_type=rule.component_type,
                        component_name=fpath.name,
                        file=rel, line=None,
                        snippet=f"model artifact file named '{name}'",
                        fascsa_note=rule.fascsa_note,
                        remediation=rule.remediation,
                    ))

            # --- content rules ---------------------------------------
            try:
                size = fpath.stat().st_size
            except OSError:
                continue
            if size > MAX_TEXT_BYTES:
                continue
            try:
                raw = fpath.read_bytes()
            except OSError:
                continue
            if _looks_binary(raw[:8192]):
                continue
            text = raw.decode("utf-8", errors="replace")
            files_scanned += 1
            lines = text.splitlines()

            for rule in text_rules:
                if not _glob_match(rel, name, rule.file_globs):
                    continue
                for lineno, line in enumerate(lines, start=1):
                    for pat in compiled[rule.id]:
                        m = pat.search(line)
                        if m:
                            snippet = _redact(line.strip())[:MAX_SNIPPET]
                            add(Finding(
                                rule_id=rule.id, rule_name=rule.name,
                                severity=rule.severity,
                                evidence_type=rule.evidence_type,
                                component_type=rule.component_type,
                                component_name=m.group(0)[:80],
                                file=rel, line=lineno, snippet=snippet,
                                fascsa_note=rule.fascsa_note,
                                remediation=rule.remediation,
                            ))
                            break  # one finding per rule per line

    findings.sort(key=lambda f: (
        SEVERITY_ORDER.get(f.severity, 99), f.file, f.line or 0, f.rule_id,
    ))
    return ScanResult(target=str(root), files_scanned=files_scanned, findings=findings)
