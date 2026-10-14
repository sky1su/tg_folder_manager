from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import os

class ProxyConfig(BaseModel):
    server: str
    port: int
    secret: Optional[str] = None
    type: str = "socks5"

class TelegramCredentials(BaseModel):
    api_id: str
    api_hash: str
    app_title: Optional[str] = None
    app_short_name: Optional[str] = None
    session_name: str = "session"

class FolderSettings(BaseModel):
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)

class FolderManagerSettings(BaseModel):
    export_enabled: bool = False
    export_filename: str = "folders_export.yaml"
    dry_run: bool = False
    warn_on_duplicates: bool = True
    unmatched_strategy: str = "ignore"

class LLMConfig(BaseModel):
    model: str
    temperature: float = 0.3
    max_tokens: int = 500
    timeout_seconds: float = 3600.0
    base_url: Optional[str] = None
    auth_type: str = "credentials"
    gigachat_client_id: Optional[str] = None
    gigachat_secret: Optional[str] = None
    gigachat_token: Optional[str] = None

class AppConfig(BaseModel):
    telegram: TelegramCredentials
    proxy: Optional[ProxyConfig] = None
    folder_manager: FolderManagerSettings = Field(default_factory=FolderManagerSettings)
    summarizer: Optional[LLMConfig] = None
