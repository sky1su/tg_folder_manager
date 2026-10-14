import asyncio
import logging
import yaml
from abc import ABC, abstractmethod
from typing import Optional, List
import httpx
from datetime import datetime, timedelta

from core.config import LLMConfig, ProxyConfig
from core.utils import build_http_proxy

logger = logging.getLogger(__name__)

class BaseSummarizer(ABC):
    def __init__(self, config: LLMConfig, proxy: Optional[ProxyConfig] = None):
        self.config = config
        self.proxy = proxy

    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass

class LMStudioSummarizer(BaseSummarizer):
    async def summarize(self, text: str) -> str:
        if not text:
            raise ValueError("Текст пуст")

        proxy_url = build_http_proxy(self.proxy)
        
        try:
            logger.info("📝 Отправляю сообщения в LM Studio для суммаризации...")
            async with httpx.AsyncClient(proxy=proxy_url, timeout=self.config.timeout_seconds) as client:
                url = f"{self.config.base_url}/v1/chat/completions"
                payload = {
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": (
                            "Ты профессиональный ассистент, который создает краткое резюме диалога. "
                            "Выделяй ключевые моменты, решения и действия. "
                            "Форматируй ответ с использованием маркированных списков. Ответ должен быть строго на русском языке."
                        )},
                        {"role": "user", "content": f"Создай краткое резюме:\n\n{text}"}
                    ],
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    raise Exception(f"Ошибка {response.status_code}: {response.text}")
                result = response.json()
                return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"✗ Ошибка LM Studio: {e}")
            raise

class GigaChatSummarizer(BaseSummarizer):
    def __init__(self, config: LLMConfig, proxy: Optional[ProxyConfig] = None):
        super().__init__(config, proxy)
        self._access_token = None
        self._token_expires_at = None

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        if self._access_token and self._token_expires_at and datetime.now() < self._token_expires_at:
            return self._access_token

        url = "https://ngw.devices.sberbank.ru/api/v2/oauth"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": "default-uuid"
        }

        import base64
        if self.config.auth_type == "credentials":
            creds = f"{self.config.gigachat_client_id}:{self.config.gigachat_secret}"
            encoded = base64.b64encode(creds.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
            data = {"scope": "GIGACHAT_API_PERS"}
        else:
            headers["Authorization"] = f"Bearer {self.config.gigachat_token}"
            data = {"scope": "GIGACHAT_API_PERS"}

        try:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code != 200:
                raise Exception(f"Auth failed {response.status_code}: {response.text}")

            auth_data = response.json()
            self._access_token = auth_data['access_token']
            # Simple expiry handling: add 1 hour
            self._token_expires_at = datetime.now() + timedelta(hours=1)
            return self._access_token
        except Exception as e:
            logger.error(f"✗ Ошибка авторизации GigaChat: {e}")
            raise
