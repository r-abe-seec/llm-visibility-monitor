# BigQuery Result Schema

## Overview

This document describes the BigQuery schema used to store LLM execution results.

Each prompt execution is stored as an independent row.

```text
1 prompt execution = 1 row
```

When a batch contains multiple prompts, one row is inserted for each prompt execution.