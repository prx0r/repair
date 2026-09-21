from __future__ import annotations
import argparse, json
from .registry import filter_sources, get_source
from .probe import probe
from .models.scenario import run_file

def demo():
    from .models.diffusion import forecast, richards
    from .models.shadow import shadow_prices
    from .models.synergy import interaction_uplift
    import numpy as np
    t=np.arange(30.0)
    y=richards(t,1000,0.22,16,1.2)
    f=forecast(t[:22],y[:22],[22,24,26,28,30])
    print('diffusion deployment rate:',np.round(f['deployment_rate'],2).tolist())
    B=np.array([[2,1],[1,3]],float); supply=np.array([100,120],float)
    print('shadow:',shadow_prices(B,supply,[4,6]))
    rng=np.random.default_rng(4); x1=rng.normal(size=100); x2=rng.normal(size=100); yy=x1+x2+2*x1*x2+rng.normal(scale=.4,size=100)
    print('synergy screen:',interaction_uplift(x1,x2,yy))

def main():
    ap=argparse.ArgumentParser(prog='powlab')
    sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('sources'); p.add_argument('--priority'); p.add_argument('--family')
    p=sp.add_parser('probe'); p.add_argument('source_id'); p.add_argument('--param',action='append',default=[])
    p=sp.add_parser('scenario'); p.add_argument('path')
    sp.add_parser('demo')
    a=ap.parse_args()
    if a.cmd=='sources':
        for s in filter_sources(a.priority,a.family): print(f"{s['priority']:2} {s['family']:20} {s['id']:24} {s['name']}")
    elif a.cmd=='probe':
        params=dict(x.split('=',1) for x in a.param)
        print(json.dumps(probe(a.source_id,params),indent=2,default=str))
    elif a.cmd=='scenario': print(json.dumps(run_file(a.path),indent=2))
    elif a.cmd=='demo': demo()

if __name__=='__main__': main()
