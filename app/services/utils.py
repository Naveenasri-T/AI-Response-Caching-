import json, hashlib

def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',',':'))

def make_cache_key(task_type: str, model_name: str, input_obj) -> str:
    canon = canonical_json(input_obj)
    digest = hashlib.sha256(canon.encode('utf-8')).hexdigest()
    return f"{task_type}:{model_name}:{digest}"
