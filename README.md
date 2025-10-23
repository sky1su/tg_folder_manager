# Telegram Folder Manager

Автоматизация управления папками (folders) Telegram. Скрипт позволяет автоматически сортировать чаты и каналы по папкам, основываясь на шаблонах и исключениях, а также экспортировать структуру папок в YAML файл.

---

## Возможности

- ✅ Автоматическая сортировка чатов по папкам на основе паттернов
- ✅ Поддержка исключающих шаблонов для точного контроля
- ✅ Определение **основной** папки — один чат только в одной папке
- ✅ Автоматическое удаление из других папок при перемещении
- ✅ **Экспорт структуры папок и списка групп в YAML файл**
- ✅ **Подсчёт и отображение количества групп в каждой папке**
- ✅ Гибкие стратегии обработки несопоставленных чатов
- ✅ Обнаружение дубликатов (чатов в нескольких папках)
- ✅ Поддержка регулярных выражений и простых подстрок
- ✅ Работа как модуль Python

---

## Требования

- Python 3.12+
- Аккаунт Telegram
- API ID и API Hash из https://my.telegram.org

---

## Установка

1. **Клонировать репозиторий:**

```

git clone https://github.com/sky1su/tg_folder_manager.git
cd tg_folder_manager

```

2. **Установить зависимости:**

```

pip install telethon python-dotenv PyYAML

```

Или с `requirements.txt`:

```

pip install -r requirements.txt

```

3. **Создать файл `.env` в корне проекта:**

```

app_api_id=ВАШ_API_ID
app_api_hash=ВАШ_API_HASH
app_title=telegram_session

```

---

## Регистрация клиента Telegram

### Получение API ID и API Hash

