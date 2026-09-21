"""Lead/lag screening + optional PCMCI adapter.
Correlation is not promoted to causality. Use this to shortlist lag windows; then
run PCMCI+/event studies with known graph constraints and falsification tests.
"""
import numpy as np

def best_lead_lag(x,y,max_lag=30):
    x=np.asarray(x,float); y=np.asarray(y,float)
    if len(x)!=len(y): raise ValueError('same length required')
    rows=[]
    for lag in range(-max_lag,max_lag+1):
        if lag>0: a,b=x[:-lag],y[lag:]
        elif lag<0: a,b=x[-lag:],y[:lag]
        else: a,b=x,y
        mask=np.isfinite(a)&np.isfinite(b)
        if mask.sum()<4: continue
        c=float(np.corrcoef(a[mask],b[mask])[0,1])
        rows.append({'lag':lag,'correlation':c,'n':int(mask.sum())})
    best=max(rows,key=lambda r:abs(r['correlation'])) if rows else None
    return {'best':best,'all':rows,'lag_semantics':'positive lag => x leads y'}

def latency_to_threshold(event_times, target_times):
    """For each event timestamp (numeric), find first target timestamp >= event."""
    targets=sorted(target_times); out=[]
    import bisect
    for e in event_times:
        i=bisect.bisect_left(targets,e)
        out.append(None if i==len(targets) else targets[i]-e)
    vals=[v for v in out if v is not None]
    return {'latencies':out,'median':None if not vals else float(np.median(vals)),'n':len(vals)}

def pcmci_plus(data, var_names, tau_max=12, alpha=0.05):
    """Optional Tigramite PCMCI+ wrapper. Install `tigramite` separately."""
    try:
        from tigramite import data_processing as pp
        from tigramite.pcmci import PCMCI
        from tigramite.independence_tests.parcorr import ParCorr
    except ImportError as e:
        raise ImportError('pip install tigramite to enable PCMCI+') from e
    arr=np.asarray(data,float)
    df=pp.DataFrame(arr,var_names=var_names)
    pcmci=PCMCI(dataframe=df,cond_ind_test=ParCorr(),verbosity=0)
    r=pcmci.run_pcmciplus(tau_min=0,tau_max=tau_max,pc_alpha=alpha)
    links=[]; p=r['p_matrix']; val=r['val_matrix']
    for i,src in enumerate(var_names):
        for j,dst in enumerate(var_names):
            for tau in range(p.shape[2]):
                if p[i,j,tau] <= alpha:
                    links.append({'src':src,'dst':dst,'lag':tau,'p':float(p[i,j,tau]),'strength':float(val[i,j,tau])})
    return {'links':links,'graph':r.get('graph').tolist() if hasattr(r.get('graph'),'tolist') else None}
