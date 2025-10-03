import sys
import os
import tempfile
import yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from charapi.clients.charityapi_client import CharityAPIClient
from charapi.data.data_field_manager import DataFieldManager
from charapi.data.charity_evaluation_result import Ident


def create_test_config(mock_mode, cache_enabled):
    """Helper to create temporary config file"""
    config = {
        "mock_mode": mock_mode,
        "charityapi": {
            "base_url": "https://api.charityapi.org/api",
            "api_key": "test_key",
            "timeout": 30,
            "mock_mode": False
        },
        "caching": {
            "enabled": cache_enabled,
            "database_path": "cache/test_cache.db",
            "default_ttl_hours": 24,
            "charityapi_ttl_hours": 168,
            "cleanup_on_startup": False
        },
        "data_fields": {
            "in_pub78": {
                "source": "charityapi",
                "field": "deductibility"
            },
            "is_revoked": {
                "source": "charityapi",
                "field": "status"
            },
            "has_recent_filing": {
                "source": "charityapi",
                "field": "tax_period"
            },
            "ntee_code": {
                "source": "charityapi",
                "field": "ntee_cd"
            },
            "subsection": {
                "source": "charityapi",
                "field": "subsection"
            },
            "foundation_type": {
                "source": "charityapi",
                "field": "foundation"
            },
            "filing_requirement": {
                "source": "charityapi",
                "field": "filing_req_cd"
            },
            "ruling_year": {
                "source": "charityapi",
                "field": "ruling"
            }
        }
    }

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file)
    temp_file.close()
    return temp_file.name


def test_mock_mode_initialization():
    """Test client initializes in mock mode correctly"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        assert client.mock_mode == True
        assert client.cache_enabled == False
    finally:
        os.unlink(config_path)


def test_real_mode_with_cache():
    """Test client initializes in real mode with caching"""
    config_path = create_test_config(mock_mode=False, cache_enabled=True)
    try:
        client = CharityAPIClient(config_path)
        assert client.mock_mode == False
        assert client.cache_enabled == True
    finally:
        os.unlink(config_path)


def test_get_organization_mock_red_cross():
    """Test getting Red Cross data in mock mode"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_organization("530196605")

        assert result is not None
        assert result["ein"] == "530196605"
        assert "AMERICAN NATIONAL RED CROSS" in result["name"]
        assert result["status"] == 1
        assert result["deductibility"] == 1
        assert result["subsection"] == 3
        assert result["foundation"] == 15
        assert result["ntee_cd"] == "P12"
        assert result["filing_req_cd"] == 1
    finally:
        os.unlink(config_path)


def test_get_organization_mock_salvation_army():
    """Test getting Salvation Army data in mock mode"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_organization("131624147")

        assert result is not None
        assert result["ein"] == "131624147"
        assert "SALVATION ARMY" in result["name"]
        assert result["ntee_cd"] == "P20"
    finally:
        os.unlink(config_path)


def test_get_organization_unknown_ein():
    """Test getting unknown EIN returns None"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_organization("999999999")

        assert result is None
    finally:
        os.unlink(config_path)


def test_get_deductibility_status_eligible():
    """Test deductibility status for eligible organization"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_deductibility_status("530196605")

        assert result == True
    finally:
        os.unlink(config_path)


def test_get_deductibility_status_unknown_ein():
    """Test deductibility status for unknown EIN returns False"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_deductibility_status("999999999")

        assert result == False
    finally:
        os.unlink(config_path)


def test_get_revocation_status_active():
    """Test revocation status for active organization"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_revocation_status("530196605")

        assert result == False
    finally:
        os.unlink(config_path)


def test_get_revocation_status_unknown_ein():
    """Test revocation status for unknown EIN returns True"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_revocation_status("999999999")

        assert result == True
    finally:
        os.unlink(config_path)


def test_get_recent_filing_status_recent():
    """Test recent filing status for organization with recent filing"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_recent_filing_status("530196605")

        assert result == True
    finally:
        os.unlink(config_path)


def test_get_recent_filing_status_unknown_ein():
    """Test recent filing status for unknown EIN returns False"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_recent_filing_status("999999999")

        assert result == False
    finally:
        os.unlink(config_path)


