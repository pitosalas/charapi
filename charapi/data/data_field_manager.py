from ..clients.manual_data_client import ManualDataClient
from ..data.charity_evaluation_result import Ident


class DataFieldManager:
    def __init__(self, config: dict):
        self.config = config
        self.data_fields = config.get("data_fields", {})
        self.manual_client = ManualDataClient(config)

    def get_field(self, field_name: Ident, ein: str):
        field_name_str = field_name.value
        if field_name_str not in self.data_fields:
            raise KeyError(f"Field {field_name_str} not configured in data_fields")

        field_config = self.data_fields[field_name_str]
        source = field_config.get("source")

        if source == "manual":
            json_path = field_config.get("path", field_name_str)

            if "fiscal_year_2024" in json_path:
                for year in ["2024", "2023", "2022"]:
                    year_path = json_path.replace("fiscal_year_2024", f"fiscal_year_{year}")
                    value = self.manual_client.get_value(year_path, ein)
                    if value is not None and value != 0:
                        return value
                return None
            else:
                return self.manual_client.get_value(json_path, ein)
        elif source == "api":
            raise NotImplementedError(f"API source for {field_name_str} must be handled by caller")
        else:
            raise ValueError(f"Unknown source '{source}' for field {field_name_str}")
