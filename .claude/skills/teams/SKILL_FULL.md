---
name: teams
description: Microsoft Teams skill for chat messages, online meetings, and channel communication via Microsoft Graph API. Use when user wants to work with Teams chats, meetings, or channels.
---

# Microsoft Teams Skill

Communication and collaboration with Microsoft Teams via Graph API.

## Capabilities

**Messages & Chats:**
- List recent chats and conversations
- Read messages from specific chat
- Send messages to chat or channel
- Search messages

**Meetings:**
- Create online meetings
- List upcoming meetings
- Get meeting details

**Teams & Channels:**
- List user's teams
- List channels in team
- Post to channel

## Important: Working Directory

**Always run commands from the skill directory:**
```bash
cd "../../.claude/skills/teams"
```

## Authentication

Uses OAuth token from database (shared with Outlook skill). User must connect Microsoft account in Settings page with Teams permissions enabled.

**Token Loading:**
1. **Database** (if `AGENT_USER_ID` environment variable is set) - automatic in agent
2. **Requires reconnection** if new permissions were added

## Usage Examples

### List recent chats

```bash
cd "../../.claude/skills/teams" && python -c "from teams_helper import get_chats; print(get_chats(count=10))"
```

### Read chat messages

```bash
cd "../../.claude/skills/teams" && python -c "from teams_helper import get_chat_messages; print(get_chat_messages('CHAT_ID'))"
```

### Send chat message

```bash
cd "../../.claude/skills/teams" && python -c "from teams_helper import send_chat_message; print(send_chat_message('CHAT_ID', 'Hello from bot!'))"
```

### Create meeting

```bash
cd "../../.claude/skills/teams" && python -c "from teams_helper import create_meeting; print(create_meeting('Team Sync', '2024-12-20T10:00:00', '2024-12-20T11:00:00'))"
```

### List teams

```bash
cd "../../.claude/skills/teams" && python -c "from teams_helper import get_teams; print(get_teams())"
```

### Post to channel

```bash
cd "../../.claude/skills/teams" && python -c "from teams_helper import post_to_channel; print(post_to_channel('TEAM_ID', 'CHANNEL_ID', 'Update message'))"
```

## Available Functions

| Function | Description |
|---------|------------|
| `get_chats(count=10)` | List recent chats with preview |
| `get_chat_messages(chat_id, count=20)` | Read messages from chat |
| `send_chat_message(chat_id, message)` | Send message to chat |
| `create_meeting(subject, start, end, attendees)` | Create online meeting |
| `get_meetings(days=7)` | List upcoming meetings |
| `get_teams()` | List user's teams |
| `get_channels(team_id)` | List channels in team |
| `post_to_channel(team_id, channel_id, message)` | Post to channel |

## Required Permissions

- Chat.Read, Chat.ReadWrite - read/send chat messages
- OnlineMeetings.ReadWrite - create meetings
- Team.ReadBasic.All - list teams
- Channel.ReadBasic.All - list channels
- ChannelMessage.Send - post to channels

## Troubleshooting

**"Token expired"** - User must reconnect Microsoft account in Settings

**"Insufficient privileges"** - User needs to reconnect with updated permissions (Teams scopes were added)
