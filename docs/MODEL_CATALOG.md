# Model catalog and what data each model forces POW to collect

| Model | Question | Minimum data | Primary output |
|---|---|---|---|
| Richards diffusion | How fast will technology T deploy? | adoption level through time | future installed base + deployment derivative |
| Leontief network | What does a demand/productivity shock hit upstream? | input-output coefficients | direct + indirect exposure |
| LP shadow prices | Which resource is actually binding? | resource intensity, supply, inventory, substitutes | marginal value of +1 resource unit |
| Synergy/PID screen | Which inputs matter only in combination? | synchronized input/output series | complementarity candidates |
| Hazard cohorts | What maintenance wave follows deployment? | install cohorts + failure hazards + parts | future replacement/repair demand |
| Skill scarcity | Does labour become the bottleneck? | skill intensity, workers, mobility, training | skill pressure + training gap |
| Link reconstruction | What supplier edges probably exist but are unobserved? | known links + firm industry/location/size | edge probability |
| Directed innovation | Where should substitution/complement R&D move next? | scarcity + market size + patents/papers/repos | innovation pressure |
| Lag/PCMCI | Which physical series leads which narrative/market series? | synchronized historical states | lag distributions / candidate edges |
| Event study | Does the relation survive historical episodes? | timestamped shocks + outcomes | abnormal response by horizon |

## Exact implementation roadmap

### V0 — included in this ZIP

Executable lightweight versions of diffusion, network propagation, LP duals, interaction screening, hazards, skills, link reconstruction and lag scans.

### V1 — clone/port paper implementations

1. Port the Wagenvoort/Lafond/Dyer/Farmer Bayesian diffusion application code, preserving posterior distributions.
2. Add Tigramite PCMCI+ and J-PCMCI+ for high-dimensional time-series discovery.
3. Add exact PID for shortlisted triplets/pairs; do not brute-force exact PID over the full universe.
4. Implement synthetic supply-network ensembles using public IO + firm populations.
5. Add an endogenous supplier-rewiring simulator inspired by Vu/Carrella/Axtell/Guerrero.
6. Backtest every signal in walk-forward time, with data-availability timestamps to prevent lookahead.

## Critical anti-lookahead rule

POW stores **event time**, **first observed time**, and **revision time** separately. Backtests may only use information actually available at the historical decision timestamp. Revised ONS/IO data cannot silently leak into an earlier backtest.
