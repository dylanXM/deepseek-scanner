# DeepSeek Exposure Scan

**One command scans a codebase for DeepSeek components — hosted API endpoints, SDKs, model identifiers, dependencies, container pulls, local model files — and writes an evidence report you can hand to the customer or team asking the question.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)

`deepseek-scan` is an AI supply-chain transparency tool. It does static, local, read-only scanning: no network calls, no code leaves the machine, zero third-party dependencies.

## Why this exists

On **2026-10-20**, the U.S. Department of Homeland Security's **Exclusion and Removal Order #2026-01** was published in the Federal Register (**FR Doc. 2026-21447**, docket **DHS-2026-0628**). The order, issued under the Federal Acquisition Supply Chain Security Act (FASCSA) and signed **2026-07-24**, directs federal civilian agencies to stop procuring DeepSeek products and to remove DeepSeek products — including **third-party products and services developed using DeepSeek implementations** — from their systems. Through **FAR 52.204-30**, the same obligation flows down to contractors and their suppliers, who are now being asked to show what is inside the software they deliver.

The order does **not** restrict the general public or private companies using DeepSeek on their own account. It creates a documentation problem for one specific group: vendors who sell into the U.S. federal civilian market and need to find — and show they found — every place DeepSeek appears in their stack.

That is the problem this tool addresses: evidence collection, in the open, with its limits printed on the report.

