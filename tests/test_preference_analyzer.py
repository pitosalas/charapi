import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from charapi.analyzers.preference_analyzer import PreferenceAnalyzer
from charapi.data.charity_evaluation_result import MetricStatus, MetricCategory


def test_mission_alignment_high_priority():
    config = {
        "preferences": {
            "mission_alignment": {
                "enabled": True,
                "priorities": {
                    "B": "high",
                    "E": "high",
                    "P": "high"
                }
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"ntee_cd": "B40"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    mission_metrics = [m for m in metrics if m.name == "Mission Alignment"]
    assert len(mission_metrics) == 1
    assert mission_metrics[0].status == MetricStatus.OUTSTANDING
    assert "Education" in mission_metrics[0].display_value
    assert "High" in mission_metrics[0].display_value


def test_mission_alignment_medium_priority():
    config = {
        "preferences": {
            "mission_alignment": {
                "enabled": True,
                "priorities": {
                    "A": "medium",
                    "C": "medium"
                }
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"ntee_cd": "A20"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    mission_metrics = [m for m in metrics if m.name == "Mission Alignment"]
    assert len(mission_metrics) == 1
    assert mission_metrics[0].status == MetricStatus.ACCEPTABLE
    assert "Arts" in mission_metrics[0].display_value


def test_mission_alignment_low_priority():
    config = {
        "preferences": {
            "mission_alignment": {
                "enabled": True,
                "priorities": {
                    "N": "low",
                    "X": "low"
                }
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"ntee_cd": "N20"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    mission_metrics = [m for m in metrics if m.name == "Mission Alignment"]
    assert len(mission_metrics) == 1
    assert mission_metrics[0].status == MetricStatus.UNACCEPTABLE


def test_mission_alignment_disabled():
    config = {
        "preferences": {
            "mission_alignment": {
                "enabled": False,
                "priorities": {"B": "high"}
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"ntee_cd": "B40"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    mission_metrics = [m for m in metrics if m.name == "Mission Alignment"]
    assert len(mission_metrics) == 0


def test_mission_alignment_no_ntee_code():
    config = {
        "preferences": {
            "mission_alignment": {
                "enabled": True,
                "priorities": {"B": "high"}
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    mission_metrics = [m for m in metrics if m.name == "Mission Alignment"]
    assert len(mission_metrics) == 1
    assert mission_metrics[0].status == MetricStatus.UNKNOWN


def test_geographic_alignment_preferred_state():
    config = {
        "preferences": {
            "geographic_alignment": {
                "enabled": True,
                "preferred_states": ["MA", "DC"],
                "acceptable_states": ["NH", "VT"]
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"state": "MA"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    geo_metrics = [m for m in metrics if m.name == "Geographic Alignment"]
    assert len(geo_metrics) == 1
    assert geo_metrics[0].status == MetricStatus.OUTSTANDING
    assert "MA" in geo_metrics[0].display_value
    assert "Pref" in geo_metrics[0].display_value


def test_geographic_alignment_acceptable_state():
    config = {
        "preferences": {
            "geographic_alignment": {
                "enabled": True,
                "preferred_states": ["MA"],
                "acceptable_states": ["NH", "VT"]
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"state": "NH"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    geo_metrics = [m for m in metrics if m.name == "Geographic Alignment"]
    assert len(geo_metrics) == 1
    assert geo_metrics[0].status == MetricStatus.ACCEPTABLE


def test_geographic_alignment_not_preferred():
    config = {
        "preferences": {
            "geographic_alignment": {
                "enabled": True,
                "preferred_states": ["MA"],
                "acceptable_states": ["NH"]
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"state": "CA"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    geo_metrics = [m for m in metrics if m.name == "Geographic Alignment"]
    assert len(geo_metrics) == 1
    assert geo_metrics[0].status == MetricStatus.UNACCEPTABLE


def test_geographic_alignment_disabled():
    config = {
        "preferences": {
            "geographic_alignment": {
                "enabled": False,
                "preferred_states": ["MA"]
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"state": "MA"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 1000000)

    geo_metrics = [m for m in metrics if m.name == "Geographic Alignment"]
    assert len(geo_metrics) == 0


def test_organization_size_small():
    config = {
        "preferences": {
            "organization_size": {
                "enabled": True,
                "small_max": 500000,
                "medium_max": 5000000
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)

    metrics = analyzer.get_preference_metrics({}, 250000)

    size_metrics = [m for m in metrics if m.name == "Organization Size"]
    assert len(size_metrics) == 1
    assert size_metrics[0].status == MetricStatus.OUTSTANDING
    assert "Small" in size_metrics[0].display_value


def test_organization_size_medium():
    config = {
        "preferences": {
            "organization_size": {
                "enabled": True,
                "small_max": 500000,
                "medium_max": 5000000
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)

    metrics = analyzer.get_preference_metrics({}, 2000000)

    size_metrics = [m for m in metrics if m.name == "Organization Size"]
    assert len(size_metrics) == 1
    assert size_metrics[0].status == MetricStatus.ACCEPTABLE
    assert "Med" in size_metrics[0].display_value


def test_organization_size_large():
    config = {
        "preferences": {
            "organization_size": {
                "enabled": True,
                "small_max": 500000,
                "medium_max": 5000000
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)

    metrics = analyzer.get_preference_metrics({}, 10000000)

    size_metrics = [m for m in metrics if m.name == "Organization Size"]
    assert len(size_metrics) == 1
    assert size_metrics[0].status == MetricStatus.UNACCEPTABLE
    assert "Large" in size_metrics[0].display_value


def test_organization_size_disabled():
    config = {
        "preferences": {
            "organization_size": {
                "enabled": False,
                "small_max": 500000
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)

    metrics = analyzer.get_preference_metrics({}, 250000)

    size_metrics = [m for m in metrics if m.name == "Organization Size"]
    assert len(size_metrics) == 0


def test_all_preferences_enabled():
    config = {
        "preferences": {
            "mission_alignment": {
                "enabled": True,
                "priorities": {"B": "high"}
            },
            "geographic_alignment": {
                "enabled": True,
                "preferred_states": ["MA"],
                "acceptable_states": ["NH"]
            },
            "organization_size": {
                "enabled": True,
                "small_max": 500000,
                "medium_max": 5000000
            }
        }
    }
    analyzer = PreferenceAnalyzer(config)
    charityapi_data = {"ntee_cd": "B40", "state": "MA"}

    metrics = analyzer.get_preference_metrics(charityapi_data, 250000)

    assert len(metrics) == 3
    assert all(m.category == MetricCategory.PREFERENCE for m in metrics)


if __name__ == "__main__":
    test_mission_alignment_high_priority()
    test_mission_alignment_medium_priority()
    test_mission_alignment_low_priority()
    test_mission_alignment_disabled()
    test_mission_alignment_no_ntee_code()
    test_geographic_alignment_preferred_state()
    test_geographic_alignment_acceptable_state()
    test_geographic_alignment_not_preferred()
    test_geographic_alignment_disabled()
    test_organization_size_small()
    test_organization_size_medium()
    test_organization_size_large()
    test_organization_size_disabled()
    test_all_preferences_enabled()
    print("All preference analyzer tests passed!")
