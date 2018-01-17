from datetime import date, timedelta


def week_from_now():
    """
    Return a date object one week from now.
    """
    today = date.today()
    delta = timedelta(days=7)

    return today + delta
