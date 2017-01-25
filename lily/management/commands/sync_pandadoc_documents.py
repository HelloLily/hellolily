import logging

from django.core.management.base import BaseCommand

from lily.deals.models import Deal
from lily.integrations.models import Document
from lily.tenant.models import Tenant

from lily.integrations.credentials import get_credentials
from lily.utils.functions import send_get_request

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Retrieve documents that might not have been stored in our own database."""

    imported_documents_count = 0

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=int)

    def handle(self, *args, **options):
        tenant = Tenant.objects.get(pk=options['tenant_id'])

        if tenant:
            credentials = get_credentials('pandadoc', tenant)

            if credentials:
                logger.info('Syncing documents for tenant %s' % tenant.id)
                # Get all current documents.
                tenant_documents = Document.objects.filter(tenant=tenant)

                url = 'https://api.pandadoc.com/public/v1/documents'
                # Get all documents from PandaDoc.
                response = send_get_request(url, credentials)

                if response.status_code == 200:
                    documents = response.json().get('results')

                    for document in documents:
                        document_id = document.get('id')

                        # Document doesn't exist (so something probably went wrong while creating the quote).
                        if not tenant_documents.filter(document_id=document_id):
                            details_url = url + '/%s/details' % document_id
                            response = send_get_request(details_url, credentials)

                            if response.status_code == 200:
                                deal_id = response.json().get('metadata').get('deal')

                                if deal_id:
                                    deal = Deal.objects.get(pk=deal_id)

                                    document = Document.objects.create(
                                        contact=deal.contact,
                                        deal=deal,
                                        document_id=document_id,
                                        tenant=tenant,
                                    )

                                    self.imported_documents_count += 1
                            else:
                                message = '[PandaDoc] Something went wrong while syncing document %s: ' % document_id
                                message = message + response.text
                                logger.warning(message)
                else:
                    message = '[PandaDoc] Something went while syncing documents: ' + response.json()
                    logger.warning(message)
            else:
                message = '[PandaDoc] Tenant %s doesn\'t have PandaDoc credentials' % options['tenant_id']
                logger.warning(message)

            logger.info('%s documents have been imported' % self.imported_documents_count)
        else:
            logger.error('Please enter a valid tenant')
