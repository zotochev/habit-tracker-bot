import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URL = os.getenv('DB_URL')
ROOT_DIRECTORY = Path(__file__).parent
LOCALES_DIRECTORY = Path(ROOT_DIRECTORY, os.getenv('LOCALES_PATH')).resolve(strict=True)
BACKEND_URL = os.getenv('BACKEND_URL')

MAX_HABIT_NAME = 30
MAX_HABIT_DESCRIPTION = 300

MONTHS = {
    'ru': [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
    ],
    'en': [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
}
