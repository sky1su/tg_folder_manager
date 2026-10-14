# tg_summarise_chat Module

A specialized module within the **Telegram Folder Manager** system designed to generate concise summaries of chat conversations using Large Language Models (LLM).

## Overview

The `tg_summarise_chat` module automates the process of:
- Fetching all messages from a specific Telegram chat for the current day.
- Formatting messages with sender information and timestamps.
- Sending the formatted text to a local (or remote) LLM (e.g., **LM Studio**, **GigaChat**) for summarization.
- Displaying the final summary directly in the console.

## Features

- 📱 **Smart Extraction**: Retrieves messages from the current day in the user's local timezone.
- 👤 **Human-Readable**: Converts Telegram IDs into names/usernames for better context.
- 🧠 **LLM Integration**: Ready-to-use integration with **LM Studio** (via OpenAI-compatible API) and **GigaChat**.
- ⚙️ **Configurable**: All LLM parameters (temperature, max tokens, timeout, base URL) are manageable via the central `config.yaml`.
- 🏗 **Modular Design**: Built using the `core` architecture, following strict separation of concerns.

## Architecture & Dependencies

This module is a component of the larger `tg_folder_manager` project. It relies on the `core` package for:
- **Telegram Connectivity**: via `core.telegram_service`.
- **Central Configuration**: via `core.config`.

## Configuration

Settings are managed through the central `config.yaml` file. Below is the required schema for the summarizer component:

```yaml
summarizer:
  model: "qwen/qwen2.5-7b" # Name of the model in LM Studio
  temperature: 0.3        # 0.0 to 1.0 (0.3 is recommended)
  max_tokens: 500         # Maximum length of the summary
  timeout_seconds: 3600   # Request timeout in seconds
  # base_url is optional, defaults to LM Studio standard if provided
```

*Note: API credentials for Telegram are provided via environment variables (`.env`).*

## Usage

This module is intended to be used as part of the main application via the `run.py` entry point.

### 1. Installation
Ensure you have all dependencies installed from the root directory:
```bash
pip install -r requirements.txt
```

### 2. Running Summarization
To generate a summary for a specific chat (by ID or username), use the `--summarize` flag:

```bash
python run.py --summarize <chat_id_or_username>
```

**Example:**
```bash
python run.py --summarize @my_important_chat
```
OR
```bash
python run.py --summarize -100123456789
```
