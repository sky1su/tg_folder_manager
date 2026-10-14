import logging
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
import yaml

from telethon.tl.types import (
    DialogFilter,
    TextWithEntities,
    Channel,
    Chat,
    InputPeerChannel,
    InputPeerChat
)

from .models import (
    UnmatchedChatsStrategy,
    ChatInfo,
    FolderInfo,
    ChatDuplicateInfo
)
from core.telegram_service import TelegramService

logger = logging.getLogger(__name__)

class TelegramFolderManager:
    def __init__(
            self,
            telegram_service: TelegramService,
            settings: Any # FolderManagerSettings
    ):
        self.telegram = telegram_service
        self.settings = settings
        
        self._chat_map: Dict[int, ChatInfo] = {}
        self._folder_map: Dict[int, FolderInfo] = {}
        self._chat_folders: Dict[int, List[str]] = {}
        self.dry_run = settings.dry_run
        self.warn_dupes = settings.warn_on_duplicates

    async def get_chats(self) -> List[ChatInfo]:
        dialogs = await self.telegram.client.get_dialogs()
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
        res = await self.telegram.get_filters()
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

    async def _build_map(self):
        self._chat_folders = {}
        for fi in await self.get_folders():
            for p in fi.include_peers:
                cid = self.telegram.get_peer_id(p)
                if cid:
                    if cid not in self._chat_folders:
                        self._chat_folders[cid] = []
                    self._chat_folders[cid].append(fi.title)

    async def _find_duplicates(self) -> List[ChatDuplicateInfo]:
        dup: List[ChatDuplicateInfo] = []
        for cid, titles in self._chat_folders.items():
            if len(titles) > 1:
                ci = self._chat_map[cid]
                dup.append(ChatDuplicateInfo(ci.title, cid, titles))
        return dup

    def _count_chats_in_folders(self) -> Dict[str, int]:
        folder_counts = {}
        for fi in self._folder_map.values():
            chat_count = 0
            for peer in fi.include_peers:
                peer_id = self.telegram.get_peer_id(peer)
                if peer_id and peer_id in self._chat_map:
                    chat_info = self._chat_map[peer_id]
                    if chat_info.is_group or chat_info.is_megagroup or chat_info.is_channel:
                        chat_count += 1
            folder_counts[fi.title] = chat_count
        return folder_counts

    def _print_folder_stats(self):
        folder_counts = self._count_chats_in_folders()
        if folder_counts:
            logger.info("📊 Статистика папок:")
            for folder_name, count in sorted(folder_counts.items()):
                logger.info(f"   📁 {folder_name}: {count} групп/каналов")
        else:
            logger.info("📊 Папки не найдены")

    async def organize_chats(self):
        chats = await self.get_chats()
        await self._build_map()

        logger.info("📊 Статистика папок ПЕРЕД обработкой:")
        self._print_folder_stats()

        if self.warn_dupes:
            dups = await self._find_duplicates()
            if dups:
                logger.warning('⚠ Дубликаты обнаружены:')
                for d in dups:
                    logger.warning(f'  {d.chat_title}: {", ".join(d.folders)}')

        # Prepare targets: Dict[folder_name, Set[chat_id]]
        targets: Dict[str, Set[int]] = {name: set() for name in self.settings.folders}
        unmatched: List[ChatInfo] = []

        folder_patterns = {
            name: (list(f.include_patterns), list(f.exclude_patterns))
            for name, f in self.settings.folders.items()
        }

        # Match chats to folders based on patterns
        from .matcher import ChatMatcher
        for ci in chats:
            matched_folder = None
            for folder_name, (inc, exc) in folder_patterns.items():
                if ChatMatcher.match_primary(ci.title, {folder_name: inc}, {folder_name: exc}):
                    matched_folder = folder_name
                    break
            
            if matched_folder:
                targets[matched_folder].add(ci.id)
            else:
                unmatched.append(ci)

        # 1. Handle removals from existing folders
        for folder_name, ids in targets.items():
            fi = next((f for f in self._folder_map.values() if f.title == folder_name), None)
            if fi:
                cur_ids = {self.telegram.get_peer_id(p) for p in fi.include_peers if self.telegram.get_peer_id(p)}
                to_remove = cur_ids - ids
                if to_remove:
                    if not self.dry_run:
                        new_peers = [self._chat_map[i].input_peer for i in ids if i in self._chat_map]
                        df = DialogFilter(
                            id=fi.id, title=TextWithEntities(text=folder_name, entities=[]),
                            pinned_peers=[], include_peers=new_peers,
                            exclude_peers=[], contacts=False,
                            non_contacts=False, groups=False,
                            broadcasts=False, bots=False,
                            exclude_muted=False, exclude_read=False,
                            exclude_archived=False, emoticon=None
                        )
                        await self.telegram.update_dialog_filter(fi.id, df)
                        logger.info(f'− Removed {len(to_remove)} chat(s) from "{folder_name}"')
                    else:
                        logger.info(f'− [DRY RUN] Would remove {len(to_remove)} chat(s) from "{folder_name}"')

        # 2. Add to target folders
        for folder_name, ids in targets.items():
            if not ids:
                continue
            fi = next((f for f in self._folder_map.values() if f.title == folder_name), None)
            
            if fi:
                cur_ids = {self.telegram.get_peer_id(p) for p in fi.include_peers if self.telegram.get_peer_id(p)}
                to_add = ids - cur_ids
                if to_add:
                    new_peers = [self._chat_map[i].input_peer for i in ids if i in self._chat_map]
                    if not self.dry_run:
                        df = DialogFilter(
                            id=fi.id, title=TextWithEntities(text=folder_name, entities=[]),
                            pinned_peers=[], include_peers=new_peers,
                            exclude_peers=[], contacts=False,
                            non_contacts=False, groups=False,
                            broadcasts=False, bots=False,
                            exclude_muted=False, exclude_read=False,
                            exclude_archived=False, emoticon=None
                        )
                        await self.telegram.update_dialog_filter(fi.id, df)
                        logger.info(f'✚ Added {len(to_add)} chat(s) to "{folder_name}"')
                    else:
                        logger.info(f'✚ [DRY RUN] Would add {len(to_add)} chat(s) to "{folder_name}"')
            else:
                new_peers = [self._chat_map[i].input_peer for i in ids if i in self._chat_map]
                nid = max(self._folder_map.keys(), default=1) + 1
                if not self.dry_run:
                    df = DialogFilter(
                        id=nid, title=TextWithEntities(text=folder_name, entities=[]),
                        pinned_peers=[], include_peers=new_peers,
                        exclude_peers=[], contacts=False,
                        non_contacts=False, groups=False,
                        broadcasts=False, bots=False,
                        exclude_muted=False, exclude_read=False,
                        exclude_archived=False, emoticon=None
                    )
                    await self.telegram.client(UpdateDialogFilterRequest(id=nid, filter=df))
                    logger.info(f'✚ Created new folder "{folder_name}" (ID={nid}, {len(new_peers)} chats)')
                else:
                    logger.info(f'✚ [DRY RUN] Would create new folder "{folder_name}" (ID={nid}, {len(new_peers)} chats)')
                self._folder_map[nid] = FolderInfo(id=nid, title=folder_name, include_peers=new_peers, pinned_peers=[], exclude_peers=[])

        # 3. Handle unmatched
        if self.settings.unmatched_strategy == "move_to_folder":
             # In a real app, we'd create an 'Unmatched' folder and move chats there.
             # For now, let's just log it if we don't want to change the logic too much.
             pass

        logger.info("✅ Organization completed.")
    
    async def export_folders_to_yaml(self, filename: str):
        export_data = {
            'export_date': datetime.now().iso_format(),
            'folders': {}
        }

        for fi in self._folder_map.values():
            chats_list = []
            for peer in fi.include_peers:
                peer_id = self.telegram.get_peer_id(peer)
                if peer_id and peer_id in self._chat_map:
                    chat_info = self._chat_map[peer_id]
                    chats_list.append({
                        'id': chat_info.id,
                        'title': chat_info.title
                    })
            export_data['folders'][fi.title] = chats_list

        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, allow_unicode=True, sort_keys=False)
