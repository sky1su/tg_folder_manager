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
        connection_mode, proxy_tuple = self._prepare_proxy(proxy)
        self.client = TelegramClient(
            credentials.session_name,
            credentials.api_id,
            credentials.api_hash,
            proxy=proxy_tuple,
            connection=connection_mode
        )

    def _prepare_proxy(self, proxy: Optional[ProxyConfig]) -> tuple[Optional[Any], Optional[tuple]]:
        if not proxy:
            return None, None

        p_type = proxy.type.lower()
        if p_type not in ["socks5", "http", "mtproto"]:
            logger.warning(f"Unknown proxy type: {p_type}. Defaulting to socks5")
            p_type = "socks5"

        if p_type == "mtproto":
            # Для MTProto в Telethon нужно передать connection=... и proxy=(server, port, secret)
            return connection.ConnectionTcpMTProxyRandomizedIntermediate, (proxy.server, proxy.port, proxy.secret)

        # Для socks5/http: (type, server, port, rdns, username, password)
        return None, (p_type, proxy.server, proxy.port, True, proxy.username, proxy.password)

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
