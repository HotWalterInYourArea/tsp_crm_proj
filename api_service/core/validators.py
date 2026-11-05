import re


PHONE_REGEX = re.compile(r"^\+?[0-9]+$")


def is_valid_phone(phone: str | None) -> bool:
    if phone is None or phone == "":
        return True
    return bool(PHONE_REGEX.match(phone))


def normalize_phone(phone: str | None) -> str | None:
    if phone is None:
        return None
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    return cleaned or None