import logging
from typing import List, Optional, Dict, Any
from telethon import TelegramClient, connection
from telethon.tl.functions.messages import GetDialogFiltersRequest, UpdateDialogFilterRequest
from telethon.tl.types import DialogFilter, TextWithEntities, Channel, Chat, InputPeerChannel, InputPeerChat
from core.config import TelegramCredentials, ProxyConfig

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, credentials: TelegramCredentials, proxy: Optional[ProxyConfig] = None):
        self.credentials = credentials
        self.proxy = self._prepare_proxy(proxy)
        self.client = TelegramClient(
            credentials.session_name,
            credentials.api_id,
            credentials.api_hash,
            proxy=self.proxy
        )

    def _prepare_proxy(self, proxy: Optional[ProxyConfig]) -> Optional[tuple]:
        if not proxy:
            return None
        
        p_type = "socks5" if proxy.type == "socks5" else "http"
        return (
            p_type,
            proxy.server,
            proxy.port,
            True,  # rdns
            None,  # username
            proxy.secret
        )

    async def __aenter__(self):
        await self.client.start()
        logger.info("Connected to Telegram")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()
        logger.info("Disconnected from Telegram")

    async def get_dialogs(self):
        return await self.client.get_dialogs()

    async def get_filters(self):
        return await self.client(GetDialogFiltersRequest())

    async def update_dialog_filter(self, filter_id: int, new_filter: DialogFilter):
        return await self.client(UpdateDialogFilterRequest(id=filter_id, filter=new_filter))

    async def send_message(self, entity, message):
        return await self.client.send_message(entity, message)

    def get_peer_id(self, peer) -> Optional[int]:
        return getattr(peer, 'channel_id', None) or getattr(peer, 'chat_id', None) or getattr(peer, 'user_id', None)
