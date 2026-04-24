from datetime import date, time, datetime
import pytz
import re

LOCAL_TZ = pytz.timezone('Asia/Shanghai')

def parse_date(date_str):
    """
    Parse date string from frontend.
    Handles:
    - 'YYYY-MM-DD'
    - 'YYYY-MM-DDT16:00:00.000Z' (UTC)
    - 'YYYY-MM-DDT08:00:00.000+08:00' (with timezone offset)
    
    Returns a naive date in local timezone (Asia/Shanghai).
    """
    if not date_str:
        return None
    
    date_str = str(date_str)
    
    # If it's just a date string (YYYY-MM-DD)
    if 'T' not in date_str:
        return date.fromisoformat(date_str)
    
    # Parse full datetime with possible timezone info
    try:
        # Replace Z with +00:00 for standard ISO format
        iso_str = date_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(iso_str)
        
        # If the datetime has timezone info, convert to local timezone
        if dt.tzinfo is not None:
            dt = dt.astimezone(LOCAL_TZ)
        
        # Return naive date in local timezone
        return dt.date()
    except (ValueError, TypeError):
        # Fallback: just extract the date part
        return date.fromisoformat(date_str.split('T')[0])

def parse_time(time_str):
    """
    Parse time from frontend.
    Handles:
    - 'HH:MM:SS'
    - 'HH:MM'
    - Full datetime strings like '2026-04-24T07:00:27.000Z' or with timezone offset
    
    Returns a naive time in local timezone (Asia/Shanghai).
    """
    if not time_str:
        return None
    
    time_str = str(time_str)
    
    # If it's a full datetime string
    if 'T' in time_str:
        try:
            iso_str = time_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(iso_str)
            
            # Convert to local timezone if it has timezone info
            if dt.tzinfo is not None:
                dt = dt.astimezone(LOCAL_TZ)
            
            return dt.time()
        except (ValueError, TypeError):
            pass
    
    # Try parsing as HH:MM:SS or HH:MM
    try:
        if len(time_str.split(':')) == 2:
            time_str = time_str + ':00'
        return time.fromisoformat(time_str)
    except (ValueError, TypeError):
        return None

def now_local():
    """Return current datetime in local timezone (naive)."""
    return datetime.now(LOCAL_TZ).replace(tzinfo=None)

def today_local():
    """Return current date in local timezone (Asia/Shanghai)."""
    return datetime.now(LOCAL_TZ).date()
