from unittest import TestCase

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

        html = """
<html>
	<head>
		<style type="text/css">
			body {
				background-image: url(dolfijn.jpg);
				background-position: right center;
				background-repeat: no-repeat;
				font-family: sans;
				font-size: 36pt;
				font-weight: bold;
			}
		</style>
		<title>Dolfijnwoorden</title>
	</head>
	<body>
		<h3>Dolfijnwoorden 26-02-2014</h3>
		<ul>
			<li>Wit</li>
			<li>Badpak</li>
			<li>Bedisputeren</li>
			<li>Dolfijnwoord</li>
			<li>Hogere wiskunde</li>
			<li>Moeder</li>
			<li>Pinpointen</li>
			<li>Redetwisten</li>
			<li>Schildpadwoord</li>
			<li>Sukkelseks</li>
			<li>Vakantie</li>
			<li>Vingerpistool</li>
			<li>Voor jouw beeldvorming</li>
			<li>Never gonna give you up</li>
			<li>Never gonna let you down</li>
		</ul>
	</body>
</html>"""

        result = """
Dolfijnwoorden 26-02-2014

Wit
Badpak
Bedisputeren
Dolfijnwoord
Hogere wiskunde
Moeder
Pinpointen
Redetwisten
Schildpadwoord
Sukkelseks
Vakantie
Vingerpistool
Voor jouw beeldvorming
Never gonna give you up
Never gonna let you down

"""
        self.assertEqual(convert_html_to_text(html, keep_linebreaks=True), result)

    def test_link(self):

        html = '<a href="http://www.test.com">Test link title</a>'

        result = 'Test link title <http://www.test.com>'

        self.assertEqual(convert_html_to_text(html, keep_linebreaks=True), result)