1. Откройте браузер и перейдите по ссылке  
[https://my.telegram.org](https://my.telegram.org)

2. Войдите с помощью своего номера телефона  
- Введите номер телефона  
- Подтвердите вход кодом из Telegram

3. Перейдите в раздел **API Development Tools**

4. Создайте новое приложение:
- **App title:** любое имя, например `TG Folder Manager`
- **Short name:** короткое уникальное имя, например `tgfolder`
- Остальные поля можно заполнить произвольно

5. Скопируйте выданные значения:
- **API ID**
- **API Hash**

6. Добавьте их в файл `.env` вашего проекта

> ⚠️ **Важно:** Эти ключи дают полный доступ к вашему аккаунту. Никогда не публикуйте их в открытом доступе!

---

## Конфигурирование

Создайте файл `config.yaml` в корне проекта:

```yaml


# Настройки экспорта

settings:
    export_enabled: true                    \# включить/выключить экспорт папок в YAML
    export_filename: folders_export.yaml    \# имя файла для экспорта

# Определение папок

folders:
    Работа:
        include_patterns:
            - work
            - проект
            - работа
        exclude_patterns:
            - тест
            - demo
    
    Крипто:
        include_patterns:
            - bitcoin
            - ethereum
            - крипто
        exclude_patterns:
            - testnet
            - тест
    
    Dev:
        include_patterns:
            - python
            - django
            - fastapi
        exclude_patterns:
            - старое
            - архив

```

### Параметры конфигурации

#### Секция `settings`
- **export_enabled** (boolean): включить/выключить экспорт структуры папок
- **export_filename** (string): имя файла для экспорта (по умолчанию `folders_export.yaml`)

#### Секция `folders`
Для каждой папки:
- **include_patterns**: список паттернов (regex или подстроки) для включения чата в папку
- **exclude_patterns**: список паттернов исключений — если чат совпадает, он НЕ попадёт в эту папку

---

## Использование

### Запуск как модуль

```

python3 -m tg_folder_manage

```

### Первый запуск

При первом запуске Telethon запросит:
1. Номер телефона
2. Код подтверждения из Telegram
3. Двухфакторный пароль (если включен)

После этого создаётся файл сессии, и повторный ввод не потребуется.

---

## Экспорт структуры папок

При включении экспорта (`export_enabled: true`) после обработки папок автоматически создаётся YAML файл с текущей структурой папок.

### Пример экспортированного файла:

```

export_date: '2025-10-23T14:37:00.123456'
folders:
Работа:
folder_id: 2
chats_count: 5
chats:
- id: 123456789
title: Работа Project Alpha
type: megagroup
- id: 987654321
title: Команда разработки
type: group

Крипто:
folder_id: 3
chats_count: 12
chats:
- id: 111222333
title: Bitcoin Обсуждения
type: megagroup
- id: 444555666
title: Ethereum Новости
type: channel

```

### Типы чатов в экспорте:
- `group` — обычная группа
- `megagroup` — супергруппа
- `channel` — канал

---

## Работа с паттернами

### Простые подстроки
```

include_patterns:

- python
- django

```

### Регулярные выражения
```

include_patterns:

- ^work.*project\$  \# Начинается с "work" и заканчивается на "project"
- \d{4}            \# Содержит 4 цифры подряд

```

### Экранирование спецсимволов

Если нужно искать точку или другой спецсимвол regex, используйте обратный слэш:

```

include_patterns:

- д\.р\.           \# Ищет именно "д.р.", а не "д" + любой символ + "р"

```

Без экранирования `д.р.` совпадёт с "лидер", "дар" и т.д.

### Исключения
```

exclude_patterns:

- test
- demo
- архив

```

---

## Стратегии обработки несопоставленных чатов

В коде можно настроить поведение для чатов, которые не подошли ни под один паттерн:

```

UnmatchedChatsStrategy.IGNORE            \# Игнорировать (по умолчанию)
UnmatchedChatsStrategy.MOVE_TO_FOLDER    \# Переместить в папку "Прочие"
UnmatchedChatsStrategy.LOG_ONLY          \# Только вывести в лог
UnmatchedChatsStrategy.REMOVE_FROM_FOLDERS \# Удалить из всех папок

```

Настройка в `__main__.py`:

```

async with TelegramFolderManager(
unmatched_strategy=UnmatchedChatsStrategy.MOVE_TO_FOLDER,
warn_on_duplicates=True
) as manager:
await manager.organize_chats_by_config(config_path=config_path)

```

---

## Структура проекта

```

tg_folder_manager/
├── tg_folder_manage/
│   ├── __init__.py
│   ├── __main__.py
│   └── tg_folder_manager.py
├── config.yaml
├── .env
├── requirements.txt
├── README.md
└── folders_export.yaml          \# создаётся автоматически при экспорте

```

---

## Логирование

Скрипт выводит подробные логи с эмодзи для наглядности:

- ✔ Подключение/отключение
- ✚ Создание папок
- ✎ Обновление папок
- − Удаление чатов
- ⚠ Обнаружение дубликатов
- 📊 Статистика папок
- 📤 Экспорт данных

### Пример вывода:

```

2025-10-23 14:37:00 - INFO - ✔ Connected to Telegram
2025-10-23 14:37:01 - INFO - 📊 Статистика папок ПЕРЕД обработкой:
2025-10-23 14:37:01 - INFO -    📁 Работа: 5 групп/каналов
2025-10-23 14:37:01 - INFO -    📁 Крипто: 12 групп/каналов
2025-10-23 14:37:01 - INFO -    📁 Dev: 8 групп/каналов
2025-10-23 14:37:02 - INFO - ✎ Updated folder "Работа" (7 chats)
2025-10-23 14:37:03 - INFO - − Removed 2 chat(s) from "Dev" after moving to "Работа"
2025-10-23 14:37:04 - INFO - 📊 Статистика папок ПОСЛЕ обработки:
2025-10-23 14:37:04 - INFO -    📁 Работа: 7 групп/каналов
2025-10-23 14:37:04 - INFO -    📁 Крипто: 12 групп/каналов
2025-10-23 14:37:04 - INFO -    📁 Dev: 6 групп/каналов
2025-10-23 14:37:05 - INFO - 📤 Экспортировано 3 папок в файл "folders_export.yaml"
2025-10-23 14:37:06 - INFO - ✔ Disconnected from Telegram

```

---

## Устранение неполадок

### Ошибка "API credentials not set"
Убедитесь, что файл `.env` создан и содержит корректные значения `app_api_id` и `app_api_hash`.

### Ошибка "FileNotFoundError: config.yaml"
Файл `config.yaml` должен находиться в корне проекта (на том же уровне, что и папка `tg_folder_manage`).

### Логи не отображаются
Убедитесь, что в `__main__.py` настроен `logging.basicConfig()` перед запуском `asyncio.run()`.

### Чаты не перемещаются
1. Проверьте правильность паттернов в `config.yaml`
2. Убедитесь, что названия чатов совпадают (регистр не учитывается)
3. Проверьте `exclude_patterns` — возможно, чат исключается

### Паттерн с точкой работает неправильно
Если паттерн `д.р.` совпадает с "лидер", экранируйте точки: `д\.р\.`

### Экспорт не создаётся
Проверьте, что в `config.yaml` установлено `export_enabled: true`

---

## Безопасность

- ⚠️ Никогда не публикуйте файл `.env` с API ключами
- ⚠️ Добавьте `.env` и `*.session` в `.gitignore`
- ⚠️ API ключи дают полный доступ к вашему аккаунту Telegram
- ⚠️ Файл экспорта может содержать конфиденциальную информацию о ваших чатах

### Пример .gitignore:

```

.env
*.session
*.session-journal
folders_export.yaml
__pycache__/
*.pyc
.DS_Store

```

---

## Лицензия

MIT License

---

## Поддержка

Если у вас возникли вопросы или проблемы, создайте Issue в репозитории проекта.

---

Разработано с использованием [Telethon](https://github.com/LonamiWebs/Telethon), [python-dotenv](https://github.com/theskumar/python-dotenv) и [PyYAML](https://github.com/yaml/pyyaml)