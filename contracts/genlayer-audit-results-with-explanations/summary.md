# Audit Summary

## Executors observed:
- audit_executor
- social_executor
- consensus_executor
- financial_executor

## Key observations:
- Correct routing for audit-related queries
- Fallback used for ambiguous inputs
- Injection attempt detected but still influenced routing (risk area)
- Consensus triggered only for non-classifiable inputs

## Risk Notes:
- Weak input sanitization against executor injection patterns
- Inconsistent fallback classification behavior
