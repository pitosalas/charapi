import sys
import os
import tempfile
import yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from charapi.analyzers.compliance_checker import ComplianceChecker


def create_test_config():
    """Helper to create temporary config file with CharityAPI data source"""
    config = {
        "mock_mode": True,
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
            }
        },
        "manual_data": {
            "directory": "manual",
            "filename": "brief_manual.yaml"
        }
    }

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_file)
    temp_file.close()
    return temp_file.name, config


def test_compliance_checker_all_compliant():
    """Test compliance checker with fully compliant organization"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        charityapi_data = {
            "ein": "530196605",
            "deductibility": 1,
            "status": 1,
            "tax_period": 202306
        }

        checker.data_manager.set_charityapi_data(charityapi_data)

        result = checker.check_compliance("530196605")

        assert result.is_compliant == True
        assert len(result.issues) == 0
        assert result.in_pub78 == True
        assert result.is_revoked == False
        assert result.has_recent_filing == True
    finally:
        os.unlink(config_path)


def test_compliance_checker_not_in_pub78():
    """Test compliance checker with organization not in Publication 78"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        charityapi_data = {
            "ein": "999999999",
            "deductibility": 0,
            "status": 1,
            "tax_period": 202306
        }

        checker.data_manager.set_charityapi_data(charityapi_data)

        result = checker.check_compliance("999999999")

        assert result.is_compliant == False
        assert "Not in IRS Publication 78" in result.issues
        assert result.in_pub78 == False
        assert result.is_revoked == False
        assert result.has_recent_filing == True
    finally:
        os.unlink(config_path)


def test_compliance_checker_revoked():
    """Test compliance checker with revoked organization"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        charityapi_data = {
            "ein": "999999999",
            "deductibility": 1,
            "status": 0,
            "tax_period": 202306
        }

        checker.data_manager.set_charityapi_data(charityapi_data)

        result = checker.check_compliance("999999999")

        assert result.is_compliant == False
        assert "Tax-exempt status revoked" in result.issues
        assert result.in_pub78 == True
        assert result.is_revoked == True
        assert result.has_recent_filing == True
    finally:
        os.unlink(config_path)


def test_compliance_checker_no_recent_filing():
    """Test compliance checker with organization with no recent filing"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        charityapi_data = {
            "ein": "999999999",
            "deductibility": 1,
            "status": 1,
            "tax_period": 201906
        }

        checker.data_manager.set_charityapi_data(charityapi_data)

        result = checker.check_compliance("999999999")

        assert result.is_compliant == False
        assert "No recent Form 990 filing" in result.issues
        assert result.in_pub78 == True
        assert result.is_revoked == False
        assert result.has_recent_filing == False
    finally:
        os.unlink(config_path)


def test_compliance_checker_multiple_issues():
    """Test compliance checker with multiple compliance issues"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        charityapi_data = {
            "ein": "999999999",
            "deductibility": 0,
            "status": 0,
            "tax_period": 201906
        }

        checker.data_manager.set_charityapi_data(charityapi_data)

        result = checker.check_compliance("999999999")

        assert result.is_compliant == False
        assert len(result.issues) == 3
        assert "Not in IRS Publication 78" in result.issues
        assert "Tax-exempt status revoked" in result.issues
        assert "No recent Form 990 filing" in result.issues
        assert result.in_pub78 == False
        assert result.is_revoked == True
        assert result.has_recent_filing == False
    finally:
        os.unlink(config_path)


def test_compliance_checker_missing_tax_period():
    """Test compliance checker with missing tax period"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        charityapi_data = {
            "ein": "999999999",
            "deductibility": 1,
            "status": 1,
            "tax_period": None
        }

        checker.data_manager.set_charityapi_data(charityapi_data)

        result = checker.check_compliance("999999999")

        assert result.is_compliant == False
        assert "No recent Form 990 filing" in result.issues
        assert result.has_recent_filing == False
    finally:
        os.unlink(config_path)


def test_compliance_checker_no_charityapi_data():
    """Test compliance checker when CharityAPI data is not available"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        result = checker.check_compliance("999999999")

        assert result.is_compliant == False
        assert len(result.issues) == 2
        assert "Not in IRS Publication 78" in result.issues
        assert "No recent Form 990 filing" in result.issues
        assert result.in_pub78 == False
        assert result.is_revoked == False
        assert result.has_recent_filing == False
    finally:
        os.unlink(config_path)


def test_compliance_checker_red_cross():
    """Test compliance checker with real Red Cross data from mock"""
    config_path, config = create_test_config()

    try:
        checker = ComplianceChecker(config)

        charityapi_data = {
            "name": "AMERICAN NATIONAL RED CROSS",
            "status": 1,
            "ein": "530196605",
            "deductibility": 1,
            "foundation": 15,
            "subsection": 3,
            "tax_period": 202306
        }

        checker.data_manager.set_charityapi_data(charityapi_data)

        result = checker.check_compliance("530196605")

        assert result.is_compliant == True
        assert len(result.issues) == 0
        assert result.in_pub78 == True
        assert result.is_revoked == False
        assert result.has_recent_filing == True
    finally:
        os.unlink(config_path)


if __name__ == "__main__":
    test_compliance_checker_all_compliant()
    test_compliance_checker_not_in_pub78()
    test_compliance_checker_revoked()
    test_compliance_checker_no_recent_filing()
    test_compliance_checker_multiple_issues()
    test_compliance_checker_missing_tax_period()
    test_compliance_checker_no_charityapi_data()
    test_compliance_checker_red_cross()
    print("All compliance checker tests passed!")
