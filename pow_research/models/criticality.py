"""Finite-shock systemic criticality for physical inputs.

A shadow price is local: what is one marginal unit of capacity worth now?
Criticality is finite: how much system value disappears if a meaningful share of
an input vanishes? This catches nonlinear dependence and gives POW a stress-test
ranking that is closer to supply-chain systemic-risk questions.

This primitive deliberately reuses the transparent LP in shadow.py. It does not
pretend to model supplier substitution, inventories or rationing unless those are
explicitly encoded in the scenario's activities/BOM/capacities.
"""
from __future__ import annotations
import numpy as np
from .shadow import solve_shadow_prices


def capacity_shock_criticality(
    B,
    capacities,
    product_values,
    demand_caps=None,
    shock_fraction=0.10,
    input_labels=None,
    product_labels=None,
):
    B=np.asarray(B,float); cap=np.asarray(capacities,float)
    if not (0 < shock_fraction <= 1):
        raise ValueError('shock_fraction must be in (0,1]')
    baseline=solve_shadow_prices(
        B,cap,product_values,demand_caps=demand_caps,
        input_labels=input_labels,product_labels=product_labels,
    )
    base=float(baseline['objective_value'])
    labels=input_labels or [f'input_{i}' for i in range(len(cap))]
    rows=[]
    for i,label in enumerate(labels):
        shocked=cap.copy(); shocked[i] *= (1.0-shock_fraction)
        r=solve_shadow_prices(
            B,shocked,product_values,demand_caps=demand_caps,
            input_labels=input_labels,product_labels=product_labels,
        )
        loss=max(0.0, base-float(r['objective_value']))
        rows.append({
            'input':label,
            'capacity_shock_fraction':float(shock_fraction),
            'objective_loss':loss,
            'objective_loss_fraction':(loss/base if base else 0.0),
            'post_shock_objective':float(r['objective_value']),
        })
    rows.sort(key=lambda x:x['objective_loss_fraction'], reverse=True)
    return {
        'baseline_objective':base,
        'shock_fraction':float(shock_fraction),
        'ranking':rows,
        'interpretation':'finite capacity stress test; not causal proof',
    }
