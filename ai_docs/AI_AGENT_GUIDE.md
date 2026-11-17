# AI Agent Guide: Telegram Folder Manager

This document provides a comprehensive technical overview of the Telegram Folder Manager project, specifically designed for AI agents to understand, maintain, and extend the codebase.

## 🎯 Project Purpose
The application serves two primary goals:
1. **Automated Folder Management**: Automatically sorts Telegram chats and channels into folders based on user-defined regex/substring patterns.
2. **Chat Summarization**: Extracts recent messages from a specific chat and uses an LLM (via LM Studio or GigaChat) to create a concise summary.

## 🏗 Architecture Overview
The project follows a **Layered Modular Architecture** with a strict **Separation of Concerns (SoC)**.

### Layer Diagram
`[ CLI (tg_tool.py) ]` $\rightarrow$ `[ Infrastructure (core/) ]` $\rightarrow$ `[ Business Logic (modules/) ]` $\rightarrow$ `[ External APIs ]`

### Component Breakdown

#### 1. Orchestration Layer (`tg_tool.py`)
- **Role**: System entry point and lifecycle manager.
- **Responsibilities**:
    - CLI argument parsing (`argparse`).
    - Global logging configuration.
    - Loading configuration via `FileService`.
    - Initializing the `TelegramService` context manager.
    - Routing execution to either `TelegramFolderManager` or `SummarizerApp`.

#### 2. Infrastructure Layer (`core/`)
This layer abstracts technical details and provides shared services.
- **`config.py`**: Uses **Pydantic** to define the system's configuration schema.
    - `AppConfig`: Root configuration object.
    - `TelegramCredentials`: API ID, Hash, and session settings.
    - `FolderManagerSettings`: Rules for folder organization.
    - `LLMConfig`: Settings for AI models (base URL, prompts, etc.).
- **`telegram_service.py`**: A wrapper for the **Telethon** library.
    - Manages the `TelegramClient` connection.
    - Provides simplified methods for common operations: `get_dialogs()`, `get_filters()`, `update_dialog_filter()`, `send_message()`.
    - Handles proxy configuration (SOCKS5, HTTP, MTProto).
- **`file_service.py`**: Standardized file operations, primarily for loading the YAML configuration.

#### 3. Business Logic Layer
Business modules are agnostic to the underlying API implementation; they depend on `TelegramService` via **Dependency Injection**.

##### **Module: Folder Manager (`tg_folder_manager/`)**
- **`tg_folder_manager.py`**: The main engine.
    - Fetches chats and existing folders.
    - Uses `ChatMatcher` to map chats to target folders based on patterns.
    - Calculates diffs (added/removed chats) and updates Telegram filters.
    - Supports `dry_run` mode (logs changes without applying them).
- **`matcher.py`**: Contains `ChatMatcher` logic.
    - Implements primary matching: `Exclude Patterns` $\rightarrow$ `Include Patterns`.
    - Supports both regex and simple substring matching.
- **`models.py`**: Internal data structures for chats and folders.

##### **Module: Chat Summarizer (`tg_summarise_chat/`)**
- **`tg_summarise_chat.py`**: The application wrapper.
    - Coordinates the extraction and summarization flow.
    - Selects the appropriate summarizer (`LMStudioSummarizer` vs `GigaChatSummarizer`) based on configuration.
- **`extractor.py`**: Handles message retrieval.
    - `get_messages_for_period`: Fetches messages within a specific time window.
    - `format_for_llm`: Converts raw Telethon messages into a clean text format for LLM consumption.
- **`summarizers.py`**: Implements LLM API clients.

---

## 🔄 Key Data Flows

### Folder Organization Flow
1. `tg_tool.py` $\rightarrow$ initializes `TelegramFolderManager`.
2. `TelegramFolderManager.organize_chats()` $\rightarrow$ `TelegramService.get_dialogs()` & `get_filters()`.
3. `TelegramFolderManager` $\rightarrow$ `ChatMatcher.match_primary()` (iterates through all chats and config patterns).
4. `TelegramFolderManager` $\rightarrow$ calculates changes $\rightarrow$ `TelegramService.update_dialog_filter()`.

### Summarization Flow
1. `tg_tool.py` $\rightarrow$ initializes `SummarizerApp`.
2. `SummarizerApp.run()` $\rightarrow$ `TelegramMessageExtractor.get_messages_for_period()`.
3. `TelegramMessageExtractor` $\rightarrow$ `TelegramService.client.iter_messages()`.
4. `SummarizerApp` $\rightarrow$ `Summarizer.summarize()` $\rightarrow$ External LLM API call.

---

## 🛠 Development Guidelines for AI Agents

### Adding a New Feature
- **New Infrastructure**: Add to `core/` (e.g., a new database service).
- **New Business Logic**: Create a new module in a separate directory or add to existing ones in `tg_folder_manager/` or `tg_summarise_chat/`.
- **Configuration**: Always add new settings to `core/config.py` (Pydantic model) and update `config.yaml.example`.
- **Entry Point**: Update `tg_tool.py` to expose the new functionality via CLI arguments.

### Modifying Existing Logic
- **Pattern Matching**: Modify `tg_folder_manager/matcher.py`.
- **LLM Prompting**: Modify `LLMConfig` in `core/config.py` or the specific summarizer class in `tg_summarise_chat/summarizers.py`.
- **Telegram API**: Modify `core/telegram_service.py` to add new Telethon wrappers.

### Testing
- Use `dry_run: true` in `config.yaml` when testing folder organization to avoid modifying your actual Telegram account.
- Run `pytest` (if tests are present in `tests/`) before committing changes.

## 📦 Dependencies
- **Telethon**: Telegram API client.
- **Pydantic**: Data validation and settings management.
- **PyYAML**: Configuration file parsing.
- **python-dotenv**: Environment variable management.
