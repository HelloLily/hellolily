import logging
import random
import time
import anyjson

from StringIO import StringIO

from django.conf import settings
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.client import HttpAccessTokenRefreshError

from .credentials import get_credentials, InvalidCredentialsError
from .services import GmailService

logger = logging.getLogger(__name__)


class FailedServiceCallException(Exception):
    pass


class ConnectorError(Exception):
    pass


class AuthError(ConnectorError):
    pass


class NotFoundError(ConnectorError):
    pass


class LabelNotFoundError(ConnectorError):
    pass


class IllegalLabelError(ConnectorError):
    pass


class MailNotEnabledError(ConnectorError):
    pass


class GmailConnector(object):
    gmail_service = None

    def __init__(self, email_account):
        self.email_account = email_account
        self.history_id = self.email_account.history_id

        try:
            credentials = get_credentials(self.email_account)
        except InvalidCredentialsError:
            logger.exception('cannot sync account, no valid credentials')
            raise
        else:
            self.gmail_service = GmailService(credentials)

    def execute_service_call(self, service):
        """
        Try to execute a service call.

        If the call fails because the rate limit is exceeded, sleep x seconds to try again.

        Args:
            service (instance): service instance
        Returns
            response from service instance
        """
        for n in range(0, 6):
            try:
                return self.gmail_service.execute_service(service)
            except HttpError as error:
                try:
                    error = anyjson.loads(error.content)
                    # Error could be nested, so unwrap if necessary.
                    error = error.get('error', error)

                    if error.get('code') == 403 and error.get('errors')[0].get('reason') in ['rateLimitExceeded',
                                                                                             'userRateLimitExceeded']:
                        # Apply exponential backoff.
                        sleep_time = (2 ** n) + random.randint(0, 1000) / 1000
                        logger.warning('Limit overrated, sleeping for %s seconds' % sleep_time)
                        time.sleep(sleep_time)
                    elif error.get('code') == 429:
                        # Apply exponential backoff.
                        sleep_time = (2 ** n) + random.randint(0, 1000) / 1000
                        logger.warning('Too many concurrent requests for user, sleeping for %d seconds' % sleep_time)
                        time.sleep(sleep_time)
                    elif error.get('code') == 503 or error.get('code') == 500:
                        # Apply exponential backoff.
                        sleep_time = (2 ** n) + random.randint(0, 1000) / 1000
                        logger.warning('Backend error, sleeping for %d seconds' % sleep_time)
                        time.sleep(sleep_time)
                    elif error.get('code') == 400 and error.get('message') == 'labelId not found':
                        raise LabelNotFoundError
                    elif error.get('code') == 400 and error.get('message') == 'Invalid label: SENT':
                        raise IllegalLabelError('Not allowed to set label SENT.')
                    elif error.get('code') == 400 and error.get('message') == 'Mail service not enabled':
                        raise MailNotEnabledError
                    elif error.get('code') == 404:
                        raise NotFoundError
                    else:
                        logger.exception('Unkown error code for error %s' % error)
                        if service.body_size < 25000:
                            # Log the actual API call to Google in case of an error. But restrict on the (arbitrary
                            # chosen) body_size. Size can be very large due to inline images / html tags.
                            logger.exception(service.to_json())
                        else:
                            logger.exception('Did not log api call, body size to large: %d' % service.body_size)
                        raise

                except ValueError:
                    # The error couldn't be loaded as json.
                    if error.resp.status == 404:
                        raise NotFoundError
                    else:
                        logger.exception('Unkown error code for error %s' % error)
                        if service.body_size < 25000:
                            logger.exception(service.to_json())
                        else:
                            logger.exception('Did not log api call, body size to large: %d' % service.body_size)
                        raise
            except HttpAccessTokenRefreshError:
                # Thrown when a user removes Lily from the connected apps or
                # changes the credentials of the Google account.
                self.email_account.is_authorized = False
                self.email_account.is_syncing = False
                self.email_account.save()
                logger.error('Invalid access token for account %s' % self.email_account)
                raise

        logger.exception('Service call failed after all retries')
        raise FailedServiceCallException('Service call failed after all retries')

    def get_history(self):
        """
        Fetch the history list from the gmail api. This includes email and chat messages.

        Returns:
            list with messageIds and threadIds
        """
        response = self.execute_service_call(self.gmail_service.service.users().history().list(
            userId='me',
            startHistoryId=self.history_id,
            quotaUser=self.email_account.id,
        ))

        history = response.get('history', [])

        # Check if there are more pages.
        while 'nextPageToken' in response:
            page_token = response.get('nextPageToken')
            response = self.execute_service_call(self.gmail_service.service.users().history().list(
                userId='me',
                startHistoryId=self.history_id,
                pageToken=page_token
            ))

            history.extend(response.get('history', []))

        # History id's are for successive history pages identical, so no need to update with each nextPageToken.
        new_history_id = response.get('historyId', self.history_id)
        if new_history_id > self.history_id:
            # Store new history id if it's past the current one.
            self.history_id = new_history_id

        return history

    def get_all_message_id_list(self):
        """
        Fetch all messageIds from the gmail api. Chat messages are filtered out.

        Returns:
            list with messageIds and threadIds
        """
        # First retrieve user profile including the latest history id.
        response = self.get_history_id()
        history_id = response.get('historyId', 0)

        response = self.execute_service_call(
            self.gmail_service.service.users().messages().list(
                userId='me',
                quotaUser=self.email_account.id,
                q='!in:chats',
            ))

        messages = response['messages'] if 'messages' in response else []

        # Check if there are more pages.
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.execute_service_call(self.gmail_service.service.users().messages().list(
                userId='me',
                quotaUser=self.email_account.id,
                pageToken=page_token,
                q='!in:chats',
            ))
            messages.extend(response.get('messages', []))

        if history_id > self.history_id:
            # Store if it's past the current history id.
            self.history_id = history_id

        return messages

    def get_message_info(self, message_id):
        """
        Fetch message information given message_id.

        Args:
            message_id (string): id of the message

        Returns:
            dict with message info
        """
        response = self.execute_service_call(self.gmail_service.service.users().messages().get(
            userId='me',
            id=message_id,
            quotaUser=self.email_account.id,
        ))

        return response

    def get_label_list(self):
        """
        Fetch all labels from the email account.

        Returns:
            list with label info
        """
        response = self.execute_service_call(self.gmail_service.service.users().labels().list(
            userId='me',
            quotaUser=self.email_account.id,
        ))

        return response['labels']

    def get_label_info(self, label_id):
        """
        Fetch label info given label_id

        Args:
            label_id (string): id of the label

        Return dict with label info
        """
        response = self.execute_service_call(self.gmail_service.service.users().labels().get(
            userId='me',
            id=label_id,
            quotaUser=self.email_account.id,
        ))
        return response

    def get_short_message_info(self, message_id):
        """
        Fetch labels & threadId for given message.

        Args:
            message_id (string): id of the message

        Returns:
            dict with message info, with threadId & labels
        """
        response = self.execute_service_call(self.gmail_service.service.users().messages().get(
            userId='me',
            id=message_id,
            fields='labelIds,threadId',
            quotaUser=self.email_account.id,
        ))
        return response

    def save_history_id(self):
        """
        Save currently set history_id to the EmailAccount.
        """
        self.email_account.history_id = self.history_id
        self.email_account.save(update_fields=["history_id"])

    def get_attachment(self, message_id, attachment_id):
        """
        Fetch attachment given message_id and attachment_id

        Args:
            message_id (string): id of the message
            attachment_id (string): id of the attachment

        Returns:
            dict with attachment info
        """
        response = self.execute_service_call(
            self.gmail_service.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id,
                quotaUser=self.email_account.id,
            ))
        return response

    def update_labels(self, message_id, labels):
        response = self.execute_service_call(
            self.gmail_service.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=labels,
                quotaUser=self.email_account.id,
            ))
        return response

    def trash_email_message(self, message_id):
        response = self.execute_service_call(
            self.gmail_service.service.users().messages().trash(
                userId='me',
                id=message_id,
                quotaUser=self.email_account.id,
            ))
        return response

    def delete_email_message(self, message_id):
        # TODO: LILY-1906 Email messages are never deleted.
        response = self.execute_service_call(
            self.gmail_service.service.users().messages().delete(
                userId='me',
                id=message_id,
                quotaUser=self.email_account.id,
            ))
        return response

    def send_email_message(self, message_string, thread_id=None):
        # Possible TODO: only use MediaIOBaseUpload on large email bodys instead of always:
        # http://stackoverflow.com/questions/27875858/#33155212
        fd = StringIO(message_string)
        media = MediaIoBaseUpload(
            fd,
            mimetype='message/rfc822',
            chunksize=settings.GMAIL_CHUNK_SIZE,
            resumable=settings.GMAIL_UPLOAD_RESUMABLE
        )

        message_dict = {}
        if thread_id:
            message_dict.update({'threadId': thread_id})

        response = self.execute_service_call(
            self.gmail_service.service.users().messages().send(
                userId='me',
                body=message_dict,
                media_body=media,
                quotaUser=self.email_account.id,
            ))

        return response

    def create_draft_email_message(self, message_string):
        # Possible TODO: only use MediaIOBaseUpload on large email bodys instead of always:
        # http://stackoverflow.com/questions/27875858/#33155212
        fd = StringIO(message_string)
        media = MediaIoBaseUpload(
            fd,
            mimetype='message/rfc822',
            chunksize=settings.GMAIL_CHUNK_SIZE,
            resumable=settings.GMAIL_UPLOAD_RESUMABLE
        )

        response = self.execute_service_call(
            self.gmail_service.service.users().drafts().create(
                userId='me',
                media_body=media,
                quotaUser=self.email_account.id,
            ))
        return response

    def update_draft_email_message(self, message_string, draft_id):
        # Possible TODO: only use MediaIOBaseUpload on large email bodys instead of always:
        # http://stackoverflow.com/questions/27875858/#33155212
        fd = StringIO(message_string)
        media = MediaIoBaseUpload(
            fd,
            mimetype='message/rfc822',
            chunksize=settings.GMAIL_CHUNK_SIZE,
            resumable=settings.GMAIL_UPLOAD_RESUMABLE
        )

        response = self.execute_service_call(
            self.gmail_service.service.users().drafts().update(
                userId='me',
                media_body=media,
                id=draft_id,
                quotaUser=self.email_account.id,
            ))
        return response

    def delete_draft_email_message(self, message_id):
        response = self.execute_service_call(
            self.gmail_service.service.users().drafts().delete(
                userId='me',
                id=message_id,
                quotaUser=self.email_account.id,
            ))
        return response

    def get_history_id(self):
        response = self.execute_service_call(
            self.gmail_service.service.users().getProfile(
                userId='me',
                fields='historyId',
            ))
        return response

    def cleanup(self):
        """
        Cleanup references, to prevent reference cycle.
        """
        self.gmail_service = None
        self.email_account = None
        self.history_id = None
