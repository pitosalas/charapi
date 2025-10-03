import requests
from datetime import datetime
from typing import Optional, Dict, Any
from .base_client import BaseAPIClient


class CharityAPIClient(BaseAPIClient):
    def __init__(self, config_path: str):
        super().__init__(config_path, "charityapi")
        self.base_url = self.service_config["base_url"]
        self.api_key = self.service_config["api_key"]
        self.timeout = self.service_config.get("timeout", 30)

    def get_organization(self, ein: str):
        return self.get_cached_or_fetch(
            endpoint="organizations",
            identifier=ein,
            fetch_function=lambda: self._fetch_organization(ein),
            mock_function=lambda: self._get_mock_data(ein)
        )

    def _fetch_organization(self, ein: str):
        url = f"{self.base_url}/organizations/{ein}"
        headers = {"apikey": self.api_key}

        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()

        json_response = response.json()
        return json_response.get("data")

    def _get_mock_data(self, ein: str):
        mock_data = {
            "530196605": {
                "name": "AMERICAN NATIONAL RED CROSS",
                "status": 1,
                "state": "DC",
                "zip": "20006",
                "group": 0,
                "organization": 1,
                "ein": "530196605",
                "deductibility": 1,
                "acct_pd": 6,
                "activity": 540000000,
                "affiliation": 3,
                "asset_amt": 3019994931,
                "asset_cd": 9,
                "city": "WASHINGTON",
                "classification": 1000,
                "filing_req_cd": 1,
                "foundation": 15,
                "ico": "GAIL MCGOVERN",
                "income_amt": 3217077611,
                "income_cd": 9,
                "ntee_cd": "P12",
                "pf_filing_req_cd": 0,
                "revenue_amt": 3217077611,
                "ruling": 191801,
                "sort_name": None,
                "street": "2025 E STREET NW",
                "subsection": 3,
                "tax_period": 202306
            },
            "131624147": {
                "name": "SALVATION ARMY NATIONAL CORPORATION",
                "status": 1,
                "state": "NY",
                "zip": "10038",
                "group": 0,
                "organization": 1,
                "ein": "131624147",
                "deductibility": 1,
                "acct_pd": 9,
                "activity": 540000000,
                "affiliation": 3,
                "asset_amt": 2500000000,
                "asset_cd": 9,
                "city": "NEW YORK",
                "classification": 1000,
                "filing_req_cd": 1,
                "foundation": 15,
                "ico": "COMMISSIONER DAVID HUDSON",
                "income_amt": 2000000000,
                "income_cd": 9,
                "ntee_cd": "P20",
                "pf_filing_req_cd": 0,
                "revenue_amt": 2000000000,
                "ruling": 195001,
                "sort_name": None,
                "street": "440 WEST NYACK RD",
                "subsection": 3,
                "tax_period": 202309
            }
        }
        return mock_data.get(ein)

    def get_deductibility_status(self, ein: str):
        org = self.get_organization(ein)
        if not org:
            return False
        return org.get("deductibility") == 1

    def get_revocation_status(self, ein: str):
        org = self.get_organization(ein)
        if not org:
            return True
        return org.get("status") != 1

    def get_recent_filing_status(self, ein: str):
        org = self.get_organization(ein)
        if not org or not org.get("tax_period"):
            return False

        tax_period = str(org["tax_period"])
        tax_year = int(tax_period[:4])
        current_year = datetime.now().year
        return (current_year - tax_year) <= 3

    def get_ntee_code(self, ein: str):
        org = self.get_organization(ein)
        if not org:
            return None
        return org.get("ntee_cd")

    def get_subsection(self, ein: str):
        org = self.get_organization(ein)
        if not org:
            return None
        return org.get("subsection")

    def get_foundation_type(self, ein: str):
        org = self.get_organization(ein)
        if not org:
            return None
        return org.get("foundation")

    def get_filing_requirement(self, ein: str):
        org = self.get_organization(ein)
        if not org:
            return None
        return org.get("filing_req_cd")

    def get_ruling_year(self, ein: str):
        org = self.get_organization(ein)
        if not org or not org.get("ruling"):
            return None
        return org["ruling"] // 100

    def get_years_operating(self, ein: str):
        ruling_year = self.get_ruling_year(ein)
        if not ruling_year:
            return None
        return datetime.now().year - ruling_year
