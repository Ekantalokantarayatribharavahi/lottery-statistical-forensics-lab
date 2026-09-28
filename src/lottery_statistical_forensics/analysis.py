from __future__ import annotations
import hashlib
from collections import Counter
from itertools import combinations
import numpy as np
import pandas as pd
from scipy.stats import chisquare, chi2_contingency
from statsmodels.stats.multitest import multipletests
from .model import NullModel
from .simulation import simulate_draws, draw_sums, parity_counts, consecutive_counts

def load_draws(path: str, game: str) -> tuple[pd.DataFrame, np.ndarray]:
    df = pd.read_csv(path)
    required = {"draw_date","draw_id","main_numbers"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if "game" in df.columns:
        df = df[df["game"].eq(game)].copy()
    if df.empty:
        raise ValueError(f"No draws found for game={game!r}")
    draws = np.array(
        [[int(x) for x in str(v).split(",") if x.strip()] for v in df["main_numbers"]],
        dtype=int,
    )
    if len({len(x) for x in draws}) != 1:
        raise ValueError("All draws must have equal width")
    return df, draws

def dataset_hash(df: pd.DataFrame) -> str:
    raw = df.sort_values(["draw_date","draw_id"]).to_csv(index=False,lineterminator="\n")
    return hashlib.sha256(raw.encode()).hexdigest()

def marginal_test(draws: np.ndarray, model: NullModel) -> dict:
    observed = np.bincount(draws.ravel()-model.main_min,minlength=model.population_size)
    expected = np.full(model.population_size,len(draws)*model.main_count/model.population_size,dtype=float)
    _, p = chisquare(observed, expected)
    standardized = ((observed-expected)/np.sqrt(expected)).tolist()
    return {"observed_count":observed.tolist(),"expected_count":expected.tolist(),"standardized_deviation":standardized,"p_value":float(p)}

def pair_test(draws: np.ndarray, model: NullModel) -> dict:
    counts = Counter()
    for d in draws:
        counts.update(combinations(sorted(map(int,d)),2))
    pairs = list(combinations(range(model.main_min,model.main_max+1),2))
    total = len(draws) * (model.main_count*(model.main_count-1)//2)
    expected = total/len(pairs)
    observed = np.array([counts[p] for p in pairs],dtype=float)
    _, p = chisquare(observed,np.full_like(observed,expected))
    return {"pair_count":len(pairs),"expected_per_pair":expected,"p_value":float(p)}

def mc_tail(observed: float, simulated: np.ndarray) -> float:
    center = float(simulated.mean())
    distance = abs(observed-center)
    return float((np.count_nonzero(np.abs(simulated-center)>=distance)+1)/(len(simulated)+1))

def structure_tests(draws: np.ndarray, model: NullModel, runs: int, seed: int) -> list[dict]:
    sim = simulate_draws(model,runs,seed)
    block = len(draws)
    if runs < block:
        return [{"name":n,"test":"Monte Carlo null comparison","p_value":None,"status":"insufficient_simulations"} for n in ["draw_sum","parity","consecutive_numbers"]]
    refs = lambda fn: np.array([fn(sim[i:i+block]).mean() for i in range(0,runs-block+1,block)])
    return [
        {"name":"draw_sum","test":"Monte Carlo mean-sum comparison","p_value":mc_tail(draw_sums(draws).mean(),refs(draw_sums))},
        {"name":"parity","test":"Monte Carlo mean odd-count comparison","p_value":mc_tail(parity_counts(draws).mean(),refs(parity_counts))},
        {"name":"consecutive_numbers","test":"Monte Carlo mean consecutive-pair comparison","p_value":mc_tail(consecutive_counts(draws).mean(),refs(consecutive_counts))},
    ]

def temporal_test(draws: np.ndarray) -> dict:
    if len(draws) < 3:
        return {"name":"temporal_dependence","test":"lag-1 parity contingency","p_value":None,"status":"insufficient_sample"}
    labels = np.array([(d%2).mean() >= 0.5 for d in draws],dtype=int)
    table = np.zeros((2,2),dtype=int)
    for a,b in zip(labels[:-1],labels[1:]):
        table[a,b]+=1
    _,p,_,_ = chi2_contingency(table)
    return {"name":"temporal_dependence","test":"lag-1 parity contingency","p_value":float(p),"contingency_table":table.tolist()}

def classify(items: list[dict], alpha: float = 0.05) -> list[dict]:
    values = [i["p_value"] if i["p_value"] is not None else 1.0 for i in items]
    adjusted = multipletests(values,alpha=alpha,method="fdr_bh")[1]
    for item,p in zip(items,adjusted):
        item["adjusted_p_value"]=float(p)
        item["evidence_state"]="SUPPORTED" if p < alpha else "NOT_SUPPORTED"
    return items

def split(draws: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
    if len(draws)<2:
        return draws,np.empty((0,draws.shape[1]),dtype=int)
    n=max(1,int(len(draws)*.7)); n=min(n,len(draws)-1)
    return draws[:n],draws[n:]
