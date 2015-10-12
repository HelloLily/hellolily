from datetime import datetime, timedelta


def week_from_now():
    """
    Return a date object one week from now.
    """
    today = datetime.today()
    delta = timedelta(days=7)

    return today + delta
