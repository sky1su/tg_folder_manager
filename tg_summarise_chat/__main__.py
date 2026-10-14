import asyncio
import argparse
import logging
from core.config import AppConfig
from core.telegram_service import TelegramService
from core.file_service import FileService
from .tg_summarise_chat import SummarizerApp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main(chat_id: str, config_path: str, verbose: bool, days: int):
    # Attempt to convert numeric string to int for Telethon
    if chat_id.isdigit():
        chat_id = int(chat_id)

    # Load configuration
    try:
        config = FileService.load_config(config_path)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    if not config.summarizer:
        logger.error("Summarizer configuration is missing in config.yaml")
        return

    async with TelegramService(config.telegram, config.proxy) as tg_service:
        app = SummarizerApp(tg_service, config.summarizer, verbose)
        await app.run(chat_id, days)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize Telegram chats.")
    parser.add_argument("--chat-id", required=True, help="Telegram chat identifier (ID or username)")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--days", type=int, default=1, help="Number of days to include in the summary")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.chat_id, args.config, args.verbose, args.days))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Runtime error: {e}", exc_info=True)