def test_get_ntee_code():
    """Test getting NTEE code"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_ntee_code("530196605")

        assert result == "P12"
    finally:
        os.unlink(config_path)


def test_get_ntee_code_unknown_ein():
    """Test getting NTEE code for unknown EIN returns None"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_ntee_code("999999999")

        assert result is None
    finally:
        os.unlink(config_path)


def test_get_subsection():
    """Test getting subsection"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_subsection("530196605")

        assert result == 3
    finally:
        os.unlink(config_path)


def test_get_foundation_type():
    """Test getting foundation type"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_foundation_type("530196605")

        assert result == 15
    finally:
        os.unlink(config_path)


def test_get_filing_requirement():
    """Test getting filing requirement"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_filing_requirement("530196605")

        assert result == 1
    finally:
        os.unlink(config_path)


def test_get_ruling_year():
    """Test getting ruling year"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_ruling_year("530196605")

        assert result == 1918
    finally:
        os.unlink(config_path)


def test_get_years_operating():
    """Test calculating years operating"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        result = client.get_years_operating("530196605")

        assert result is not None
        assert result > 100
    finally:
        os.unlink(config_path)


def test_data_field_manager_in_pub78():
    """Test DataFieldManager retrieves in_pub78 from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.IN_PUB78, "530196605")
        assert result == True
    finally:
        os.unlink(config_path)


def test_data_field_manager_is_revoked():
    """Test DataFieldManager retrieves is_revoked from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.IS_REVOKED, "530196605")
        assert result == False
    finally:
        os.unlink(config_path)


def test_data_field_manager_has_recent_filing():
    """Test DataFieldManager retrieves has_recent_filing from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.HAS_RECENT_FILING, "530196605")
        assert result == True
    finally:
        os.unlink(config_path)


def test_data_field_manager_ntee_code():
    """Test DataFieldManager retrieves ntee_code from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.NTEE_CODE, "530196605")
        assert result == "P12"
    finally:
        os.unlink(config_path)


def test_data_field_manager_subsection():
    """Test DataFieldManager retrieves subsection from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.SUBSECTION, "530196605")
        assert result == 3
    finally:
        os.unlink(config_path)


def test_data_field_manager_foundation_type():
    """Test DataFieldManager retrieves foundation_type from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.FOUNDATION_TYPE, "530196605")
        assert result == 15
    finally:
        os.unlink(config_path)


def test_data_field_manager_filing_requirement():
    """Test DataFieldManager retrieves filing_requirement from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.FILING_REQUIREMENT, "530196605")
        assert result == 1
    finally:
        os.unlink(config_path)


def test_data_field_manager_ruling_year():
    """Test DataFieldManager retrieves ruling_year from charityapi source"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        client = CharityAPIClient(config_path)
        manager = DataFieldManager(config)

        charityapi_data = client.get_organization("530196605")
        manager.set_charityapi_data(charityapi_data)

        result = manager.get_field(Ident.RULING_YEAR, "530196605")
        assert result == 1918
    finally:
        os.unlink(config_path)


def test_cache_stats_disabled():
    """Test cache stats when caching is disabled"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = CharityAPIClient(config_path)
        stats = client.get_cache_stats()

        assert stats["cache_enabled"] == False
    finally:
        os.unlink(config_path)


if __name__ == "__main__":
    test_mock_mode_initialization()
    test_real_mode_with_cache()
    test_get_organization_mock_red_cross()
    test_get_organization_mock_salvation_army()
    test_get_organization_unknown_ein()
    test_get_deductibility_status_eligible()
    test_get_deductibility_status_unknown_ein()
    test_get_revocation_status_active()
    test_get_revocation_status_unknown_ein()
    test_get_recent_filing_status_recent()
    test_get_recent_filing_status_unknown_ein()
    test_get_ntee_code()
    test_get_ntee_code_unknown_ein()
    test_get_subsection()
    test_get_foundation_type()
    test_get_filing_requirement()
    test_get_ruling_year()
    test_get_years_operating()
    test_data_field_manager_in_pub78()
    test_data_field_manager_is_revoked()
    test_data_field_manager_has_recent_filing()
    test_data_field_manager_ntee_code()
    test_data_field_manager_subsection()
    test_data_field_manager_foundation_type()
    test_data_field_manager_filing_requirement()
    test_data_field_manager_ruling_year()
    test_cache_stats_disabled()
    print("All CharityAPI client tests passed!")
