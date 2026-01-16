---
name: google-drive-management
description: Manages Google Drive operations including listing files, searching, reading file content, creating files, and downloading files.
---

# Google Drive Management Skill

This skill provides comprehensive Google Drive operations through the Google Drive API.

## Important: Working Directory

**Always run commands from the skill directory:**
```bash
cd "../../.claude/skills/google-drive-management"
```

## Available Functions

### 1. List Files
Lists recent files from Google Drive with formatted output including file icons.

```bash
cd "../../.claude/skills/google-drive-management" && python -c "from drive_helper import list_files; print(list_files())"
```

Or in Python:
```python
from drive_helper import list_files

# List last 10 files (default)
result = list_files()
print(result)

# List specific number of files
result = list_files(limit=20)
print(result)
```

Returns formatted list with icons:
- 📄 for files
- 📁 for folders  
- ☁️ for Google Docs/Sheets/Slides

### 2. Search Files
Searches for files by name in Google Drive.

```bash
cd "../../.claude/skills/google-drive-management" && python -c "from drive_helper import search_files; print(search_files('report'))"
```

Or in Python:
```python
from drive_helper import search_files

# Search for files containing "report" in name
result = search_files("report")
print(result)

# Search for specific file name
result = search_files("presentation.pptx")
print(result)
```

Returns list of matching files with IDs and types.

### 3. Read File Content
Reads and returns the text content of various file types:
- Plain text files (.txt, .py, .json, etc.)
- PDF files (requires PyPDF2)
- Google Docs (exported as text)
- Google Sheets (exported as CSV)

```bash
cd "../../.claude/skills/google-drive-management" && python -c "from drive_helper import read_file_content; print(read_file_content('FILE_ID'))"
```

Or in Python:
```python
from drive_helper import read_file_content

# Read file by ID
file_id = "1abc...xyz"
content = read_file_content(file_id)
print(content)
```

**Note:** Requires `PyPDF2` package for PDF support. Install with:
```bash
pip install PyPDF2
```

### 4. Create Text File
Creates a new text file on Google Drive with specified content.

```python
from drive_helper import create_text_file

# Create new text file
name = "my_document.txt"
content = "This is the file content.\nIt can have multiple lines."
result = create_text_file(name, content)
print(result)  # Returns file ID
```

### 5. Download File
Downloads a file from Google Drive to local disk.

```python
from drive_helper import download_file

# Download to specific path
file_id = "1abc...xyz"
destination = "C:/Downloads/document.pdf"
result = download_file(file_id, destination)
print(result)

# Download to current directory (uses original filename)
result = download_file(file_id, ".")
print(result)
```

Automatically handles:
- Google Docs → exported as PDF
- Google Sheets → exported as XLSX
- Regular files → downloaded directly

## Google Drive Search Operators

When using `search_files()`, you can use these search patterns:
- Exact match: `"exact filename"`
- Contains: `report` (finds all files with "report" in name)
- Multiple words: `meeting notes` (finds files with both words)

## Authentication

This skill requires:
- `credentials.json` - OAuth client credentials
- `token_drive.json` - User authentication token (auto-generated on first run)

Both files must be present in the skill directory.

## Error Handling

All functions include comprehensive error handling:
- Missing credentials → Clear error message
- Invalid file ID → Returns error description
- Network issues → Detailed error info
- Missing PyPDF2 for PDF → Instructions to install

## Usage Examples

**Example 1: Find and read a document**
```python
# Search for the file
from drive_helper import search_files, read_file_content

results = search_files("annual report")
print(results)  # Shows file IDs

# Read the content
file_id = "extracted_from_search_results"
content = read_file_content(file_id)
print(content)
```

**Example 2: Create and verify new file**
```python
from drive_helper import create_text_file, list_files

# Create file
result = create_text_file("meeting_notes.txt", "Meeting on 2024-01-15\nAttendees: ...")
print(result)

# Verify it appears
files = list_files(limit=5)
print(files)
```

**Example 3: Download multiple files**
```python
from drive_helper import search_files, download_file

# Find all PDFs with "invoice"
results = search_files("invoice")
# Extract file IDs from results and download each
# file_id = ... (extract from results)
# download_file(file_id, "C:/Invoices/")
```
