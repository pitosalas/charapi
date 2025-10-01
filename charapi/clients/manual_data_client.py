import json
from pathlib import Path


class ManualDataClient:
    def __init__(self, config: dict):
        self.manual_dir = Path(config.get("manual_data", {}).get("directory", "manual"))
        self._cache = {}

    def get_data(self, ein: str) -> dict:
        normalized_ein = ein.replace("-", "")

        if normalized_ein in self._cache:
            return self._cache[normalized_ein]

        json_path = self.manual_dir / f"{normalized_ein}.json"

        if not json_path.exists():
            return {}

        with open(json_path, "r") as f:
            data = json.load(f)

        self._cache[normalized_ein] = data
        return data

    def get_value(self, field_name: str, ein: str):
        data = self.get_data(ein)

        if not data:
            return None

        parts = field_name.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current
