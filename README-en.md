[English](README-en.md) | [Русский](README.md)
# Telegram Folder Manager (English Translation)

Automation of Telegram folder management. The script allows you to automatically sort chats and channels into folders based on patterns and exclusions, as well as export the folder structure to a YAML file with dry-run mode support.

***

## Features

- ✅ Automatic sorting of chats into folders based on patterns
- ✅ Support for exclude patterns for precise control
- ✅ Define primary folder — one chat in only one folder
- ✅ Automatic removal from other folders when moving
- ✅ Dry-run mode — check changes without applying them to Telegram
- ✅ Export folder structure and group list to YAML file
- ✅ Count and display number of groups in each folder
- ✅ Flexible strategies for handling unmatched chats
- ✅ Duplicate detection (chats in multiple folders)
- ✅ Support for regular expressions and simple substrings
- ✅ Works as a Python module

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
pip install telethon python-dotenv PyYAML
```

Or using `requirements.txt`:

```
pip install -r requirements.txt
```

3. **Create a `.env` file in the project root:**

```
app_api_id=YOUR_API_ID
app_api_hash=YOUR_API_HASH
app_title=telegram_session
```


***

## Telegram Client Registration

### Getting API ID and API Hash

1. Open your browser and navigate to
[https://my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
    - Enter your phone number
    - Confirm login with the code from Telegram
3. Go to **API Development Tools** section
4. Create a new application:
    - **App title:** any name, for example `TG Folder Manager`
    - **Short name:** short unique name, for example `tgfolder`
    - Other fields can be filled arbitrarily
5. Copy the issued values:
    - **API ID**
    - **API Hash**
6. Add them to your project's `.env` file

> ⚠️ **Important:** These keys provide full access to your account. Never publish them publicly!

***

## Configuration

Create a `config.yaml` file in the project root:

```yaml
# Settings
settings:
    dry_run: false                          # Enable dry run (no changes to Telegram)
    export_enabled: true                    # Enable/disable export to YAML
    export_filename: folders_export.yaml    # Export file name

# Folder definitions
folders:
  Work:
    include_patterns:
      - work
      - project
      - работа
    exclude_patterns:
      - test
      - demo

  Crypto:
    include_patterns:
      - bitcoin
      - ethereum
      - крипто
    exclude_patterns:
      - testnet
      - тест

  Dev:
    include_patterns:
      - python
      - django
      - fastapi
    exclude_patterns:
      - old
      - archive
```


### Configuration Parameters

#### `settings` Section

| Parameter | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `dry_run` | boolean | `false` | Enable dry run mode (no changes applied to Telegram) |
| `export_enabled` | boolean | `false` | Enable folder structure export to YAML file |
| `export_filename` | string | `folders_export.yaml` | Export file name |

#### `folders` Section

For each folder:

- **include_patterns**: list of patterns (regex or substrings) to include chats in the folder
- **exclude_patterns**: list of exclusion patterns — if a chat matches, it will NOT be included in this folder

***

## Usage

### Normal Mode

```
python3 -m tg_folder_manage
```

The script will connect to Telegram and apply all changes according to the configuration.

### Dry-Run Mode (Trial Run)

To check changes without applying them to Telegram, set in `config.yaml`:

```
settings:
  dry_run: true
```

Then run:

```
python3 -m tg_folder_manage
```

In this mode:

- ✅ All operations are logged and marked with `[DRY RUN]`
- ✅ YAML export is performed (marked with `dry_run: true`)
- ✅ **No changes are applied to Telegram**
- ✅ Logs show which folders would be created/updated


### First Run

On first run, Telethon will request:

1. Phone number
2. Confirmation code from Telegram
3. Two-factor password (if enabled)

After that, a session file is created and re-entry is not required.

***

## Dry-Run Mode (Trial Run)

Dry-run mode is ideal for:

- ✅ Verifying configuration before applying
- ✅ Testing new patterns
- ✅ Planning changes
- ✅ Exporting current folder state


### Example dry-run output:

```
2025-10-23 14:37:00 - WARNING - ⚠️ DRY RUN MODE ENABLED - No changes will be applied to Telegram
2025-10-23 14:37:01 - INFO - 📊 Folder statistics BEFORE processing:
2025-10-23 14:37:01 - INFO -    📁 Work: 5 groups/channels
2025-10-23 14:37:01 - INFO -    📁 Crypto: 12 groups/channels
2025-10-23 14:37:01 - INFO -    📁 Dev: 8 groups/channels
2025-10-23 14:37:02 - INFO - ✚ [DRY RUN] Would create folder "Work" (ID=3, 7 chats)
2025-10-23 14:37:03 - INFO - ✎ [DRY RUN] Would update folder "Crypto" (12 chats)
2025-10-23 14:37:04 - INFO - − [DRY RUN] Would remove 2 chat(s) from "Dev" after moving to "Work"
2025-10-23 14:37:05 - INFO - 📊 Folder statistics AFTER processing:
2025-10-23 14:37:05 - INFO -    📁 Work: 7 groups/channels
2025-10-23 14:37:05 - INFO -    📁 Crypto: 12 groups/channels
2025-10-23 14:37:05 - INFO -    📁 Dev: 6 groups/channels
2025-10-23 14:37:06 - INFO - 📤 [DRY RUN] Exported 3 folders to file "folders_export.yaml"
```

Note that all operations are marked with `[DRY RUN]` and end with the word `Would`.

***

## Folder Structure Export

When export is enabled (`export_enabled: true`), after processing folders, a YAML file is automatically created with the current folder structure.

### Example exported file:

```
export_date: '2025-10-23T14:37:00.123456'
dry_run: false
folders:
  Work:
    folder_id: 2
    chats_count: 5
    chats:
    - id: 123456789
      title: Work Project Alpha
      type: megagroup
    - id: 987654321
      title: Development Team
      type: group
  
  Crypto:
    folder_id: 3
    chats_count: 12
    chats:
    - id: 111222333
      title: Bitcoin Discussion
      type: megagroup
    - id: 444555666
      title: Ethereum News
      type: channel
