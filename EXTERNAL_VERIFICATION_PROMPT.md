# External LLM verification workflow

Use this workflow when verifying records with ChatGPT or Claude instead of the local API verifier. Verify **five apps per conversation turn**; it produces more reliable citations and makes each result easy to audit.

1. Copy five records from `final_findings.json` (IDs 1-50 only).
2. Paste them into the prompt below.
3. Save each JSON response in one combined `external_verification.json` file using the schema below.
4. Run `python import_external_verification.py external_verification.json` to validate the file, calculate metrics, and regenerate `report.html`.

## Prompt to paste into ChatGPT or Claude

```text
You are an evidence-first SaaS API verification analyst. Verify ONLY the app records pasted below.

For each app:
1. Search and use official developer documentation or the vendor's official API pages only. Do not use blogs, directory listings, or search-result snippets as evidence.
2. Compare the record's auth_methods, accessibility_tier, api_surface, and buildability_verdict against the evidence.
3. Set a field to true only when the official documentation supports it; false when it contradicts it; null when the evidence is insufficient.
4. Do not infer that an API is self-serve simply because documentation exists. Do not infer an MCP server unless official evidence explicitly establishes it.
5. If a page is inaccessible, unclear, or does not support the claim, use overall_status "Unverifiable" or "Partial". Never guess.
6. Cite one or more direct official documentation URLs for each app.

Return ONLY valid JSON: an array with one object per app. Do not use Markdown fences or commentary.

Required JSON schema:
[
  {
    "app_id": 1,
    "app_name": "Vendor name",
    "auth_methods_verified": true,
    "accessibility_tier_verified": null,
    "api_surface_verified": false,
    "buildability_verdict_verified": null,
    "evidence_url_verified": true,
    "overall_status": "Correct",
    "evidence_summary": "Short evidence-grounded summary, including the specific limitation when relevant.",
    "corrections": "None or a concise correction to the original record.",
    "evidence_urls": ["https://official-vendor-docs.example/page"]
  }
]

Records to verify:
PASTE UP TO FIVE RECORDS HERE
```

## Combined file format

Create `external_verification.json` with the outputs from every batch. The top-level object must look like this:

```json
{
  "provider": "ChatGPT" ,
  "verified_apps": [
    {
      "app_id": 1,
      "app_name": "Salesforce",
      "auth_methods_verified": true,
      "accessibility_tier_verified": null,
      "api_surface_verified": true,
      "buildability_verdict_verified": null,
      "evidence_url_verified": true,
      "overall_status": "Partial",
      "evidence_summary": "...",
      "corrections": "None",
      "evidence_urls": ["https://developer.salesforce.com/docs/apis"]
    }
  ]
}
```

The import script rejects duplicate IDs, IDs outside the completed 50-app dataset, and records without the required fields. It preserves `Unverifiable` results instead of treating them as passes.
