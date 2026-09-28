import hashlib
import json
from .model import NullModel

RULES = {
    "lotto-current": NullModel("lotto",6,1,52),
    "powerball-current": NullModel("powerball",5,1,50),
    "daily_lotto-current": NullModel("daily_lotto",5,1,36),
}

def resolve_rule(game: str, rule_version: str | None = None) -> tuple[str, NullModel]:
    key = rule_version or f"{game}-current"
    if key not in RULES:
        raise ValueError(f"Unknown rule version: {key}")
    return key, RULES[key]

def rule_hash(version: str, model: NullModel) -> str:
    payload = {"version":version,"model":model.__dict__}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
