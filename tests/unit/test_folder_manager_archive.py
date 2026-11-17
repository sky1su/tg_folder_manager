import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from telethon.errors import RPCError

from tg_folder_manager.tg_folder_manager import TelegramFolderManager
from tg_folder_manager.models import ChatInfo


def make_chat(cid, title=None, archived=False, peer=True):
    return ChatInfo(
        id=cid, title=title or f"chat{cid}", access_hash=None,
        is_megagroup=True, is_channel=False, is_group=False,
        input_peer=f"peer{cid}" if peer else None, is_archived=archived,
    )


def make_manager(dry_run=False):
    settings = SimpleNamespace(dry_run=dry_run, warn_on_duplicates=False,
                               archive_after_move=True, folders={})
    telegram = MagicMock()
    telegram.archive_chats = AsyncMock(side_effect=lambda peers: len(peers))
    return TelegramFolderManager(telegram, settings), telegram


def test_select_skips_already_archived():
    m, _ = make_manager()
    m._chat_map = {1: make_chat(1), 2: make_chat(2, archived=True), 3: make_chat(3)}
    ids = {c.id for c in m._select_chats_to_archive({"A": {1, 2}, "B": {3}})}
    assert ids == {1, 3}


def test_select_skips_unknown_and_peerless_and_dedupes():
    m, _ = make_manager()
    m._chat_map = {1: make_chat(1), 2: make_chat(2, peer=False)}
    selected = m._select_chats_to_archive({"A": {1, 2, 99}, "B": {1}})
    assert [c.id for c in selected] == [1]


@pytest.mark.asyncio
async def test_archive_sends_only_non_archived():
    m, tg = make_manager()
    m._chat_map = {1: make_chat(1), 2: make_chat(2, archived=True)}
    count = await m._archive_moved_chats({"A": {1, 2}})
    assert count == 1
    tg.archive_chats.assert_awaited_once_with(["peer1"])
    assert m._chat_map[1].is_archived is True


@pytest.mark.asyncio
async def test_archive_is_idempotent():
    m, tg = make_manager()
    m._chat_map = {1: make_chat(1)}
    await m._archive_moved_chats({"A": {1}})
    count = await m._archive_moved_chats({"A": {1}})
    assert count == 0
    assert tg.archive_chats.await_count == 1


@pytest.mark.asyncio
async def test_archive_nothing_when_all_archived():
    m, tg = make_manager()
    m._chat_map = {1: make_chat(1, archived=True)}
    assert await m._archive_moved_chats({"A": {1}}) == 0
    tg.archive_chats.assert_not_awaited()


@pytest.mark.asyncio
async def test_archive_dry_run_does_not_call_api():
    m, tg = make_manager(dry_run=True)
    m._chat_map = {1: make_chat(1)}
    assert await m._archive_moved_chats({"A": {1}}) == 0
    tg.archive_chats.assert_not_awaited()
    assert m._chat_map[1].is_archived is False


@pytest.mark.asyncio
async def test_archive_rpc_error_is_handled():
    m, tg = make_manager()
    tg.archive_chats = AsyncMock(side_effect=RPCError(request=None, message="CHANNEL_PRIVATE"))
    m._chat_map = {1: make_chat(1)}
    assert await m._archive_moved_chats({"A": {1}}) == 0
    assert m._chat_map[1].is_archived is False
