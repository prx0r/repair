"""Deterministic Richards-curve baseline.
For production research, compare against the 2026 Wagenvoort/Lafond/Dyer/Farmer
Bayesian replication package. This module is deliberately small and backtestable.
"""
import numpy as np
from scipy.optimize import curve_fit

def richards_curve(t, K, r, t0, nu):
    t=np.asarray(t,dtype=float)
    z=np.clip(-r*(t-t0), -700, 700)
    return K / np.power(1.0 + nu*np.exp(z), 1.0/nu)

def fit_richards(t, y, horizon=12):
    t=np.asarray(t,dtype=float); y=np.asarray(y,dtype=float)
    if len(t)<5 or np.any(y<0): raise ValueError('need >=5 nonnegative observations')
    K0=max(float(y.max())*1.3,1.0); r0=0.2; t00=float(np.median(t)); nu0=1.0
    lo=[max(float(y.max()),1e-9),1e-5,float(t.min())-10*max(1,len(t)),0.05]
    hi=[max(K0*100, float(y.max())+1),10.0,float(t.max())+10*max(1,len(t)),20.0]
    popt,_=curve_fit(richards_curve,t,y,p0=[K0,r0,t00,nu0],bounds=(lo,hi),maxfev=50000)
    future_t=np.arange(t.max()+1,t.max()+1+horizon)
    fitted=richards_curve(t,*popt); forecast=richards_curve(future_t,*popt)
    new_build=np.diff(np.r_[richards_curve([t.max()],*popt),forecast])
    return {'K':popt[0],'r':popt[1],'t0':popt[2],'nu':popt[3],
            'rmse':float(np.sqrt(np.mean((fitted-y)**2))),
            'future_t':future_t.tolist(),'forecast':forecast.tolist(),'implied_new_build':new_build.tolist()}
