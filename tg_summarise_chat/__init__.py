"""
Модуль для суммаризации сообщений из Telegram чатов с помощью LLM.
"""

from .tg_summarise_chat import SummarizerApp, TelegramConfig, SummarizeConfig
from .extractor import TelegramMessageExtractor
from .summarizers import LMStudioSummarizer, GigaChatSummarizer

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    "SummarizerApp",
    "TelegramConfig",
    "SummarizeConfig",
    "TelegramMessageExtractor",
    "LMStudioSummarizer",
    "GigaChatSummarizer"
]
