"""Скачивание данных грейдера из API окнами по времени."""

import logging
from datetime import datetime, timedelta

import requests

import config

log = logging.getLogger(__name__)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def iter_windows(start, end, window_days):
    """Отдает пары (начало, конец) окнами по window_days суток."""
    current = datetime.strptime(start, TIME_FORMAT)
    finish = datetime.strptime(end, TIME_FORMAT)
    step = timedelta(days=window_days)

    while current < finish:
        window_end = min(current + step, finish)
        yield current, window_end
        current = window_end


def fetch_window(window_start, window_end):
    """Скачивает одно окно и возвращает список записей."""
    params = {
        "client": config.API_CLIENT,
        "client_key": config.API_CLIENT_KEY,
        "start": window_start.strftime(TIME_FORMAT),
        "end": window_end.strftime(TIME_FORMAT),
    }
    response = requests.get(config.API_URL, params=params, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(f"API вернул {response.status_code}: {response.text[:200]}")

    return response.json()


def fetch_all(start=config.PERIOD_START, end=config.PERIOD_END, window_days=config.WINDOW_DAYS):
    """Скачивает период окнами; ошибки отдельных окон логирует и продолжает."""
    for window_start, window_end in iter_windows(start, end, window_days):
        log.info("скачивание началось: %s — %s", window_start, window_end)
        started = datetime.now()
        try:
            records = fetch_window(window_start, window_end)
        except (requests.RequestException, RuntimeError) as error:
            log.error("скачивание не удалось: %s — %s: %s", window_start, window_end, error)
            continue
        elapsed = (datetime.now() - started).total_seconds()
        log.info(
            "скачивание завершилось: %s — %s, записей %d, %.1f с",
            window_start, window_end, len(records), elapsed,
        )
        yield records