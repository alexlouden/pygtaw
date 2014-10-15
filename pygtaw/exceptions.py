class UnsupportedLanguageError(ValueError):
    pass


class TranslationError(ValueError):

    def __init__(self, response):
        error = response.get('error', {})
        self.code = error.get('code')
        self.errors = error.get('errors')
        self.message = error.get('message')

        super(TranslationError, self).__init__(response)
