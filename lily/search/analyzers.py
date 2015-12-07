def get_analyzers():
    '''
    The custom analyzers for our model mappings.
    '''
    analyzers = {
        'analysis': {
            'analyzer': {
                # The analyzer to be used for the most important fields.
                # Ngram filter allows for searching in the middle of tokens.
                'normal_ngram_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'whitespace',
                    'filter': ['lowercase', 'my_ascii', 'my_ngram_filter'],
                },
                # Use this for fields that are of normal importance.
                # Edge gram filter allows for "starts with" searches.
                'normal_edge_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'whitespace',
                    'filter': ['lowercase', 'my_ascii', 'my_edge_filter'],
                },
                # For fields that have large amount of text.
                # It basically chops tokens on whitespaces.
                'normal_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'whitespace',
                    'filter': ['lowercase', 'my_ascii'],
                },
                # Email addresses will be tokenized on '@' and '.'.
                # And will also use edge gram.
                'email_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'email_tokenizer',
                    'filter': ['lowercase', 'my_ascii'],
                },
                # Websites will be tokenized on component hierarchy, i.e.
                # www.example.org will hit on the following search terms:
                # 'org', 'example.org' and 'www.example.org'
                'domain_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'domain_tokenizer',
                    'filter': ['lowercase', 'my_ascii'],
                },
                # The analyzer used for searching across all fields.
                # It is a union of the indexing tokenizers.
                'cross_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'cross_tokenizer',
                    'filter': ['lowercase', 'my_ascii'],
                }
            },
            'filter': {
                'my_ascii': {
                    'type': 'asciifolding',
                    'preserve_original': False,
                },
                'my_ngram_filter': {
                    'type': 'nGram',
                    'min_gram': 1,
                    'max_gram': 50,
                },
                'my_edge_filter': {
                    'type': 'edgeNGram',
                    'min_gram': 1,
                    'max_gram': 50,
                },
            },
            'tokenizer': {
                'email_tokenizer': {
                    'type': 'pattern',
                    'pattern': '@|\\.',
                },
                'domain_tokenizer': {
                    'type': 'path_hierarchy',
                    'delimiter': '.',
                    'reverse': True,
                },
                'cross_tokenizer': {
                    'type': 'pattern',
                    'pattern': '@|\\.|\\s',
                },
            },
        }
    }
    return analyzers
