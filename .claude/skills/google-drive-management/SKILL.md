---
name: google-drive-management
description: Google Drive operations - upload/download/list files. Always cd to skill directory first.
---

# Google Drive Management

## Working Directory
**REQUIRED:** `cd "../../.claude/skills/google-drive-management"` before all operations.

## Functions

### list_files(count=20, query="")
Lists files in Drive.
```bash
cd "../../.claude/skills/google-drive-management" && python -c "from drive_helper import list_files; print(list_files(20))"
```

### upload_file(file_path, folder_id=None)
Uploads file to Drive.

### download_file(file_id, destination_path)
Downloads file from Drive.

### create_folder(folder_name, parent_folder_id=None)
Creates new folder.

### search_files(query, count=20)
Searches files by name/content.

**Query Syntax:**
- `name contains 'report'` - Filename contains
- `'folder_id' in parents` - In specific folder
- `mimeType='application/pdf'` - Specific file type

## Auth
First use opens browser for OAuth. Token saved to `token.json`.
