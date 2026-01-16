---
name: outlook
description: Microsoft Outlook skill for reading and sending emails via Microsoft Graph API. Use when user wants to work with Outlook emails, calendar or contacts.
---

# Outlook Skill

## Overview

This skill enables:
- Reading emails from Outlook mailbox
- Sending emails
- Searching in emails
- Working with calendar (optional)

## Prerequisites

1. Registered application in Azure Portal (Microsoft Entra ID)
2. Python package: `msal`, `requests`
3. Environment variable: `MICROSOFT_CLIENT_ID` in `.env` file

## Important: Working Directory

**Always run commands from the skill directory:**
```bash
cd "../../.claude/skills/outlook"
```

## Authentication

**Two authentication methods:**

### 1. Via Application Settings (Recommended for logged-in users)
- Go to Settings page in the application
- Click "Connect" button in Microsoft Outlook section
- Login with your Microsoft account in popup window
- Token is automatically saved to database per-user

### 2. Local File Authentication (For testing)

```bash
cd "../../.claude/skills/outlook" && python outlook_helper.py --auth-browser
```

This opens browser for login. Token is saved to local file `.outlook_token_cache.json`.

## Token Loading Priority

The helper automatically loads tokens in this order:
1. **Database** (if `AGENT_USER_ID` environment variable is set)
2. **Local file** (fallback for manual testing)

### Reading emails

```bash
cd "../../.claude/skills/outlook" && python -c "from outlook_helper import get_emails; emails = get_emails(count=5); print(emails)"
```

### Sending email

```bash
cd "../../.claude/skills/outlook" && python -c "from outlook_helper import send_email; send_email('recipient@example.com', 'Subject', 'Email body')"
```

### Searching

```bash
cd "../../.claude/skills/outlook" && python -c "from outlook_helper import search_emails; results = search_emails('invoice'); print(results)"
```

## Available Functions

| Function | Description |
|--------|-------|
| `get_emails(count=10, folder='inbox')` | Retrieves last N emails |
| `send_email(to, subject, body, cc=None)` | Sends email |
| `search_emails(query, count=10)` | Searches emails |
| `get_calendar_events(days=7)` | Retrieves calendar events |
| `create_calendar_event(...)` | Creates event |

## Troubleshooting

**"Token expired"** - Run `python outlook_helper.py --auth` again

**"Insufficient privileges"** - Verify application permissions in Azure Portal
