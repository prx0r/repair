"""Composable scarcity-migration scenario runner.

Scenario numbers are hypotheses/assumptions, never measurements unless the JSON
explicitly points to POW observations. The point is to make causal paths testable:
change a cost/capacity/demand assumption and inspect propagated costs, local duals,
and finite-shock criticality.
"""
from __future__ import annotations
import json
from pathlib import Path
from .models.network import leontief_cost_propagation
from .models.shadow import solve_shadow_prices
from .models.criticality import capacity_shock_criticality


def run_scenario(spec):
    out={'scenario':spec.get('scenario'),'status':'hypothesis_not_forecast'}
    if 'cost_network' in spec:
        n=spec['cost_network']
        out['cost_propagation']=leontief_cost_propagation(
            n['A'],n['primary_cost_shock'],n.get('labels'))
    if 'capacity_model' in spec:
        c=spec['capacity_model']
        kwargs=dict(
            B=c['B'],capacities=c['capacities'],product_values=c['product_values'],
            demand_caps=c.get('demand_caps'),input_labels=c.get('input_labels'),
            product_labels=c.get('product_labels'),
        )
        out['shadow_prices']=solve_shadow_prices(**kwargs)
        out['criticality_10pct']=capacity_shock_criticality(**kwargs,shock_fraction=0.10)
        out['criticality_50pct']=capacity_shock_criticality(**kwargs,shock_fraction=0.50)
    out['falsification']=spec.get('falsification',[])
    out['required_observations']=spec.get('required_observations',[])
    return out


def run_scenario_file(path):
    spec=json.loads(Path(path).read_text())
    return run_scenario(spec)
