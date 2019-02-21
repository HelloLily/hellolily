from django_elasticsearch_dsl import TextField

from lily.search import analyzers


class EmailAddressField(TextField):
    """
    Elasticsearch field type for email addresses.
    """
    def __init__(self, **kwargs):
        # Default field definition.
        settings = {
            'analyzer': analyzers.email_main_analyzer(),
            'fields': {
                'ngram': TextField(analyzer=analyzers.email_ngram_analyzer()),
            },
        }

        # Override the defaults with the custom kwargs.
        settings.update(kwargs)

        super(EmailAddressField, self).__init__(**settings)


class CharField(TextField):
    """
    Elasticsearch field type for generic short strings (names, titles, etc.).
    """
    def __init__(self, **kwargs):
        settings = {
            'analyzer': analyzers.standard_ascii_analyzer(),
            'fields': {
                'ngram': TextField(analyzer=analyzers.bigram_analyzer()),
            },
        }

        settings.update(kwargs)

        super(CharField, self).__init__(**settings)


class PhoneNumberField(TextField):
    """
    Elasticsearch field type for phone numbers.
    """
    def __init__(self, **kwargs):
        settings = {'analyzer': analyzers.phone_number_analyzer()}
        settings.update(kwargs)

        super(PhoneNumberField, self).__init__(**settings)


class URLField(TextField):
    """
    Elasticsearch field for URLs.
    """
    def __init__(self, **kwargs):
        settings = {
            'analyzer': analyzers.url_main_analyzer(),
            'fields': {
                'ngram': TextField(analyzer=analyzers.url_ngram_analyzer()),
            },
        }

        settings.update(kwargs)

        super(URLField, self).__init__(**settings)
