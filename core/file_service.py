import yaml
import logging
from typing import Any, Dict
from core.config import AppConfig

logger = logging.getLogger(__name__)

class FileService:
    @staticmethod
    def load_config(path: str) -> AppConfig:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return AppConfig(**data)

    @staticmethod
    def save_yaml(data: Dict[str, Any], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
