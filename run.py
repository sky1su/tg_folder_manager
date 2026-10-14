import asyncio
import logging
import sys
import argparse
from dotenv import load_dotenv

from core.config import AppConfig
from core.telegram_service import TelegramService
from core.file_service import FileService
from tg_folder_manager.tg_folder_manager import TelegramFolderManager
from tg_summarise_chat.tg_summarise_chat import SummarizerApp

load_dotenv()

def setup_logging(verbosity: str):
    """Sets the global logging level based on verbosity setting."""
    if verbosity == "debug":
        level = logging.DEBUG
    elif verbosity == "info":
        level = logging.INFO
    else:
        level = logging.ERROR
    
    logging.basicConfig(
        level=level, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def run_app(args, config, tg_service):
    """Contains the main business logic loop."""
    if args.summarize:
        # Summarization mode
        if not config.summarizer:
            logging.error("Summarizer configuration is missing in config.yaml")
            return
        
        if args.chat_id is None:
            logging.error("Usage: python run.py --summarize <chat_id>")
            return
            
        chat_id = args.chat_id
        # We pass the verbosity flag to the app to allow it to use logger.debug/info/etc.
        # although the global logging level also controls visibility.
        summarizer = SummarizerApp(tg_service, config.summarizer, verbose=args.verbose or args.debug)
        await summarizer.run(chat_id)
    else:
        # Folder management mode (default)
        folder_manager = TelegramFolderManager(tg_service, config.folder_manager)
        await folder_manager.organize_chats()

async def main_async(args, config):
    """Async entry point."""
    async with TelegramService(config.telegram, config.proxy) as tg_service:
        await run_app(args, config, tg_service)

def main():
    # 1. Parse Arguments
    parser = argparse.ArgumentParser(description="Telegram Manager")
    parser.add_argument("--summarize", action="store_true", help="Run in summarization mode")
    parser.add_argument("chat_id", nargs="?", help="Chat ID for summarization")
    parser.add_argument("--verbose", action="store_true", help="Show info messages (current default)")
    parser.add_argument("--debug", action="store_true", help="Show debug messages")
    
    args = parser.parse_args()

    # 2. Determine verbosity and setup logging
    verbosity = "error"
    if args.debug:
        verbosity = "debug"
    elif args.verbose:
        verbosity = "info"
    
    setup_logging(verbosity)
    logger = logging.getLogger(__name__)

    # 3. Load Config
    config_path = "config.yaml"
    try:
        config = FileService.load_config(config_path)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # 4. Execute
    asyncio.run(main_async(args, config))

if __name__ == "__main__":
    main()
