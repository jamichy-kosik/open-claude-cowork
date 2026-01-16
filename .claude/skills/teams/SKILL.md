---
name: teams
description: Microsoft Teams - send messages, create meetings, access chats/channels. Always cd to skill directory first.
---

# Microsoft Teams

## Working Directory
**REQUIRED:** `cd "../../.claude/skills/teams"` before all operations.

## Functions

### get_chats(count=10)
Lists recent chats.
```bash
cd "../../.claude/skills/teams" && python -c "from teams_helper import get_chats; print(get_chats(10))"
```

### send_message(chat_id, message)
Sends message to chat.

### create_meeting(subject, start_time, end_time, attendees=[])
Creates online meeting. Times in ISO format.

### get_teams()
Lists user's teams.

### get_channels(team_id)
Lists channels in team.

### post_to_channel(team_id, channel_id, message)
Posts message to channel.

## Auth
Uses OAuth from database. User must connect Microsoft account in Settings with Teams permissions.
