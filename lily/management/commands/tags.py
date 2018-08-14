from django.core.management.base import BaseCommand

from lily.tags.models import Tag

import difflib


class Command(BaseCommand):
    help = """Find similar tags based on the difflib module, usefull to identify duplicates & typos."""
    ratio_cut_off_default = 0.65

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--cutoff',
            action='store',
            dest='cutoff',
            default='',
            help='Choose similarity cut-off value. Decimal in range [0,1]. Defaults to 0.65.'
        )

    def handle(self, *args, **options):

        if options['cutoff']:
            cutoff = float(options['cutoff'])
        else:
            cutoff = self.ratio_cut_off_default

        original_tags = Tag.objects.all()
        tags_to_check = Tag.objects.all()
        tag_list = []
        # Loop over each tag and compare with all other tags.
        for original_tag in original_tags:
            for tag_to_check in tags_to_check:
                if ((original_tag.name, tag_to_check.name) not in tag_list) and \
                        ((tag_to_check.name, original_tag.name) not in tag_list) and \
                        (original_tag.id != tag_to_check.id):
                    # Determine similarity ratio between the two tag names.
                    diffl = difflib.SequenceMatcher(a=original_tag.name, b=tag_to_check.name).ratio()
                    if diffl > cutoff and diffl != 1.0:
                        tag_list.insert(0, (original_tag.name, tag_to_check.name))

                        # Encode & decode to handle special characters.
                        # This is a work around for encoding problems in outputting to docker shell.
                        name_original = original_tag.name.encode('utf-8')
                        name_original = name_original.decode('ascii', 'ignore')
                        name_duplicate = tag_to_check.name.encode('utf-8')
                        name_duplicate = name_duplicate.decode('ascii', 'ignore')
                        print u"{0}\t{1}\t{2:.3f}".format(name_original, name_duplicate, diffl)
