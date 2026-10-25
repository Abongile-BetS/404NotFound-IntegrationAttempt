from datetime import date


def luhn_valid(value: str) -> bool:
    if not value.isdigit() or len(value) != 13:
        return False
    total = 0
    parity = len(value) % 2
    for i, char in enumerate(value):
        digit = int(char)
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def validate_sa_id(value: str) -> dict:
    result = {"valid_format": value.isdigit() and len(value) == 13, "valid_checksum": False, "dob": None, "citizenship": None}
    if not result["valid_format"]:
        return result
    yy, mm, dd = int(value[:2]), int(value[2:4]), int(value[4:6])
    years = [1900 + yy, 2000 + yy]
    candidates = []
    for year in years:
        try:
            candidate = date(year, mm, dd)
            if candidate <= date.today():
                candidates.append(candidate)
        except ValueError:
            pass
    if candidates:
        result["dob"] = max(candidates).isoformat()
    result["valid_checksum"] = luhn_valid(value)
    result["citizenship"] = "citizen" if value[10] == "0" else "permanent_resident"
    result["valid"] = bool(result["dob"] and result["valid_checksum"])
    return result


def compare_ids(left: str, right: str) -> dict:
    positions = [i + 1 for i, (a, b) in enumerate(zip(left, right)) if a != b]
    positions += list(range(min(len(left), len(right)) + 1, max(len(left), len(right)) + 1))
    return {"distance": len(positions), "differing_positions": positions, "match_type": "exact" if not positions else "near" if len(positions) <= 2 else "different"}

