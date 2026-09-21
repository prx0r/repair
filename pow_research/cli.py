from __future__ import annotations
import argparse, json
from .registry import sources, coverage

def cmd_sources(args):
    rows=sources(priority=args.priority,family=args.family)
    for r in rows: print(f"{r['priority']:>2}  {r['source_id']:<30} {r['family']:<22} {r['cadence']:<16} {r['recoverability']}")
    print(f"\n{len(rows)} sources")

def cmd_coverage(args):
    for r in coverage(): print(f"{r['model']:<22} {r['source_count']:>2} sources  {', '.join(r['sources'][:8])}{'…' if len(r['sources'])>8 else ''}")

def cmd_demo(args):
    from .models.network import leontief_cost_propagation
    from .models.shadow import solve_shadow_prices
    from .models.synergy import synergy_screen
    import numpy as np
    A=np.array([[0,0.2,0.1],[0,0,0.25],[0,0,0]])
    print('NETWORK',json.dumps(leontief_cost_propagation(A,[-0.5,0,0],['GPU','robot','service']),indent=2))
    B=np.array([[2,1],[1,3],[0.2,0.2]])
    print('SHADOW',json.dumps(solve_shadow_prices(B,[100,80,20],[10,16],input_labels=['sensor','motor','power'],product_labels=['robotA','robotB']),indent=2))
    rng=np.random.default_rng(3); x1=rng.normal(size=600); x2=rng.normal(size=600); y=((x1>0)&(x2>0)).astype(int)
    print('SYNERGY',json.dumps(synergy_screen(x1,x2,y),indent=2))


def cmd_scenario(args):
    from .scenario import run_scenario_file
    print(json.dumps(run_scenario_file(args.path),indent=2))

def main():
    ap=argparse.ArgumentParser(prog='pow-research'); sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('sources'); p.add_argument('--priority'); p.add_argument('--family'); p.set_defaults(fn=cmd_sources)
    p=sub.add_parser('coverage'); p.set_defaults(fn=cmd_coverage)
    p=sub.add_parser('demo'); p.set_defaults(fn=cmd_demo)
    p=sub.add_parser('scenario'); p.add_argument('path'); p.set_defaults(fn=cmd_scenario)
    a=ap.parse_args(); a.fn(a)
if __name__=='__main__': main()
