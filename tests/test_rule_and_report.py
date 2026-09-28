from pathlib import Path
import json
from lottery_statistical_forensics.report import write_reports
from lottery_statistical_forensics.rules import resolve_rule, rule_hash

def test_all_declared_games_have_rule_hash():
    for game in ["lotto","powerball","daily_lotto"]:
        version, model = resolve_rule(game)
        assert len(rule_hash(version, model)) == 64

def test_reports_have_required_outputs(tmp_path: Path):
    report = {"game":"lotto","dataset_hash":"a"*64,"rule_version_hash":"b"*64,"seed":42,"sample_size":10,"multiple_testing_method":"fdr_bh","findings":[]}
    jp, mp = write_reports(report, tmp_path)
    assert jp.exists() and mp.exists()
    assert json.loads(jp.read_text())["seed"] == 42
