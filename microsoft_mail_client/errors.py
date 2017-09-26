class Error(Exception):
    """Base error for this module."""
    pass


class UnknownApiVersion(Error):
    """No API with that version exists."""
    pass


class NoMessageId(Error):
    """Message id not provided."""
    pass


class NoMessage(Error):
    """Message not provided."""
    pass


class NoFolderId(Error):
    """Folder id not provided."""
    pass


class NoComment(Error):
    """No comment provided."""
    pass


class NoRecipients(Error):
    """No recipient provided."""
    pass


class InvalidWritableProperty(Error):
    """Unknown or not writable property provided."""
    pass


class InvalidWritableMessageProperty(Error):
    """Unknown or not writable message property provided."""
    pass


class InvalidWritableFileProperty(InvalidWritableProperty):
    """Unknown or not writable file property provided."""
    pass


class InvalidWritableItemProperty(InvalidWritableProperty):
    """Unknown or not writable item property provided."""
    pass


class InvalidWritableReferenceProperty(InvalidWritableProperty):
    """Unknown or not writable reference property provided."""
    pass


class InvalidClassification(Error):
    """Unknown classification provided."""
    pass


class InvalidSettingsOption(Error):
    """Unknown settings option provided."""
    pass


class NoName(Error):
    """No name provided."""
    pass


class NoFileName(NoName):
    """No file name provided."""
    pass


class NoItemName(NoName):
    """No item name provided."""
    pass


class NoReferenceName(NoName):
    """No reference name provided."""
    pass


class NoFile(Error):
    """No file provided."""
    pass


class NoItem(Error):
    """No item provided."""
    pass


class NoUrl(Error):
    """No url provided."""
    pass


class NoAttachmentId(Error):
    """Attachment id not provided."""
    pass


class NoDestinationFolderId(Error):
    """No destination folder id provided."""
    pass


class BatchIdError(Error):
    """There is an error with the batch id."""
    pass


class BatchMaxSizeError(Error):
    """Maximum capacity batch size exceeded."""
    pass


class CallbackError(Error):
    """No callback provided."""
    pass


class NoMailboxSettings(Error):
    """No mailbox settings provided."""
    pass


class NoProperties(Error):
    """No properties provided."""
    pass


class HttpError(Error):
    """Wrapper for erroneous responses in a batch."""

    def __init__(self, reason):
        self.reason = reason

    def __repr__(self):
        return self.reason

    __str__ = __repr__
