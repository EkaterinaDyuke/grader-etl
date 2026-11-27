"""Преобразование одной записи API в строку для таблицы PostgreSQL."""

import ast
import re
from datetime import datetime, timezone

# регулярное выражение: начало строки, ровно 32 символа, конец строки
USER_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
ALLOWED_ATTEMPTS = ("run", "submit")


def parse_passback(raw):
    """Разбирает passback_params в словарь.

    Внутри строка вида repr словаря Python,
    поэтому подходит ast.literal_eval (не json.loads).
    """
    value = ast.literal_eval(raw)
    if not isinstance(value, dict):
        raise ValueError("ожидался словарь")
    return value


def convert(row):
    """Проверяет запись и приводит ее к виду таблицы.

    Возвращает (record, None) или (None, причина_ошибки).
    Вызывающий код: error - в лог, record - в базу.
    """
    user_id = row.get("lti_user_id")
    # является ли значение строкой (защита от None)
    if not isinstance(user_id, str) or not USER_ID_PATTERN.match(user_id):
        return None, "lti_user_id отсутствует или не 32 hex-символа"

    raw = row.get("passback_params")
    if not isinstance(raw, str):
        return None, "passback_params отсутствует"
    try:
        params = parse_passback(raw)
    except (ValueError, SyntaxError):
        return None, "passback_params не разбирается"

    sourcedid = params.get("lis_result_sourcedid")
    if not isinstance(sourcedid, str) or not sourcedid:
        return None, "нет lis_result_sourcedid"

    consumer_key = params.get("oauth_consumer_key", "")
    if not isinstance(consumer_key, str):
        return None, "oauth_consumer_key не строка"

    attempt_type = row.get("attempt_type")
    if attempt_type not in ALLOWED_ATTEMPTS:
        # f-строке показывает значение как в коде, нужно для сообщений об ошибках
        return None, f"неизвестный attempt_type: {attempt_type!r}"

    is_correct = row.get("is_correct")
    if attempt_type == "run":
        if is_correct is not None:
            return None, "у run не должно быть оценки"
    elif is_correct not in (0, 1):
        return None, f"у submit оценка не 0/1: {is_correct!r}"

    # если ключа нет, вернет None, а не выбросит KeyError
    created_raw = row.get("created_at")
    try:
        # разбирает строку времени как есть (с микросекундами и без)
        # время в UTC: сервер работает в нулевом часовом поясе
        created_at = datetime.fromisoformat(created_raw).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None, f"created_at не разбирается: {created_raw!r}"

    record = {
        "user_id": user_id,
        "oauth_consumer_key": consumer_key,
        "lis_result_sourcedid": sourcedid,
        "lis_outcome_service_url": params.get("lis_outcome_service_url"),
        "is_correct": None if is_correct is None else bool(is_correct),
        "attempt_type": attempt_type,
        "created_at": created_at,
    }

    return record, None