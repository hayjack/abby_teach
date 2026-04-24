from datetime import date, time, datetime

def parse_date(date_str):
    """
    Parse ISO date string from frontend.
    Handles both 'YYYY-MM-DD' and 'YYYY-MM-DDT16:00:00.000Z' formats.
    Returns None if input is empty or None.
    """
    if not date_str:
        return None
    return date.fromisoformat(date_str.split('T')[0])

def parse_time(time_str):
    """
    Parse time from frontend.
    Handles both 'HH:MM:SS' and full datetime strings like '2026-04-24T07:00:27.000Z'.
    Returns None if input is empty or None.
    """
    if not time_str:
        return None
    if 'T' in str(time_str):
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.time()
    return time.fromisoformat(time_str)
