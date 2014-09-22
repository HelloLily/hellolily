
LOGIN_ERRORS = [
    '[ALERT] Invalid credentials',
    '[ALERT] Please log in via your web browser',
    '[AUTHENTICATIONFAILED]',
    'Invalid credentials'
]

TEMPORARY_ERRORS = [
    '[THROTTLED]',
    '[OVERQUOTA]'
]


class IMAPConnectionError(Exception):
    pass


def is_login_error(e):
    for ex in LOGIN_ERRORS:
        if str(e).startswith(ex):
            return True
    return False


def is_temporary_error(e):
    for ex in TEMPORARY_ERRORS:
        if str(e).contains(ex):
            return True
    return False
