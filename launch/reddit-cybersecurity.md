# r/cybersecurity draft — DO NOT POST without owner review

**Title:**
Open-source scanner for DeepSeek exposure in your codebase (evidence reports for DHS Order #2026-01 supplier questions)

**Body:**

Context: DHS Exclusion and Removal Order #2026-01 (Federal Register, 2026-10-20, docket DHS-2026-0628) directs federal civilian agencies to remove DeepSeek products, including third-party products "developed using DeepSeek implementations." FAR 52.204-30 flows this to contractors, and agencies have started asking suppliers to disclose model components. The manual audit guides circulating this week are four-question checklists; this automates the evidence-collection part.

**What it does**

Static, local, read-only scan of a repo. Zero-dependency Python. Rules are one JSON file, each rule has an id, severity, the regulatory context, and remediation text:

- `api.deepseek.com` endpoints in source/config (critical)
- `DEEPSEEK_API_KEY` and related config variables
- Model ids: `deepseek-chat`, `deepseek-reasoner`, `deepseek-r1`, `deepseek-v3`, `deepseek-ai/*` hub references
- SDK imports (Python/JS/Go)
- DeepSeek packages in dependency manifests, and in lockfiles as transitive deps
- `Dockerfile` / compose references, e.g. `ollama pull deepseek-r1:7b`
- Model artifacts by filename (`.safetensors`, `.gguf`) and `config.json` files declaring DeepSeek architectures

Output: Markdown evidence report (file:line + snippet per finding; secrets redacted) or JSON in an AI-BOM-style shape. Also ships as a GitHub Action with a severity gate.

**Limits, up front**

It cannot detect distilled-and-renamed models, metadata-stripped weights, or traffic proxied through a third-party gateway. A clean result is "no known indicators found," and the report says exactly that. Weight fingerprinting (Cisco Model Provenance Kit integration) is the planned phase 2, not a claim about the current release.

Repo: https://github.com/dylanXM/deepseek-scanner — rules live in `rules/deepseek.rules.json`; rule PRs with fixtures are the most useful contribution if your stack hides DeepSeek somewhere the current set misses.

Not affiliated with DeepSeek or DHS; built for the vendor side of the disclosure question.
