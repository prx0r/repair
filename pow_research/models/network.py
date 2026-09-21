"""Production-network shock propagation.
Convention: A[i,j] = units/cost-share of input i used per unit of output j.
Then unit prices satisfy p = A.T @ p + v, so primary-cost shocks propagate via
(I - A.T)^-1. This is a baseline Leontief model; nonlinear substitution belongs
in scenario ensembles, not hidden inside this primitive.
"""
import numpy as np

def leontief_cost_propagation(A, primary_cost_shock, labels=None):
    A=np.asarray(A,dtype=float); s=np.asarray(primary_cost_shock,dtype=float)
    n=A.shape[0]
    if A.shape!=(n,n) or s.shape!=(n,): raise ValueError('A must be nxn and shock length n')
    M=np.eye(n)-A.T
    cond=float(np.linalg.cond(M))
    if not np.isfinite(cond) or cond>1e12: raise ValueError('near-singular production network')
    L=np.linalg.inv(M); effect=L@s
    labels=labels or [str(i) for i in range(n)]
    return {'effects':dict(zip(labels,effect.tolist())), 'multiplier_matrix':L.tolist(), 'condition_number':cond}

def shock_paths(A, shock_idx, depth=4, threshold=1e-6):
    """Simple path expansion for explanation, not causal proof."""
    A=np.asarray(A,float); frontier={shock_idx:1.0}; out=[]
    for d in range(1,depth+1):
        nxt={}
        for src,w in frontier.items():
            for dst,val in enumerate(A[src,:]):
                score=w*float(val)
                if abs(score)>=threshold:
                    out.append((d,src,dst,score)); nxt[dst]=nxt.get(dst,0)+score
        frontier=nxt
    return out


def implied_input_demand(new_build, bom, input_labels=None, product_labels=None):
    """Translate product new-build flows into physical input demand.

    `new_build` can be one product vector (P,) or a time-by-product matrix (T,P).
    `bom` is input-by-product (I,P): units of input i per unit of product p.
    This is the bridge from diffusion forecasts to component/material/skill load.
    """
    q=np.asarray(new_build,float); B=np.asarray(bom,float)
    if B.ndim!=2: raise ValueError('bom must be input x product')
    if q.ndim==1:
        if q.shape[0]!=B.shape[1]: raise ValueError('product dimension mismatch')
        d=B@q
    elif q.ndim==2:
        if q.shape[1]!=B.shape[1]: raise ValueError('product dimension mismatch')
        d=q@B.T
    else: raise ValueError('new_build must be 1d or 2d')
    il=input_labels or [f'input_{i}' for i in range(B.shape[0])]
    pl=product_labels or [f'product_{j}' for j in range(B.shape[1])]
    return {'input_labels':il,'product_labels':pl,'demand':d.tolist()}
