"""Точка входа: скачивает статистику грейдера и загружает ее в PostgreSQL."""

import argparse
import logging
from datetime import datetime

import aggregate
import api_client
import config
import notify
import sheets
from db import Database
from loader import load_records
from logging_setup import setup_logging

log = logging.getLogger("main")


def parse_args():
    parser = argparse.ArgumentParser(description="Выгрузка статистики грейдера в PostgreSQL")
    parser.add_argument("--start", default=config.PERIOD_START, help="начало периода")
    parser.add_argument("--end", default=config.PERIOD_END, help="конец периода")
    parser.add_argument(
        "--window-days",
        type=int,
        default=config.WINDOW_DAYS,
        help="размер окна в сутках",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    log.info("старт выгрузки: %s — %s, окно %d дн.", args.start, args.end, args.window_days)
    started = datetime.now()

    db = Database(**config.DB_CONFIG)
    totals = {"inserted": 0, "duplicates": 0, "invalid": 0}
    windows = 0

    try:
        for chunk in api_client.fetch_all(args.start, args.end, args.window_days):
            windows += 1
            stats = load_records(db, chunk)
            for key, value in stats.items():
                totals[key] += value
            log.info(
                "окно %d: вставлено %d, дублей %d, отброшено %d",
                windows,
                stats["inserted"],
                stats["duplicates"],
                stats["invalid"],
            )
        log.info("расчет агрегатов за день")
        daily_rows = aggregate.daily_stats(db)
    finally:
        db.close()
    log.info("выгрузка агрегатов в Google Sheets")
    sheets_ok = sheets.upload(daily_rows)

    elapsed = (datetime.now() - started).total_seconds()
    log.info("загрузка в базу завершилась")
    log.info(
        "итог: окон %d, вставлено %d, дублей %d, отброшено %d, время %.0f с",
        windows,
        totals["inserted"],
        totals["duplicates"],
        totals["invalid"],
        elapsed,
    )
    text = (
        "Выгрузка завершена.\n\n"
        f"Период: {args.start} – {args.end}\n"
        f"Окон: {windows}\n"
        f"Вставлено строк: {totals['inserted']}\n"
        f"Дублей: {totals['duplicates']}\n"
        f"Отброшено: {totals['invalid']}\n"
        f"Google-таблица: {'обновлена' if sheets_ok else 'не обновлена'}\n"
        f"Время: {elapsed:.0f} с"
    )
    notify.send_report("Выгрузка грейдера завершена", text)
    print(
        f"Готово. Окон: {windows}. Вставлено: {totals['inserted']}. "
        f"Дублей: {totals['duplicates']}. Отброшено: {totals['invalid']}. "
        f"Время: {elapsed:.0f} с."
    )


if __name__ == "__main__":
    main()