[Русский](README.md) | [**English**](README-en.md)
# Telegram Folder Manager

Automation of Telegram folder management. The script allows you to automatically sort chats and channels into folders based on patterns and exclusions, as well as export the folder structure to a YAML file. It also supports chat summarization via LLM.

***

## Features

### 📂 Folder Management
- ✅ Automatic sorting of chats into folders based on patterns
- ✅ Support for exclude patterns for precise control
- ✅ Define primary folder — one chat in only one folder
- ✅ Automatic removal from other folders when moving
- ✅ **Dry-run mode** — check changes without applying them to Telegram
- ✅ Export folder structure and group list to YAML file
- ✅ Count and display number of groups in each folder
- ✅ Flexible strategies for handling unmatched chats
- ✅ Duplicate detection (chats in multiple folders)
- ✅ Support for regular expressions and simple substrings

### 📝 Chat Summarization
- ✅ Create brief summaries of the current day's messages
- ✅ Support for various LLMs (LM Studio, GigaChat)
- ✅ Formatting messages for optimal LLM context

***

## Requirements

- Python 3.12+
- Telegram account
- API ID and API Hash from https://my.telegram.org

***

## Installation

1. **Clone the repository:**

```
git clone https://github.com/sky1su/tg_folder_manager.git
cd tg_folder_manager
```

2. **Install dependencies:**

```
pip install -r requirements.txt
```

***

## Usage

### 1. Configuration
Create a `config.yaml` file (you can use the provided example as a template) and fill in your API ID, API Hash, and LLM/Proxy settings.
Supported proxy types: socks5, http, mtproto.

### 2. Folder Management (Default)
Run the script to automatically sort chats:
```
python run.py
```

### 3. Chat Summarization
To create a summary of messages for a specific period, use the `--summarize` flag. Optionally, use `--days <number>` to specify the number of days (default: 1):

```
# Summary for today (default)
python run.py --summarize <chat_id_or_username>

# Summary for the last 3 days
python run.py --summarize <chat_id_or_username> --days 3
```

***

## Development
The project is built on the principles of modularity and separation of concerns. All infrastructure components (Telegram API, file operations) are encapsulated in the `core/` package.
