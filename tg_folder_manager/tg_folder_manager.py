import logging
from enum import Enum
from collections import defaultdict
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

from dotenv import load_dotenv
from os import getenv
import yaml
import re

from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest, UpdateDialogFilterRequest
from telethon.tl.types import (
    DialogFilter,
    TextWithEntities,
    Channel,
    Chat,
    InputPeerChannel,
    InputPeerChat
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UnmatchedChatsStrategy(Enum):
    IGNORE = 'ignore'
    MOVE_TO_FOLDER = 'move_to_folder'
    REMOVE_FROM_FOLDERS = 'remove_from_folders'
    LOG_ONLY = 'log_only'


@dataclass
class ChatInfo:
    id: int
    title: str
    access_hash: Optional[int]
    is_megagroup: bool
    is_channel: bool
    is_group: bool
    input_peer: any


@dataclass
class FolderInfo:
    id: int
    title: str
    include_peers: List[any]
    pinned_peers: List[any]
    exclude_peers: List[any]


@dataclass
class ChatDuplicateInfo:
    chat_title: str
    chat_id: int
    folders: List[str]

    def is_duplicate(self) -> bool:
        return len(self.folders) > 1


class ConfigLoader:
    @staticmethod
    def load_config(config_path: str = 'config.yaml') -> (
            Dict[str, List[str]], Dict[str, List[str]], Dict
    ):
        with open(config_path, encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}

        # Загружаем настройки
        settings = cfg.get('settings', {})
        export_settings = {
            'enabled': settings.get('export_enabled', False),
            'filename': settings.get('export_filename', 'folders_export.yaml'),
            'dry_run': settings.get('dry_run', False)
        }

        folders_cfg = cfg.get('folders', {})
        include_patterns: Dict[str, List[str]] = {}
        exclude_patterns: Dict[str, List[str]] = {}

        for name, params in folders_cfg.items():
            inc = params.get('include_patterns', [])
            exc = params.get('exclude_patterns', [])
            if not isinstance(inc, list):
                inc = [inc] if inc else []
            if not isinstance(exc, list):
                exc = [exc] if exc else []
            include_patterns[name] = [p for p in inc if p]
            exclude_patterns[name] = [p for p in exc if p]

        return include_patterns, exclude_patterns, export_settings


class ChatMatcher:
    @staticmethod
    def match_primary(
            chat_title: str,
            include_patterns: Dict[str, List[str]],
            exclude_patterns: Dict[str, List[str]]
    ) -> Optional[str]:
        title = chat_title.lower()
        for folder, inc_pats in include_patterns.items():
            # проверка исключений
            skip = False
            for pat in exclude_patterns.get(folder, []):
                if not pat:
                    continue
                try:
                    if re.search(pat.lower(), title):
                        skip = True
                        break
                except re.error:
                    if pat.lower() in title:
                        skip = True
                        break
            if skip:
                continue
            # проверка включений
            for pat in inc_pats:
                if not pat:
                    continue
                try:
                    if re.search(pat.lower(), title):
                        return folder
                except re.error:
                    if pat.lower() in title:
                        return folder
        return None


class TelegramFolderManager:
    def __init__(
            self,
            unmatched_strategy: UnmatchedChatsStrategy = UnmatchedChatsStrategy.IGNORE,
            warn_on_duplicates: bool = True,
            dry_run: bool = False
    ):
        load_dotenv()
        session = getenv('app_title', 'telegram_session')
        api_id = getenv('app_api_id')
        api_hash = getenv('app_api_hash')
        if not api_id or not api_hash:
            raise ValueError('API credentials not set')
        self.client = TelegramClient(session, int(api_id), api_hash)
        self.strategy = unmatched_strategy
        self.warn_dupes = warn_on_duplicates
        self.dry_run = dry_run
        self._chat_map: Dict[int, ChatInfo] = {}
        self._folder_map: Dict[int, FolderInfo] = {}
        self._chat_folders: Dict[int, List[str]] = defaultdict(list)

    async def __aenter__(self):
        await self.client.start()
        if self.dry_run:
            logger.info('✔ Connected to Telegram (DRY RUN MODE - no changes will be made)')
        else:
            logger.info('✔ Connected to Telegram')
        return self

    async def __aexit__(self, *args):
        await self.client.disconnect()
        if self.dry_run:
            logger.info('✔ Disconnected from Telegram (DRY RUN MODE)')
        else:
            logger.info('✔ Disconnected from Telegram')

    async def get_chats(self) -> List[ChatInfo]:
        dialogs = await self.client.get_dialogs()
        out: List[ChatInfo] = []
        for d in dialogs:
            e = d.entity
            if isinstance(e, (Channel, Chat)):
                peer = InputPeerChannel(e.id, e.access_hash) if isinstance(e, Channel) else InputPeerChat(e.id)
                title = e.title if isinstance(e.title, str) else e.title.text
                ci = ChatInfo(
                    id=e.id, title=title,
                    access_hash=getattr(e, 'access_hash', None),
                    is_megagroup=getattr(e, 'megagroup', False),
                    is_channel=isinstance(e, Channel) and not getattr(e, 'megagroup', False),
                    is_group=isinstance(e, Chat),
                    input_peer=peer
                )
                out.append(ci)
                self._chat_map[ci.id] = ci
        return out

    async def get_folders(self) -> List[FolderInfo]:
        res = await self.client(GetDialogFiltersRequest())
        out: List[FolderInfo] = []
        for f in res.filters:
            if not isinstance(f, DialogFilter):
                continue
            title = f.title.text if hasattr(f.title, 'text') else str(f.title)
            fi = FolderInfo(
                id=f.id, title=title,
                include_peers=f.include_peers,
                pinned_peers=f.pinned_peers,
                exclude_peers=f.exclude_peers
            )
            out.append(fi)
            self._folder_map[fi.id] = fi
        return out

    def _peer_id(self, p) -> Optional[int]:
        return getattr(p, 'channel_id', None) or getattr(p, 'chat_id', None) or getattr(p, 'user_id', None)

    async def _build_map(self):
        self._chat_folders.clear()
        for fi in await self.get_folders():
            for p in fi.include_peers:
                cid = self._peer_id(p)
                if cid:
                    self._chat_folders[cid].append(fi.title)

    async def _find_duplicates(self) -> List[ChatDuplicateInfo]:
        dup: List[ChatDuplicateInfo] = []
        for cid, titles in self._chat_folders.items():
            if len(titles) > 1:
                ci = self._chat_map[cid]
                dup.append(ChatDuplicateInfo(ci.title, cid, titles))
        return dup

    def _count_chats_in_folders(self) -> Dict[str, int]:
        """Подсчёт количества чатов в каждой папке"""
        folder_counts = defaultdict(int)
        for fi in self._folder_map.values():
            chat_count = 0
            for peer in fi.include_peers:
                peer_id = self._peer_id(peer)
                if peer_id and peer_id in self._chat_map:
                    chat_info = self._chat_map[peer_id]
                    if chat_info.is_group or chat_info.is_megagroup or chat_info.is_channel:
                        chat_count += 1
            folder_counts[fi.title] = chat_count
        return dict(folder_counts)

    def _print_folder_stats(self):
        """Вывод статистики по папкам"""
        folder_counts = self._count_chats_in_folders()
        if folder_counts:
            logger.info("📊 Статистика папок:")
            for folder_name, count in sorted(folder_counts.items()):
                logger.info(f"   📁 {folder_name}: {count} групп/каналов")
        else:
            logger.info("📊 Папки не найдены")

    async def export_folders_to_yaml(self, filename: str, dry_run: bool = False):
        """Экспорт папок и чатов в YAML файл"""
        export_data = {
            'export_date': datetime.now().isoformat(),
            'dry_run': dry_run,
            'folders': {}
        }

        for fi in self._folder_map.values():
            chats_list = []
            for peer in fi.include_peers:
                peer_id = self._peer_id(peer)
                if peer_id and peer_id in self._chat_map:
                    chat_info = self._chat_map[peer_id]
                    chat_type = 'channel'
                    if chat_info.is_group:
                        chat_type = 'group'
                    elif chat_info.is_megagroup:
                        chat_type = 'megagroup'

                    chats_list.append({
                        'id': chat_info.id,
                        'title': chat_info.title,
                        'type': chat_type
                    })

            export_data['folders'][fi.title] = {
                'folder_id': fi.id,
                'chats_count': len(chats_list),
                'chats': sorted(chats_list, key=lambda x: x['title'])
            }

        # Сохранение в файл
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        if dry_run:
            logger.info(f'📤 [DRY RUN] Экспортировано {len(self._folder_map)} папок в файл "{filename}"')
        else:
            logger.info(f'📤 Экспортировано {len(self._folder_map)} папок в файл "{filename}"')

    async def organize_chats_by_config(self, config_path: str):
        include_pats, exclude_pats, settings = ConfigLoader.load_config(config_path)

        # Устанавливаем режим dry-run из конфига
        self.dry_run = settings.get('dry_run', False)

        if self.dry_run:
            logger.warning('⚠️ DRY RUN MODE ENABLED - Никакие изменения не будут применены к Telegram')

        chats = await self.get_chats()
        await self._build_map()

        # Вывод статистики ДО обработки
        logger.info("📊 Статистика папок ПЕРЕД обработкой:")
        self._print_folder_stats()

        if self.warn_dupes:
            dup = await self._find_duplicates()
            if dup:
                logger.warning('⚠ Дубликаты обнаружены:')
                for d in dup:
                    logger.warning(f'  {d.chat_title}: {", ".join(d.folders)}')

        targets: Dict[str, Set[int]] = {name: set() for name in include_pats}
        unmatched: List[ChatInfo] = []

        for ci in chats:
            primary = ChatMatcher.match_primary(ci.title, include_pats, exclude_pats)
            if primary:
                targets[primary].add(ci.id)
            else:
                unmatched.append(ci)

        for name, ids in targets.items():
            await self._process_folder(name, ids)

        await self._handle_unmatched(unmatched, unmatched_folder='Прочие')

        # Обновляем карту и выводим статистику ПОСЛЕ обработки
        await self._build_map()
        logger.info("📊 Статистика папок ПОСЛЕ обработки:")
        self._print_folder_stats()

        # Экспорт если включён
        if settings.get('enabled', False):
            await self.export_folders_to_yaml(
                settings.get('filename', 'folders_export.yaml'),
                dry_run=self.dry_run
            )

    async def _process_folder(self, name: str, ids: Set[int]):
        title_ent = TextWithEntities(text=name, entities=[])
        peers = [self._chat_map[i].input_peer for i in ids if i in self._chat_map]
        fi = next((f for f in self._folder_map.values() if f.title == name), None)

        if fi:
            cur = {self._peer_id(p) for p in fi.include_peers}
            to_add = ids - cur
            to_remove = cur - ids
            if to_add or to_remove:
                if not self.dry_run:
                    df = DialogFilter(
                        id=fi.id, title=title_ent,
                        pinned_peers=[], include_peers=peers,
                        exclude_peers=[], contacts=False,
                        non_contacts=False, groups=False,
                        broadcasts=False, bots=False,
                        exclude_muted=False, exclude_read=False,
                        exclude_archived=False, emoticon=None
                    )
                    await self.client(UpdateDialogFilterRequest(id=fi.id, filter=df))
                    logger.info(f'✎ Updated folder "{name}" ({len(peers)} chats)')
                else:
                    logger.info(f'✎ [DRY RUN] Would update folder "{name}" ({len(peers)} chats)')
        else:
            nid = max(self._folder_map.keys(), default=1) + 1
            if not self.dry_run:
                df = DialogFilter(
                    id=nid, title=title_ent,
                    pinned_peers=[], include_peers=peers,
                    exclude_peers=[], contacts=False,
                    non_contacts=False, groups=False,
                    broadcasts=False, bots=False,
                    exclude_muted=False, exclude_read=False,
                    exclude_archived=False, emoticon=None
                )
                await self.client(UpdateDialogFilterRequest(id=nid, filter=df))
                logger.info(f'✚ Created folder "{name}" (ID={nid}, {len(peers)} chats)')
            else:
                logger.info(f'✚ [DRY RUN] Would create folder "{name}" (ID={nid}, {len(peers)} chats)')

            self._folder_map[nid] = FolderInfo(
                id=nid, title=name,
                include_peers=peers,
                pinned_peers=[], exclude_peers=[]
            )

        # Remove these chats from other folders
        for other in list(self._folder_map.values()):
            if other.title == name:
                continue
            new_peers = [p for p in other.include_peers if self._peer_id(p) not in ids]
            if len(new_peers) != len(other.include_peers):
                removed_count = len(other.include_peers) - len(new_peers)
                if not self.dry_run:
                    df = DialogFilter(
                        id=other.id,
                        title=TextWithEntities(text=other.title, entities=[]),
                        pinned_peers=[], include_peers=new_peers,
                        exclude_peers=[], contacts=False,
                        non_contacts=False, groups=False,
                        broadcasts=False, bots=False,
                        exclude_muted=False, exclude_read=False,
                        exclude_archived=False, emoticon=None
                    )
                    await self.client(UpdateDialogFilterRequest(id=other.id, filter=df))
                    logger.info(
                        f'− Removed {removed_count} chat(s) from "{other.title}" '
                        f'after moving to "{name}"'
                    )
                else:
                    logger.info(
                        f'− [DRY RUN] Would remove {removed_count} chat(s) from "{other.title}" '
                        f'after moving to "{name}"'
                    )
                other.include_peers = new_peers

    async def _handle_unmatched(self, unmatched: List[ChatInfo], unmatched_folder: str):
        if self.strategy == UnmatchedChatsStrategy.IGNORE:
            return

        title_ent = TextWithEntities(text=unmatched_folder, entities=[])
        peers = [c.input_peer for c in unmatched]

        if self.strategy == UnmatchedChatsStrategy.LOG_ONLY:
            logger.warning(f'Несопоставленные чаты ({len(unmatched)}):')
            for c in unmatched:
                logger.warning(f'  {c.title}')
            return

        fi = next((f for f in self._folder_map.values() if f.title == unmatched_folder), None)
        fid = fi.id if fi else max(self._folder_map.keys(), default=1) + 1

        if self.strategy == UnmatchedChatsStrategy.MOVE_TO_FOLDER:
            existing = fi.include_peers if fi else []
            combined = existing + peers
            unique, seen = [], set()
            for p in combined:
                pid = self._peer_id(p)
                if pid and pid not in seen:
                    seen.add(pid)
                    unique.append(p)

            if not self.dry_run:
                df = DialogFilter(
                    id=fid, title=title_ent,
                    pinned_peers=[], include_peers=unique,
                    exclude_peers=[], contacts=False,
                    non_contacts=False, groups=False,
                    broadcasts=False, bots=False,
                    exclude_muted=False, exclude_read=False,
                    exclude_archived=False, emoticon=None
                )
                await self.client(UpdateDialogFilterRequest(id=fid, filter=df))
                logger.info(f'✚ Moved {len(peers)} unmatched chats to "{unmatched_folder}"')
            else:
                logger.info(f'✚ [DRY RUN] Would move {len(peers)} unmatched chats to "{unmatched_folder}"')

        elif self.strategy == UnmatchedChatsStrategy.REMOVE_FROM_FOLDERS:
            rem = {c.id for c in unmatched}
            total_removed = 0
            for other in self._folder_map.values():
                kept = [p for p in other.include_peers if self._peer_id(p) not in rem]
                if len(kept) != len(other.include_peers):
                    removed_count = len(other.include_peers) - len(kept)
                    total_removed += removed_count
                    if not self.dry_run:
                        df = DialogFilter(
                            id=other.id,
                            title=TextWithEntities(text=other.title, entities=[]),
                            pinned_peers=[], include_peers=kept,
                            exclude_peers=[], contacts=False,
                            non_contacts=False, groups=False,
                            broadcasts=False, bots=False,
                            exclude_muted=False, exclude_read=False,
                            exclude_archived=False, emoticon=None
                        )
                        await self.client(UpdateDialogFilterRequest(id=other.id, filter=df))

            if not self.dry_run:
                logger.info(f'− Removed {total_removed} unmatched chats from all folders')
            else:
                logger.info(f'− [DRY RUN] Would remove {total_removed} unmatched chats from all folders')
