# Configuration (config.yaml)

The `config.yaml` file is used to configure the system settings. It must be located in the project root.

## File Structure

The file must follow this structure:

### 1. Telegram (`telegram`)
Settings for connecting to the Telegram API.
- `api_id`: Your API ID (number or string).
- `api_hash`: Your API Hash (string).
- `app_title`: (Optional) Application title.
- `app_short_name`: (Optional) Application short name.
- `session_name`: (Optional) Session file name. Default is `session`.

### 2. Proxy (`proxy`) - *Optional*
Proxy settings for connecting.
- `type`: Proxy type: `socks5`, `http`, or `mtproto`.
- `server`: Server address.
- `port`: Server port.
- `secret`: (Optional) Secret for `mtproto`.
- `username`: (Optional) Username.
- `password`: (Optional) Password.

### 3. Folder Manager (`folder_manager`)
Settings for automated sorting.
- `export_enabled`: Enable exporting structure to YAML (`true`/`false`).
- `export_filename`: Filename for the export. Default is `folders_export.yaml`.
- `dry_run`: Test mode without making changes to Telegram (`true`/`false`).
- `warn_on_duplicates`: Warn if a chat is assigned to multiple folders.
- `unmatched_strategy`: What to do with chats that don't match any folder (`ignore` - ignore, or other strategies).
- `folders`: Dictionary of folders. Key is the folder name, value is the folder settings:
    - `include_patterns`: List of patterns (regex or substrings) for including chats.
    - `exclude_patterns`: List of patterns for excluding chats.

### 4. Summarizer (`summarizer`) - *Optional*
Settings for LLM interaction.
- `model`: Model name (e.g., `gpt-4`, `llama3`, or the model name in LM Studio).
- `temperature`: Temperature (0.0 - 1.0).
- `max_tokens`: Maximum tokens in the response.
- `timeout_seconds`: Request timeout.
- `base_url`: API URL (e.g., for LM Studio: `http://localhost:1234/v1`).
- `auth_type`: Authentication type (`credentials` - via API key, or others).
- `gigachat_client_id`: (For GigaChat) Client ID.
- `gigachat_secret`: (For GigaChat) Secret.
- `gigachat_token`: (For GigaChat) Token.
- `system_prompt`: Instruction for the model.
- `user_prompt_template`: User prompt template.

## Example config.yaml

```yaml
telegram:
  api_id: 123456
  api_hash: "abcdef1234567890abcdef1234567890"
  session_name: "my_session"

# proxy:
#   type: "socks5"
#   server: "127.0.0.1"
#   port: 9050

folder_manager:
  export_enabled: true
  dry_run: true
  warn_on_duplicates: true
  folders:
    "News":
      include_patterns:
        - ".*news.*"
        - ".*news.*"
      exclude_patterns:
        - ".*spam.*"
    "Crypto":
      include_patterns:
        - "crypto"
        - "bitcoin"

summarizer:
  model: "local-model"
  base_url: "http://localhost:1234/v1"
  gigachat_client_id: "your_id"
  gigachat_secret: "your_secret"
```
