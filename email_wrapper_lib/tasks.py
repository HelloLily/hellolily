from celery.app.task import Task


class LogErrorsTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.save_failed_task(exc, task_id, args, kwargs, einfo)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def save_failed_task(self, exc, task_id, args, kwargs, traceback):
        """
        :type exc: Exception
        """
        print 'This is the custom error handling task class.'
        print exc
        print task_id
        print args
        print kwargs
        print traceback

        # task = FailedTask()
        # task.celery_task_id = task_id
        # task.full_name = self.name
        # task.name = self.name.split('.')[-1]
        # task.exception_class = exc.__class__.__name__
        # task.exception_msg = unicode(exc).strip()
        # task.traceback = unicode(traceback).strip()
        # task.updated_at = timezone.now()
        #
        # if args:
        #     task.args = json.dumps(list(args))
        # if kwargs:
        #     task.kwargs = json.dumps(kwargs)
        #
        # # Find if task with same args, name and exception already exists
        # # If it do, update failures count and last updated_at
        # #: :type: FailedTask
        # existing_task = FailedTask.objects.filter(
        #     args=task.args,
        #     kwargs=task.kwargs,
        #     full_name=task.full_name,
        #     exception_class=task.exception_class,
        #     exception_msg=task.exception_msg,
        # )
        #
        # if len(existing_task):
        #     existing_task = existing_task[0]
        #     existing_task.failures += 1
        #     existing_task.updated_at = task.updated_at
        #     existing_task.save(force_update=True,
        #                        update_fields=('updated_at', 'failures'))
        # else:
        #     task.save(force_insert=True)


# class FailedTask(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(null=True, blank=True)
#     name = models.CharField(max_length=125)
#     full_name = models.TextField()
#     args = models.TextField(null=True, blank=True)
#     kwargs = models.TextField(null=True, blank=True)
#     exception_class = models.TextField()
#     exception_msg = models.TextField()
#     traceback = models.TextField(null=True, blank=True)
#     celery_task_id = models.CharField(max_length=36)
#     failures = models.PositiveSmallIntegerField(default=1)
#
#     class Meta:
#         ordering = ('-updated_at',)
#
#     def __unicode__(self):
#         return '%s %s [%s]' % (self.name, self.args, self.exception_class)
#
#     def retry_and_delete(self, inline=False):
#
#         import importlib
#
#         # Import real module and function
#         mod_name, func_name = self.full_name.rsplit('.', 1)
#         mod = importlib.import_module(mod_name)
#         func = getattr(mod, func_name)
#
#         args = json.loads(self.args) if self.args else ()
#         kwargs = json.loads(self.kwargs) if self.kwargs else {}
#         if inline:
#             try:
#                 res = func(*args, **kwargs)
#                 self.delete()
#                 return res
#             except Exception as e:
#                 raise e
#
#         self.delete()
#         return func.delay(*args, **kwargs)











# from celery import shared_task
#
# from email_wrapper_lib.manager import EmailAccountManager
# from email_wrapper_lib.models.models import EmailAccount, EmailFolder
# from email_wrapper_lib.providers import Google, Microsoft
#
#
# @shared_task
# def sync_scheduler():
#     # TODO: filter(is_authorized=True, is_deleted=False): ?
#     for email_account_id in EmailAccount.objects.all().values_list('id', flat=True):
#         sync_account.delay(email_account_id)
#
#
# @shared_task
# def sync_account(account_id):
#     account = EmailAccount.objects.get(pk=account_id)
#
#     if account.status in [EmailAccount.SYNCING, EmailAccount.ERROR]:
#         # TODO: move to sync_scheduler() filter.
#         return
#
#     manager = EmailAccountManager(account)
#     manager.sync_folders()
#
#     # Google history.list end point synchronizes over 'all' mail where MS has a history for each folder. Google and MS
#     # message.list end point retrieves the messages for all folders. So in that case of a history sync, differentiate
#     # between Google and MS.
#     if account.provider_id == Google.id or account.status in [EmailAccount.NEW, EmailAccount.RESYNC]:
#         sync_messages.delay(account_id)
#     elif account.provider_id == Microsoft.id:
#         folder_ids = EmailFolder.objects.filter(account=account).values_list('id', flat=True)
#         for folder_id in folder_ids:
#             sync_messages_by_folder.delay(account_id, folder_id)
#
#
# @shared_task
# def sync_messages(account_id):
#     account = EmailAccount.objects.get(pk=account_id)
#     manager = EmailAccountManager(account)
#
#     manager.sync_messages()
#
#     # TODO: No need to reload account / retrieve updated data from db?
#     if account.page_token:
#         # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
#         sync_messages.delay(account_id)
#
#
# @shared_task
# def sync_messages_by_folder(account_id, folder_id):
#     account = EmailAccount.objects.get(pk=account_id)
#     folder = EmailFolder.objects.get(pk=folder_id)
#     manager = EmailAccountManager(account, folder)
#
#     manager.sync_messages_by_folder()
#
#     # TODO: No need to reload folder / retrieve updated data from db?
#     if folder.page_token:
#         # Indicated by the page_token, syncing is not done yet. Fire up new task to continue syncing.
#         sync_messages_by_folder.delay(account_id, folder_id)
#
