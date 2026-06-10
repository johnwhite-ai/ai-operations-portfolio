# data-profiler

**Team:** Operations
**Role:** Turns messy raw data into a structured, sourced input set.

## Does
- Ingests raw, inconsistent data.
- Outputs a clean structure with every field tagged Confirmed / Estimated / Missing and a per-field source.
- Never invents a value. A gap is returned as Missing.

## Why it matters
Bad inputs flow downstream into bad decisions. This agent is the quality gate that makes everything after it trustworthy.
