from django.test import TestCase

from python_imap.utils import convert_html_to_text


class ConvertHTMLToTextTestCase(TestCase):

    def test_br_to_newline(self):
        html = 'Hello VoipGRID,<br><br>This is a test'
        result = 'Hello VoipGRID,\n\nThis is a test'

        self.assertEqual(convert_html_to_text(html, keep_linebreaks=True), result)

    def test_br_to_space(self):
        html = 'Hello VoipGRID,<br><br>This is a test'

        result = 'Hello VoipGRID,  This is a test'

        self.assertEqual(convert_html_to_text(html, keep_linebreaks=False), result)

    def test_remove_different_source_of_tags(self):
        html = 'Hello VoipGRID,<br><br><i>This is a test</i><br><br><b><i>dsfg</i></b><br><b>dsfg</b><br><b>ds</b>'

        result = """Hello VoipGRID,

This is a test

dsfg
dsfg
ds"""
        self.assertEqual(convert_html_to_text(html, keep_linebreaks=True), result)

    def test_convert_nbsp_to_space(self):
        html = 'Hello&nbsp;VoipGRID'

        result = 'Hello VoipGRID'

        self.assertEqual(convert_html_to_text(html), result)

    def test_list_to_newlines(self):

        html = """Hi there!
<script>console.log('hello');</script>
<ul><li>1</li> <li>2</li></ul>
Bye!
"""
        result = """Hi there!

1 2
Bye!
"""

        self.assertEqual(convert_html_to_text(html, keep_linebreaks=True), result)

    def test_link(self):

        html = '<a href="http://www.test.com">Test link title</a>'

        result = 'Test link title <http://www.test.com>'

        self.assertEqual(convert_html_to_text(html, keep_linebreaks=True), result)
