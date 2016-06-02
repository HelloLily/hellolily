from optparse import make_option
from django.core.management.base import BaseCommand

from lily.tags.models import Tag

import difflib


class Command(BaseCommand):
    help = """Find similar tags based on the difflib module, usefull to identify duplicates & typos."""
    ratio_cut_off_default = 0.65

    option_list = BaseCommand.option_list + (
        make_option('-c', '--cutoff',
                    action='store',
                    dest='cutoff',
                    default='',
                    help='Choose similarity cut-off value. Decimal in range [0,1]. Defaults to 0.65.'
                    ),
    )

    def handle(self, *args, **options):

        if options['cutoff']:
            cutoff = float(options['cutoff'])
        else:
            cutoff = self.ratio_cut_off_default

        tags1 = Tag.objects.all()
        tags2 = Tag.objects.all()
        tag_list = []
        # Loop over each tag and compare with all other tags.
        for tag1 in tags1:
            for tag2 in tags2:
                if ((tag1.name, tag2.name) not in tag_list) and ((tag2.name, tag1.name) not in tag_list):
                    # Determine similarity ratio between the two tag names.
                    diffl = difflib.SequenceMatcher(a=tag1.name, b=tag2.name).ratio()
                    if diffl > cutoff and diffl != 1.0:
                        # Encode & decode to handle special characters.
                        # This is a work around for encoding problems in outputting to docker shell.
                        n1 = tag1.name.encode('utf-8')
                        n1 = n1.decode('ascii', 'ignore')
                        n2 = tag2.name.encode('utf-8')
                        n2 = n2.decode('ascii', 'ignore')
                        tag_list.insert(0, (tag1.name, tag2.name))

                        print u"{0}\t{1}\t{2:.3f}".format(n1, n2, diffl)
