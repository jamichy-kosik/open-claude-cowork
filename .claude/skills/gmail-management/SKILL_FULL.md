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

```bash
cd "../../.claude/skills/gmail-management" && python -c "from gmail_helper import search_emails; print(search_emails('is:unread', count=5))"
```

Or in Python:
```python
from gmail_helper import search_emails

# Search by sender
results = search_emails(query="from:someone@example.com", count=3)

# Search by subject
results = search_emails(query="subject:meeting", count=5)

# Search unread emails
results = search_emails(query="is:unread", count=10)
```

## Available Functions

### read_recent_emails(count=5)
Retrieves the most recent emails from Gmail inbox.

**Parameters:**
- `count` (int): Number of emails to retrieve (default: 5)

**Returns:** List of email dictionaries with keys: `from`, `subject`, `date`, `body`

### send_email(to_email, subject, body)
Sends a plain text email.

**Parameters:**
- `to_email` (str): Recipient email address
- `subject` (str): Email subject line
- `body` (str): Email body text

**Returns:** Success message

### send_email_with_attachment(to_email, subject, body, attachment_path)
Sends an email with a file attachment.

**Parameters:**
- `to_email` (str): Recipient email address
- `subject` (str): Email subject line  
- `body` (str): Email body text
- `attachment_path` (str): Path to file to attach

**Returns:** Success message

### search_emails(query, count=3)
Searches Gmail using Gmail search syntax.

**Parameters:**
- `query` (str): Gmail search query (e.g., "from:user@example.com", "subject:report")
- `count` (int): Max results to return (default: 3)

**Returns:** List of matching email dictionaries

## Gmail Search Query Syntax

Common search operators:
- `from:email@example.com` - Emails from specific sender
- `to:email@example.com` - Emails to specific recipient
- `subject:keyword` - Emails with keyword in subject
- `is:unread` - Unread emails only
- `is:read` - Read emails only
- `has:attachment` - Emails with attachments
- `after:2024/01/01` - Emails after specific date
- `before:2024/12/31` - Emails before specific date

Combine operators with spaces (AND) or OR:
- `from:john subject:meeting` - From John AND about meeting
- `from:john OR from:jane` - From either John or Jane

## Error Handling

All functions handle common errors:
- Missing credentials file
- Authentication failures  
- Network issues
- Invalid email addresses
- Missing attachment files

Errors return descriptive messages to help diagnose issues.

## Authentication Flow

On first use:
1. Script checks for `token.json`
2. If missing, opens browser for Google OAuth
3. User authorizes access
4. Token saved to `token.json` for future use

Subsequent uses load token automatically.

## Best Practices

**When reading emails:**
- Use specific counts to limit results
- Check body length before displaying (use `[:200]` for preview)
- Handle missing headers gracefully

**When sending emails:**
- Validate email addresses before sending
- Keep subjects clear and concise
- For mass sending, add delays between messages

**When searching:**
- Use specific queries to narrow results
- Combine operators for precise matches
- Test queries with small count first

## Workflow Example: Email Report

```python
# 1. Search for report emails
reports = search_emails(query="subject:weekly report", count=3)

# 2. Process results
for email in reports:
    print(f"Report from {email['from']}: {email['subject']}")

# 3. Send summary
send_email(
    to_email="manager@company.com",
    subject="Weekly Reports Summary",
    body=f"Found {len(reports)} weekly reports..."
)
```

## Troubleshooting

**"Credentials not found"**
- Ensure `credentials.json` exists in working directory
- Download from Google Cloud Console if missing

**"Token expired"**
- Delete `token.json`
- Re-run to trigger new OAuth flow

**"Permission denied"**
- Check Gmail API scopes in credentials
- Ensure `gmail.modify` scope is enabled

**"Attachment not found"**
- Verify file path is absolute or relative to working directory
- Check file exists and is readable
