import asyncio
import logging
import yaml
from abc import ABC, abstractmethod
from typing import Optional, List
import httpx
from datetime import datetime, timedelta
from urllib.parse import urlparse

from core.config import LLMConfig, ProxyConfig
from core.utils import build_http_proxy

logger = logging.getLogger(__name__)

class BaseSummarizer(ABC):
    def __init__(self, config: LLMConfig, proxy: Optional[ProxyConfig] = None, verbose: bool = False):
        self.config = config
        self.proxy = proxy
        self.verbose = verbose

    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass

class LMStudioSummarizer(BaseSummarizer):
    def __init__(self, config: LLMConfig, proxy: Optional[ProxyConfig] = None, verbose: bool = False):
        super().__init__(config, proxy, verbose)

    async def summarize(self, text: str) -> str:
        if not text:
            raise ValueError("Текст пуст")

        proxy_url = build_http_proxy(self.proxy)

        # Bypass proxy for local LLM servers
        if proxy_url and self.config.base_url:
            parsed = urlparse(self.config.base_url)
            if parsed.hostname and parsed.hostname.lower() in ["localhost", "127.0.0.1", "[::1]"]:
                proxy_url = None

        try:
            logger.info("📝 Отправляю сообщения в LM Studio для суммаризации...")
            async with httpx.AsyncClient(proxy=proxy_url, timeout=self.config.timeout_seconds) as client:
                url = f"{self.config.base_url}/v1/chat/completions"
                payload = {
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": self.config.system_prompt},
                        {"role": "user", "content": self.config.user_prompt_template.format(text=text)}
                    ],
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }
                
                if self.verbose:
                    logger.info(f"--- DEBUG: Payload sent to LLM ---\n{payload}\n-----------------------------------")
                
                response = await client.post(url, json=payload)
                
                if self.verbose:
                    logger.info(f"--- DEBUG: Raw response status: {response.status_code} ---")
                    logger.info(f"--- DEBUG: Raw response body: {response.text} ---")

                if response.status_code != 200:
                    raise Exception(f"Ошибка {response.status_code}: {response.text}")
                
                result = response.json()
                if 'choices' not in result or not result['choices']:
                    raise Exception("Unexpected response format: 'choices' not found in response")
                
                message = result['choices'][0].get('message', {})
                content = message.get('content', "").strip()
                reasoning = message.get('reasoning_content', "").strip()

                if not content and reasoning:
                    logger.warning("⚠️ Model's 'content' is empty, but 'reasoning_content' contains data. Returning reasoning content.")
                    return reasoning

                if not content:
                    finish_reason = result['choices'][0].get('finish_reason')
                    raise Exception(f"Model returned an empty content. Finish reason: {finish_reason}")

                return content
                
        except Exception as e:
            logger.error(f"✗ Ошибка LM Studio: {e}")
            raise

class GigaChatSummarizer(BaseSummarizer):
    def __init__(self, config: LLMConfig, proxy: Optional[ProxyConfig] = None, verbose: bool = False):
        super().__init__(config, proxy, verbose)
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
