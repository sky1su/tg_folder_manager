import logging
import asyncio
import os
from dotenv import load_dotenv
from .tg_folder_manager import TelegramFolderManager, UnmatchedChatsStrategy

# Load environment variables from .env file
load_dotenv()

async def main():
    # Автоматически находим config.yaml в корне проекта
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, 'config.yaml')

    try:
        # Загружаем конфигурацию перед инициализацией менеджера
        config = TelegramFolderManager.load_config(config_path)
        
        async with TelegramFolderManager(
            config=config,
            unmatched_strategy=UnmatchedChatsStrategy.MOVE_TO_FOLDER,
            warn_on_duplicates=True
        ) as manager:
            await manager.organize_chats_by_config(config_path=config_path)
            
    except FileNotFoundError as e:
        logging.error(f"Файл конфигурации не найден: {e}")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}", exc_info=True)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
