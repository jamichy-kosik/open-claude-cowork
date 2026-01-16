"""
Outlook Helper - Microsoft Graph API integration for Outlook.

This module provides access to Microsoft Outlook via Graph API.
Uses MSAL (Microsoft Authentication Library) for OAuth 2.0 authentication.

Supported flows:
- Device Code Flow (for CLI applications)
- Interactive Browser Flow (for desktop applications)

Usage:
    from outlook_helper import get_emails, send_email, search_emails
    
    # Get emails
    emails = get_emails(count=5)
    
    # Send email
    send_email("recipient@example.com", "Subject", "Body")
"""

import os
import sys
import json
import atexit
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import msal
import requests
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Microsoft Graph API endpoints
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
AUTHORITY = "https://login.microsoftonline.com/consumers"  # Use /consumers for personal Microsoft accounts

# Permissions (scopes) for Graph API
SCOPES = [
    "User.Read",           # Read user profile
    "Mail.Read",           # Read emails
    "Mail.Send",           # Send emails
    "Mail.ReadWrite",      # Modify emails
    "Calendars.Read",      # Read calendar
    "Calendars.ReadWrite", # Modify calendar
]

# Path to token cache (fallback for local use)
TOKEN_CACHE_PATH = Path(__file__).parent / ".outlook_token_cache.json"

# Azure App credentials (set in .env or directly here)
CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
# For public client apps (desktop/mobile) client secret is not needed
# CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")


def _get_token_from_db() -> Dict[str, Any]:
    """
    Load Outlook access token from database for current user
    Uses AGENT_USER_ID environment variable set by agent_service.py
    
    Returns:
        Token data dict with access_token, expires_at, etc.
        
    Raises:
        ValueError: If AGENT_USER_ID not set or user doesn't have Outlook connected
    """
    user_id = os.getenv('AGENT_USER_ID')
    if not user_id:
        raise ValueError("AGENT_USER_ID not set in environment")
    
    try:
        # Nastavíme DATABASE_URL pro Docker prostředí před importem
        if os.path.exists("/app/data/agent_app.db"):
            os.environ['DATABASE_URL'] = 'sqlite:////app/data/agent_app.db'
        
        # Import here to avoid circular imports
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
        raise ValueError(f"Failed to load Outlook token from database: {str(e)}")


def _get_access_token() -> str:
    """
    Get access token for Microsoft Graph API.
    Priority:
    1. Database token (if AGENT_USER_ID is set)
    2. Local MSAL cache (fallback for interactive use)
    
    Returns:
        Valid access token string
    """
    # Try database first (when running through agent)
    if os.getenv('AGENT_USER_ID'):
        try:
            token_data = _get_token_from_db()
            access_token = token_data.get('access_token')
            if access_token:
                print("[Outlook] Using access token from database")
                return access_token
        except Exception as e:
            print(f"[Outlook] Database token load failed: {e}, falling back to MSAL")
    
    # Fallback to MSAL interactive flow
    print("[Outlook] Using MSAL interactive authentication")
    return _get_msal_token()


def _get_msal_app_old() -> msal.PublicClientApplication:
    """DEPRECATED: Get MSAL app with cache (old method)"""
    cache = msal.SerializableTokenCache()
    
    # Load from local file cache if exists
    if TOKEN_CACHE_PATH.exists():
        cache.deserialize(TOKEN_CACHE_PATH.read_text())
    
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )
    
    # Save cache on exit (only to local file, not database)
    def save_cache():
        if cache.has_state_changed and not os.getenv('AGENT_USER_ID'):
            # Only save to local file if not using database
            TOKEN_CACHE_PATH.write_text(cache.serialize())
    
    atexit.register(save_cache)
    
    return app


def _get_msal_token() -> str:
    """Fallback: Get token using MSAL interactive flow"""
    app = _get_msal_app_old()
    
    # Try silent first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]
    
    # Interactive fallback
    print("[*] Opening browser for authentication...")
    result = app.acquire_token_interactive(scopes=SCOPES, prompt="select_account")
    
    if "access_token" in result:
        return result["access_token"]
    else:
        raise ValueError(f"Authentication failed: {result.get('error_description', 'Unknown error')}")



