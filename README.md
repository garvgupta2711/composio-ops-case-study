# SaaS Integration Research Case Study

This repository contains a scoped Product Operations research study of 50 SaaS APIs for AI-agent integration.

The deliverable is [report.html](report.html). It is self-contained and can be opened locally or deployed as a static site.

## Scope

The original research list contained 100 apps. This submission includes 50 completed records. Apps 51–100 are retained as explicit `UNKNOWN` placeholders in the raw data and are excluded from the case study.

For each completed app, the dataset records:

- Category and one-line product description
- Authentication method
- Developer-access tier
- API surface
- Buildability verdict and blocker
- Developer-documentation URL

## Findings

- 40 of 50 apps are buildable today.
- 40 of 50 offer Tier 1 self-serve access.
- 80% use OAuth2.
- 40 are immediate toolkit candidates.
- 50 of 50 records were reviewed through a cited, ChatGPT-assisted verification workflow.
- The review produced 83.5% field alignment across 200 explicit pass/fail checks and led to 23 refinements.

Field alignment is an evidence-review metric, not a claim of independent human validation or ground truth.

## Repository contents

- `report.html` — final case-study page
- `final_findings.json` — research records and evidence URLs
- `patterns.json` — aggregated findings
- `verification_report.json` — external verification results and citations
- `main.py` — research pipeline
- `modern_report.py` — data-driven report renderer
- `analyze_patterns.py` — pattern aggregation
- `EXTERNAL_VERIFICATION_PROMPT.md` — prompt for the external verification workflow
- `import_external_verification.py` — validates imported verification JSON and regenerates the report

## Reproduce the report

Install the dependencies:

```bash
pip install -r requirements.txt
```

Regenerate the HTML from the committed data:

```bash
python generate_final_report.py
```

To run a new research pass, set `OPENAI_API_KEY` and optionally `COMPOSIO_API_KEY`, then run:

```bash
python run_pipeline.py
```

To repeat the external review workflow, follow `EXTERNAL_VERIFICATION_PROMPT.md`, save the output as `external_verification.json`, then run:

```bash
python import_external_verification.py external_verification.json
```

## Limitations

The study is limited to 50 completed apps. Verification is ChatGPT-assisted and based on cited official documentation; unresolved or partial results are retained in the verification output rather than treated as confirmed facts.
