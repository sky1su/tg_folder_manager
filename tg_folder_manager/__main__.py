import logging
import asyncio
import os
from dotenv import load_dotenv
from core.file_service import FileService
from core.telegram_service import TelegramService
from .tg_folder_manager import TelegramFolderManager

# Load environment variables from .env file
load_dotenv()

async def main():
    # Автоматически находим config.yaml в корне проекта
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, 'config.yaml')

    try:
        # 1. Загружаем конфигурацию через FileService
        config = FileService.load_config(config_path)
        
        # 2. Инициализируем сервис Telegram
        async with TelegramService(config.telegram, config.proxy) as telegram_service:
            # 3. Инициализируем менеджер папок
            manager = TelegramFolderManager(
                telegram_service=telegram_service,
                settings=config.folder_manager
            )
            # 4. Запускаем процесс организации чатов
            await manager.organize_chats()
            
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