def authenticate_device_code() -> Dict[str, Any]:
    """
    Authentication using Device Code Flow.
    
    User gets a code and URL where to enter it.
    Suitable for CLI applications without GUI.
    
    Returns:
        Dictionary with login information
    """
    if not CLIENT_ID:
        return {
            "success": False,
            "error": "Missing MICROSOFT_CLIENT_ID in .env file."
        }
    
    app = _get_msal_app_old()
    
    # Initiate device code flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    
    if "user_code" not in flow:
        return {
            "success": False,
            "error": f"Failed to initiate authentication: {flow.get('error_description', 'Unknown error')}"
        }
    
    print("\n" + "=" * 60)
    print("🔐 MICROSOFT AUTHENTICATION")
    print("=" * 60)
    print(f"\n{flow['message']}")
    print("\n" + "=" * 60)
    
    # Wait for authentication completion
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        # Save cache
        cache = app.token_cache
        if cache.has_state_changed:
            TOKEN_CACHE_PATH.write_text(cache.serialize())
        
        return {
            "success": True,
            "message": "Authentication successful!",
            "user": result.get("id_token_claims", {}).get("preferred_username", "Unknown")
        }
    else:
        return {
            "success": False,
            "error": result.get("error_description", result.get("error", "Unknown error"))
        }


def is_authenticated() -> bool:
    """
    Checks if user is logged in (has valid token in cache).

    Returns:
        True if logged in, False otherwise
    """
    if not CLIENT_ID:
        return False

    try:
        token = _get_access_token()
        return token is not None
    except:
        return False


def logout() -> str:
    """
    Logs out user - deletes token cache.
    
    Returns:
        Status message
    """
    if TOKEN_CACHE_PATH.exists():
        TOKEN_CACHE_PATH.unlink()
        return "✅ Logout successful. Token cache deleted."
    else:
        return "ℹ️ No user was logged in."


def get_current_user() -> Optional[str]:
    """
    Returns email of currently logged in user.
    
    Returns:
        User email or None if not logged in
    """
    if not CLIENT_ID:
        return None
    
    app = _get_msal_app_old()
    accounts = app.get_accounts()
    
    if accounts:
        return accounts[0].get("username")
    
    return None


