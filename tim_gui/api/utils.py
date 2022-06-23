from typing import Any

def replace_params(
    path: str,
    path_params: dict[str, Any],
) -> tuple[str, dict]:
    for key, value in list(path_params.items()):
        if "{" + key + "}" in path:
            path = path.replace("{" + key + "}", str(value))
            path_params.pop(key)
    return path, path_params
