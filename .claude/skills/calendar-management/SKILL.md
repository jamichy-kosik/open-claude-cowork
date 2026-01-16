---
name: calendar-management
description: Google Calendar operations - create/list/update events. Always cd to skill directory first.
---

# Calendar Management

## Working Directory
**REQUIRED:** `cd "../../.claude/skills/calendar-management"` before all operations.

## Functions

### list_events(count=10)
Lists upcoming calendar events.
```bash
cd "../../.claude/skills/calendar-management" && python -c "from calendar_helper import list_events; print(list_events(10))"
```

### create_event(summary, start_time, end_time, description="", attendees=[])
Creates calendar event. Times in ISO 8601 format (2024-12-25T14:00:00).

### update_event(event_id, summary=None, start_time=None, end_time=None)
Updates existing event.

### delete_event(event_id)
Deletes event.

### search_events(query, count=10)
Searches events by keyword.

## Auth
First use opens browser for OAuth. Token saved to `token.json`.
