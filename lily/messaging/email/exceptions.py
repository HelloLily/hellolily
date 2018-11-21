class UnsupportedMessageException(Exception):
    pass


class FailedServiceCallException(Exception):
    pass


class ConnectorError(Exception):
    pass


class NotFoundError(ConnectorError):
    pass


class LabelNotFoundError(ConnectorError):
    pass


class IllegalLabelError(ConnectorError):
    pass


class MailNotEnabledError(ConnectorError):
    pass


class InvalidCredentialsError(Exception):
    pass


class EmailHeaderInputException(Exception):
    pass
