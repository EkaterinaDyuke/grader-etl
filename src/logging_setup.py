"""Настройка логирования: файл с именем по дате и чистка логов старше 3 дней."""

import logging
from datetime import date, datetime, timedelta
from pathlib import Path

LOG_DIR = Path("logs")
KEEP_DAYS = 3


def cleanup_old_logs(log_dir=LOG_DIR, keep_days=KEEP_DAYS):
    """Удаляет файлы вида ГГГГ-ММ-ДД.log, которые старше keep_days календарных дней."""
    today = date.today()
    oldest_kept = today - timedelta(days=keep_days - 1)
    removed = 0

    for path in log_dir.glob("*.log"):
        try:
            file_date = datetime.strptime(path.stem, "%Y-%m-%d").date()
        except ValueError:
            continue
        if file_date < oldest_kept:
            path.unlink()
            removed += 1

    return removed


def setup_logging(log_dir=LOG_DIR):
    """Включает запись лога в файл <дата>.log и в консоль."""
    log_dir.mkdir(exist_ok=True)
    removed = cleanup_old_logs(log_dir)
    log_file = log_dir / f"{date.today():%Y-%m-%d}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logging.info("Лог открыт: %s (удалено старых файлов: %d)", log_file, removed)
    return log_file