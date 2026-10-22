# X thread draft — DO NOT POST without owner review

1/ DHS just published its DeepSeek exclusion order (signed in July, public Oct 20). Federal civilian agencies must remove DeepSeek — including third-party products "developed using DeepSeek implementations."

If you sell software to that market, your customer is about to ask what's inside it. 🧵

2/ The obligation flows down through FAR 52.204-30 to contractors and suppliers. This week people are circulating manual audit checklists for it.

So I automated the boring part.

3/ Meet DeepSeek Exposure Scan — a zero-dependency Python CLI:

`deepseek-scan scan ./your-repo`

It looks for:
• api.deepseek.com endpoints
• DEEPSEEK_API_KEY & friends
• deepseek-chat / -reasoner / -r1 model ids
• SDK imports
• deps in manifests + lockfiles
• `ollama pull deepseek-*` in Dockerfiles
• weight files + model configs in the tree

4/ Output is an evidence report: every finding with file:line, the matched snippet (secrets redacted), severity, and remediation text. Markdown for humans, JSON (AI-BOM-style) for inventory tooling. There's also a GitHub Action if you want it as a CI gate.

5/ The honest part, printed on every report: this cannot detect a model that was distilled from DeepSeek and renamed, or weights stripped of metadata. A clean scan = "no known indicators found." Nothing more. Weight fingerprinting is on the roadmap, not in this release.

6/ Rules are a single JSON file — pattern, severity, regulatory context, remediation. Adding coverage for a new hiding place is a data PR, not a code change.

7/ Apache-2.0, no network calls, everything runs locally:
https://github.com/dylanXM/deepseek-scanner

If your stack hides DeepSeek somewhere the rules miss, I want the issue.
