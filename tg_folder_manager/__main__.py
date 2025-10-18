import logging
import asyncio
import os
from .tg_folder_manager import TelegramFolderManager, UnmatchedChatsStrategy

async def main():
    # Автоматически находим config.yaml в корне проекта
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, 'config.yaml')

    async with TelegramFolderManager(
        unmatched_strategy=UnmatchedChatsStrategy.MOVE_TO_FOLDER,
        warn_on_duplicates=True
    ) as manager:
        await manager.organize_chats_by_config(config_path=config_path)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())