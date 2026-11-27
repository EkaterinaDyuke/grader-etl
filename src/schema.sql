-- Структура таблицы для данных грейдера.
-- Выполняется один раз: psql -U postgres -d grader_stats -f src\schema.sql

CREATE TABLE IF NOT EXISTS grader_attempts (
    id                      bigserial PRIMARY KEY,
    user_id                 text        NOT NULL,
    oauth_consumer_key      text        NOT NULL DEFAULT '',
    lis_result_sourcedid    text        NOT NULL,
    lis_outcome_service_url text,
    is_correct              boolean,
    attempt_type            text        NOT NULL,
    created_at              timestamptz NOT NULL,
    CONSTRAINT grader_attempts_attempt_type_check
        CHECK (attempt_type IN ('run', 'submit')),
    CONSTRAINT grader_attempts_unique_attempt
        UNIQUE (user_id, lis_result_sourcedid, attempt_type, created_at)
);

COMMENT ON TABLE grader_attempts IS
    'Попытки студентов в грейдере: запуски кода и отправки на проверку.';
COMMENT ON COLUMN grader_attempts.created_at IS
    'Время попытки в UTC: сервер отдаёт время в нулевом часовом поясе.';