```


### Export fields:

- `export_date`: export date and time in ISO format
- `dry_run`: whether dry-run mode was used
- `folders`: dictionary of folders with their contents
    - `folder_id`: Telegram folder ID
    - `chats_count`: number of chats in the folder
    - `chats`: list of chats with ID, title, and type


### Chat types in export:

- `group` — regular group
- `megagroup` — supergroup
- `channel` — channel

***

## Working with Patterns

### Simple Substrings

```
include_patterns:
  - python
  - django
```


### Regular Expressions

```
include_patterns:
  - ^work.*project$  # Starts with "work" and ends with "project"
  - \d{4}            # Contains 4 consecutive digits
  - (dev|dev-team)   # Contains "dev" or "dev-team"
```


### Escaping Special Characters

If you need to search for a dot or other regex special character, use a backslash:

```
include_patterns:
  - d\.r\.           # Searches for exactly "d.r.", not "d" + any character + "r"
```

Without escaping `d.r.` would match "leader", "gift", etc.

### Exclusions

```
exclude_patterns:
  - test
  - demo
  - archive
```


***

## Unmatched Chats Handling Strategies

In the code, you can configure behavior for chats that don't match any pattern:

```
UnmatchedChatsStrategy.IGNORE            # Ignore (default)
UnmatchedChatsStrategy.MOVE_TO_FOLDER    # Move to "Other" folder
UnmatchedChatsStrategy.LOG_ONLY          # Log only
UnmatchedChatsStrategy.REMOVE_FROM_FOLDERS # Remove from all folders
```

Configuration in `__main__.py`:

```
async with TelegramFolderManager(
    unmatched_strategy=UnmatchedChatsStrategy.MOVE_TO_FOLDER,
    warn_on_duplicates=True
) as manager:
    await manager.organize_chats_by_config(config_path=config_path)
```


***

## Project Structure

```
tg_folder_manager/
├── tg_folder_manage/
│   ├── __init__.py
│   ├── __main__.py
│   └── tg_folder_manager.py
├── config.yaml
├── .env
├── requirements.txt
├── README.md
└── folders_export.yaml          # created automatically on export
```


***

## Logging

The script outputs detailed logs with emojis for clarity:

- ✔ Connection/disconnection
- ✚ Folder creation
- ✎ Folder updates
- − Chat removal
- ⚠ Duplicate detection
- 📊 Folder statistics
- 📤 Data export
- [DRY RUN] Operations in dry-run mode


### Example normal output:

```
2025-10-23 14:37:00 - INFO - ✔ Connected to Telegram
2025-10-23 14:37:01 - INFO - 📊 Folder statistics BEFORE processing:
2025-10-23 14:37:01 - INFO -    📁 Work: 5 groups/channels
2025-10-23 14:37:02 - INFO - ✎ Updated folder "Work" (7 chats)
2025-10-23 14:37:03 - INFO - − Removed 2 chat(s) from "Dev" after moving to "Work"
2025-10-23 14:37:04 - INFO - 📊 Folder statistics AFTER processing:
2025-10-23 14:37:04 - INFO -    📁 Work: 7 groups/channels
2025-10-23 14:37:05 - INFO - 📤 Exported 3 folders to file "folders_export.yaml"
2025-10-23 14:37:06 - INFO - ✔ Disconnected from Telegram
```


***

## Recommended Workflow

1. **Create configuration** in `config.yaml`
2. **Enable dry-run mode**: `dry_run: true`
3. **Run the script**: `python3 -m tg_folder_manage`
4. **Check logs** — verify that changes match expectations
5. **Disable dry-run**: `dry_run: false`
6. **Run the script again** — apply real changes

***

## Troubleshooting

### Error "API credentials not set"

Make sure the `.env` file is created and contains the correct values for `app_api_id` and `app_api_hash`.

### Error "FileNotFoundError: config.yaml"

The `config.yaml` file should be in the project root (at the same level as the `tg_folder_manage` folder).

### Logs not displaying

Make sure `logging.basicConfig()` is configured in `__main__.py` before running `asyncio.run()`.

### Chats are not being moved

1. Check pattern correctness in `config.yaml`
2. Make sure chat names match (case is not considered)
3. Check `exclude_patterns` — the chat may be excluded
4. Use `dry_run: true` to verify without applying changes

### Pattern with dot works incorrectly

If pattern `d.r.` matches "leader", escape the dots: `d\.r\.`

### Export is not created

Check that `export_enabled: true` is set in `config.yaml`

### Dry-run mode doesn't work

Make sure `dry_run: true` is specified in `settings` in the `config.yaml` file, not elsewhere

***

## Security

- ⚠️ Never publish the `.env` file with API keys
- ⚠️ Add `.env` and `*.session` to `.gitignore`
- ⚠️ API keys provide full access to your Telegram account
- ⚠️ Export file may contain sensitive information about your chats


### Example .gitignore:

```
.env
*.session
*.session-journal
folders_export.yaml
__pycache__/
*.pyc
.DS_Store
.venv/
venv/
```


***

## License

MIT License

***

## Support

If you have questions or issues, create an Issue in the project repository.

***

Built with [Telethon](https://github.com/LonamiWebs/Telethon), [python-dotenv](https://github.com/theskumar/python-dotenv), and [PyYAML](https://github.com/yaml/pyyaml)
<span style="display:none">[^1]</span>

<div align="center">⁂</div>

[^1]: README.md

