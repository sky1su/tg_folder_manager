import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.telegram_service import TelegramService
from core.config import TelegramCredentials, ProxyConfig

@pytest.fixture
def credentials():
    return TelegramCredentials(api_id=12345, api_hash="hash123", session_name="test_session")

@pytest.fixture
def proxy_config():
    return ProxyConfig(type="socks5", server="127.0.0.1", port=9050)

@pytest.mark.asyncio
async def test_telegram_service_lifecycle(credentials):
    with patch("core.telegram_service.TelegramClient") as MockClient:
        instance = MockClient.return_value
        instance.start = AsyncMock()
        instance.disconnect = AsyncMock()
        instance.get_dialogs = AsyncMock(return_value=[])
        
        async with TelegramService(credentials) as service:
            assert service.credentials == credentials
            instance.start.assert_called_once()
        
        instance.disconnect.assert_called_once()

@pytest.mark.asyncio
async def test_telegram_service_get_dialogs(credentials):
    with patch("core.telegram_service.TelegramClient") as MockClient:
        instance = MockClient.return_value
        instance.start = AsyncMock()
        instance.disconnect = AsyncMock()
        instance.get_dialogs = AsyncMock(return_value=["dialog1", "dialog2"])
        
        async with TelegramService(credentials) as service:
            dialogs = await service.get_dialogs()
            assert len(dialogs) == 2
            assert dialogs == ["dialog1", "dialog2"]

@pytest.mark.asyncio
async def test_telegram_service_send_message(credentials):
    with patch("core.telegram_service.TelegramClient") as MockClient:
        instance = MockClient.return_value
        instance.start = AsyncMock()
        instance.disconnect = AsyncMock()
        instance.send_message = AsyncMock()
        
        async with TelegramService(credentials) as service:
            await service.send_message("peer", "hello")
            instance.send_message.assert_called_once_with("peer", "hello")

def test_telegram_service_get_peer_id(credentials):
    with patch("core.telegram_service.TelegramClient"):
        service = TelegramService(credentials)
    
    class MockPeer:
        def __init__(self, channel_id):
            self.channel_id = channel_id
            
    peer = MockPeer(12345)
    assert service.get_peer_id(peer) == 12345

# --- archive_chats ---------------------------------------------------------

from telethon.tl.functions.folders import EditPeerFoldersRequest
from core.telegram_service import ARCHIVE_FOLDER_ID, ARCHIVE_BATCH_SIZE


@pytest.mark.asyncio
async def test_archive_chats_empty_does_not_call_api(credentials):
    with patch("core.telegram_service.TelegramClient") as MockClient:
        instance = MockClient.return_value
        service = TelegramService(credentials)
        assert await service.archive_chats([]) == 0
        instance.assert_not_called()


@pytest.mark.asyncio
async def test_archive_chats_uses_edit_peer_folders(credentials):
    with patch("core.telegram_service.TelegramClient") as MockClient:
        instance = AsyncMock()
        MockClient.return_value = instance
        service = TelegramService(credentials)
        assert await service.archive_chats(["p1", "p2", "p3"]) == 3
        instance.assert_awaited_once()
        req = instance.await_args.args[0]
        assert isinstance(req, EditPeerFoldersRequest)
        assert [fp.peer for fp in req.folder_peers] == ["p1", "p2", "p3"]
        assert all(fp.folder_id == ARCHIVE_FOLDER_ID for fp in req.folder_peers)


@pytest.mark.asyncio
async def test_archive_chats_batches(credentials):
    with patch("core.telegram_service.TelegramClient") as MockClient:
        instance = AsyncMock()
        MockClient.return_value = instance
        service = TelegramService(credentials)
        n = ARCHIVE_BATCH_SIZE * 2 + 50
        assert await service.archive_chats([f"p{i}" for i in range(n)]) == n
        sizes = [len(c.args[0].folder_peers) for c in instance.await_args_list]
        assert sizes == [ARCHIVE_BATCH_SIZE, ARCHIVE_BATCH_SIZE, 50]
