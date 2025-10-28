# tg_summarise_chat.py

import os
import sys
import argparse
import yaml
from typing import List, Dict, Optional, Union
from datetime import datetime, time, timedelta, timezone
import logging
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Message
import httpx

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_local_timezone_offset() -> timezone:
    """
    Получает смещение локальной временной зоны.

    Returns:
        timezone: Объект временной зоны
    """
    import time

    # Получаем смещение в секундах
    if time.daylight:
        # Летнее время
        offset_seconds = -time.altzone
    else:
        # Зимнее время
        offset_seconds = -time.timezone

    offset = timedelta(seconds=offset_seconds)
    return timezone(offset)


class TelegramConfig:
    """Конфигурация для подключения к Telegram API."""

    def __init__(self):
        self.api_id = os.getenv('app_api_id')
        self.api_hash = os.getenv('app_api_hash')
        self.app_title = os.getenv('app_title')
        self.app_short_name = os.getenv('app_short_name')
        self.session_name = self.app_short_name or 'session'

        self._validate()

    def _validate(self):
        """Проверяет наличие необходимых параметров."""
        if not self.api_id or not self.api_hash:
            raise ValueError(
                "Ошибка конфигурации: app_api_id и app_api_hash "
                "должны быть установлены в файле .env"
            )

        logger.info(f"✓ Конфигурация Telegram загружена ({self.app_title})")


class LMStudioConfig:
    """Конфигурация для подключения к LM Studio из config.yaml."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.base_url = None
        self.model = None
        self.temperature = None
        self.max_tokens = None
        self.timeout_seconds = None

        self._load_config()

    def _load_config(self):
        """Загружает конфигурацию из YAML файла."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Файл конфигурации '{self.config_path}' не найден"
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка при чтении YAML файла: {e}")
        except Exception as e:
            raise Exception(f"Ошибка при загрузке конфигурации: {e}")

        # Получаем секцию llm_api
        if not config or 'llm_api' not in config:
            raise ValueError(
                "Ошибка конфигурации: секция 'llm_api' не найдена в config.yaml"
            )

        llm_config = config['llm_api']

        # Читаем параметры с проверкой
        self.base_url = llm_config.get('base_url')
        self.model = llm_config.get('model')
        self.temperature = llm_config.get('temperature')
        self.max_tokens = llm_config.get('max_tokens')
        self.timeout_seconds = llm_config.get('timeout_seconds')

        if not self.base_url:
            raise ValueError(
                "Ошибка конфигурации: параметр 'base_url' не найден в config.yaml -> llm_api"
            )
        if not self.model:
            raise ValueError(
                "Ошибка конфигурации: параметр 'model' не найден в config.yaml -> llm_api"
            )

        # Конвертируем параметры в нужные типы
        try:
            self.temperature = float(self.temperature) if self.temperature is not None else 0.3
            self.max_tokens = int(self.max_tokens) if self.max_tokens is not None else 500
            self.timeout_seconds = float(self.timeout_seconds) if self.timeout_seconds is not None else 3600.0
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Ошибка конфигурации: параметры должны быть числами: {e}"
            )

        logger.info(f"✓ Конфигурация LM Studio загружена из {self.config_path}")
        logger.info(f"  • Base URL: {self.base_url}")
        logger.info(f"  • Model: {self.model}")
        logger.info(f"  • Temperature: {self.temperature}")
        logger.info(f"  • Max tokens: {self.max_tokens}")
        logger.info(f"  • Timeout: {self.timeout_seconds} сек ({self.timeout_seconds / 60:.0f} мин)")


