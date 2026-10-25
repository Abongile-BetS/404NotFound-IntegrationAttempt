from app.services.identity import compare_ids, luhn_valid, validate_sa_id


def test_known_valid_sa_id_checksum_and_dob():
    result = validate_sa_id("8001015009087")
    assert result["valid"] is True
    assert result["dob"] == "1980-01-01"


def test_invalid_checksum_is_rejected():
    assert luhn_valid("8001015009088") is False


def test_near_id_difference_positions_are_explainable():
    result = compare_ids("8001015009087", "8001015009187")
    assert result == {"distance": 1, "differing_positions": [11], "match_type": "near"}

