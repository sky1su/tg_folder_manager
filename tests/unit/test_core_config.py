import pytest
from core.config import (
    TelegramCredentials, 
    ProxyConfig, 
    FolderSettings, 
    FolderManagerSettings, 
    LLMConfig, 
    AppConfig
)

def test_telegram_credentials_valid():
    creds = TelegramCredentials(api_id=12345, api_hash="hash123")
    assert creds.api_id == 12345
    assert creds.api_hash == "hash123"
    assert creds.session_name == "session"

def test_telegram_credentials_invalid():
    with pytest.raises(ValueError):
        # Missing api_hash
        TelegramCredentials(api_id=12345)

def test_proxy_config_valid():
    proxy = ProxyConfig(type="socks5", server="127.0.0.1", port=9050)
    assert proxy.type == "socks5"
    assert proxy.server == "127.0.0.1"
    assert proxy.port == 9050

def test_folder_settings():
    settings = FolderSettings(
        include_patterns=[".*test.*"],
        exclude_patterns=["spam"]
    )
    assert ".*test.*" in settings.include_patterns
    assert "spam" in settings.exclude_patterns

def test_folder_manager_settings():
    folders = {
        "News": FolderSettings(include_patterns=["news"])
    }
    settings = FolderManagerSettings(
        export_enabled=True,
        folders=folders
    )
    assert settings.export_enabled is True
    assert "News" in settings.folders
    assert settings.folders["News"].include_patterns == ["news"]

def test_llm_config_defaults():
    config = LLMConfig(model="test-model")
    assert config.model == "test-model"
    assert config.temperature == 0.3
    assert config.max_tokens == 500

def test_app_config_full():
    telegram = TelegramCredentials(api_id="123", api_hash="hash")
    summarizer = LLMConfig(model="gpt-4")
    config = AppConfig(
        telegram=telegram,
        summarizer=summarizer
    )
    assert config.telegram.api_id == "123"
    assert config.summarizer.model == "gpt-4"
