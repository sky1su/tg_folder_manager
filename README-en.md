[**English**](README-en.md) | [**Русский**](README.md)

# Telegram Folder Manager

Telegram folder management automation. The script allows automatically sorting chats and channels based on patterns, as well as creating brief summaries of dialogues using LLMs (LM Studio, GigaChat).

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- 📂 **Folder Management**: Automatic chat sorting by patterns (regex or substring) with exclusion support.
- 🛡 **Safety**: `dry-run` mode for previewing changes without applying them in Telegram.
- 📝 **Summarization**: LLM integration to create chat summaries for a specific period.
- 📊 **Export**: Ability to export folder structure to a YAML file.
- 🔍 **Validation**: Strict configuration validation using Pydantic.

## Quick Start

### Requirements

- Python 3.12+
- Telegram account (API ID and API Hash from [my.telegram.org](https://my.telegram.org))

### Installation

```bash
# Clone the repository
git clone https://github.com/sky1su/tg_folder_manager.git
cd tg_folder_manager

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # For Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running

To run the main module, use:

```bash
# Run using your configuration
python tg_tool.py
```

## Configuration

Settings are stored in the `config.yaml` file.

| Section | Required | Description | Example |
|---|---:|---|---|
| `telegram` | Yes | API settings (ID, Hash, session) | `api_id: 123456` |
| `folder_manager` | Yes | Sorting rules, patterns, dry_run mode | `dry_run: true` |
| `summarizer` | No | LLM settings (model, base_url, prompts) | `model: "gemma-4"` |

> [!IMPORTANT]
> Never add real `api_id`, `api_hash`, or tokens to the repository. Use `config.yaml.example` as a template.

## Usage

### Folder Management
The script automatically analyzes your chats and distributes them into folders according to the rules in `config.yaml`.

### Summarization
The `tg_summarise_chat` module collects messages and sends them to an LLM to create a brief report.

## Architecture

The system is built based on a **Layered Modular Architecture** with **Separation of Concerns (SoC)**:

```text
[ CLI / User ] -> [ tg_tool.py ] -> [ Infrastructure (core/) ]
                                          |
                                          -> [ Business Logic (modules/) ]
                                                 |
                                                 -> [ Telegram / LLM / Filesystem ]
```
Detailed architecture is available in [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md).

## Testing

```bash
# Run tests (if configured)
pytest
```

## Development

The project follows modularity rules: the business logic in the `tg_folder_manager` and `tg_summarise_chat` modules must be completely independent of the `core` infrastructure layer.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).  
Before creating a PR: make sure you have updated the configuration files and documentation if you changed the system behavior.

## Security

Do not publish vulnerabilities in Issues. Reporting procedure: [SECURITY.md](SECURITY.md).

## License

The project is licensed under [MIT](LICENSE).
