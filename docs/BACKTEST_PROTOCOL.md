# POW backtest protocol

A result is not alpha until it survives this protocol.

1. **Point-in-time dataset**: use `observed_at`, not today's revised historical value.
2. **Hypothesis freeze**: define source variables, lag window, transform and outcome before reading test-period results.
3. **Walk-forward**: fit only on past; predict next block; roll forward.
4. **Episode split**: hold out entire shock episodes, not random rows.
5. **Multiple-testing control**: record every tested pair/triplet; use FDR/Benjamini-Hochberg or a stricter family rule.
6. **Economic significance**: report effect size and transaction/implementation constraints, not only p-values.
7. **Graph uncertainty**: for inferred supply chains, run the signal over an ensemble and report robustness.
8. **Source latency**: backtest the actual publication/update latency of the source.
9. **Kill gate**: every causal edge has a falsifier, e.g. sign reversal, lag instability, supply response, substitution, or non-replication.
10. **Outcome receipt**: append the realized result back into POW so model selection itself becomes historical data.

Suggested edge record:

```json
{
  "src":"component:foo.stock",
  "dst":"firm:bar.price",
  "method":"pcmci+",
  "train_window":["2027-01-01","2029-12-31"],
  "lag_days":17,
  "effect":-0.24,
  "p":0.003,
  "oos_effect":-0.19,
  "episodes":8,
  "robust_network_share":0.91,
  "state":"inferred"
}
```
