import re
from typing import Dict, List, Optional
from .models import UnmatchedChatsStrategy

class ChatMatcher:
    @staticmethod
    def match_primary(
            chat_title: str,
            include_patterns: Dict[str, List[str]],
            exclude_patterns: Dict[str, List[str]]
    ) -> Optional[str]:
        """
        Returns the name of the first folder that matches the chat title.
        """
        title = chat_title.lower()
        for folder, inc_pats in include_patterns.items():
            # check exclusions
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
            
            # check inclusions
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
