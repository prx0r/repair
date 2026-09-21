"""Installed-base cohort -> replacement/maintenance demand."""
import numpy as np

def weibull_failure_profile(max_age, shape, scale):
    ages=np.arange(max_age+1,dtype=float)
    cdf=1-np.exp(-np.power(ages/scale,shape))
    probs=np.diff(cdf,prepend=0.0)
    return probs/probs.sum() if probs.sum()>0 else probs

def cohort_parts_demand(installs, failure_profile, parts_per_failure=1.0):
    installs=np.asarray(installs,float); f=np.asarray(failure_profile,float)
    # discrete convolution: install cohort at t contributes failures by age in f
    d=np.convolve(installs,f)[:len(installs)]*float(parts_per_failure)
    return d
