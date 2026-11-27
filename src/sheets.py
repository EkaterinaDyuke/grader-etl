"""Выгрузка агрегатов в Google Sheets."""

import logging
import gspread
import config

log = logging.getLogger(__name__)

HEADER = ["День", "Попыток", "Отправок", "Успешных", "Доля успешных, %", "Студентов"]


def is_configured():
    """Проверяет, что ключ и идентификатор таблицы заданы."""
    return bool(config.GOOGLE_CREDENTIALS and config.SHEET_ID)


def upload(rows):
    """Перезаписывает первый лист: заголовок и строки. Возвращает True при успехе."""
    if not is_configured():
        log.warning("Google Sheets не настроен — выгрузка в таблицу пропущена")
        return False

    try:
        client = gspread.service_account(filename=config.GOOGLE_CREDENTIALS)
        worksheet = client.open_by_key(config.SHEET_ID).sheet1
        worksheet.clear()
        worksheet.update([HEADER] + rows, "A1")
        worksheet.format("A1:F1", {"textFormat": {"bold": True}})
    except (gspread.GSpreadException, OSError) as error:
        log.error("не удалось записать в таблицу: %s", error)
        return False

    log.info("в таблицу записано строк: %d", len(rows))
    return True