import time

from django.core.management.base import BaseCommand

from lily.search.connections_utils import get_es_client


class Command(BaseCommand):
    help = """Delete all indexes. Obviously, use with caution."""

    def handle(self, *args, **options):
        es = get_es_client()

        cluster = es.nodes.stats()['nodes'].values()[0]['host']  # pretty host name
        if '.' not in cluster:
            cluster = es.nodes.stats()['nodes'].values()[0]['ip'][0]  # use ip instead
        self.stdout.write('This command will irreversibly DELETE ALL INDEXES from cluster %s!' % cluster)

        confirm = None
        while True:
            if confirm == 'yes':
                self.stdout.write('Proceeding.')
                break
            elif confirm == 'no':
                self.stdout.write('Aborted.')
                return
            confirm = raw_input('Do you wish to proceed? Enter "yes" or "no": ')

        self.stdout.write('Deleting all indexes in 10 seconds. Hit ctrl+c to abort.')
        time.sleep(10)
        result = es.indices.delete('_all')
        self.stdout.write(str(result))
