from dateutil import parser
from datetime import datetime

def parse_datetime(text):
    try:
        dt = parser.parse(text, fuzzy=True)
        return dt.isoformat()
    except:
        return None