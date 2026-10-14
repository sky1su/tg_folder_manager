import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Union, Optional, Dict, Any

from telethon import TelegramClient, connection
from telethon.tl.types import Message, TextWithEntities
from core.telegram_service import TelegramService

logger = logging.getLogger(__name__)

class TelegramMessageExtractor:
    def __init__(self, telegram_service: TelegramService):
        self.telegram_service = telegram_service
        self._user_cache: Dict[int, str] = {}

    async def get_messages_for_period(
            self,
            chat_identifier: Union[str, int],
            days: int = 1
    ) -> tuple[List[Message], str]:
        """
        Получает сообщения из чата за указанный период (количество дней).
        """
        # Границы периода в локальной временной зоне
        now = datetime.now(timezone.utc)
        start_date = datetime.combine(now.date() - timedelta(days=days-1), datetime.min.time(), tzinfo=timezone.utc)
        tomorrow_start = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)

        messages = []

        try:
            client = self.telegram_service.client
            chat = await client.get_entity(chat_identifier)
            chat_name = self._get_chat_name(chat)
            logger.info(f"✓ Найден чат: {chat_name} (период: {days} дн.)")

            async for message in client.iter_messages(
                    chat,
                    offset_date=tomorrow_start,
                    reverse=False
            ):
                if message.date < start_date:
                    break
                messages.append(message)

            messages.reverse()
            logger.info(f"✓ Получено сообщений: {len(messages)}")
            return messages, chat_name

        except ValueError as e:
            logger.error(f"✗ Чат '{chat_identifier}' не найден")
            raise ValueError(f"Чат '{chat_identifier}' не найден: {e}")
        except Exception as e:
            logger.error(f"✗ Ошибка при получении сообщений: {e}")
            raise

    @staticmethod
    def _get_chat_name(chat) -> str:
        if hasattr(chat, 'title') and chat.title:
            return chat.title
        if hasattr(chat, 'first_name') and chat.first_name:
            last_name = getattr(chat, 'last_name', "") or ""
            return f"{chat.first_name} {last_name}".strip()
        if hasattr(chat, 'username') and chat.username:
            return f"@{chat.username}"
        if hasattr(chat, 'id'):
            return str(chat.id)
        return "Неизвестный чат"

    async def format_for_llm(self, messages: List[Message]) -> str:
        formatted = []
        for msg in messages:
            if msg.text:
                formatted.append(f"[{msg.date.strftime('%H:%M')}] {msg.from_id}: {msg.text}")
            elif msg.media:
                formatted.append(f"[{msg.date.strftime('%H:%M')}] {msg.from_id}: [Media]")
        return "\n".join(formatted)
