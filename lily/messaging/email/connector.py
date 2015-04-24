import base64
import logging
import random
import time

import anyjson
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest

from .credentials import get_credentials, InvalidCredentialsError
from .services import build_gmail_service

logger = logging.getLogger(__name__)


class ConnectorError(Exception):
    pass


class AuthError(ConnectorError):
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
            except HttpError, e:
                try:
                    error = anyjson.loads(e.content)
                    # Error could be nested, so unwrap if nessecary
                    error = error.get('error', error)
                except ValueError:
                    logger.exception('error %s' % e)
                    error = e
                if error.get('code') == 403 and error.get('errors')[0].get('reason') in ['rateLimitExceeded', 'userRateLimitExceeded']:
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
                else:
                    logger.exception(error)
                    raise

    def get_history(self):
        """
        Fetch the history list from the gmail api.

        Returns:
            list with messageIds and threadIds
        """
        response = self.execute_service_call(self.service.users().history().list(
            userId='me',
            startHistoryId=self.history_id,
        ))

        # Get the messageIds.
        history = response.get('history', [])

        # Check if there are more pages but stop after 10 pages
        i = 0
        while 'nextPageToken' in response and i < 10:
            page_token = response['nextPageToken']
            response = self.execute_service_call(self.service.users().history().list(
                userId='me',
                startHistoryId=self.history_id,
                pageToken=page_token
            ))
            history.extend(response.get('history', []))
            i += 1

        if len(history) and self.history_id < history[-1]['id']:
            self.history_id = history[-1]['id']

        return history

    def get_all_message_id_list(self):
        """
        Fetch all messageIds from the gmail api.

        Returns:
            list with messageIds and threadIds
        """
        response = self.execute_service_call(self.service.users().messages().list(userId='me'))

        messages = response['messages'] if 'messages' in response else []

        # Check if there are more pages.
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.execute_service_call(self.service.users().messages().list(userId='me', pageToken=page_token))
            messages.extend(response.get('messages', []))

        # Store history_id
        if messages:
            message = self.get_message_info(messages[0]['id'])
            if message['historyId'] > self.history_id:
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
        return self.execute_service_call(self.service.users().messages().get(userId='me', id=message_id))

    def get_label_list(self):
        """
        Fetch all labels from the email account

        Returns:
            list with label info
        """
        response = self.execute_service_call(self.service.users().labels().list(userId='me'))
        return response['labels']

    def get_label_info(self, label_id):
        """
        Fetch label info given label_id

        Args:
            label_id (string): id of the label

        Return dict with label info
        """
        return self.execute_service_call(self.service.users().labels().get(userId='me', id=label_id))

    def get_message_label_list(self, message_id):
        """
        Fetch labels for given message

        Args:
            message_id (string): id of the message

        Returns:
            list with labels given message_id
        """
        labels = self.execute_service_call(self.service.users().messages().get(
            userId='me',
            id=message_id,
            fields='labelIds'
        ))
        return labels.get('labelIds', [])

    def save_history_id(self):
        """
        Save currently set history_id to the EmailAccount
        """
        self.email_account.history_id = self.history_id
        self.email_account.save()

    def get_message_list_info(self, message_ids):
        """
        Batch fetch message info given message_ids

        Args:
            message_ids (list): of message_ids

        Returns:
            dict with messages info
        """
        messages_info = {}

        # Callback function for every service request
        def get_message_info(request_id, response, exception):
            if response:
                messages_info[response['id']] = response
            if exception:
                # If 404, message no longer exists, otherwise raise error
                if exception.resp.status != 404:
                    raise exception
                else:
                    logger.error('404 error: %s' % exception)

        # Setup batch
        batch = BatchHttpRequest(callback=get_message_info)
        for message_id in message_ids:
            batch.add(self.service.users().messages().get(userId='me', id=message_id))

        self.execute_service_call(batch)

        return messages_info

    def get_label_list_info(self, messages_ids):
        """
        Batch fetch label info given message_ids

        Args:
            message_ids (list): of message_ids

        Returns:
            dict with label info
        """
        label_info_dict = {}

        # Callback function for every service request
        def get_label_info(request_id, response, exception):
            if response:
                label_info_dict[response['id']] = response
            if exception:
                # If 404, message no longer exists, otherwise raise error
                if exception.resp.status != 404:
                    raise exception

        batch = BatchHttpRequest(callback=get_label_info)

        for message_id in messages_ids:
            # Temporary add snippet
            # TODO: remove snippet
            batch.add(self.service.users().messages().get(
                userId='me',
                id=message_id,
                fields='labelIds,id,threadId,snippet'
            ))

        self.execute_service_call(batch)

        return label_info_dict

    def get_labels_from_message(self, message_id):
        label_info = self.get_label_list_info([message_id])
        return label_info[message_id].get('labelIds', [])

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
            self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id)
        )

    def update_labels(self, message_id, labels):
        return self.execute_service_call(
            self.service.users().messages().modify(userId='me', id=message_id, body=labels)
        )

    def trash_email_message(self, message_id):
        return self.execute_service_call(
            self.service.users().messages().trash(userId='me', id=message_id)
        )

    def delete_email_message(self, message_id):
        return self.execute_service_call(
            self.service.users().messages().delete(userId='me', id=message_id)
        )

    def send_email_message(self, message_string, thread_id=None):
        message_dict = {'raw': base64.urlsafe_b64encode(message_string)}
        if thread_id:
            message_dict.update({'threadId': thread_id})
        return self.execute_service_call(
            self.service.users().messages().send(userId='me', body=message_dict)
        )

    def create_draft_email_message(self, message_string):
        message_dict = {'message': {'raw': base64.urlsafe_b64encode(message_string)}}
        return self.execute_service_call(
            self.service.users().drafts().create(userId='me', body=message_dict)
        )

    def remove_draft_email_message(self, message_id):
        return self.execute_service_call(
            self.service.users().drafts().delete(userId='me', id=message_id)
        )

    def cleanup(self):
        """
        Cleanup references, to prevent reference cycle
        """
        self.service = None
        self.email_account = None
        self.history_id = None
