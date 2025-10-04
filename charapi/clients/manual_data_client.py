import yaml
from pathlib import Path


class ManualDataClient:
    """
    READ-ONLY Manual Data Client

    WARNING: This class must NEVER write to manual_data.yaml.
    Only the user should edit manual_data.yaml directly.
    Do not add any write/save/update methods to this class.
    """
    _global_data = None

    def __init__(self, config: dict):
        manual_dir_str = config.get("manual_data", {}).get("directory", "manual")
        manual_dir_path = Path(manual_dir_str)

        if not manual_dir_path.is_absolute() and "_config_file_path" in config:
            config_file_path = Path(config["_config_file_path"]).resolve()
            project_root = self._find_project_root(config_file_path)
            self.manual_dir = project_root / manual_dir_path
        else:
            self.manual_dir = manual_dir_path

        self.filename = config.get("manual_data", {}).get("filename", "manual_data.yaml")

        if ManualDataClient._global_data is None:
            self._load_data()

    def _find_project_root(self, start_path: Path) -> Path:
        current = start_path.parent
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        return start_path.parent

    def _load_data(self):
        yaml_path = self.manual_dir / self.filename

        if not yaml_path.exists():
            ManualDataClient._global_data = {}
            return

        with open(yaml_path, "r") as f:
            raw_data = yaml.safe_load(f) or {}

        normalized_data = {}
        for key, value in raw_data.items():
            if key.startswith("ein_"):
                ein_part = key[4:]
                normalized_ein = ein_part.replace("-", "").replace("_", "")
                normalized_key = f"ein_{normalized_ein}"
                normalized_data[normalized_key] = value
            else:
                normalized_data[key] = value

        ManualDataClient._global_data = normalized_data

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
