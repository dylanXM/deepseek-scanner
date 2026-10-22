# Repository setup checklist (run once, at repo creation)

## Name

- **First choice: `deepseek-scanner`** — `github.com/dylanXM/deepseek-scanner`
- Fallbacks, in order, if the name is taken or reads badly:
  1. `deepseek-exposure-scan` (matches the PyPI package name)
  2. `ds-exposure-scan`
  3. `model-exposure-scan` (vendor-neutral; weaker search value)

## About (right-hand sidebar)

Description (one line):

> Scan a codebase for DeepSeek exposure surface — API endpoints, SDKs, model ids, dependencies, container pulls, model artifacts — and generate an evidence report. Built for supplier disclosure under DHS Order #2026-01.

Website: leave blank until a landing page exists (do not link the repo itself).

## Topics (GitHub allows up to 20)

```
deepseek
security-scanner
supply-chain-security
ai-bom
sbom
fascsa
govtech
devsecops
llm
model-provenance
static-analysis
cli
python
github-action
vendor-risk
ai-security
federal-contracting
```

## Social preview (Settings → Social preview, 1280×640)

Text for the preview image:

> **DeepSeek Exposure Scan**
> Find DeepSeek components in your codebase.
> Evidence reports for supplier disclosure — limits printed on the report.

Suggested image: dark background, terminal-style excerpt of the sample
report (the severity table + one critical finding), project name large
at top-left. Generate from `examples/sample-report.md` output; do not
use any vendor or government logo.

## One-time settings

- [ ] Add the deploy key (public half lives with the project owner;
      title it `deepseek-scanner deploy (local build machine)`)
- [ ] Actions: enabled (CI workflow + dogfood scan already in repo)
- [ ] Default branch: `main`
- [ ] Releases: create `v0.1.0` after the first push; attach
      `examples/sample-report.md` and `examples/sample-report.json`
- [ ] Issues: enable; Discussions: optional, enable if Show HN /
      Reddit threads start producing questions
- [ ] Pin nothing yet; add the repo to the profile's pinned list only
      after the launch posts go out
