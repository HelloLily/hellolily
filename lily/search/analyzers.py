from elasticsearch_dsl import tokenizer, analyzer, token_filter


def email_main_analyzer():
    """
    An analyzer for creating "words" from email addresses.

    This analyzer splits email addresses on special characters. For example,
    john.doe+crm@example.com would become [john, doe, crm, example, com].
    These tokens, when combined with ngrams, provide nice fuzzy matching while
    boosting full word matches.

    Returns:
        Analyzer: An analyzer suitable for analyzing email addresses.
    """
    return analyzer(
        'email',
        # We tokenize with token filters, so use the no-op keyword tokenizer.
        tokenizer='keyword',
        filter=[
            'lowercase',
            # Split the email address on special characters.
            token_filter(
                'email_word_delimiter',
                type='word_delimiter',
                # Ensure words like hello2lily are kept as one token or not.
                split_on_numerics=False,
            ),
        ],
    )


def email_ngram_analyzer():
    """
    An analyzer for creating email safe ngrams.

    This analyzer first splits the local part and domain name, then creates
    n-grams (overlapping fragments) from the remaining strings, minus any
    special characters.

    Returns:
        Analyzer: An analyzer suitable for analyzing email addresses.
    """
    return analyzer(
        'email_ngram',
        # Split the email address at the @ sign.
        tokenizer=tokenizer(
            'at_sign_tokenizer',
            type='pattern',
            pattern='@',
        ),
        filter=[
            'lowercase',
            # Strip any special characters from the email address.
            token_filter(
                'email_ngram_word_delimiter',
                type='word_delimiter',
                split_on_numerics=False,
                catenate_all=True,
            ),
            # Create trigrams from the address.
            token_filter(
                'email_ngram_filter',
                type='ngram',
                min_gram=3,
                max_gram=3,
            ),
        ],
    )


def url_main_analyzer():
    """
    An analyzer for creating "words" from URLs.

    Returns:
        Analyzer
    """
    return analyzer(
        'url',
        tokenizer='keyword',
        filter=[
            'lowercase',
            # Strip the protocol, we don't need it for searching.
            token_filter(
                'url_protocol_filter',
                type='pattern_replace',
                pattern='^\w+:\/\/',
                replace='',
            ),
            'word_delimiter',
        ],
    )


def url_ngram_analyzer():
    """
    An analyzer for creating URL safe n-grams.

    Returns:
        Analyzer
    """
    return analyzer(
        'url_ngram',
        tokenizer='keyword',
        filter=[
            'lowercase',
            # Strip the protocol, we don't need it for searching.
            token_filter(
                'url_protocol_filter',
                type='pattern_replace',
                pattern='^\w+:\/\/',
                replace='',
            ),
            'word_delimiter',
            # Create trigrams from the address.
            token_filter(
                'url_ngram_filter',
                type='ngram',
                min_gram=3,
                max_gram=3,
            ),
        ],
    )


def phone_number_analyzer():
    """
    An analyzer to do complex partial matching on phone numbers.

    Returns:
        Analyzer: An analyzer suitable for searching phone numbers.
    """
    return analyzer(
        'phone_number',
        # We only want n-grams, which we want to create as late as possible.
        tokenizer='keyword',
        filter=[
            # Strip all special chars, don't tokenize.
            token_filter(
                'phone_word_delimiter',
                type='word_delimiter',
                generate_word_parts=False,
                generate_number_parts=False,
                catenate_all=True,
            ),
            # Strip any zeros from the start of the number.
            token_filter(
                'leading_zero_filter',
                type='pattern_replace',
                pattern='^(0+)',
                replace='',
            ),
            # Create n-grams of all lengths to support partial matching.
            token_filter(
                'phone_ngram_filter',
                type='ngram',
                # Still undecided on whether this should be 3 or 4.
                # 3 means users have to type less numbers to get results,
                # but the matching is less accurate.
                min_gram=3,
                max_gram=32,
            ),
        ],
    )


def bigram_analyzer():
    """
    A n-gram analyzer of length 2.

    Bigrams provide nice partial, fuzzy matching.

    Returns:
        Analyzer
    """
    return analyzer(
        'bigram',
        tokenizer=tokenizer(
            'bigram_tokenizer',
            type='ngram',
            min_gram=2,
            max_gram=2,
            token_chars=['letter', 'digit'],
        ),
        filter=[
            'standard',
            'lowercase',
            'asciifolding',
        ],
    )


def standard_ascii_analyzer():
    """
    Elasticsearch's standard analyzer with asciifolding.

    The asciifolding filter converts non-ascii letters to their ascii
    counterparts. It essentially cleans diacritics from strings.

    Returns:
        Analyzer
    """
    return analyzer(
        'standard_ascii',
        tokenizer='standard',
        filter=[
            'standard',
            'lowercase',
            'asciifolding',
        ]
    )
