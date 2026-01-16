"""
Google Calendar Helper Functions
Provides Python functions for Google Calendar operations via Google Calendar API.
"""

import os
import sys
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Přidáme cestu k agent-web-app do sys.path
# Pro Docker: /app je přímo backend root
# Pro lokální: 4 úrovně nahoru + agent-web-app/backend
if os.path.exists("/app/app/core/database.py"):
    # Docker prostředí
    agent_web_app_path = "/app"
else:
    # Lokální prostředí
    agent_web_app_path = Path(__file__).parent.parent.parent.parent / "agent-web-app" / "backend"

if str(agent_web_app_path) not in sys.path:
    sys.path.insert(0, str(agent_web_app_path))


class OAuthRequiredException(Exception):
    """Exception raised when OAuth credentials are missing"""
    def __init__(self, service):
        self.service = service
        super().__init__(f"OAuth credentials required for {service}")

def get_calendar_service():
    """
    Authenticates and returns Google Calendar API service from database.
    """
    try:
        # Nastavíme DATABASE_URL pro Docker prostředí před importem
        if os.path.exists("/app/data/agent_app.db"):
            os.environ['DATABASE_URL'] = 'sqlite:////app/data/agent_app.db'
        
        from app.core.database import SessionLocal
        from app.services.oauth_service import get_user_credentials
        import json
        
        # Získáme user_id z config souboru (vytvoří agent_service.py)
        # Config je v root složce OLD AI (4 úrovně nahoru od tohoto souboru)
        config_file = Path(__file__).parent.parent.parent.parent / ".agent_config.json"
        if not config_file.exists():
            raise Exception(f"Agent config not found at {config_file}. Please use the web app to run the agent.")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
            user_id = config.get('user_id', 0)
        
        if user_id == 0:
            raise Exception("User ID not set. Please authenticate first through the web app.")
        
        db = SessionLocal()
        try:
            creds = get_user_credentials(user_id, 'calendar', db)
            if not creds:
                raise OAuthRequiredException('calendar')
            
            return build('calendar', 'v3', credentials=creds)
        except ValueError:
            raise OAuthRequiredException('calendar')
        finally:
            db.close()
            
    except OAuthRequiredException:
        raise
    except ImportError as e:
        raise Exception(f"Failed to import database services: {str(e)}. Make sure the agent-web-app backend is available.")
    except Exception as e:
        raise Exception(f"Failed to get Calendar service: {str(e)}")


def list_upcoming_events(count: int = 5) -> str:
    """
    Lists the next N upcoming events from the primary calendar.
    
    Args:
        count: Maximum number of events to return (default 5)
    
    Returns:
        Formatted string with event list including dates and summaries
    """
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=count,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return "Žádné nadcházející události."

    output = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', '(Bez názvu)')
        output.append(f"📅 {start} - {summary}")

    return "\n".join(output)


def create_event(summary: str, start_time: str, end_time: str, description: str = "") -> str:
    """
    Creates a new calendar event in the primary calendar.
    
    Args:
        summary: Event title/name (required)
        start_time: Event start time in ISO 8601 format (required)
                   Example: '2025-12-05T14:00:00'
        end_time: Event end time in ISO 8601 format (required)
                 Example: '2025-12-05T15:00:00'
        description: Additional event details (optional)
    
    Returns:
        Success message with event link, or error message
    """
    service = get_calendar_service()
    
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Prague'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Prague'
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Událost vytvořena: {event.get('htmlLink')}"
    except Exception as e:
        return f"❌ Chyba při vytváření: {str(e)}"
