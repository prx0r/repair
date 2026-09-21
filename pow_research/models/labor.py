"""Skill-shadow-price proxy from vacancies, workforce, mobility and training."""
import numpy as np

def labor_pressure(vacancies, workers, mobility=None, retraining_fraction=0.05, training_throughput=None, labels=None):
    v=np.asarray(vacancies,float); w=np.asarray(workers,float); n=len(v)
    if w.shape!=(n,): raise ValueError('workers shape mismatch')
    if mobility is None: M=np.eye(n)
    else:
        M=np.asarray(mobility,float)
        if M.shape!=(n,n): raise ValueError('mobility must be nxn')
    # M[i,j] is fraction/relative feasibility for workers in i to transition to j.
    reachable=w + float(retraining_fraction)*(w[:,None]*M).sum(axis=0)
    if training_throughput is not None: reachable += np.asarray(training_throughput,float)
    pressure=np.divide(v,reachable,out=np.full(n,np.inf),where=reachable>0)
    labels=labels or [str(i) for i in range(n)]
    return {'effective_supply':dict(zip(labels,reachable.tolist())),
            'pressure':dict(zip(labels,pressure.tolist())),
            'ranking':[labels[i] for i in np.argsort(-pressure)]}
