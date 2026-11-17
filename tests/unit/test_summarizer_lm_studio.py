import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import patch
from tg_summarise_chat.summarizers import LMStudioSummarizer
from core.config import LLMConfig

@pytest.mark.asyncio
async def test_lm_studio_summarizer_success():
    config = LLMConfig(
        model="test-model",
        base_url="http://localhost:1234/v1",
        user_prompt_template="Summary: {text}"
    )
    summarizer = LMStudioSummarizer(config)
    
    # Mock the response
    mock_response_data = {
        "choices": [{
            "message": {
                "content": "This is a summary"
            }
        }]
    }

    # We patch httpx.AsyncClient
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = mock_response_data
        
        result = await summarizer.summarize("some long text")
        
        assert result == "This is a summary"
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_lm_studio_summarizer_empty_text():
    config = LLMConfig(model="test-model")
    summarizer = LMStudioSummarizer(config)
    
    with pytest.raises(ValueError, match="Текст пуст"):
        await summarizer.summarize("")

@pytest.mark.asyncio
async def test_lm_studio_summarizer_error_response():
    config = LLMConfig(model="test-model", base_url="http://localhost:1234/v1")
    summarizer = LMStudioSummarizer(config)
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(status_code=500)
        mock_post.return_value.text = "Internal Server Error"
        
        with pytest.raises(Exception, match="Ошибка 500"):
            await summarizer.summarize("test")
