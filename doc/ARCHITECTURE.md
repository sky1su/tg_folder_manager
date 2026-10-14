# Project Architecture: Telegram Automation System (v2.0)

## Overview
The system is a modular framework designed for Telegram automation. After a major refactoring in version 2.0, the project moved from a monolithic script-based approach to a **Layered Modular Architecture**. This architecture enforces a strict **Separation of Concerns (SoC)**, ensuring that business logic is independent of infrastructure and external APIs.

---

## 🏗 Architecture Layers

The system is divided into three distinct layers to ensure scalability, testability, and maintainability.

### 1. Orchestration Layer (`run.py`)
The highest level of the application. It acts as the "brain" that coordinates the startup and shutdown of the system.
- **Responsibilities:** 
    - Parsing command-line arguments.
    - Initializing the global configuration.
    - Instantiating the necessary services from the `core` and business modules.
    - Dispatching execution to the correct module (Folder Management or Summarization) based on user input.

### 2. Infrastructure Layer (`core/`)
The foundation of the system. It handles the "how" of interacting with the outside world (Telegram, Files, Environment).
- **Key Components:**
    - **`config.py`**: Centralized configuration management using **Pydantic**. It provides a single, validated source of truth for all application settings.
    - **`telegram_service.py`**: An abstraction layer for the **Telethon** library. It manages the `TelegramClient` lifecycle and provides high-level, simplified methods for the business logic to interact with the Telegram API.
    - **`file_service.py`**: Handles all filesystem operations (YAML serialization, file I/ing) in a standardized way.
    - **`utils.py`**: General-purpose utility functions used across the project.

### 3. Business Logic Layer (`tg_folder_manager/`, `tg_summarise_chat/`)
This layer contains the "what" — the actual rules and processes that define the application's value. These modules are **agnostic** to the underlying implementation of Telegram or files.

#### **Module: Telegram Folder Manager (`tg_folder_manager/`)**
*Focus: Automated chat organization.*
- **Logic:** Uses pattern matching and exclusion rules to determine which chats belong in which folders.
- **State Management:** Manages the mapping between chats and Telegram folders.
- **Execution Modes:** Supports a `dry-run` mode for safe testing of changes.

#### **Module: Chat Summarizer (`tg_summarise_chat/`)**
*Focus: Generative AI integration for chat summaries.*
* **Workflow:** 
    1. **Extraction:** Fetches and formats chat messages for LLM context.
    2. **Summarization:** Interacts with LLMs (via LM Studio or GigaChat) to generate summaries.

---

## 🛠 Design Principles & Patterns

### Dependency Injection (DI)
To ensure high testability and modularity, the system heavily uses **Dependency Injection**. Business logic modules do not create their own connections; instead, they receive pre-configured service instances (e.g., `TelegramService`) through their constructors.

### Separation of Concerns (SoC)
- **Infrastructure** handles *communication* (e.g., `TelegramClient.get_dialogs()`).
- **Business Logic** handles *decisions* (e.g., `if chat_title matches pattern then move`).
- **Orchestration** handles *lifecycle* (e.g., `client.start()`, `client.disconnect()`).

### Strict Configuration Flow
Configuration flows downwards:
`Environment/YAML` $\rightarrow$ `core.config (Pydantic)` $\rightarrow$ `Business Modules (via DI)`.
Direct access to `os.getenv` or raw file reading within business modules is strictly prohibited.

---

## Component Diagram (Conceptual)

```text
      [ CLI / User Input ]
               |
               v
      [ Orchestration (run.py) ]
               |
      +--------+-----------------------------+
      |                                     |
[ Infrastructure (core/) ]        [ Business Logic Layers ]
| - TelegramService               | - Folder Manager      |
| - Config (Pydantic)             | - Summarizer          |
| - FileService                   |                       |
+---------------------------------+-----------------------+
               |
               v
      [ External Systems ]
      (Telegram, LLMs, Filesystem)
```
