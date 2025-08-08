import logging
from .istatable import IStatable


logger = logging.getLogger(__name__)


class INoneSwitchable(IStatable):
    pass
