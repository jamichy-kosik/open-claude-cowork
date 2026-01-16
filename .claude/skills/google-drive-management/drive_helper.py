"""
Google Drive Helper Functions
Provides Python functions for Google Drive operations via Google Drive API.
"""

import os
import sys
import io
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
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

def get_drive_service():
    """
    Authenticates and returns Google Drive API service from database.
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
            creds = get_user_credentials(user_id, 'google_drive', db)
            if not creds:
                raise OAuthRequiredException('google_drive')
            
            return build('drive', 'v3', credentials=creds)
        except ValueError:
            raise OAuthRequiredException('google_drive')
        finally:
            db.close()
            
    except OAuthRequiredException:
        raise
    except ImportError as e:
        raise Exception(f"Failed to import database services: {str(e)}. Make sure the agent-web-app backend is available.")
    except Exception as e:
        raise Exception(f"Failed to get Drive service: {str(e)}")


def list_files(limit: int = 10) -> str:
    """
    Lists recent files from Google Drive.
    
    Args:
        limit: Maximum number of files to return (default 10)
    
    Returns:
        Formatted string with file list including icons
    """
    service = get_drive_service()
    
    results = service.files().list(
        pageSize=limit,
        fields="files(id, name, mimeType, modifiedTime)",
        orderBy="modifiedTime desc"
    ).execute()
    
    items = results.get('files', [])
    
    if not items:
        return "📭 Žádné soubory nenalezeny"
    
    output = []
    for item in items:
        mime = item['mimeType']
        
        # Icon based on type
        if 'folder' in mime:
            icon = '📁'
        elif 'google-apps' in mime:
            icon = '☁️'
        else:
            icon = '📄'
        
        output.append(f"{icon} {item['name']} (ID: {item['id']})")
    
    return '\n'.join(output)


def search_files(query_name: str) -> str:
    """
    Searches for files by name in Google Drive.
    
    Args:
        query_name: Search term to find in file names
    
    Returns:
        Formatted string with matching files
    """
    service = get_drive_service()
    
    query = f"name contains '{query_name}'"
    results = service.files().list(
        q=query,
        pageSize=20,
        fields="files(id, name, mimeType)"
    ).execute()
    
    items = results.get('files', [])
    
    if not items:
        return f"🔍 Žádné soubory nenalezeny pro: '{query_name}'"
    
    output = [f"🔍 Nalezeno {len(items)} souborů:"]
    for item in items:
        mime = item['mimeType']
        
        if 'folder' in mime:
            icon = '📁'
        elif 'google-apps' in mime:
            icon = '☁️'
        else:
            icon = '📄'
        
        output.append(f"{icon} {item['name']} (ID: {item['id']})")
    
    return '\n'.join(output)


def read_file_content(file_id: str) -> str:
    """
    Reads and returns the text content of a file from Google Drive.
    Supports plain text, PDF, Google Docs, and Google Sheets.
    
    Args:
        file_id: The ID of the file to read
    
    Returns:
        File content as string, or error message
    """
    service = get_drive_service()
    
    try:
        # Get file metadata
        file_meta = service.files().get(fileId=file_id).execute()
        mime_type = file_meta['mimeType']
        file_name = file_meta['name']
        
        # Handle Google Docs/Sheets
        if "application/vnd.google-apps" in mime_type:
            if "document" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType='text/plain')
            elif "spreadsheet" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType='text/csv')
            else:
                return f"❌ Typ souboru {mime_type} není podporován pro čtení"
        else:
            # Regular file
            request = service.files().get_media(fileId=file_id)
        
        # Download content
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        # Get content
        fh.seek(0)
        content_bytes = fh.read()
        
        # Handle PDF
        if mime_type == 'application/pdf':
            try:
                from PyPDF2 import PdfReader
                pdf_reader = PdfReader(io.BytesIO(content_bytes))
                text_parts = []
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())
                return '\n'.join(text_parts)
            except ImportError:
                return "❌ Pro čtení PDF je potřeba nainstalovat PyPDF2: pip install PyPDF2"
        
        # Decode as text
        try:
            return content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return content_bytes.decode('latin-1')
    
    except Exception as e:
        return f"❌ Chyba při čtení souboru: {str(e)}"


def create_text_file(name: str, content: str) -> str:
    """
    Creates a new text file on Google Drive.
    
    Args:
        name: Name for the new file
        content: Text content to write
    
    Returns:
        Success message with file ID
    """
    service = get_drive_service()
    
    file_metadata = {'name': name}
    media = MediaIoBaseUpload(
        io.BytesIO(content.encode('utf-8')),
        mimetype='text/plain'
    )
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return f"✅ Soubor vytvořen s ID: {file.get('id')}"


def download_file(file_id: str, destination_path: str) -> str:
    """
    Downloads a file from Google Drive to local disk.
    
    Args:
        file_id: ID of the file on Google Drive
        destination_path: Local path where to save the file
    
    Returns:
        Success message with file path, or error message
    """
    service = get_drive_service()
    
    try:
        # Get file metadata
        file_meta = service.files().get(fileId=file_id).execute()
        file_name = file_meta['name']
        mime_type = file_meta['mimeType']
        
        # Handle destination path
        if not destination_path or destination_path == ".":
            destination_path = file_name
        
        if destination_path.endswith('/') or destination_path.endswith('\\'):
            destination_path = os.path.join(destination_path, file_name)
        
        # Setup download request
        request = None
        if "application/vnd.google-apps" in mime_type:
            # Google Doc/Sheet - export
            if "document" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                if not destination_path.endswith('.pdf'):
                    destination_path += '.pdf'
            elif "spreadsheet" in mime_type:
                request = service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                if not destination_path.endswith('.xlsx'):
                    destination_path += '.xlsx'
            else:
                return f"❌ Typ souboru {mime_type} nelze stáhnout"
        else:
            # Regular file
            request = service.files().get_media(fileId=file_id)
        
        # Download to file
        with open(destination_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
        return f"✅ Soubor '{file_name}' stažen do: {os.path.abspath(destination_path)}"
    
    except Exception as e:
        return f"❌ Chyba při stahování: {str(e)}"
