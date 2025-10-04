from datetime import datetime
from typing import Optional, Dict, Any
from ..clients.manual_data_client import ManualDataClient
from ..data.charity_evaluation_result import Ident


class DataFieldManager:
    def __init__(self, config: dict):
        self.config = config
        self.data_fields = config.get("data_fields", {})
        self.manual_client = ManualDataClient(config)
        self.charityapi_data = None

    def set_charityapi_data(self, charityapi_data: Optional[Dict[str, Any]]):
        self.charityapi_data = charityapi_data

    def get_field(self, field_name: Ident, ein: str):
        field_name_str = field_name.value
        if field_name_str not in self.data_fields:
            raise KeyError(f"Field {field_name_str} not configured in data_fields")

        field_config = self.data_fields[field_name_str]
        source = field_config.get("source")

        if source == "manual":
            return self._get_from_manual(field_config, field_name_str, ein)
        elif source == "charityapi":
            return self._get_from_charityapi(field_config, field_name_str)
        elif source == "propublicaapi":
            raise NotImplementedError(f"ProPublica API source for {field_name_str} must be handled by caller")
        else:
            raise ValueError(f"Unknown source '{source}' for field {field_name_str}")

    def _get_from_manual(self, field_config: dict, field_name_str: str, ein: str):
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

    def _get_from_charityapi(self, field_config: dict, field_name_str: str):
        if not self.charityapi_data:
            return None

        charityapi_field = field_config.get("field", field_name_str)

        if field_name_str == "in_pub78":
            return self.charityapi_data.get("deductibility") == 1
        elif field_name_str == "is_revoked":
            return self.charityapi_data.get("status") != 1
        elif field_name_str == "has_recent_filing":
            return self._check_recent_filing(self.charityapi_data)
        elif field_name_str == "ruling_year":
            ruling = self.charityapi_data.get("ruling")
            return ruling // 100 if ruling else None
        else:
            return self.charityapi_data.get(charityapi_field)

    def _check_recent_filing(self, charityapi_data: dict) -> bool:
        tax_period = charityapi_data.get("tax_period")
        if not tax_period:
            return False

        tax_period_str = str(tax_period)
        tax_year = int(tax_period_str[:4])
        current_year = datetime.now().year
        return (current_year - tax_year) <= 3
