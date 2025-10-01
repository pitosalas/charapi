import sys
import os
import tempfile
import yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from charapi.clients.propublica_client import ProPublicaClient


def create_test_config(mock_mode, cache_enabled):
    """Helper to create temporary config file"""
    config = {
        "mock_mode": mock_mode,
        "propublica": {
            "base_url": "https://projects.propublica.org/nonprofits/api/v2",
            "timeout": 10,
            "mock_mode": False
        },
        "caching": {
            "enabled": cache_enabled,
            "database_path": "cache/test_cache.db",
            "default_ttl_hours": 24,
            "propublica_ttl_hours": 24,
            "cleanup_on_startup": False
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
        client = ProPublicaClient(config_path)
        assert client.mock_mode == True
        assert client.cache_enabled == False
    finally:
        os.unlink(config_path)


def test_real_mode_with_cache():
    """Test client initializes in real mode with caching"""
    config_path = create_test_config(mock_mode=False, cache_enabled=True)
    try:
        client = ProPublicaClient(config_path)
        assert client.mock_mode == False
        assert client.cache_enabled == True
    finally:
        os.unlink(config_path)


def test_get_organization_mock_red_cross():
    """Test getting Red Cross data in mock mode"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = ProPublicaClient(config_path)
        result = client.get_organization("530196605")

        assert result["ein"] == "530196605"
        assert "AMERICAN NATIONAL RED CROSS" in result["name"]
        assert "filings" in result
        assert len(result["filings"]) > 0
    finally:
        os.unlink(config_path)


def test_get_organization_mock_unknown_ein():
    """Test getting unknown EIN returns fallback data"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = ProPublicaClient(config_path)
        result = client.get_organization("999999999")

        assert result["ein"] == "999999999"
        assert "Mock Organization" in result["name"]
    finally:
        os.unlink(config_path)


def test_get_all_filings_mock():
    """Test getting filings for Red Cross in mock mode"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = ProPublicaClient(config_path)
        filings = client.get_all_filings("530196605")

        assert len(filings) > 0
        assert filings[0].get("tax_prd_yr") is not None
        assert filings[0].get("totrevenue") is not None
    finally:
        os.unlink(config_path)


def test_search_organizations_mock():
    """Test searching for organizations in mock mode"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = ProPublicaClient(config_path)
        results = client.search_organizations("red cross")

        assert len(results) > 0
        assert any("red cross" in org["name"].lower() for org in results)
    finally:
        os.unlink(config_path)


def test_cache_stats_disabled():
    """Test cache stats when caching is disabled"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = ProPublicaClient(config_path)
        stats = client.get_cache_stats()

        assert stats["cache_enabled"] == False
    finally:
        os.unlink(config_path)


def test_filings_data_structure():
    """Test that filings have expected financial fields"""
    config_path = create_test_config(mock_mode=True, cache_enabled=False)
    try:
        client = ProPublicaClient(config_path)
        filings = client.get_all_filings("530196605")

        first_filing = filings[0]
        assert "totrevenue" in first_filing
        assert "totfuncexpns" in first_filing
        assert "totassetsend" in first_filing
        assert "totliabend" in first_filing
    finally:
        os.unlink(config_path)


if __name__ == "__main__":
    test_mock_mode_initialization()
    test_real_mode_with_cache()
    test_get_organization_mock_red_cross()
    test_get_organization_mock_unknown_ein()
    test_get_all_filings_mock()
    test_search_organizations_mock()
    test_cache_stats_disabled()
    test_filings_data_structure()
    print("All ProPublica client tests passed!")