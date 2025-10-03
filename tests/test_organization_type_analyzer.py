import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from charapi.analyzers.organization_type_analyzer import OrganizationTypeAnalyzer


def create_test_config():
    """Helper to create test config"""
    return {
        "scoring": {
            "organization_type": {
                "non_501c3_penalty": 25,
                "public_charity_code": 15,
                "private_foundation_penalty": 15,
                "no_filing_requirement_penalty": 10,
                "established_years_threshold": 20,
                "established_bonus": 5
            }
        }
    }


def test_analyze_perfect_organization():
    """Test organization with perfect type (501c3, public charity, files, established)"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 3,
        "foundation": 15,
        "filing_req_cd": 1,
        "ruling": 199001
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == 5.0
    assert len(result.issues) == 0
    assert result.subsection == 3
    assert result.foundation_type == 15
    assert result.filing_requirement == 1
    assert result.years_operating > 30


def test_analyze_non_501c3():
    """Test organization that is not 501(c)(3)"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 4,
        "foundation": 15,
        "filing_req_cd": 1,
        "ruling": 199001
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == -20.0
    assert "Not a 501(c)(3) organization" in result.issues[0]
    assert result.subsection == 4


def test_analyze_private_foundation():
    """Test private foundation"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 3,
        "foundation": 10,
        "filing_req_cd": 1,
        "ruling": 199001
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == -10.0
    assert "Private foundation, not public charity" in result.issues[0]
    assert result.foundation_type == 10


def test_analyze_no_filing_requirement():
    """Test organization not required to file"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 3,
        "foundation": 15,
        "filing_req_cd": 2,
        "ruling": 199001
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == -5.0
    assert "Not required to file Form 990" in result.issues[0]
    assert result.filing_requirement == 2


def test_analyze_young_organization():
    """Test young organization (under 20 years)"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 3,
        "foundation": 15,
        "filing_req_cd": 1,
        "ruling": 201501
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == 0.0
    assert len(result.issues) == 0
    assert result.years_operating < 20


def test_analyze_multiple_issues():
    """Test organization with multiple issues"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 4,
        "foundation": 10,
        "filing_req_cd": 2,
        "ruling": 201501
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == -50.0
    assert len(result.issues) == 3
    assert "Not a 501(c)(3) organization" in result.issues[0]
    assert "Private foundation" in result.issues[1]
    assert "Not required to file Form 990" in result.issues[2]


def test_analyze_no_ruling():
    """Test organization with no ruling date"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 3,
        "foundation": 15,
        "filing_req_cd": 1,
        "ruling": None
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == 0.0
    assert len(result.issues) == 0
    assert result.years_operating is None


def test_analyze_no_data():
    """Test when CharityAPI data is not available"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    result = analyzer.analyze(None)

    assert result.score == 0.0
    assert "Organization type data not available" in result.issues[0]
    assert result.subsection is None
    assert result.foundation_type is None
    assert result.filing_requirement is None
    assert result.years_operating is None


def test_analyze_red_cross():
    """Test Red Cross data from mock"""
    config = create_test_config()
    analyzer = OrganizationTypeAnalyzer(config)

    charityapi_data = {
        "subsection": 3,
        "foundation": 15,
        "filing_req_cd": 1,
        "ruling": 191801
    }

    result = analyzer.analyze(charityapi_data)

    assert result.score == 5.0
    assert len(result.issues) == 0
    assert result.subsection == 3
    assert result.foundation_type == 15
    assert result.filing_requirement == 1
    assert result.years_operating > 100


if __name__ == "__main__":
    test_analyze_perfect_organization()
    test_analyze_non_501c3()
    test_analyze_private_foundation()
    test_analyze_no_filing_requirement()
    test_analyze_young_organization()
    test_analyze_multiple_issues()
    test_analyze_no_ruling()
    test_analyze_no_data()
    test_analyze_red_cross()
    print("All OrganizationTypeAnalyzer tests passed!")
