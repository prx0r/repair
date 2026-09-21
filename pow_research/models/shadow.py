"""Physical bottleneck / shadow-price solver.
Maximize economic value of product activities subject to physical input capacity.
B[input, product] is input required per unit product.
"""
import numpy as np
from scipy.optimize import linprog

def solve_shadow_prices(B, capacities, product_values, demand_caps=None, input_labels=None, product_labels=None):
    B=np.asarray(B,float); cap=np.asarray(capacities,float); val=np.asarray(product_values,float)
    m,n=B.shape
    if cap.shape!=(m,) or val.shape!=(n,): raise ValueError('shape mismatch')
    A=B.copy(); b=cap.copy()
    if demand_caps is not None:
        dc=np.asarray(demand_caps,float)
        if dc.shape!=(n,): raise ValueError('demand_caps length mismatch')
        A=np.vstack([A,np.eye(n)]); b=np.r_[b,dc]
    res=linprog(-val,A_ub=A,b_ub=b,bounds=[(0,None)]*n,method='highs')
    if not res.success: raise RuntimeError(res.message)
    x=res.x; used=B@x; util=np.divide(used,cap,out=np.zeros_like(used),where=cap>0)
    # HiGHS reports marginals for minimization. Since objective is -value, negate capacity marginals.
    marg=np.asarray(res.ineqlin.marginals[:m]); shadow=np.maximum(0,-marg)
    il=input_labels or [f'input_{i}' for i in range(m)]; pl=product_labels or [f'product_{j}' for j in range(n)]
    return {'objective_value':float(val@x),'activities':dict(zip(pl,x.tolist())),
            'shadow_prices':dict(zip(il,shadow.tolist())), 'utilization':dict(zip(il,util.tolist())),
            'binding':[il[i] for i,u in enumerate(util) if u>0.999]}
