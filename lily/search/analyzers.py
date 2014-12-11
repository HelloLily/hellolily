def get_analyzers():
    '''
    The custom analyzers for our model mappings.
    '''
    analyzers = {
        'analysis': {
            'analyzer': {
                'letter_ngram_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'letter',
                    'filter': ['lowercase', 'my_ascii', 'my_ngram_filter'],
                },
                'letter_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'letter',
                    'filter': ['lowercase', 'my_ascii'],
                },
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
            }
        }
    }
    return analyzers
