import logging
import random
import time

import anyjson
from django.conf import settings
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaInMemoryUpload

from .credentials import get_credentials, InvalidCredentialsError
from .services import build_gmail_service

logger = logging.getLogger(__name__)


class FailedServiceCallException(Exception):
    pass


class ConnectorError(Exception):
    pass


class AuthError(ConnectorError):
    pass


class MessageNotFoundError(ConnectorError):
    pass


class LabelNotFoundError(ConnectorError):
    pass


class GmailConnector(object):
    service = None

    def __init__(self, email_account):
        self.email_account = email_account
        self.history_id = self.email_account.history_id

        self.service = self.create_service()

    def create_service(self):
        """
        Get or create GMail api service
        """
        try:
            credentials = get_credentials(self.email_account)
        except InvalidCredentialsError:
            logger.exception('cannot sync account, no valid credentials')
            raise
        else:
            return build_gmail_service(credentials)

    def execute_service_call(self, service):
        """
        Try to execute a service call.

        If the call fails because the rate limit is exceeded, sleep x seconds to try again.

        Args:
            service (instance): service instance
        Returns:
            response from service instance
        """
        for n in range(0, 6):
            try:
                return service.execute()
            except HttpError as e:
                try:
                    error = anyjson.loads(e.content)
                    # Error could be nested, so unwrap if necessary.
                    error = error.get('error', error)
                except ValueError:
                    logger.exception('error %s' % e)
                    error = e

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
                elif error.get('code') == 404:
                    raise MessageNotFoundError
                else:
                    logger.exception('Unkown error code for error %s' % error)
                    raise

        logger.warning('Service call failed after all retries')
        raise FailedServiceCallException('Service call failed after all retries')

    def get_history(self):
        """
        Fetch the history list from the gmail api.

        Returns:
            list with messageIds and threadIds
        """
        response = self.execute_service_call(self.service.users().history().list(
            userId='me',
            startHistoryId=self.history_id,
            quotaUser=self.email_account.id,
        ))

        history = response.get('history', [])

        # Check if there are more pages.
        while 'nextPageToken' in response:
            page_token = response.get('nextPageToken')
            response = self.execute_service_call(self.service.users().history().list(
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
        Fetch all messageIds from the gmail api.

        Returns:
            list with messageIds and threadIds
        """
        response = self.execute_service_call(self.service.users().messages().list(
            userId='me',
            quotaUser=self.email_account.id,
            q='!in:chats',
        ))

        messages = response['messages'] if 'messages' in response else []

        # Check if there are more pages.
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.execute_service_call(
                self.service.users().messages().list(
                    userId='me',
                    pageToken=page_token,
                    quotaUser=self.email_account.id,
                    q='!in:chats',
                ))
            messages.extend(response.get('messages', []))

        if messages:
            # The history is in reverse chronological order, so the first message has the latest history id.
            message = self.get_message_info(messages[0]['id'])
            if message['historyId'] > self.history_id:
                # Store if it's past the current history id.
                self.history_id = message['historyId']

        return messages

    def get_message_info(self, message_id):
        """
        Fetch message information given message_id.

        Args:
            message_id (string): id of the message

        Returns:
            dict with message info
        """
        return self.execute_service_call(self.service.users().messages().get(
            userId='me',
            id=message_id,
            quotaUser=self.email_account.id,
        ))

    def get_label_list(self):
        """
        Fetch all labels from the email account.

        Returns:
            list with label info
        """
        response = self.execute_service_call(self.service.users().labels().list(
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
        return self.execute_service_call(self.service.users().labels().get(
            userId='me',
            id=label_id,
            quotaUser=self.email_account.id,
        ))

    def get_short_message_info(self, message_id):
        """
        Fetch labels & threadId for given message.

        Args:
            message_id (string): id of the message

        Returns:
            dict with message info, with threadId & labels
        """
        return self.execute_service_call(self.service.users().messages().get(
            userId='me',
            id=message_id,
            fields='labelIds,threadId',
            quotaUser=self.email_account.id,
        ))

    def save_history_id(self):
        """
        Save currently set history_id to the EmailAccount
        """
        self.email_account.history_id = self.history_id
        self.email_account.save()

    def get_attachment(self, message_id, attachment_id):
        """
        Fetch attachment given message_id and attachment_id

        Args:
            message_id (string): id of the message
            attachment_id (string): id of the attachment

        Returns:
            dict with attachment info
        """
        return self.execute_service_call(
            self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id,
                quotaUser=self.email_account.id,
            ))

    def update_labels(self, message_id, labels):
        return self.execute_service_call(
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=labels,
                quotaUser=self.email_account.id,
            ))

    def trash_email_message(self, message_id):
        return self.execute_service_call(
            self.service.users().messages().trash(
                userId='me',
                id=message_id,
                quotaUser=self.email_account.id,
            ))

    def delete_email_message(self, message_id):
        return self.execute_service_call(
            self.service.users().messages().delete(
                userId='me',
                id=message_id,
                quotaUser=self.email_account.id,
            ))

    def send_email_message(self, message_string, thread_id=None):
        message_dict = {}
        media = MediaInMemoryUpload(
            message_string,
            mimetype='message/rfc822',
            chunksize=settings.GMAIL_CHUNK_SIZE,
            resumable=True
        )
        if thread_id:
            message_dict.update({'threadId': thread_id})
        return self.execute_service_call(
            self.service.users().messages().send(
                userId='me',
                body=message_dict,
                media_body=media,
                quotaUser=self.email_account.id,
            ))

    def create_draft_email_message(self, message_string):
        media = MediaInMemoryUpload(
            message_string,
            mimetype='message/rfc822',
            chunksize=settings.GMAIL_CHUNK_SIZE,
            resumable=True
        )
        return self.execute_service_call(
            self.service.users().drafts().create(
                userId='me',
                media_body=media,
                quotaUser=self.email_account.id,
            ))

    def update_draft_email_message(self, message_string, draft_id):
        media = MediaInMemoryUpload(
            message_string,
            mimetype='message/rfc822',
            chunksize=settings.GMAIL_CHUNK_SIZE,
            resumable=True
        )
        return self.execute_service_call(
            self.service.users().drafts().update(
                userId='me',
                media_body=media,
                id=draft_id,
                quotaUser=self.email_account.id,
            ))

    def delete_draft_email_message(self, message_id):
        return self.execute_service_call(
            self.service.users().drafts().delete(
                userId='me',
                id=message_id,
                quotaUser=self.email_account.id,
            ))

    def cleanup(self):
        """
        Cleanup references, to prevent reference cycle
        """
        self.service = None
        self.email_account = None
        self.history_id = None
