from ..clients.manual_data_client import ManualDataClient


class DataFieldManager:
    def __init__(self, config: dict):
        self.config = config
        self.data_fields = config.get("data_fields", {})
        self.manual_client = ManualDataClient(config)

    def get_field(self, field_name: str, ein: str):
        if field_name not in self.data_fields:
            raise KeyError(f"Field {field_name} not configured in data_fields")

        source = self.data_fields[field_name].get("source")

        if source == "manual":
            return self.manual_client.get_value(field_name, ein)
        elif source == "api":
            raise NotImplementedError(f"API source for {field_name} must be handled by caller")
        else:
            raise ValueError(f"Unknown source '{source}' for field {field_name}")
