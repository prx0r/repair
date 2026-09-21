"""Complementarity screening.

`synergy_screen` is deliberately labelled a SCREEN, not formal PID. It computes
I([X1,X2];Y) - max(I(X1;Y),I(X2;Y)) after discrete binning. Positive values flag
pairs whose joint state contains predictive information beyond either input alone.
For publishable PID, use JIDT / the Rajpal-Guerrero method on shortlisted pairs.
"""
import numpy as np
from collections import Counter

def _disc(x,bins=5):
    x=np.asarray(x)
    if np.issubdtype(x.dtype,np.number):
        # Preserve already-discrete numeric variables instead of collapsing
        # binary/categorical inputs through quantile binning.
        vals, inv = np.unique(x, return_inverse=True)
        if len(vals) <= max(2, bins):
            return inv
        q=np.unique(np.quantile(x,np.linspace(0,1,bins+1)))
        if len(q)<=2:
            return inv
        return np.digitize(x,q[1:-1],right=True)
    _,inv=np.unique(x.astype(str),return_inverse=True); return inv

def _mi(x,y):
    x=list(map(str,x)); y=list(map(str,y)); n=len(x)
    cx=Counter(x); cy=Counter(y); cxy=Counter(zip(x,y)); out=0.0
    for (a,b),c in cxy.items():
        p=c/n; out += p*np.log2(p/((cx[a]/n)*(cy[b]/n)))
    return float(out)

def synergy_screen(x1,x2,y,bins=5):
    a=_disc(x1,bins); b=_disc(x2,bins); z=_disc(y,bins)
    joint=[f'{i}|{j}' for i,j in zip(a,b)]
    i1=_mi(a,z); i2=_mi(b,z); ij=_mi(joint,z)
    return {'mi_x1_y':i1,'mi_x2_y':i2,'mi_joint_y':ij,'synergy_screen_bits':max(0.0,ij-max(i1,i2)),
            'method':'screen_only_not_formal_PID'}
