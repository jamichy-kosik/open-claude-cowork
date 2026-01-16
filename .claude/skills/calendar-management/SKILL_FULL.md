---
name: calendar-management
description: Manages Google Calendar operations including listing upcoming events and creating new calendar events.
---

# Google Calendar Management Skill

This skill provides Google Calendar operations through the Google Calendar API.

## Important: Working Directory

**Always run commands from the skill directory:**
```bash
cd "../../.claude/skills/calendar-management"
```

## Available Functions

### 1. List Upcoming Events
Lists the next N upcoming events from the primary calendar.

```bash
cd "../../.claude/skills/calendar-management" && python -c "from calendar_helper import list_upcoming_events; print(list_upcoming_events())"
```

Or in Python:
```python
from calendar_helper import list_upcoming_events

# List next 5 events (default)
result = list_upcoming_events()
print(result)

# List specific number of events
result = list_upcoming_events(count=10)
print(result)
```

Returns formatted list with icons:
- 📅 for each event with start time and summary
- Shows date/time and event name
- Returns "Žádné nadcházející události." if no events found

### 2. Create Event
Creates a new calendar event with specified details.

```bash
cd "../../.claude/skills/calendar-management" && python -c "from calendar_helper import create_event; print(create_event('Meeting', '2025-12-20T10:00:00', '2025-12-20T11:00:00'))"
```

Or in Python:
```python
from calendar_helper import create_event

# Create event with required parameters
summary = "Team Meeting"
start_time = "2025-12-05T14:00:00"  # ISO 8601 format
end_time = "2025-12-05T15:00:00"
description = "Discuss Q4 results"

result = create_event(summary, start_time, end_time, description)
print(result)

# Minimal event (without description)
result = create_event(
    summary="Lunch Break",
    start_time="2025-12-05T12:00:00",
    end_time="2025-12-05T13:00:00"
)
print(result)
```

**Time Format Requirements:**
- Must use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`
- Example: `2025-12-05T14:30:00` (December 5, 2025 at 2:30 PM)
- Timezone: Europe/Prague (automatically applied)

**Parameters:**
- `summary` (required): Event title/name
- `start_time` (required): Event start time in ISO format
- `end_time` (required): Event end time in ISO format  
- `description` (optional): Additional event details

## Time Format Examples

```python
# Morning meeting
start = "2025-12-10T09:00:00"
end = "2025-12-10T10:00:00"

# Afternoon appointment
start = "2025-12-15T14:30:00"
end = "2025-12-15T15:30:00"

# Evening event
start = "2025-12-20T18:00:00"
end = "2025-12-20T20:00:00"
```

## Authentication

This skill requires:
- `credentials.json` - OAuth client credentials
- `token_calendar.json` - User authentication token (auto-generated on first run)

Both files must be present in the skill directory.

## Error Handling

All functions include comprehensive error handling:
- Missing credentials → Clear error message
- Invalid time format → Returns error with format requirements
- API errors → Detailed error description
- Network issues → Timeout and connection error info

## Usage Examples

**Example 1: Check today's schedule**
```python
from calendar_helper import list_upcoming_events

# Get today's events
events = list_upcoming_events(count=10)
print("📅 Today's Schedule:")
print(events)
```

**Example 2: Schedule a meeting**
```python
from calendar_helper import create_event

# Schedule meeting for tomorrow
result = create_event(
    summary="Client Presentation",
    start_time="2025-12-02T10:00:00",
    end_time="2025-12-02T11:30:00",
    description="Present Q4 roadmap to client"
)
print(result)

# Verify it was created
events = list_upcoming_events(count=5)
print("\nUpdated schedule:")
print(events)
```

**Example 3: Create recurring reminders**
```python
from calendar_helper import create_event
import datetime

# Create daily standup for next week
base_date = datetime.date(2025, 12, 2)
for i in range(5):  # Monday to Friday
    day = base_date + datetime.timedelta(days=i)
    start = f"{day}T09:00:00"
    end = f"{day}T09:15:00"
    
    result = create_event(
        summary="Daily Standup",
        start_time=start,
        end_time=end,
        description="Team sync meeting"
    )
    print(result)
```

## Timezone Information

All events are created in **Europe/Prague** timezone by default. The skill automatically converts times to the correct timezone for calendar storage.

## Limitations

- Only works with primary calendar (`calendarId='primary'`)
- Does not support all-day events (requires dateTime format)
- Does not support recurring events (rrule)
- No support for inviting attendees
- No support for event updates or deletions

For these advanced features, use the Google Calendar API directly or extend the skill.
