import requests
from langs import LANGUAGE_CODES, LANGUAGE_NAMES
from exceptions import UnsupportedLanguageError


class Client(object):

    def __init__(self, api_key):
        """
        api_key: type <str>, see https://cloud.google.com/translate
        for more information on obtaining an API key.
        Loads the client interface for Google Translate API.
        """
        self._api_key = api_key
        self._url = 'https://www.googleapis.com/language/translate/v2?'
        self._source = None

    def _build_payload(self, query, target, source):
        """
        Builds a dictionary of parameters as payload
        for the HTTP request.
        """
        payload = {
            'q': query,
            'target': target,
            'key': self._api_key
        }
        if source:
            payload['source'] = source
        return payload

    def _handle_response(self, response, source):
        """
        response: Object returned from requests, presumably
        passed from self.translate().
        Returns a Translation object.
        """
        try:
            self._response = response.json()['data']['translations'][0]
        except KeyError:
            # TODO handle missing 'data' key
            pass

        return Translation(self._response, source)

    @staticmethod
    def _validate_lang(lang):
        try:
            return LANGUAGE_CODES[lang]
        except KeyError:
            raise UnsupportedLanguageError('Google Translate does not currently support {}'.format(lang))

    def translate(self, query, target, source=None):
        """
        query: type <str>, required.
        target: type <str>, required, see README.md for info on which
        languages are supported.
        source: type <str>, optional, Google Translate API can
        detect source language.

        """
        target_lang = self._validate_lang(target)
        source_lang = self._validate_lang(source) if source else None

        query.decode(encoding='utf-8')  # Does this do anything?
        payload = self._build_payload(query, target_lang, source_lang)
        r = requests.get(self._url, params=payload)
        return self._handle_response(r, source)


class Translation(object):

    def __init__(self, response, source=None):
        """
        response: Object returned from Client's translate request.
        source: type <str>, language specified by user.
        Has detected_source_language and translated_text properties.
        """
        self._response = response
        self._source = source

    def get_source_language(self, detected_lang_code):
        return LANGUAGE_NAMES.get(detected_lang_code)

    @property
    def detected_source_language(self):
        """
        Returns the source language detected
        if the user does not provided a source language.
        """
        try:
            return self.get_source_language(self._response['detectedSourceLanguage'])
        except KeyError:
            return 'No detected source language, source provided by user: {}'.format(self._source)

    @property
    def translated_text(self):
        """Returns the translated text."""
        return self._response['translatedText']
