from pathlib import Path

import yaml

from data.schemas.translations import Translations
from data.schemas.user import LanguageEnum
from core import localizator


def load_locales(locales_directory: Path) -> dict[LanguageEnum, Translations]:
    result = {}

    for language_config_file in locales_directory.glob('*.yaml'):
        with language_config_file.open(encoding="utf-8") as file:
            data = yaml.unsafe_load(file)
            result[language_config_file.stem] = Translations(**data)

    return result


def setup_localizator(locales_directory: Path) -> None:
    translations = load_locales(locales_directory)
    localizator.localizator = localizator.Localizator(translations)


if __name__ == '__main__':
    pass
    # translations = load_locales(LOCALES_DIRECTORY)
    # print(translations)
    # localizator_ = Localizator(translations)
    # print(localizator_)
    #
    # print('en', localizator_.lang('en'))
    # print('sp', localizator_.lang('sp'))
