import re


def parse_time_to_minutes(text: str) -> float | None:
    text = text.strip().lower()

    m = re.match(r"(\d+(?:\.\d+)?)\s*[чh]\s*(\d+(?:\.\d+)?)\s*[мm]?", text)
    if m:
        return float(m.group(1)) * 60 + float(m.group(2))

    m = re.match(r"^(\d+):(\d{2})$", text)
    if m:
        return float(m.group(1)) * 60 + float(m.group(2))

    m = re.match(r"^(\d+(?:\.\d+)?)\s*[чh]$", text)
    if m:
        return float(m.group(1)) * 60

    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:м|мин|минут|m|min)?$", text)
    if m:
        return float(m.group(1))

    return None


def minutes_to_str(minutes: float) -> str:
    h = int(minutes // 60)
    m = int(minutes % 60)
    if h and m:
        return f"{h} ч {m} мин"
    elif h:
        return f"{h} ч"
    else:
        return f"{m} мин"
