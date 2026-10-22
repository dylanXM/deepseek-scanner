# Show HN draft — DO NOT POST without owner review

**Title:**
Show HN: DeepSeek Exposure Scan – find DeepSeek components in your codebase

**Body:**

Last week DHS published Exclusion and Removal Order #2026-01 (signed back in July, published in the Federal Register on Oct 20). Federal civilian agencies have to remove DeepSeek products, including "third-party products and services developed using DeepSeek implementations," and via FAR 52.204-30 that obligation flows down to contractors — who now have to show their customers what is actually inside the software they ship.

I looked for a tool that does the boring first pass — grep the repo for the endpoint, the SDK, the model ids, the dependency entries, the `ollama pull deepseek-*` in the Dockerfile, the weight files in the tree — and writes it up as an evidence report a contracts team can file. I could not find one, so I built a small one:

- Zero-dependency Python CLI: `deepseek-scan scan ./repo`
- Rules are a single JSON file (patterns + severity + regulatory context + remediation), so adding a rule is a data change, not a code change
- Markdown report for humans, JSON (AI-BOM-style) for inventory tooling
- GitHub Action with `--fail-on high` if you want it as a CI gate
- Anything that looks like a live API key is redacted before it can end up in a shared report

The part I care most about is what it cannot do, which is printed on every report: it cannot detect a model that was distilled from DeepSeek and renamed, weights stripped of metadata, or calls proxied through someone else's gateway. A clean scan means "none of these indicators were found," nothing more. If you need weight-level provenance, Cisco's Model Provenance Kit does fingerprinting and integrating it is on the roadmap.

It does not apply to the general public using DeepSeek — this is for vendors selling into the federal civilian market who suddenly need receipts.

Repo: https://github.com/dylanXM/deepseek-scanner

Feedback I would especially value: rules I am missing (other manifest formats? other places DeepSeek hides in a stack?), and false positives — the fixtures under tests/fixtures/ show what the current rules fire on.
