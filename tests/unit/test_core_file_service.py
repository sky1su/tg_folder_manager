import yaml
import os
from core.file_service import FileService
from core.config import AppConfig, TelegramCredentials

def test_file_service_save_and_load_yaml(tmp_path):
    # Setup
    file_path = tmp_path / "test_config.yaml"
    data = {
        "key": "value",
        "number": 123,
        "nested": {"a": 1}
    }

    # Test Save
    FileService.save_yaml(data, str(file_path))
    
    assert file_path.exists()

    # Test Load (Manual check of content)
    with open(file_path, 'r', encoding='utf-8') as f:
        loaded_data = yaml.safe_load(f)
    
    assert loaded_data == data

def test_file_service_load_config(tmp_path):
    # Setup a valid config YAML
    file_path = tmp_path / "valid_config.yaml"
    config_data = {
        "telegram": {
            "api_id": 12345,
            "api_hash": "test_hash",
            "session_name": "test_session"
        },
        "folder_manager": {
            "export_enabled": True,
            "folders": {}
        }
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f)

    # Test Load
    config = FileService.load_config(str(file_path))
    
    assert isinstance(config, AppConfig)
    assert config.telegram.api_id == 12345
    assert config.telegram.api_hash == "test_hash"
    assert config.folder_manager.export_enabled is True
