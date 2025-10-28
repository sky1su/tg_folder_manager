"""
Модуль для суммаризации сообщений из Telegram чатов с помощью LM Studio.
"""

from tg_summarise_chat.tg_summarise_chat import (
    TgSummariseChat,
    TelegramConfig,
    LMStudioConfig,
    TelegramMessageExtractor,
    MessageFormatter,
    LMStudioSummarizer,
    main
)

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    "TgSummariseChat",
    "TelegramConfig",
    "LMStudioConfig",
    "TelegramMessageExtractor",
    "MessageFormatter",
    "LMStudioSummarizer",
    "main"
]