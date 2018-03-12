class BatchRequestException(Exception):
    pass


class IllegalLabelException(Exception):
    pass


# TODO: maybe just have one type of exception for the account status?
class ErrorStatusException(Exception):
    """
    Exception that is thrown when an email account has error status but an action is called on it anyway.
    """
    pass


class UnexpectedSyncStatusException(Exception):
    """
    Exception that is thrown when an email account has an unexpected status.
    """
    pass
