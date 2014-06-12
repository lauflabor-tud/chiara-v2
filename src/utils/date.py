import datetime
from exception.exceptions import CannotParseStringToDateException

def get_date(str_date):
    """Returns a date object by a given date string 
    in Format: dd.mm.yyyy ; mm.yyyy ; yyyy"""
    try:
        date_values = [int(i) for i in str_date.split(".")]
        if len(date_values) == 3:
            date = datetime.date(date_values[2], date_values[1], date_values[0])
        elif len(date_values) == 2:
            date = datetime.date(date_values[1], date_values[0], 1)
        elif len(date_values) == 1:
            date = datetime.date(date_values[0], 1, 1)
    except ValueError:
        raise CannotParseStringToDateException(str_date)
        
    return date