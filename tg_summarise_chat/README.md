## Usage

This module is intended to be used as part of the main application via the `tg_tool.py` entry point.

### 1. Installation
Ensure you have all dependencies installed from the root directory:

```bash
pip install -r requirements.txt
```

### 2. Running summarization

```bash
python tg_tool.py --summarize <chat_id_or_username>
```

**Example:**
```bash
python tg_tool.py --summarize @my_important_chat
```
OR
```bash
python tg_tool.py --summarize -100123456789
```
