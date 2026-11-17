[**Русский**](README.md) | [English](README-en.md)

# Telegram Folder Manager

Автоматизация управления папками в Telegram. Скрипт позволяет автоматически сортировать чаты и каналы на основе шаблонов, а также создавать краткие резюме (summary) диалогов с помощью LLM (LM Studio, GigaChat).

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Возможности

- 📂 **Управление папками**: Автоматическая сортировка чатов по паттернам (regex или подстрока) с поддержкой исключений.
- 🛡 **Безопасность**: Режим `dry-run` для предварительного просмотра изменений без их применения в Telegram.
- 📝 **Суммаризация**: Интеграция с LLM для создания резюме чатов за определенный период.
- 📊 **Экспорт**: Возможность экспорта структуры папок в YAML файл.
- 🔍 **Валидация**: Строгая проверка конфигурации с использованием Pydantic.

## Быстрый старт

### Требования

- Python 3.12+
- Аккаунт Telegram (API ID и API Hash с [my.telegram.org](https://my.telegram.org))

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/sky1su/tg_folder_manager.git
cd tg_folder_manager

# Создать и активировать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Для Windows: .venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### Запуск

Для запуска основного модуля используйте:

```bash
# Запуск с использованием вашей конфигурации
python tg_tool.py
```

## Конфигурация

Настройки хранятся в файле `config.yaml`.

| Секция | Обязательна | Описание | Пример |
|---|---:|---|---|
| `telegram` | Да | Настройки API (ID, Hash, session) | `api_id: 123456` |
| `folder_manager` | Да | Правила сортировки, шаблоны, режим dry_run | `dry_run: true` |
| `summarizer` | Нет | Настройки LLM (model, base_url, prompts) | `model: "gemma-4"` |

> [!IMPORTANT]
> Никогда не добавляйте в репозиторий реальные `api_id`, `api_hash` или токены. Используйте `config.yaml.example` в качестве основы.

## Использование

### Управление папками
Скрипт автоматически анализирует ваши чаты и распределяет их по папкам согласно правилам из `config.yaml`.

### Суммаризация
Модуль `tg_summarise_chat` собирает сообщения и отправляет их на обработку LLM для создания краткого отчета.

## Архитектура

Система построена по принципу многослойной модульной архитектуры (Layered Modular Architecture) с разделением ответственности (SoC):

```text
[ CLI / User ] -> [ tg_tool.py ] -> [ Infrastructure (core/) ]
                                          |
                                          -> [ Business Logic (modules/) ]
                                                 |
                                                 -> [ Telegram / LLM / Filesystem ]
```

Подробное описание архитектуры доступно в [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md).

## Тестирование

```bash
# Запуск тестов (если настроено)
pytest
```

## Разработка

Проект следует правилам модульности: бизнес-логика в модулях `tg_folder_manager` и `tg_summarise_chat` должна быть полностью независима от инфраструктурного слоя `core`.

## Вклад в проект

Смотрите [CONTRIBUTING.md](CONTRIBUTING.md).  
Перед созданием PR: убедитесь, что вы обновили конфигурационные файлы и документацию, если меняли поведение системы.

## Безопасность

Уязвимости не публикуйте в Issues. Порядок сообщения: [SECURITY.md](SECURITY.md).

## Лицензия

Проект распространяется по лицензии [MIT](LICENSE).

## Контакты

- Maintainer: [sky1su](https://github.com/sky1su)
- Issues: [https://github.com/sky1su/tg_folder_manager/issues](https://github.com/sky1su/tg_folder_manager/issues)
