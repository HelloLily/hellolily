import mimetypes
from email.utils import formataddr

from bs4 import BeautifulSoup, Comment, Doctype


def format_addresses(addresses):
    """
    Return array with formatted addresses.
    """
    formatted = []
    for address in addresses:
        formatted.append(formataddr(address))

    return formatted


def extract_tags_from_soup(soup, tags):
    """
    Remove all instances of *tags* from soup including child elements.
    """
    for element in soup.findAll(tags):
        element.extract()


def convert_br_to_newline(soup, newline='\n'):
    """
    Replace html line breaks with spaces to prevent lines appended after one another.
    """
    for linebreak in soup.findAll('br'):
        linebreak.replaceWith(newline)


def convert_html_to_text(html, keep_linebreaks=False):
    """
    Convert html encoded in utf-8 to text using BeautifulSoup by cleaning it up
    and replacing <br> tags with \n or whitespace.
    """
    if html is None:
        return ''

    soup = BeautifulSoup(html)

    # Remove doctype and html comments to prevent these from being included in
    # the plain text version
    html_comments = soup.findAll(text=lambda text: isinstance(text, (Comment, Doctype)))
    for html_comment in html_comments:
        html_comment.extract()

    # Remove these tags
    tags = [
        'audio',
        'head',
        'img',
        'object',
        'script',
        'style',
        'video'
    ]
    extract_tags_from_soup(soup, tags)

    # Replace html breaks with newline or spaces
    convert_br_to_newline(soup, '\n' if keep_linebreaks else ' ')

    # Return text version of body without keeping whitespace
    body = soup.body if soup.body else soup
    return body.get_text(separator=' ', strip=True)


def parse_search_keys(search_string):
    TOKENS_START = ['from', 'to', 'cc', 'bcc', 'subject', 'has']
    TOKEN_END = ','
    TOKEN_VALUE_START = ':'

    def get_next_token(search_string, begin_index):
        token = None
        token_value = None

        # Find token start index
        token_start_index = next_begin_index = begin_index
        first_token_start_index = len(search_string)
        for TOKEN_START in TOKENS_START:
            try:
                temp_token_start_index = search_string.index(TOKEN_START, begin_index)
            except ValueError:
                continue
            else:
                if temp_token_start_index <= first_token_start_index:
                    token_start_index = first_token_start_index = temp_token_start_index
                    token = TOKEN_START
            next_begin_index = token_start_index

        # Search for TOKEN_END preceding first_token_start_index
        try:
            token_end_index = search_string.index(TOKEN_END, begin_index, token_start_index)
        except ValueError:
            pass
        else:
            # Replace token with whatever comes next as return value
            token = None
            next_begin_index = first_token_start_index
            token_value = search_string[token_end_index:token_start_index].strip(' %s' % TOKEN_END)

        # Find token value
        if token is not None:
            # Assume start for token_value is after TOKEN_VALUE_START
            token_value_start_index = search_string.index(TOKEN_VALUE_START, token_start_index) + len(TOKEN_VALUE_START)
            # Find end of token_value by TOKEN_END or end of string
            try:
                token_value_end_index = search_string.index(TOKEN_END, token_value_start_index - 1)
            except ValueError:
                token_value_end_index = len(search_string)

            # Get token_value
            token_value = search_string[token_value_start_index:token_value_end_index]

            # Set next starting index after token_value
            next_begin_index = token_value_end_index
        elif token_value is None:
            # If no token was provided
            token_value = search_string[token_start_index:].strip(' %s' % TOKEN_END)
            next_begin_index = len(search_string)

        return token, token_value, next_begin_index

    criteria = []
    begin_index = 0
    token = not None
    while begin_index < len(search_string):
        token, token_value, begin_index = get_next_token(search_string, begin_index)

        # If valid token add to criteria 'as is'
        if token is not None and token_value is not None:
            criteria.append(u'%s %s' % (token.upper(), token_value))
        elif token_value is not None:
            # Add token_value as full-text
            criteria.append(u'TEXT "%s"' % token_value)

    if not any(criteria):
        criteria = 'TEXT "%s"' % search_string

    return criteria


def get_extensions_for_type(general_type):
    if not mimetypes.inited:
        mimetypes.init()

    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext] == general_type or mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext
