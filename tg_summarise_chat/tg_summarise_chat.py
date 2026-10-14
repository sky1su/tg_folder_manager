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

from .extractor import TelegramMessageExtractor
from .summarizers import LMStudioSummarizer, GigaChatSummarizer

# Configuration is handled by the orchestrator in run.py
logger = logging.getLogger(__name__)

class SummarizerApp:
    def __init__(self, telegram_service: TelegramService, llm_config: LLMConfig, verbose: bool = False):
        self.telegram_service = telegram_service
        self.llm_config = llm_config
        self.verbose = verbose
        
        self.extractor = TelegramMessageExtractor(self.telegram_service)
        
        # Logic for choosing summarizer
        if self.llm_config.base_url: # simple check for LM Studio
             self.summarizer = LMStudioSummarizer(self.llm_config, verbose=self.verbose)
        else:
             self.summarizer = GigaChatSummarizer(self.llm_config, verbose=self.verbose)

    async def run(self, chat_id: str, days: int = 1):
        try:
            messages, chat_name = await self.extractor.get_messages_for_period(chat_id, days)
            if not messages:
                logger.info(f"No messages found for the last {days} days.")
                return

            formatted_text = await self.extractor.format_for_llm(messages)
            
            if self.verbose:
                logger.info(f"--- DEBUG: Formatted text for LLM ---\n{formatted_text}\n---------------------------------------")

            summary = await self.summarizer.summarize(formatted_text)
            
            print(f"\n--- Summary for {chat_name} (last {days} days) ---")
            if not summary or summary.strip() == "":
                print("[!] Summary is empty. Check LLM logs.")
            else:
                print(summary)
            print("------------------------------\n")
        finally:
            pass # Disconnect handled by context manager in main