class TelegramMessageExtractor:
    """Класс для извлечения сообщений из Telegram."""

    def __init__(self, tg_config: TelegramConfig):
        self.tg_config = tg_config
        self.client = None

    async def _connect(self):
        """Подключается к Telegram API."""
        if self.client is None:
            self.client = TelegramClient(
                self.tg_config.session_name,
                self.tg_config.api_id,
                self.tg_config.api_hash
            )
            await self.client.start()
            logger.info("✓ Подключено к Telegram API")

    async def disconnect(self):
        """Отключается от Telegram API."""
        if self.client:
            await self.client.disconnect()
            logger.info("✓ Отключено от Telegram API")

    async def get_today_messages(
            self,
            chat_identifier: Union[str, int]
    ) -> tuple[List[Message], str]:
        """
        Получает все сообщения из чата за текущий день.

        Args:
            chat_identifier: Имя чата (username, title), ID или номер чата

        Returns:
            tuple: (Список сообщений, Название чата)

        Raises:
            ValueError: Если чат не найден
            Exception: Если ошибка при получении сообщений
        """
        await self._connect()

        # Границы текущего дня в локальной временной зоне
        local_tz = get_local_timezone_offset()
        now_local = datetime.now(local_tz)

        # Преобразуем в UTC для запроса
        today_start_local = datetime.combine(
            now_local.date(),
            time.min,
            tzinfo=local_tz
        )
        today_start_utc = today_start_local.astimezone(timezone.utc)

        tomorrow_start_local = today_start_local + timedelta(days=1)
        tomorrow_start_utc = tomorrow_start_local.astimezone(timezone.utc)

        messages = []

        try:
            chat = await self.client.get_entity(chat_identifier)

            # Получаем название чата для отображения
            chat_name = self._get_chat_name(chat)
            logger.info(f"✓ Найден чат: {chat_name}")

            # Получаем сообщения за текущий день
            async for message in self.client.iter_messages(
                    chat,
                    offset_date=tomorrow_start_utc,
                    reverse=False
            ):
                # Останавливаемся при достижении начала дня
                if message.date < today_start_utc:
                    break

                messages.append(message)

            # Разворачиваем для хронологического порядка
            messages.reverse()

            logger.info(f"✓ Получено сообщений: {len(messages)}")
            return messages, chat_name

        except ValueError as e:
            logger.error(f"✗ Чат '{chat_identifier}' не найден")
            raise ValueError(f"Чат '{chat_identifier}' не найден: {e}")
        except Exception as e:
            logger.error(f"✗ Ошибка при получении сообщений: {e}")
            raise Exception(f"Ошибка при получении сообщений: {e}")

    @staticmethod
    def _get_chat_name(chat) -> str:
        """
        Получает название чата из объекта.

        Args:
            chat: Объект чата

        Returns:
            str: Название чата
        """
        # Для групп и каналов
        if hasattr(chat, 'title') and chat.title:
            return chat.title

        # Для пользователей
        if hasattr(chat, 'first_name') and chat.first_name:
            last_name = chat.last_name if hasattr(chat, 'last_name') and chat.last_name else ""
            return f"{chat.first_name} {last_name}".strip()

        # Для аккаунтов с username
        if hasattr(chat, 'username') and chat.username:
            return f"@{chat.username}"

        # Последняя попытка - ID
        if hasattr(chat, 'id'):
            return str(chat.id)

        return "Неизвестный чат"


class MessageFormatter:
    """Класс для форматирования сообщений для LLM."""

    def __init__(self, client: TelegramClient):
        """
        Инициализирует форматер.

        Args:
            client: Авторизованный клиент Telethon
        """
        self.client = client
        self._user_cache: Dict[int, str] = {}
        self.local_tz = get_local_timezone_offset()

    async def _get_sender_name(self, sender_id: int) -> str:
        """
        Получает имя или никнейм отправителя сообщения.

        Args:
            sender_id: ID отправителя

        Returns:
            str: Имя отправителя в формате "Ник (ID)" или "ID"
        """
        # Если уже в кеше, возвращаем из кеша
        if sender_id in self._user_cache:
            return self._user_cache[sender_id]

        try:
            # Получаем информацию о пользователе
            user = await self.client.get_entity(sender_id)

            # Пытаемся получить никнейм
            if hasattr(user, 'username') and user.username:
                name = f"@{user.username} ({sender_id})"
            # Если никнейма нет, используем имя и фамилию
            elif hasattr(user, 'first_name') and user.first_name:
                last_name = user.last_name if hasattr(user, 'last_name') and user.last_name else ""
                name = f"{user.first_name} {last_name} ({sender_id})".strip()
            # Если ничего нет, используем только ID
            else:
                name = str(sender_id)

            # Сохраняем в кеш
            self._user_cache[sender_id] = name
            return name

        except Exception as e:
            logger.debug(f"Не удалось получить имя пользователя {sender_id}: {e}")
            # При ошибке возвращаем только ID
            return str(sender_id)

    def _convert_to_local_time(self, utc_datetime: datetime) -> str:
        """
        Конвертирует UTC время в локальное время.

        Args:
            utc_datetime: Время в UTC

        Returns:
            str: Время в локальной зоне в формате HH:MM:SS
        """
        if not utc_datetime:
            return "N/A"

        # Если datetime naive (без timezone), считаем его UTC
        if utc_datetime.tzinfo is None:
            utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)

        # Конвертируем в локальную зону
        local_datetime = utc_datetime.astimezone(self.local_tz)

        return local_datetime.strftime("%H:%M:%S")

    async def format_for_llm(self, messages: List[Message]) -> str:
        """
        Форматирует сообщения для отправки в LLM.

        Args:
            messages: Список сообщений

        Returns:
            str: Отформатированный текст
        """
        formatted_lines = []

        for msg in messages:
            # Получаем имя отправителя
            if msg.sender_id:
                sender = await self._get_sender_name(msg.sender_id)
            else:
                sender = "Система"

            # Конвертируем время в локальную зону
            time_str = self._convert_to_local_time(msg.date)
            text = msg.text or "[Медиа/Документ]"

            formatted_lines.append(f"[{time_str}] {sender}: {text}")

        return "\n".join(formatted_lines)

    def get_statistics(self, messages: List[Message]) -> dict:
        """Получает статистику по сообщениям."""
        if not messages:
            return {}

        first_time = self._convert_to_local_time(messages[0].date)
        first_date = messages[0].date.astimezone(self.local_tz).strftime("%Y-%m-%d") if messages[0].date else "N/A"

        last_time = self._convert_to_local_time(messages[-1].date)
        last_date = messages[-1].date.astimezone(self.local_tz).strftime("%Y-%m-%d") if messages[-1].date else "N/A"

        return {
            "total_messages": len(messages),
            "first_message_time": f"{first_date} {first_time}",
            "last_message_time": f"{last_date} {last_time}",
            "unique_senders": len(set(msg.sender_id for msg in messages if msg.sender_id))
        }


