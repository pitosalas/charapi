import csv
from pathlib import Path


class ManualDataClient:
    def __init__(self, config: dict):
        self.manual_dir = Path(config.get("manual_data", {}).get("directory", "manual"))

    def get_value(self, field_name: str, ein: str) -> str:
        csv_path = self.manual_dir / f"{field_name}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(f"Manual data file not found: {csv_path}")

        rows = self._read_csv(csv_path)

        for row in rows:
            if row["ein"] == ein:
                return row["value"]

        return "manual data not available"

    def _read_csv(self, csv_path: Path) -> list:
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ["ein", "value"]:
                raise ValueError(f"Invalid CSV format in {csv_path}. Expected columns: ein,value")
            return list(reader)

    def _add_row(self, csv_path: Path, ein: str, value: str):
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([ein, value])
