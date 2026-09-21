# POW causal research basis

## The synthesis

The strongest academic basis for POW is complexity economics and production-network research rather than a collapse/AGI commentator.

### Farmer / Lafond / McNerney / Carvalho — propagation

Production networks amplify technology improvements because cost/productivity changes propagate through chains of intermediate inputs. POW should therefore model the economy as a network rather than independent asset series.

Source: McNerney et al., *How production networks amplify economic growth* (PNAS, 2022).
https://pmc.ncbi.nlm.nih.gov/articles/PMC8740592/

### Wagenvoort / Lafond / Dyer / Farmer — diffusion

A 2026 working paper assembles 120 mature technologies and reports surprisingly regular S-curve diffusion. A Bayesian Bertalanffy–Richards model outperformed common alternatives in their out-of-sample backtests and could make useful forecasts from early diffusion.

POW implication: **installed-base/adoption histories are P0 data.** The derivative of an adoption curve is a latent physical demand curve.

https://www.inet.ox.ac.uk/publications/no-2026-19-universality-and-predictability-of-technology-diffusion

### Pichler / Lafond / Farmer — technology dependency graph

Innovation rates become more predictable when the surrounding technological dependency network is included. Their out-of-sample results report average predictive gains around 20% without future neighbour information and 28% in the stronger-information setting.

POW implication: research/patent/GitHub activity should be graph-linked, not counted in isolation.

https://arxiv.org/abs/2003.00580

### Rajpal / Guerrero — hidden complementarity

Their 2025 PNAS Nexus paper uses partial information decomposition to infer synergistic input interactions without imposing a production function.

POW implication: search not only for `X -> Y`, but for combinations `(X1, X2) -> Y` where the joint state contains information unavailable from either input alone.

https://academic.oup.com/pnasnexus/article/4/4/pgaf102/8096462

### Mungo / Lafond / Farmer — reconstruct missing supply networks

Firm-to-firm supply-chain data are incomplete. Their gradient-boosting link-prediction approach performs materially better than baselines; industry, location and firm size are important features.

POW implication: unknown edge != no edge. Maintain observed-edge and probabilistic-edge layers.

https://www.sciencedirect.com/science/article/pii/S0165188923000131

### Ng / Mungo / Bertrand / Lafond — synthetic network ensembles

The August 2026 working paper generates synthetic firm supply networks using public aggregate data while matching macro input-output structure and micro network properties.

POW implication: run bottleneck simulations over **ensembles of plausible networks**, and rank signals by robustness across reconstructions.

https://arxiv.org/abs/2608.03716

### Carvalho / Voigtländer — path-dependent input adoption

Firms/sectors are more likely to adopt inputs already used in the network neighbourhood of their existing suppliers.

POW implication: when a new input appears, adoption probability should depend on network distance and existing supplier neighbourhood, not only theoretical usefulness.

https://www.nber.org/papers/w20025

### Acemoglu — directed technical change

Innovation responds to both a **price/scarcity effect** and a **market-size effect**.

POW implication: after detecting a new bottleneck, predict not just its price but where substitute/economising innovation activity should accelerate. Conversely, a newly abundant factor may attract complementary innovation.

https://www.nber.org/papers/w8287

### Del Rio-Chanona / Mealy / Farmer — labour mobility networks

Labour adjustment after automation depends on feasible transitions between occupations, not simply aggregate unemployed-worker counts.

POW implication: skills are a production network. Track occupation demand, skills overlap, training capacity, completions and geographic mobility.

https://pmc.ncbi.nlm.nih.gov/articles/PMC7879770/

### Runge — PCMCI+

PCMCI+ is designed for lagged and contemporaneous causal discovery in autocorrelated nonlinear multivariate time series.

POW implication: standard correlation screens are insufficient; use causal discovery only after enough synchronized state has accumulated, and validate every edge out of sample.

https://arxiv.org/abs/2003.03685

## POW master equation

For technology `T`, future demand for physical input `i`:

```text
new_build_demand_i(t)
  = sum_T intensity[T,i] * d(installed_base_T)/dt

maintenance_demand_i(t)
  = sum_T sum_age cohort_T(t-age) * hazard_T,i(age)

total_load_i
  = new_build + maintenance + replacement + inventory_build
```

Effective supply:

```text
supply_i = current_capacity + inventory + qualified_substitute_capacity
```

The primitive pressure ratio is:

```text
pressure_i = total_load_i / max(effective_supply_i, eps)
```

But the better POW quantity is an LP dual / shadow price:

> how much does system objective improve if one more unit of resource `i` becomes available?

That makes “what becomes valuable?” mathematically testable.

## Causal assimilation latency

For physical precursor `X` and financial/narrative response `Y`:

```text
L(X -> Y) = t(first statistically durable Y response) - t(first X state transition)
```

Store the full empirical lag distribution across historical shocks. A useful edge is one that repeats across episodes and survives walk-forward validation.

## Architecture rule

**Observe broadly; infer narrowly.** Raw data can be broad. Published causal edges must carry stronger evidence.
