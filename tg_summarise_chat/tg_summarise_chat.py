import asyncio
import logging
from typing import Any
from core.telegram_service import TelegramService
from core.config import LLMConfig

import logging
import yaml
import os
from pathlib import Path

from telethon import connection
from telethon.tl.types import TextWithEntities
from .models import SummarizeConfig # This will be removed as part of consolidation
from .extractor import TelegramMessageExtractor
from .summarizers import LMStudioSummarizer, GigaChatSummarizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SummarizerApp:
    def __init__(self, telegram_service: TelegramService, llm_config: LLMConfig):
        self.telegram_service = telegram_service
        self.llm_config = llm_config
        
        self.extractor = TelegramMessageExtractor(self.telegram_service)
        
        # Logic for choosing summarizer
        if self.llm_config.base_url: # simple check for LM Studio
             self.summarizer = LMStudioSummarizer(self.llm_config)
        else:
             self.summarizer = GigaChatSummarizer(self.llm_config)

    async def run(self, chat_id: str):
        try:
            messages, chat_name = await self.extractor.get_today_messages(chat_id)
            if not messages:
                logger.info("No messages found for today.")
                return

            formatted_text = await self.extractor.format_for_llm(messages)
            summary = await self.summarizer.summarize(formatted_text)
            
            print(f"\n--- Summary for {chat_name} ---")
            print(summary)
            print("------------------------------\n")
        finally:
            pass # Disconnect handled by context manager in main