def _make_graph_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    params: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Makes request to Microsoft Graph API.
    Uses token from database (when AGENT_USER_ID set) or interactive MSAL.
    """
    token = _get_access_token()
    
    if not token:
        return {
            "success": False,
            "error": "Failed to get access token. Try running: python outlook_helper.py --auth"
        }
    
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
            return {
                "success": False,
                "error": "Token expired. Run: python outlook_helper.py --auth"
            }
        
        if response.status_code >= 400:
            return {
                "success": False,
                "error": f"API error {response.status_code}: {response.text}"
            }
        
        if response.status_code == 204:  # No content
            return {"success": True, "data": None}
        
        return {"success": True, "data": response.json()}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_profile() -> Dict[str, Any]:
    """
    Gets profile of logged in user.
    """
    result = _make_graph_request("/me")
    
    if result["success"]:
        data = result["data"]
        return {
            "success": True,
            "name": data.get("displayName"),
            "email": data.get("mail") or data.get("userPrincipalName"),
            "job_title": data.get("jobTitle"),
            "office": data.get("officeLocation")
        }
    
    return result


def get_emails(
    count: int = 10,
    folder: str = "inbox",
    unread_only: bool = False
) -> str:
    """
    Retrieves emails from Outlook mailbox.
    
    Args:
        count: Number of emails to retrieve
        folder: Folder (inbox, sentitems, drafts, archive)
        unread_only: Only unread emails
        
    Returns:
        Formatted text with emails
    """
    params = {
        "$top": count,
        "$orderby": "receivedDateTime desc",
        "$select": "subject,from,receivedDateTime,bodyPreview,isRead,importance"
    }
    
    if unread_only:
        params["$filter"] = "isRead eq false"
    
    endpoint = f"/me/mailFolders/{folder}/messages"
    result = _make_graph_request(endpoint, params=params)
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    messages = result["data"].get("value", [])
    
    if not messages:
        return "No emails found."
    
    # Use plain text without emoji when running through agent (to avoid Windows encoding issues)
    use_emoji = not bool(os.getenv('AGENT_USER_ID'))
    
    if use_emoji:
        output = [f"📬 Last {len(messages)} emails from {folder}:\n"]
    else:
        output = [f"Last {len(messages)} emails from {folder}:\n"]
    
    for i, msg in enumerate(messages, 1):
        from_email = msg.get("from", {}).get("emailAddress", {})
        from_name = from_email.get("name", "Unknown")
        from_addr = from_email.get("address", "")
        subject = msg.get("subject", "(no subject)")
        date = msg.get("receivedDateTime", "")[:10]
        preview = msg.get("bodyPreview", "")[:100]
        
        if use_emoji:
            is_read = "📖" if msg.get("isRead") else "📩"
            importance = "❗" if msg.get("importance") == "high" else ""
        else:
            is_read = "[READ]" if msg.get("isRead") else "[UNREAD]"
            importance = "[!]" if msg.get("importance") == "high" else ""
        
        output.append(f"{i}. {is_read}{importance} {subject}")
        output.append(f"   From: {from_name} <{from_addr}>")
        output.append(f"   Date: {date}")
        if preview:
            output.append(f"   Preview: {preview}...")
        output.append("")
    
    return "\n".join(output)


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    is_html: bool = False
) -> str:
    """
    Sends email.
    
    Args:
        to: Recipient (email or multiple emails separated by comma)
        subject: Subject
        body: Email body
        cc: CC recipients (optional)
        is_html: True if body is HTML
        
    Returns:
        Status message
    """
    # Prepare recipients
    to_recipients = [
        {"emailAddress": {"address": addr.strip()}}
        for addr in to.split(",")
    ]
    
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML" if is_html else "Text",
                "content": body
            },
            "toRecipients": to_recipients
        }
    }
    
    if cc:
        message["message"]["ccRecipients"] = [
            {"emailAddress": {"address": addr.strip()}}
            for addr in cc.split(",")
        ]
    
    result = _make_graph_request("/me/sendMail", method="POST", data=message)
    
    if result["success"]:
        return f"Email sent to: {to}"
    else:
        return f"Error sending: {result['error']}"


def search_emails(query: str, count: int = 10) -> str:
    """
    Searches emails by query.
    
    Args:
        query: Search query
        count: Max number of results
        
    Returns:
        Formatted text with results
    """
    params = {
        "$top": count,
        "$search": f'"{query}"',
        "$select": "subject,from,receivedDateTime,bodyPreview"
    }
    
    result = _make_graph_request("/me/messages", params=params)
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    messages = result["data"].get("value", [])
    
    if not messages:
        return f"No emails found for query '{query}'."
    
    output = [f"Results for '{query}' ({len(messages)} emails):\n"]
    
    for i, msg in enumerate(messages, 1):
        from_email = msg.get("from", {}).get("emailAddress", {})
        from_name = from_email.get("name", "Unknown")
        subject = msg.get("subject", "(no subject)")
        date = msg.get("receivedDateTime", "")[:10]
        
        output.append(f"{i}. {subject}")
        output.append(f"   From: {from_name} | Date: {date}")
        output.append("")
    
    return "\n".join(output)


def get_calendar_events(days: int = 7) -> str:
    """
    Retrieves events from calendar.
    
    Args:
        days: Number of days forward
        
    Returns:
        Formatted text with events
    """
    now = datetime.utcnow()
    end = now + timedelta(days=days)
    
    params = {
        "startDateTime": now.isoformat() + "Z",
        "endDateTime": end.isoformat() + "Z",
        "$orderby": "start/dateTime",
        "$select": "subject,start,end,location,organizer,isOnlineMeeting"
    }
    
    result = _make_graph_request("/me/calendarView", params=params)
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    events = result["data"].get("value", [])
    
    if not events:
        return f"No events in the next {days} days."
    
    output = [f"Events for next {days} days ({len(events)} events):\n"]
    
    for i, event in enumerate(events, 1):
        subject = event.get("subject", "(no title)")
        start = event.get("start", {}).get("dateTime", "")[:16].replace("T", " ")
        end_time = event.get("end", {}).get("dateTime", "")[:16].replace("T", " ")
        location = event.get("location", {}).get("displayName", "")
        is_online = "🎥 " if event.get("isOnlineMeeting") else ""
        
        output.append(f"{i}. {is_online}{subject}")
        output.append(f"   🕐 {start} - {end_time}")
        if location:
            output.append(f"   📍 {location}")
        output.append("")
    
    return "\n".join(output)


def create_calendar_event(
    subject: str,
    start: str,
    end: str,
    body: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None
) -> str:
    """
    Creates event in calendar.
    
    Args:
        subject: Event name
        start: Start time (ISO format: 2024-12-03T10:00:00)
        end: End time (ISO format)
        body: Description
        location: Location
        attendees: List of attendee emails
        
    Returns:
        Status message
    """
    event = {
        "subject": subject,
        "start": {
            "dateTime": start,
            "timeZone": "Central Europe Standard Time"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Central Europe Standard Time"
        }
    }
    
    if body:
        event["body"] = {"contentType": "Text", "content": body}
    
    if location:
        event["location"] = {"displayName": location}
    
    if attendees:
        event["attendees"] = [
            {
                "emailAddress": {"address": email},
                "type": "required"
            }
            for email in attendees
        ]
    
    result = _make_graph_request("/me/events", method="POST", data=event)
    
    if result["success"]:
        event_id = result["data"].get("id", "")
        web_link = result["data"].get("webLink", "")
        return f"Event '{subject}' created!\n   Link: {web_link}"
    else:
        return f"Error creating event: {result['error']}"


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Outlook Helper - Microsoft Graph API")
    parser.add_argument("--auth", action="store_true", help="Run authentication (Device Code)")
    parser.add_argument("--auth-browser", action="store_true", help="Authentication via browser")
    parser.add_argument("--logout", action="store_true", help="Log out")
    parser.add_argument("--status", action="store_true", help="Check login status")
    parser.add_argument("--profile", action="store_true", help="Show profile")
    parser.add_argument("--emails", type=int, metavar="N", help="Retrieve N emails")
    parser.add_argument("--calendar", type=int, metavar="DAYS", help="Events for N days")
    parser.add_argument("--search", type=str, metavar="QUERY", help="Search emails")
    
    args = parser.parse_args()
    
    if args.auth:
        result = authenticate_device_code()
        if result["success"]:
            print(f"\n✅ {result['message']}")
            print(f"👤 Logged in as: {result['user']}")
        else:
            print(f"\n❌ {result['error']}")
    
    elif args.auth_browser:
        # Force login via browser
        try:
            token = _get_access_token()
            if token:
                user = get_current_user()
                print(f"✅ Logged in as: {user}")
            else:
                print("❌ Login failed")
        except Exception as e:
            print(f"❌ Login failed: {e}")
    
    elif args.logout:
        print(logout())
    
    elif args.status:
        if is_authenticated():
            user = get_current_user()
            print(f"✅ Logged in as: {user}")
        else:
            print("❌ Not logged in")
    
    elif args.profile:
        result = get_user_profile()
        if result["success"]:
            print(f"\n👤 Profile:")
            print(f"   Name: {result['name']}")
            print(f"   Email: {result['email']}")
            if result.get('job_title'):
                print(f"   Job title: {result['job_title']}")
        else:
            print(f"\n❌ {result['error']}")
    
    elif args.emails:
        print(get_emails(count=args.emails))
    
    elif args.calendar:
        print(get_calendar_events(days=args.calendar))
    
    elif args.search:
        print(search_emails(args.search))
    
    else:
        print("=" * 60)
        print("📧 OUTLOOK HELPER - Microsoft Graph API")
        print("=" * 60)
        
        # Check CLIENT_ID
        if not CLIENT_ID:
            print("\n⚠️  MICROSOFT_CLIENT_ID is not set!")
            print("\n📝 Guide to create Azure App Registration:")
            print("   1. Go to https://portal.azure.com")
            print("   2. Azure Active Directory → App registrations → New registration")
            print("   3. Name: e.g. 'Outlook Helper'")
            print("   4. Supported account types: 'Personal Microsoft accounts only'")
            print("      (or 'Accounts in any organizational directory and personal')")
            print("   5. Redirect URI: skip or 'http://localhost'")
            print("   6. After creation, copy 'Application (client) ID'")
            print("   7. Add to .env file:")
            print("      MICROSOFT_CLIENT_ID=<your-client-id>")
            print("\n   Documentation: https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app")
        else:
            # Check login status
            if is_authenticated():
                user = get_current_user()
                print(f"\n✅ Logged in as: {user}")
            else:
                print("\n⚠️ Not logged in - browser will open on first request")
        
        print("\nUsage:")
        print("  --auth          Authentication (Device Code - for terminals without GUI)")
        print("  --auth-browser  Authentication via browser")
        print("  --logout        Log out")
        print("  --status        Check login status")
        print("  --profile       Show profile")
        print("  --emails N      Retrieve N emails")
        print("  --calendar N    Events for N days")
        print("  --search QUERY  Search emails")
        print("\nExample:")
        print("  python outlook_helper.py --emails 5")
        print("  python outlook_helper.py --calendar 7")
