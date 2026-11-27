"""Загрузка проверенных записей в таблицу grader_attempts."""

import logging

from psycopg2.extras import execute_values

from transform import convert

log = logging.getLogger(__name__)

COLUMNS = (
    "user_id",
    "oauth_consumer_key",
    "lis_result_sourcedid",
    "lis_outcome_service_url",
    "is_correct",
    "attempt_type",
    "created_at",
)

INSERT = (
    f"insert into grader_attempts ({', '.join(COLUMNS)}) values %s "
    "on conflict on constraint grader_attempts_unique_attempt do nothing"
)

BATCH_SIZE = 10000


def insert_batch(db, batch):
    """Вставляет пачку одним запросом. Возвращает, сколько строк реально добавилось."""
    execute_values(db.cursor, INSERT, batch, page_size=len(batch))
    db.connection.commit()
    return db.cursor.rowcount


def load_records(db, rows, batch_size=BATCH_SIZE):
    """Проверяет записи и вставляет их пачками.

    Возвращает счетчики: inserted, duplicates, invalid.
    """
    inserted = 0
    duplicates = 0
    invalid = 0
    batch = []

    for row in rows:
        record, error = convert(row)
        if error:
            invalid += 1
            log.warning("запись пропущена: %s", error)
            continue

        batch.append(tuple(record[column] for column in COLUMNS))

        if len(batch) >= batch_size:
            added = insert_batch(db, batch)
            inserted += added
            duplicates += len(batch) - added
            batch = []

    if batch:
        added = insert_batch(db, batch)
        inserted += added
        duplicates += len(batch) - added

    return {"inserted": inserted, "duplicates": duplicates, "invalid": invalid}