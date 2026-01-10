from datetime import datetime, timezone


def format_timestamp(dt):
    """Format datetime to ISO string"""
    if dt is None:
        return None
    return dt.isoformat()


def parse_timestamp(timestamp_str):
    """Parse ISO timestamp string"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return datetime.now(timezone.utc)