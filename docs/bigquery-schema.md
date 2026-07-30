# BigQuery Result Schema

## Overview

This document describes the BigQuery schema used to store LLM execution results.

Each prompt execution is stored as an independent row.

```text
1 prompt execution = 1 row
```

When a batch contains multiple prompts, one row is inserted for each prompt execution.
## Fields

| Column | Type | Description |
|--------|------|-------------|
| result_id | STRING | Unique ID for this row |
| run_id | STRING | ID of the batch run this row belongs to |
| executed_at | TIMESTAMP | When the batch run was executed |
| inserted_at | TIMESTAMP | When the row was inserted |
| provider | STRING | LLM provider (e.g. openai, anthropic) |
| model | STRING | Model name used |
| prompt_id | STRING | ID of the prompt |
| prompt | STRING | Prompt text |
| response | STRING | LLM response text |
| success | BOOL | Whether the execution succeeded |
| error | STRING | Error message if the execution failed |
| input_tokens | INT64 | Input token count |
| output_tokens | INT64 | Output token count |
| latency_ms | INT64 | Response latency in milliseconds |
| citations | STRING (JSON) | Source URLs returned by the provider (e.g. Perplexity); empty for providers without citations |
| target_score | FLOAT64 | Visibility score (0-100) of the target brand(s) |
| share_of_voice | FLOAT64 | Target brand mention share among all tracked brands (0-1) |
| analysis | STRING (JSON) | Full VisibilityAnalysis payload (per-brand mentions, ranks, scores) |
| metadata | STRING (JSON) | Reserved for future use |

The `target_score`, `share_of_voice`, and `analysis` columns are populated
only when visibility analysis is enabled and at least one brand is configured
in `prompts/brands.yaml`. Otherwise they are `NULL`.
