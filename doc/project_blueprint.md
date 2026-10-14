# Project Blueprint: Telegram Manager System

**Version:** 2.0 (Refactored)
**Target Audience:** AI Agents / Developers
**Purpose:** This document serves as the primary context and architectural source of truth for rapid refactoring, feature expansion, or debugging. It defines the structure, dependencies, and design principles of the system.

---

## 🏗 Architecture Overview

The project follows a **Layered Modular Architecture** with a strict **Separation of Concerns**. The architecture is divided into three primary layers:

1.  **Orchestration Layer (`run.py`)**: The single entry point. It handles command-line arguments, initializes the configuration, and dispatches execution to the appropriate functional module.
2.  **Infrastructure Layer (`core/`)**: Contains low-level services that interact with external systems (Telegram API, File System) and centralizes cross-cutting concerns (Configuration, Utilities).
3.  **Business Logic Layer (`tg_folder_manager/`, `tg_summarise_chat/`)**: Contains pure domain logic. These modules are "agnostic" to the specific implementation of the infrastructure, receiving services via **Dependency Injection**.

### Dependency Graph
```text
[run.py] 
   ├──> [core/config.py] (Settings/Validation)
   ├──> [core/telegram_service.py] (Telegram API Wrapper)
   ├──> [core/file_service.py] (File I/O)
   ├──> [core/utils.py] (Helpers)
   ├──> [tg_folder_manager/] (Folder logic) --> depends on core/
   └──> [tg_summarise_chat/] (Summarization logic) --> depends on core/
```

---

## 🧩 Module Breakdown

### 1. Core Infrastructure (`core/`)
*   **`config.py`**: The single source of truth for all application settings. Uses **Pydantic** for strict schema validation.
    *   *Key Models:* `AppConfig`, `TelegramCredentials`, `ProxyConfig`, `LLMConfig`, `FolderManagerSettings`.
*   **`telegram_service.py`**: A high-level wrapper for `Telethon`. Manages session lifecycle (`__aenter__`/`__aexit__`) and provides simplified methods for dialogs, filters, and messages.
*   **`file_service.py`**: Abstracts YAML loading/saving and configuration management.
*   **`utils.py`: General utility functions (e.g., proxy URL construction).

### 2. Folder Manager Module (`tg_folder_manager/`)
*   **Responsibility**: Automating Telegram folder organization.
*   **Core Logic**:
    *   Matching chats to folders using regex/substrings (`matcher.py`).
    *   Determining duplicate chats across folders.
    *   Executing movements (add/remove from folders) via the Telegram service.
*   **Domain Models**: `ChatInfo`, `FolderInfo`, `ChatDuplicateInfo`.

### 3. Summarizer Module (`tg_summarise_chat/`)
*   **Responsibility**: Generating daily message summaries using LLMs.
*   **Workflow**:
    1.  `extractor.py`: Fetches messages for a specified period (default: 1 day) and formats them for LLM consumption.
    2.  `summarizers.py`: Communicates with LLM APIs (LM Studio/GigaChat).
    3.  `tg_summarise_chat.py`: Orchestrates the extraction and summarization process.

#### **LLM Prompt Customization**
The summarization logic allows customizing the LLM's behavior via `config.yaml`. This is achieved through two new parameters in the `summarizer` section:

- `system_prompt`: (String) Defines the persona and instructions for the LLM.
- `user_prompt_template`: (String) A template for the user message. It must include the `{text}` placeholder where the actual chat messages will be injected.

**Example configuration (`config.yaml`):**
```yaml
summarizer:
  model: "gpt-4"
  base_url: "http://localhost:1234"
  temperature: 0.7
  max_tokens: 2048
  timeout_seconds: 60
  system_prompt: "You are a professional assistant. Summarize the following dialogue in Russian, highlighting key points and decisions."
  user_prompt_template: "Please provide a summary of the following text: {text}"
```

---

## ⚙️ Configuration & Data Flow

1. **Configuration Flow**: `config.yaml` + `.env` $\rightarrow$ `core.config (Pydantic)` $\rightarrow$ `Dependency Injection` $\rightarrow$ `Business Modules`. (Detailed guide: [doc/CONFIGURATION-en.md](doc/CONFIGURATION-en.md))
2. **Telegram Flow**: `run.py` $\rightarrow$ `core.telegram_service` $\rightarrow$ `Telethon` $\rightarrow$ `Telegram API`.
3. **Command Flow**: `CLI Args` $\rightarrow$ `run.py` $\rightarrow$ `Module Execution`.

---

## 🛠 Agent Guidelines for Refactoring/Expansion

When acting on this project, the following rules must be observed:

1. **Strict Dependency Rule**: Business logic modules (`tg_...`) must **NEVER** instantiate `TelegramClient` directly. They must receive a `TelegramService` instance via their `__init__` method.
2. **Configuration Rule**: Do not use `os.getenv` or `yaml.safe_load` inside business logic. Use the validated `AppConfig` object provided by `core.config`.
3. **Single Responsibility**: If a change requires updating how Telegram communicates, modify `core/telegram_service.py`. If a change requires changing *how* a summary is formatted, modify `tg_summarise_chat/extractor.py`.
4. **Error Handling**: Infrastructure errors (e.g., connection loss) should be raised by `core` and caught/handled by the orchestration layer or the specific business module.
5. **No Model Duplication**: All shared data structures (like `ProxyConfig`) must reside in `core/config.py`. Do not redefine them in local modules.

---
*End of Blueprint*
<EOF>