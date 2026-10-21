# NBFC Corrected QA Source Data Quality Report

- **Status:** PASS
- **Generated UTC:** 2026-10-21T11:23:36.439309+00:00
- **Git commit:** 070bf8d8f9e2a2b8c02250c40b537f52a0241bc2
- **Snowflake role:** NBFC_CI_ROLE

## Source row counts

| Source table | Rows |
|---|---:|
| `loans` | 8,476 |
| `emi_schedule` | 279,486 |
| `payments` | 93,753 |
| `collections` | 9,136 |

**Total rows across source tables:** 390,851

## Data quality checks

| Check | Status | Observed |
|---|---|---:|
| No missing loan application links | **PASS** | `0` |
| Loan/application fields consistent and application approved | **PASS** | `0` |
| No null loan IDs | **PASS** | `0` |
| No duplicate loan IDs | **PASS** | `0` |
| No orphan emi_schedule loan references | **PASS** | `0` |
| No orphan payments loan references | **PASS** | `0` |
| No orphan collections loan references | **PASS** | `0` |
| Requested amounts are present and non-negative | **PASS** | `{"null": 0, "negative": 0}` |

## Requested amount summary

```json
{
  "null_requested": 0,
  "negative_requested": 0,
  "total_requested": "8632789634.75",
  "min_requested": "50012.93",
  "max_requested": "1999846.25"
}
```

## Fact table metrics

**UNAVAILABLE** — FACT_LOAN_QA was not visible in NBFC_DW table metadata to the current CI role during this run.

## Limitations

- This report covers corrected QA source tables only.
- No fact-table, DPD, or PAR metrics are reported in this version.
- Passing source checks does not certify a reconciled financial ledger.
- Financial summaries are descriptive and not audited balances.