class LMStudioSummarizer:
    """Класс для суммаризации сообщений с помощью LM Studio."""

    def __init__(self, lm_config: LMStudioConfig):
        self.lm_config = lm_config

    async def summarize(self, formatted_text: str) -> str:
        """
        Отправляет сообщения в LM Studio для суммаризации.

        Args:
            formatted_text: Отформатированный текст сообщений

        Returns:
            str: Суммаризированный текст

        Raises:
            ValueError: Если текст пуст
            Exception: Если ошибка при подключении к LM Studio
        """
        if not formatted_text:
            raise ValueError("Текст сообщений пуст")

        try:
            logger.info("📝 Отправляю сообщения в LM Studio для суммаризации...")

            # Используем httpx для прямого HTTP запроса
            async with httpx.AsyncClient(
                    timeout=self.lm_config.timeout_seconds
            ) as client:
                # Правильный endpoint для LM Studio
                url = f"{self.lm_config.base_url}/v1/chat/completions"

                payload = {
                    "model": self.lm_config.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Ты помощник, который создает краткое резюме диалога. "
                                "Выделяй ключевые моменты, решения и действия. "
                                "Форматируй ответ с использованием маркированных списков "
                                "для лучшей читаемости."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Пожалуйста, создай краткое резюме следующего диалога:\n\n"
                                f"{formatted_text}"
                            )
                        }
                    ],
                    "temperature": self.lm_config.temperature,
                    "max_tokens": self.lm_config.max_tokens
                }

                logger.info(f"Отправляю запрос на {url}")
                response = await client.post(url, json=payload)

                logger.info(f"Статус ответа: {response.status_code}")

                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"Ошибка от LM Studio: {error_text}")
                    raise Exception(
                        f"LM Studio вернула ошибку {response.status_code}: {error_text}"
                    )

                response_json = response.json()
                logger.debug(f"Ответ JSON: {response_json}")

                # Проверяем наличие choices в ответе
                if 'choices' not in response_json or not response_json['choices']:
                    logger.error(f"В ответе нет choices: {response_json}")
                    raise ValueError("Ответ не содержит choices")

                # Извлекаем текст из первого choice
                summary = response_json['choices'][0].get('message', {}).get('content', '')

                if not summary:
                    logger.error(f"Content пустой в ответе: {response_json}")
                    raise ValueError("Ответ содержит пустой content")

                logger.info("✓ Суммаризация завершена")
                return summary

        except httpx.ConnectError as e:
            logger.error(f"✗ Ошибка подключения: {e}")
            raise Exception(
                f"Не удается подключиться к LM Studio на {self.lm_config.base_url}. "
                "Убедитесь, что сервис запущен."
            )
        except httpx.TimeoutException as e:
            logger.error(f"✗ Timeout при ожидании ответа: {e}")
            raise Exception(
                f"Timeout: LM Studio слишком долго обрабатывает запрос "
                f"({self.lm_config.timeout_seconds / 60:.0f} мин). "
                "Проверьте нагрузку на модель или увеличьте timeout в config.yaml."
            )
        except Exception as e:
            logger.error(f"✗ Ошибка при суммаризации: {e}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            raise Exception(f"Ошибка при суммаризации: {e}")


class TgSummariseChat:
    """Главный класс модуля для суммаризации чатов Telegram."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Инициализирует модуль с конфигурацией из .env и config.yaml.

        Args:
            config_path: Путь к файлу config.yaml
        """
        self.tg_config = TelegramConfig()
        self.lm_config = LMStudioConfig(config_path)

        self.extractor = TelegramMessageExtractor(self.tg_config)
        self.summarizer = LMStudioSummarizer(self.lm_config)
        self.message_formatter: Optional[MessageFormatter] = None

    async def summarize_chat_today(
            self,
            chat_identifier: Union[str, int]
    ) -> dict:
        """
        Получает и суммаризирует сообщения из чата за текущий день.

        Args:
            chat_identifier: Имя чата, username, title или ID

        Returns:
            dict: Результат с суммаризацией и статистикой

        Example:
            tg = TgSummariseChat()
            result = await tg.summarize_chat_today("my_chat")
            result = await tg.summarize_chat_today(-1001234567890)
        """
        try:
            # Получаем сообщения и название чата
            messages, chat_name = await self.extractor.get_today_messages(
                chat_identifier
            )

            if not messages:
                logger.warning(
                    f"⚠ В чате '{chat_name}' нет сообщений за сегодня"
                )
                return {
                    "chat_name": chat_name,
                    "total_messages": 0,
                    "summary": "Нет сообщений для суммаризации",
                    "statistics": {}
                }

            # Инициализируем форматер с клиентом
            self.message_formatter = MessageFormatter(
                self.extractor.client
            )

            # Форматируем сообщения с получением имен отправителей
            formatted_text = await self.message_formatter.format_for_llm(
                messages
            )

            # Получаем статистику
            stats = self.message_formatter.get_statistics(messages)

            # Суммаризируем
            summary = await self.summarizer.summarize(formatted_text)

            result = {
                "chat_name": chat_name,
                "total_messages": stats['total_messages'],
                "summary": summary,
                "statistics": stats
            }

            logger.info(f"✓ Результат готов для чата '{chat_name}'")
            return result

        except Exception as e:
            logger.error(f"✗ Ошибка при обработке чата: {e}")
            raise

    async def close(self):
        """Закрывает все соединения."""
        await self.extractor.disconnect()
        logger.info("✓ Модуль завершил работу")


def create_argument_parser():
    """Создает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description='Получить суммаризацию сообщений из Telegram чата за текущий день',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # По названию чата
  python -m tg_summarise_chat --chat-name "my_chat"

  # По username
  python -m tg_summarise_chat --chat-name "@username"

  # По ID чата
  python -m tg_summarise_chat --chat-id -1001234567890

  # С пользовательским конфигом
  python -m tg_summarise_chat --chat-name "my_chat" --config /path/to/config.yaml
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--chat-name',
        type=str,
        help='Имя, username или title чата Telegram'
    )
    group.add_argument(
        '--chat-id',
        type=int,
        help='ID чата Telegram (например: -1001234567890)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Путь к файлу конфигурации (по умолчанию: config.yaml)'
    )

    return parser


def print_result(result: dict):
    """Красиво выводит результат суммаризации."""
    print("\n" + "=" * 70)
    print(f"Чат: {result['chat_name']}")
    print("=" * 70)

    if result['total_messages'] == 0:
        print("\n⚠ Нет сообщений для суммаризации\n")
        return

    print(f"\n📊 Статистика:")
    print(f"  • Всего сообщений: {result['total_messages']}")
    stats = result['statistics']
    print(f"  • Уникальные отправители: {stats.get('unique_senders', 0)}")
    print(f"  • Первое сообщение: {stats.get('first_message_time', 'N/A')}")
    print(f"  • Последнее сообщение: {stats.get('last_message_time', 'N/A')}")

    print(f"\n📌 Суммаризация:")
    print(result['summary'])
    print("\n" + "=" * 70 + "\n")


async def main():
    """Главная функция."""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        tg_summarise = TgSummariseChat(config_path=args.config)

        try:
            # Определяем идентификатор чата
            if args.chat_name:
                chat_identifier = args.chat_name
            else:
                chat_identifier = args.chat_id

            result = await tg_summarise.summarize_chat_today(chat_identifier)
            print_result(result)

        finally:
            await tg_summarise.close()

    except KeyboardInterrupt:
        logger.info("\n✗ Операция отменена пользователем")
        sys.exit(1)

    except Exception as e:
        logger.error(f"✗ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
