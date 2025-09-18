import os
from datetime import datetime
from pathlib import Path

import dotenv

from core.bot_mode import BotMode

dotenv.load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URL = os.getenv('DB_URL')
ROOT_DIRECTORY = Path(__file__).parent
LOCALES_DIRECTORY = Path(ROOT_DIRECTORY, '../locales').resolve(strict=True)
BACKEND_URL = os.getenv('BACKEND_URL')

BOT_MODE = BotMode(os.getenv('BOT_MODE', BotMode.polling))

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')

WEB_SERVER_HOST = os.getenv('WEB_SERVER_HOST')
WEB_SERVER_PORT = os.getenv('WEB_SERVER_PORT')
if WEB_SERVER_PORT:
    WEB_SERVER_PORT = int(WEB_SERVER_PORT)

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
WEBHOOK_CERTIFICATE_PATH = os.getenv('WEBHOOK_CERTIFICATE_PATH')

if BOT_MODE == BotMode.webhook:
    for c in (WEBHOOK_HOST,
              WEBHOOK_PATH,
              WEB_SERVER_HOST,
              WEB_SERVER_PORT,
              ):
        assert c is not None

API_ENDPOINT_PORT=int(os.getenv('API_ENDPOINT_PORT'))

MAX_HABIT_NAME = 30
MAX_HABIT_DESCRIPTION = 300
SEED = int(datetime.now().timestamp())
