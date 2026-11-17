import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from tg_summarise_chat.summarizers import GigaChatSummarizer
from core.config import LLMConfig

@pytest.mark.asyncio
async def test_gigachat_summarizer_oauth_success():
    config = LLMConfig(
        model="gigachat",
        auth_type="credentials",
        gigachat_client_id="my_id",
        gigachat_secret="my_secret"
    )
    summarizer = GigaChatSummarizer(config)

    oauth_response_data = {"access_token": "fake_token"}
    completion_response_data = {
        "choices": [{
            "message": {"content": "Giga Summary"}
        }]
    }

    # Создаем мок для клиента
    mock_client = AsyncMock()
    
    # Настраиваем последовательные ответы для post(): сначала OAuth, затем Summarize
    mock_response_oauth = MagicMock()
    mock_response_oauth.status_code = 200
    mock_response_oauth.json.return_value = oauth_response_data

    mock_response_completion = MagicMock()
    mock_response_completion.status_code = 200
    mock_response_completion.json.return_value = completion_response_data

    mock_client.post.side_effect = [mock_response_oauth, mock_response_completion]

    with patch("httpx.AsyncClient") as MockAsyncClient:
        MockAsyncClient.return_value.__aenter__.return_value = mock_client
        MockAsyncClient.return_value.__aexit__.return_value = None

        result = await summarizer.summarize("some text")
        assert result == "Giga Summary"
        assert mock_client.post.call_count == 2

@pytest.mark.asyncio
async def test_gigachat_summarizer_auth_failure():
    config = LLMConfig(
        model="gigachat",
        auth_type="credentials",
        gigachat_client_id="bad_id",
        gigachat_secret="bad_secret"
    )
    summarizer = GigaChatSummarizer(config)

    mock_client = AsyncMock()
    mock_response_fail = MagicMock()
    mock_response_fail.status_code = 401
    mock_response_fail.text = "Unauthorized"
    
    mock_client.post.return_value = mock_response_fail

    with patch("httpx.AsyncClient") as MockAsyncClient:
        # Настраиваем так, чтобы async with MockAsyncClient() возвращал mock_client
        MockAsyncClient.return_value.__aenter__.return_value = mock_client
        MockAsyncClient.return_value.__aexit__.return_value = None

        with pytest.raises(Exception, match="Auth failed 401"):
            await summarizer.summarize("text")
