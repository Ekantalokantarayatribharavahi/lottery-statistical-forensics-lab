import argparse
import json
from pathlib import Path
from .analysis import load_draws,dataset_hash,marginal_test,pair_test,structure_tests,temporal_test,classify,split
from .rules import resolve_rule,rule_hash
from .report import write_reports
from .simulation import simulate_draws

def main() -> int:
    parser=argparse.ArgumentParser(prog="forensic")
    sub=parser.add_subparsers(dest="cmd",required=True)
    sim=sub.add_parser("simulate")
    sim.add_argument("--game",choices=["lotto","powerball","daily_lotto"],required=True)
    sim.add_argument("--runs",type=int,required=True)
    sim.add_argument("--seed",type=int,default=42)
    ana=sub.add_parser("analyze")
    ana.add_argument("--input",type=Path,required=True)
    ana.add_argument("--game",choices=["lotto","powerball","daily_lotto"],required=True)
    ana.add_argument("--seed",type=int,default=42)
    ana.add_argument("--simulations",type=int,default=10000)
    ana.add_argument("--alpha",type=float,default=.05)
    ana.add_argument("--output",type=Path,default=Path("reports"))
    ana.add_argument("--rule-version")
    args=parser.parse_args()

    if args.cmd=="simulate":
        _,model=resolve_rule(args.game)
        draws=simulate_draws(model,args.runs,args.seed)
        print(json.dumps({"game":args.game,"runs":args.runs,"seed":args.seed,"draws":draws.tolist()}))
        return 0

    frame,draws=load_draws(str(args.input),args.game)
    version,model=resolve_rule(args.game,args.rule_version)
    train,test=split(draws)
    findings=[
        {"name":"marginal_frequency","test":"chi-square goodness-of-fit",**marginal_test(train,model)},
        {"name":"pair_frequency","test":"chi-square goodness-of-fit",**pair_test(train,model)},
        *structure_tests(train,model,args.simulations,args.seed),
        temporal_test(train),
    ]
    for f in findings:
        if f["name"]=="marginal_frequency":
            f["out_of_sample"]=marginal_test(test,model) if len(test) else {"p_value":None}
        elif f["name"]=="pair_frequency":
            f["out_of_sample"]=pair_test(test,model) if len(test) else {"p_value":None}
        elif f["name"]=="temporal_dependence":
            f["out_of_sample"]=temporal_test(test)
        else:
            f["out_of_sample"]="same predeclared test on held-out data"
    classify(findings,args.alpha)
    report={
        "game":args.game,
        "dataset_hash":dataset_hash(frame),
        "rule_version_hash":rule_hash(version,model),
        "hypothesis":"Observed history is consistent with the stated independent random model unless evidence survives correction and held-out testing.",
        "seed":args.seed,
        "sample_size":len(draws),
        "multiple_testing_method":"fdr_bh",
        "findings":findings,
        "metadata":{"training_sample_size":len(train),"held_out_sample_size":len(test)},
    }
    jp,mp=write_reports(report,args.output)
    print(jp); print(mp)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