- Order text and docket: [regulations.gov — DHS-2026-0628](https://www.regulations.gov/docket/DHS-2026-0628)
- Coverage: [The Hacker News (2026-10-21)](https://thehackernews.com/2026/10/us-orders-deepseek-removed-from-federal.html)
- Analysis: [TechTimes (2026-10-20)](https://www.techtimes.com/articles/329253/20261020/dhs-filed-deepseek-ban-28-days-after-agencies-lost-right-request-exceptions.htm)

## What it detects

Rules are data, not code — see [`rules/deepseek.rules.json`](rules/deepseek.rules.json) (rules version `2026.10.22.1`). The current set checks for:

| Evidence | Examples |
|---|---|
| Hosted API endpoints | `api.deepseek.com` in source and configuration |
| Credential / config variables | `DEEPSEEK_API_KEY`, `DEEPSEEK_API_BASE`, `DEEPSEEK_MODEL` |
| Model identifiers | `deepseek-chat`, `deepseek-reasoner`, `deepseek-r1`, `deepseek-v3`, `deepseek-ai/...` hub ids |
| SDK usage | `import deepseek`, `require("deepseek")`, JS/Go client references |
| Dependencies | DeepSeek packages in `requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, … and in lockfiles (transitive) |
| Container / deployment | DeepSeek images or model pulls (e.g. `ollama pull deepseek-r1`) in `Dockerfile`, compose files |
| Local model artifacts | `*.safetensors` / `*.gguf` weight files with DeepSeek names; `config.json` files declaring DeepSeek architectures |

Every finding carries the rule id, severity, `file:line` location and the matched line itself (with anything that looks like a live secret redacted before it can reach a shared report).

## Install

From PyPI:

```bash
pip install deepseek-scanner
```

Or from GitHub:

```bash
pip install git+https://github.com/dylanXM/deepseek-scanner.git
```

Or from a checkout:

```bash
git clone https://github.com/dylanXM/deepseek-scanner.git
cd deepseek-scanner
pip install .
```

Requires Python 3.10+. No third-party dependencies.

## Quick start

```bash
# Human-readable evidence report on stdout
deepseek-scan scan ./my-product

# Save a report / machine-readable JSON
deepseek-scan scan ./my-product --out evidence-report.md
deepseek-scan scan ./my-product --format json --out evidence-report.json

# CI gate: exit 1 if any critical or high finding exists
deepseek-scan scan ./my-product --fail-on high
```

## Example output

Scanning the intentionally dirty sample project in [`tests/fixtures/positive`](tests/fixtures/positive) (full reports: [`examples/sample-report.md`](examples/sample-report.md), [`examples/sample-report.json`](examples/sample-report.json)):

```text
# DeepSeek Exposure Scan - Evidence Report

| Field | Value |
|---|---|
| Files scanned | 9 |
| Total findings | 26 |

## Summary by severity

| Severity | Findings |
|---|---|
| critical | 2 |
| high | 22 |
| medium | 2 |

### Critical

#### DeepSeek hosted API endpoint (DS-001)

- Location: `app.py:8`
- Component: api.deepseek.com (hosted-api-endpoint)
- Evidence type: api_endpoint

    base_url="https://api.deepseek.com",
```

The JSON report uses an AI-BOM-style shape (component name / type / vendor, evidence, source file), so it can feed inventory tooling:

```json
{
  "rule_id": "DS-001",
  "severity": "critical",
  "component": { "name": "api.deepseek.com", "type": "hosted-api-endpoint", "vendor": "DeepSeek" },
  "evidence": { "type": "api_endpoint", "source_file": "app.py", "line": 8,
                "snippet": "base_url=\"https://api.deepseek.com\"," }
}
```

## GitHub Action

```yaml
- uses: dylanXM/deepseek-scanner@v0.1.1
  with:
    path: "."
    fail-on: "high"   # turn the scan into a CI gate
    out: "deepseek-exposure-report.md"
```

A complete example workflow is in [`examples/workflow.yml`](examples/workflow.yml). The action is composite rather than Docker-based: the scanner is a zero-dependency Python package, so there is no image to build or pull, and the pinned action ref is the version pin.

## Detection limits

This scanner checks a fixed, published set of textual and filename indicators. It detects, when present in the scanned tree: references to DeepSeek-hosted API endpoints in source and configuration; DeepSeek SDK imports and package names; DeepSeek names in dependency manifests and lockfiles (direct and transitive); DeepSeek image or model pulls in container definitions; and first-party model weight files and model configs.

It cannot detect: a model distilled from DeepSeek outputs and shipped under a different name with no textual trace; weight files that were renamed and stripped of identifying metadata; calls routed through a third-party gateway under that gateway's own domains and model names; or any use that leaves no artifact in the scanned tree.

A report with findings is evidence that the listed indicators are present at the listed locations. A report without findings means only that none of the indicators in the current rule set were found in the scanned tree; it is not proof that no DeepSeek-derived component exists in a product. Determinations about obligations under DHS Exclusion and Removal Order #2026-01 or FAR 52.204-30 rest with each organization and its counsel. This tool is an evidence-collection aid, not a legal determination.

## Roadmap

- **Phase 2 — weight provenance:** integrate the [Cisco Model Provenance Kit](https://www.helpnetsecurity.com/2026/04/30/cisco-ai-model-provenance-kit/) (planned integration; that project is Apache-2.0) so renamed weight files can be compared against known DeepSeek fingerprints instead of filenames.
- **Rule packs for future exclusion orders:** the engine is vendor-neutral; when another lab is named under FASCSA, it should be a new JSON rule file, not a new tool.
- **CycloneDX AI-BOM export** alongside the current JSON shape.
- More manifest formats (conda, Maven, Gradle) and monorepo-friendly path filters.

## Contributing

Issues and rule contributions are welcome. The highest-value contribution is a new detection rule: rules are JSON entries in `rules/deepseek.rules.json` with a pattern, severity, regulatory context and remediation text — plus a positive and negative fixture under `tests/fixtures/` proving the rule fires and stays quiet. Run `pytest` and `ruff check src tests` before opening a PR.

## License

Apache-2.0 — see [LICENSE](LICENSE).

This project is an independent open-source tool. It is not affiliated with DeepSeek, the U.S. Department of Homeland Security, or Cisco. Vendor and product names are used only to describe what the rules look for.
