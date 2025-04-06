import os
from typing import Any, Union

def get_env(key: str, default: Any) -> Any:
    """Get an environment variable with a default value"""
    return os.environ.get(key, default)

def get_float_env(key: str, default: Union[int, float]) -> float:
    """Get a float environment variable with a default value"""
    try:
        return float(os.environ.get(key, default))
    except (TypeError, ValueError):
        return float(default) 