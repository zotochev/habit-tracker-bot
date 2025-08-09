from data.schemas.translations import Translations
from data.schemas.user import LanguageEnum


class Localizator:
    default_language = Translations()

    def __init__(self, translations: dict[LanguageEnum, Translations] = None):
        self.__translations = translations or {}

    def lang(self, language: LanguageEnum):
        return self.__translations.get(language, self.default_language)
