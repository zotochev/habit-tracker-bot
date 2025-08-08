import logging

from aiogram.enums import ContentType

from .icontext_type_handable import IContextTypeHandable


logger = logging.getLogger(__name__)


class ITextHandable(IContextTypeHandable):
    def is_handable(self, context_type) -> bool:
        return context_type == ContentType.TEXT
