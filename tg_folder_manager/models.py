from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

class UnmatchedChatsStrategy(str, Enum):
    IGNORE = 'ignore'
    MOVE_TO_FOLDER = 'move_to_folder'
    REMOVE_FROM_FOLDERS = 'remove_from_folders'
    LOG_ONLY = 'log_only'

@dataclass(frozen=True)
class ChatInfo:
    id: int
    title: str
    access_hash: Optional[int]
    is_megagroup: bool
    is_channel: bool
    is_group: bool
    input_peer: Any

@dataclass(frozen=True)
class FolderInfo:
    id: int
    title: str
    include_peers: List[Any]
    pinned_peers: List[Any]
    exclude_peers: List[Any]

@dataclass(frozen=True)
class ChatDuplicateInfo:
    chat_title: str
    chat_id: int
    folders: List[str]

    def is_duplicate(self) -> bool:
        return len(self.folders) > 1
