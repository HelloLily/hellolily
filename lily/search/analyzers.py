def get_analyzers():
    '''
    The custom analyzers for our model mappings.
    '''
    analyzers = {
        'analysis': {
            'analyzer': {
                'name_index_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'whitespace',
                    'filter': ['lowercase', 'my_ascii', 'my_ngram_filter'],
                },
                'name_search_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'whitespace',
                    'filter': ['lowercase', 'my_ascii'],
                },
            },
            'filter': {
                'my_ascii': {
                    'type': 'asciifolding',
                    'preserve_original': False},
                'my_ngram_filter': {
                    'type': 'nGram',
                    'min_gram': 1,
                    'max_gram': 10
                },
            }
        }
    }
    return analyzers
