"""Настройки проекта: все, что читается из .env, собрано в одном месте."""

import os

from dotenv import load_dotenv

load_dotenv()

# --- период выгрузки -------------------------------------------------------
# Начало: по фактическим данным — первые записи появляются между 1 и 15 октября 2022.
PERIOD_START = "2022-10-01 00:00:00"

# Конец: 01.06.2026 - дата, до которой данные считаются актуальными.
# Фактически сервер отдает данные и позже (проверено: 02.06, 15.06, 01.07, 01.08,
# 15.08 и 01.09.2026), но мы ограничиваемся датой из условия.
PERIOD_END = "2026-06-01 00:00:00"

# Сколько суток скачиваем одним запросом.
WINDOW_DAYS = 14


def require_env(name):
    """Читает переменную окружения, а если ее нет - падает с понятным текстом."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Не задана переменная {name} — проверьте файл .env")
    return value


API_URL = require_env("API_URL")
API_CLIENT = require_env("API_CLIENT")
API_CLIENT_KEY = require_env("API_CLIENT_KEY")

DB_CONFIG = {
    "host": require_env("DB_HOST"),
    "port": int(require_env("DB_PORT")),
    "database": require_env("DB_NAME"),
    "user": require_env("DB_USER"),
    "password": require_env("DB_PASSWORD"),
}

# Google Sheets: необязательная часть, без настроек выгрузка в таблицу пропускается
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
SHEET_ID = os.getenv("SHEET_ID")