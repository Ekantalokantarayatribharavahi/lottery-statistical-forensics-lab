import json
from pathlib import Path

def write_reports(report: dict, out: Path) -> tuple[Path,Path]:
    out.mkdir(parents=True,exist_ok=True)
    jp=out/"analysis_report.json"; mp=out/"analysis_report.md"
    jp.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lines=["# Statistical Forensics Report","",f"Game: `{report['game']}`",f"Dataset hash: `{report['dataset_hash']}`",f"Rule-version hash: `{report['rule_version_hash']}`",f"Seed: `{report['seed']}`",f"Sample size: `{report['sample_size']}`","", "| Finding | Adjusted p-value | State |","|---|---:|---|"]
    for f in report["findings"]:
        lines.append(f"| {f['name']} | {f.get('adjusted_p_value','n/a')} | {f.get('evidence_state','INCONCLUSIVE')} |")
    mp.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return jp,mp
