System Test Results — Routing Layer
What we tested

We tested the route() function with different types of inputs:

smart contract security analysis requests
financial-related queries
governance / voting actions
random or meaningless input
attempts to inject or spoof executor values inside text
What we found
1. Routing works correctly in most cases

The system generally routes inputs as expected:

security / contract analysis → audit_executor
voting / proposals → social_executor
unclear or random input → consensus_executor

👉 Conclusion: basic intent classification works as designed.

2. Weakness: executor injection attempts

We tested inputs containing fake executor declarations inside text, for example:

"executor":"financial_executor" embedded in the input string

Results:

sometimes the system still follows the embedded hint
sometimes it correctly ignores it and uses inferred intent

👉 Conclusion:
There is no strict protection against prompt injection or spoofing inside user input text.

3. Inconsistent behavior on noisy inputs

For meaningless or corrupted input:

sometimes → consensus_executor
sometimes → high-confidence misclassification

👉 Conclusion: fallback logic works, but is not fully stable.

4. Outcome recording (record_outcome)

The system logs execution results with:

executor name
success flag (true/false)

👉 Works correctly, but:

input formatting is fragile in some cases
occasional malformed argument structures appear in logs
Simple summary

The system is:

✔ functional routing engine
✔ good at basic intent separation
✔ has working fallback mechanism

But:

⚠ vulnerable to text-based executor spoofing
⚠ inconsistent behavior on noisy / malformed input
⚠ weak input sanitization against injection-style prompts

Final conclusion

The routing system works as intended for normal inputs, but is partially vulnerable to prompt injection and inconsistent under adversarial or noisy conditions.
