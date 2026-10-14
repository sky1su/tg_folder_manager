import asyncio
import argparse
import logging
import yaml
import os
from pathlib import Path

from .tg_summarise_chat import SummarizerApp, SummarizeConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main(chat_id: str, config_path: str):
    # Attempt to convert numeric string to int for Telethon
    if chat_id.isdigit():
        chat_id = int(chat_id)

    # Load configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        config = SummarizeConfig(**config_data)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return

    app = SummarizerApp(config)
    await app.run(chat_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize Telegram chats.")
    parser.add_argument("--chat-id", required=True, help="Telegram chat identifier (ID or username)")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.chat_id, args.config))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Runtime error: {e}", exc_info=True)
