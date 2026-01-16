---
name: gmail-management
description: Gmail operations - read/send emails, search inbox. Always cd to skill directory first.
---

# Gmail Management

## Working Directory
**REQUIRED:** `cd "../../.claude/skills/gmail-management"` before all operations.

## Functions

### read_recent_emails(count=10)
Reads last N emails. Returns list with 'from', 'subject', 'body', 'date'.
```bash
cd "../../.claude/skills/gmail-management" && python -c "from gmail_helper import read_recent_emails; print(read_recent_emails(5))"
```

### send_email(to_email, subject, body)
Sends email.
```bash
cd "../../.claude/skills/gmail-management" && python -c "from gmail_helper import send_email; send_email('user@example.com', 'Subject', 'Body')"
```

### send_email_with_attachment(to_email, subject, body, attachment_path)
Sends email with file attachment.

### search_emails(query, count=10)
Searches emails using Gmail query syntax.

**Query Syntax:**
- `from:user@example.com` - From sender
- `subject:keyword` - Subject contains
- `has:attachment` - Has attachment
- `is:unread` - Unread only
- `after:2024/01/01` - After date
- Combine: `from:john subject:report`

## Auth
First use opens browser for OAuth. Token saved to `token.json`.
