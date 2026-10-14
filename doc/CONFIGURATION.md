# Конфигурация (config.yaml)

Файл `config.yaml` используется для настройки работы системы. Он должен находиться в корне проекта.

## Структура файла

Файл должен соответствовать следующей структуре:

### 1. Telegram (`telegram`)
Настройки для подключения к Telegram API.
- `api_id`: Ваш API ID (число или строка).
- `api_hash`: Ваш API Hash (строка).
- `app_title`: (Опционально) Название приложения.
- `app_short_name`: (Опционально) Короткое название приложения.
- `session_name`: (Опционально) Имя файла сессии. По умолчанию `session`.

### 2. Прокси (`proxy`) - *Опционально*
Настройки прокси для подключения.
- `type`: Тип прокси: `socks5`, `http`, или `mtproto`.
- `server`: Адрес сервера.
- `port`: Порт сервера.
- `secret`: (Опционально) Секрет для `mtproto`.
- `username`: (Опционально) Имя пользователя.
- `password`: (Опционально) Пароль.

### 3. Управление папками (`folder_manager`)
Настройки автоматической сортировки.
- `export_enabled`: Включить экспорт структуры в YAML (`true`/`false`).
- `export_filename`: Имя файла для экспорта. По умолчанию `folders_export.yaml`.
- `dry_run`: Режим тестирования без внесения изменений в Telegram (`true`/`false`).
- `warn_on_duplicates`: Выводить предупреждение, если чат попал в несколько папок.
- `unmatched_strategy`: Что делать с чатами, не попавшими ни в одну папку (`ignore` - игнорировать, или другие стратегии).
- `folders`: Словарь папок. Ключ — имя папки, значение — настройки папки:
    - `include_patterns`: Список шаблонов (regex или подстроки) для включения чатов.
    - `exclude_patterns`: Список шаблонов для исключения чатов.

### 4. Суммаризация (`summarizer`) - *Опционально*
Настройки для работы с LLM.
- `model`: Название модели (например, `gpt-4`, `llama3`, или название модели в LM Studio).
- `temperature`: Температура (0.0 - 1.0).
- `max_tokens`: Максимальное количество токенов в ответе.
- `timeout_seconds`: Таймаут запроса.
- `base_url`: URL для API (например, для LM Studio: `http://localhost:1234/v1`).
- `auth_type`: Тип авторизации (`credentials` - по API ключу, или другие).
- `gigachat_client_id`: (Для GigaChat) Client ID.
- `gigachat_secret`: (Для GigaChat) Secret.
- `gigachat_token`: (Для GigaChat) Token.
- `system_prompt`: Инструкция для модели.
- `user_prompt_template`: Шаблон промпта для пользователя.

## Пример config.yaml

```yaml
telegram:
  api_id: 123456
  api_hash: "abcdef1234567890abcdef1234567890"
  session_name: "my_session"

# proxy:
#   type: "socks5"
#   server: "127.0.0.1"
#   port: 9050

folder_manager:
  export_enabled: true
  dry_run: true
  warn_on_duplicates: true
  folders:
    "Новости":
      include_patterns:
        - ".*news.*"
        - ".*новости.*"
      exclude_patterns:
        - ".*spam.*"
    "Крипта":
      include_patterns:
        - "crypto"
        - "биткоин"

summarizer:
  model: "local-model"
  base_url: "http://localhost:1234/v1"
  gigachat_client_id: "your_id"
  gigachat_secret: "your_secret"
```
