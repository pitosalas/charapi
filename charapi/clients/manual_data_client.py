import yaml
from pathlib import Path


class ManualDataClient:
    _global_data = None

    def __init__(self, config: dict):
        self.manual_dir = Path(config.get("manual_data", {}).get("directory", "manual"))
        self.filename = config.get("manual_data", {}).get("filename", "manual_data.yaml")

        if ManualDataClient._global_data is None:
            self._load_data()

    def _load_data(self):
        yaml_path = self.manual_dir / self.filename

        if not yaml_path.exists():
            ManualDataClient._global_data = {}
            return

        with open(yaml_path, "r") as f:
            ManualDataClient._global_data = yaml.safe_load(f) or {}

    def get_data(self, ein: str) -> dict:
        normalized_ein = ein.replace("-", "")
        ein_key = f"ein_{normalized_ein}"

        return ManualDataClient._global_data.get(ein_key, {})

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
