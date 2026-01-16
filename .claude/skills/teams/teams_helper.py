"""
Microsoft Teams Helper - Communication via Microsoft Graph API.

Simple and clear functions for Teams operations:
- Chat messages (read, send)
- Online meetings (create, list)
- Teams and channels (list, post)

Uses shared authentication with Outlook skill (same Microsoft Graph token).
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import requests
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Microsoft Graph API
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")


def _get_token_from_db() -> Dict[str, Any]:
    """Load access token from database (shared with Outlook)"""
    user_id = os.getenv('AGENT_USER_ID')
    if not user_id:
        raise ValueError("AGENT_USER_ID not set")
    
    try:
        # Nastavíme DATABASE_URL pro Docker prostředí před importem
        if os.path.exists("/app/data/agent_app.db"):
            os.environ['DATABASE_URL'] = 'sqlite:////app/data/agent_app.db'
        
        import sys
        # Pro Docker: /app je přímo backend root
        if os.path.exists("/app/app/core/database.py"):
            sys.path.insert(0, "/app")
        else:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'agent-web-app' / 'backend'))
        
        from app.core.database import SessionLocal
        from app.services.oauth_service import get_outlook_token_cache
        
        db = SessionLocal()
        try:
            token_json = get_outlook_token_cache(int(user_id), db)
            token_data = json.loads(token_json)
            return token_data
        finally:
            db.close()
    except Exception as e:
        raise ValueError(f"Failed to load token: {str(e)}")


def _get_access_token() -> str:
    """Get access token for Graph API"""
    try:
        token_data = _get_token_from_db()
        access_token = token_data.get('access_token')
        if access_token:
            print("[Teams] Using access token from database")
            return access_token
        raise ValueError("No access token in database")
    except Exception as e:
        raise ValueError(f"Authentication failed: {str(e)}")


def _make_graph_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    params: Optional[Dict] = None
) -> Dict[str, Any]:
    """Make request to Microsoft Graph API"""
    token = _get_access_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{GRAPH_API_ENDPOINT}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        if response.status_code == 401:
            return {"success": False, "error": "Token expired. Reconnect Microsoft account in Settings."}
        
        if response.status_code >= 400:
            return {"success": False, "error": f"API error {response.status_code}: {response.text}"}
        
        if response.status_code == 204:
            return {"success": True, "data": None}
        
        return {"success": True, "data": response.json()}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# CHATS & MESSAGES
# ============================================================================

def get_chats(count: int = 10) -> str:
    """
    List recent chats.
    
    Args:
        count: Number of chats to retrieve (default 10)
        
    Returns:
        Formatted list of chats with latest message preview
    """
    params = {
        "$top": count,
        "$expand": "lastMessagePreview",
        "$orderby": "lastMessagePreview/createdDateTime desc"
    }
    
    result = _make_graph_request("/me/chats", params=params)
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    chats = result["data"].get("value", [])
    
    if not chats:
        return "No chats found."
    
    output = [f"Last {len(chats)} chats:\n"]
    
    for i, chat in enumerate(chats, 1):
        topic = chat.get("topic") or "Direct chat"
        chat_id = chat.get("id", "")
        last_msg = chat.get("lastMessagePreview", {})
        preview = last_msg.get("body", {}).get("content", "")[:80]
        created = last_msg.get("createdDateTime", "")[:10]
        
        output.append(f"{i}. {topic}")
        output.append(f"   ID: {chat_id[:20]}...")
        output.append(f"   Last: {preview}... ({created})")
        output.append("")
    
    return "\n".join(output)


def get_chat_messages(chat_id: str, count: int = 20) -> str:
    """
    Read messages from specific chat.
    
    Args:
        chat_id: Chat ID from get_chats()
        count: Number of messages (default 20)
        
    Returns:
        Formatted messages from chat
    """
    params = {
        "$top": count,
        "$orderby": "createdDateTime desc"
    }
    
    result = _make_graph_request(f"/chats/{chat_id}/messages", params=params)
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    messages = result["data"].get("value", [])
    
    if not messages:
        return "No messages in this chat."
    
    output = [f"Last {len(messages)} messages:\n"]
    
    for i, msg in enumerate(reversed(messages), 1):
        sender = msg.get("from", {}).get("user", {}).get("displayName", "Unknown")
        body = msg.get("body", {}).get("content", "")
        created = msg.get("createdDateTime", "")[:16].replace("T", " ")
        
        # Strip HTML tags for plain text
        import re
        body_text = re.sub('<[^<]+?>', '', body)[:200]
        
        output.append(f"{i}. {sender} ({created}):")
        output.append(f"   {body_text}")
        output.append("")
    
    return "\n".join(output)


def send_chat_message(chat_id: str, message: str) -> str:
    """
    Send message to chat.
    
    Args:
        chat_id: Chat ID from get_chats()
        message: Message text
        
    Returns:
        Success or error message
    """
    data = {
        "body": {
            "content": message,
            "contentType": "text"
        }
    }
    
    result = _make_graph_request(f"/chats/{chat_id}/messages", method="POST", data=data)
    
    if result["success"]:
        return f"Message sent to chat."
    else:
        return f"Error: {result['error']}"


def search_messages(query: str, count: int = 10) -> str:
    """
    Search messages across all chats.
    
    Args:
        query: Search query
        count: Max results (default 10)
        
    Returns:
        Formatted search results
    """
    # Note: Search requires Microsoft Search API
    # Simplified version using chats endpoint with filter
    result = _make_graph_request("/me/chats")
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    return "Search in Teams messages - feature requires advanced Graph API permissions."


# ============================================================================
# MEETINGS
# ============================================================================

def create_meeting(
    subject: str,
    start: str,
    end: str,
    attendees: Optional[List[str]] = None
) -> str:
    """
    Create online meeting.
    
    Args:
        subject: Meeting title
        start: Start time (ISO format: 2024-12-20T10:00:00)
        end: End time (ISO format)
        attendees: List of attendee emails (optional)
        
    Returns:
        Meeting link and details
    """
    # Use calendar event with Teams meeting enabled
    meeting_data = {
        "subject": subject,
        "start": {
            "dateTime": start,
            "timeZone": "Central Europe Standard Time"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Central Europe Standard Time"
        },
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness"
    }
    
    if attendees:
        meeting_data["attendees"] = [
            {
                "emailAddress": {"address": email},
                "type": "required"
            }
            for email in attendees
        ]
    
    result = _make_graph_request("/me/events", method="POST", data=meeting_data)
    
    if result["success"]:
        data = result["data"]
        online_meeting = data.get("onlineMeeting") or {}
        join_url = online_meeting.get("joinUrl", "")
        event_link = data.get("webLink", "")
        
        output = [
            f"Teams meeting '{subject}' created!",
            f"Join URL: {join_url}",
            f"Calendar: {event_link}",
            f"Time: {start} - {end}"
        ]
        
        return "\n".join(output)
    else:
        return f"Error: {result['error']}"


def get_meetings(days: int = 7) -> str:
    """
    List upcoming meetings.
    
    Args:
        days: Number of days forward (default 7)
        
    Returns:
        Formatted list of meetings
    """
    now = datetime.utcnow()
    end = now + timedelta(days=days)
    
    params = {
        "startDateTime": now.isoformat() + "Z",
        "endDateTime": end.isoformat() + "Z",
        "$select": "subject,start,end,joinWebUrl,isOnlineMeeting"
    }
    
    result = _make_graph_request("/me/calendarView", params=params)
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    events = result["data"].get("value", [])
    
    # Filter only online meetings
    meetings = [e for e in events if e.get("isOnlineMeeting")]
    
    if not meetings:
        return f"No online meetings in next {days} days."
    
    output = [f"Upcoming meetings ({len(meetings)}):\n"]
    
    for i, meeting in enumerate(meetings, 1):
        subject = meeting.get("subject", "No title")
        start = meeting.get("start", {}).get("dateTime", "")[:16].replace("T", " ")
        join_url = meeting.get("joinWebUrl", "")
        
        output.append(f"{i}. {subject}")
        output.append(f"   Time: {start}")
        output.append(f"   Join: {join_url}")
        output.append("")
    
    return "\n".join(output)


# ============================================================================
# TEAMS & CHANNELS
# ============================================================================

def get_teams() -> str:
    """
    List all teams user is member of.
    
    Returns:
        Formatted list of teams
    """
    result = _make_graph_request("/me/joinedTeams")
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    teams = result["data"].get("value", [])
    
    if not teams:
        return "You are not member of any team."
    
    output = [f"Your teams ({len(teams)}):\n"]
    
    for i, team in enumerate(teams, 1):
        name = team.get("displayName", "Unknown")
        team_id = team.get("id", "")
        description = team.get("description", "")[:80]
        
        output.append(f"{i}. {name}")
        output.append(f"   ID: {team_id[:20]}...")
        if description:
            output.append(f"   {description}")
        output.append("")
    
    return "\n".join(output)


def get_channels(team_id: str) -> str:
    """
    List channels in team.
    
    Args:
        team_id: Team ID from get_teams()
        
    Returns:
        Formatted list of channels
    """
    result = _make_graph_request(f"/teams/{team_id}/channels")
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    channels = result["data"].get("value", [])
    
    if not channels:
        return "No channels found in this team."
    
    output = [f"Channels in team ({len(channels)}):\n"]
    
    for i, channel in enumerate(channels, 1):
        name = channel.get("displayName", "Unknown")
        channel_id = channel.get("id", "")
        description = channel.get("description", "")[:80]
        
        output.append(f"{i}. {name}")
        output.append(f"   ID: {channel_id[:20]}...")
        if description:
            output.append(f"   {description}")
        output.append("")
    
    return "\n".join(output)


def post_to_channel(team_id: str, channel_id: str, message: str) -> str:
    """
    Post message to channel.
    
    Args:
        team_id: Team ID from get_teams()
        channel_id: Channel ID from get_channels()
        message: Message text
        
    Returns:
        Success or error message
    """
    data = {
        "body": {
            "content": message,
            "contentType": "text"
        }
    }
    
    result = _make_graph_request(
        f"/teams/{team_id}/channels/{channel_id}/messages",
        method="POST",
        data=data
    )
    
    if result["success"]:
        return f"Message posted to channel."
    else:
        return f"Error: {result['error']}"


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Teams Helper - Microsoft Graph API")
    parser.add_argument("--chats", type=int, metavar="N", help="List N chats")
    parser.add_argument("--chat-messages", type=str, metavar="CHAT_ID", help="Read messages from chat")
    parser.add_argument("--teams", action="store_true", help="List your teams")
    parser.add_argument("--channels", type=str, metavar="TEAM_ID", help="List channels in team")
    parser.add_argument("--meetings", type=int, metavar="DAYS", help="List meetings for N days")
    
    args = parser.parse_args()
    
    if args.chats:
        print(get_chats(count=args.chats))
    elif args.chat_messages:
        print(get_chat_messages(args.chat_messages))
    elif args.teams:
        print(get_teams())
    elif args.channels:
        print(get_channels(args.channels))
    elif args.meetings:
        print(get_meetings(days=args.meetings))
    else:
        print("Microsoft Teams Helper")
        print("\nUsage:")
        print("  --chats N              List N recent chats")
        print("  --chat-messages ID     Read messages from chat")
        print("  --teams                List your teams")
        print("  --channels TEAM_ID     List channels in team")
        print("  --meetings N           List meetings for N days")
        print("\nExample:")
        print("  python teams_helper.py --chats 10")
        print("  python teams_helper.py --teams")
