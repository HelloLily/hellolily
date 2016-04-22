from multiprocessing.pool import ThreadPool

from django.core.files.storage import default_storage
from django.core.management import BaseCommand


# This will set the actual permissions on the file.
def set_acl_for_item(key):
    max_retries = 12

    for i in range(max_retries):
        try:
            key.set_canned_acl('private')
            break
        except Exception:
            if not (i < (max_retries - 1)):
                print 'Amazon S3: acl set: failed after %s retries for %s' % (max_retries, key.name)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Set the acl of all files in the media bucket to private.
        """
        # Get the media bucket.
        bucket = default_storage.bucket
        # Prepare the treadpool.
        pool = ThreadPool(256)
        # Folders to loop over, preferably this would be dynamic, but for performance we set folders manually.
        folder_list = [
            'users/',
            'messaging/email/attachments/1',
            'messaging/email/attachments/10',
            'messaging/email/attachments/2',
            'messaging/email/attachments/22',
            'messaging/email/attachments/28',
            'messaging/email/attachments/29',
            'messaging/email/attachments/3',
            'messaging/email/attachments/4',
            'messaging/email/attachments/50',
            'messaging/email/attachments/52',
            'messaging/email/attachments/58',
            'messaging/email/attachments/61',
            'messaging/email/templates/attachments/10/',
            'messaging/email/templates/attachments/50/',
            'messaging/email/templates/attachments/52/',
        ]

        # Execute the threadpool and print progress.
        print 'Starting to work now!'
        for folder in folder_list:
            print 'On to a new folder, %s it is!' % folder
            file_list = bucket.list(prefix=folder)
            for index, result in enumerate(pool.imap(set_acl_for_item, file_list), 1):
                if index % 1000 == 0:
                    print 'Amazon S3: acl set: %s files successfully set in %s' % (index, folder)

        # Close the threadpool.
        pool.close()
        pool.join()








