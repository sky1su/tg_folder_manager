"""
Точка входа для запуска модуля tg_summarise_chat как пакета.

Позволяет запустить модуль следующими командами:
    python -m tg_summarise_chat --chat-name "chat_name"
    python tg_summarise_chat/__main__.py --chat-name "chat_name"
"""

import asyncio
from tg_summarise_chat import main

if __name__ == '__main__':
    asyncio.run(main())
