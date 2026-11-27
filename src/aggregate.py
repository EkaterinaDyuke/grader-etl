"""Агрегаты по дням из таблицы grader_attempts."""

DAILY_QUERY = """
select
    created_at::date as day,
    count(*) as attempts,
    count(*) filter (where attempt_type = 'submit') as submits,
    count(*) filter (where is_correct) as success,
    count(distinct user_id) as users
from grader_attempts
group by 1
order by 1
"""


def daily_stats(db):
    """Считает агрегаты по дням. Возвращает список строк для таблицы."""
    result = []
    for row in db.select(DAILY_QUERY):
        attempts = row["attempts"]
        submits = row["submits"]
        success = row["success"]
        share = round(success / submits * 100, 1) if submits else 0.0
        result.append([row["day"].isoformat(), attempts, submits, success, share, row["users"]])
    return result