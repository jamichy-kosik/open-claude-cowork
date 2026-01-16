"""
Gmail Helper Functions
Provides simple functions for Gmail operations via Gmail API
"""
import os
import sys
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

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

def get_gmail_service():
    """Get authenticated Gmail service from database"""
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
            creds = get_user_credentials(user_id, 'gmail', db)
            if not creds:
                raise OAuthRequiredException('gmail')
            
            return build('gmail', 'v1', credentials=creds)
        except ValueError:
            # ValueError znamená že credentials neexistují
            raise OAuthRequiredException('gmail')
        finally:
            db.close()
            
    except OAuthRequiredException:
        raise  # Propagujeme OAuth exception dál
    except ImportError as e:
        raise Exception(f"Failed to import database services: {str(e)}. Make sure the agent-web-app backend is available.")
    except Exception as e:
        raise Exception(f"Failed to get Gmail service: {str(e)}")

def decode_body(part):
    """Decode email body"""
    if 'data' in part['body']:
        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
    return ""

def extract_text_from_html(html_content):
    """Extract plain text from HTML content"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        # Get text and clean up whitespace
        text = soup.get_text(separator=' ', strip=True)
        # Clean up multiple spaces and newlines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        return html_content  # Return original if parsing fails

def send_email(to_email, subject, body):
    """Send plain text email"""
    try:
        service = get_gmail_service()
        
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"Email sent successfully to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

def send_email_with_attachment(to_email, subject, body, attachment_path):
    """Send email with attachment"""
    try:
        service = get_gmail_service()

        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Attach file
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        return f"Email with attachment sent successfully to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

def read_recent_emails(count=5):
    """Read recent emails from Gmail"""
    try:
        service = get_gmail_service()

        results = service.users().messages().list(
            userId='me',
            maxResults=count,
            labelIds=['INBOX']
        ).execute()

        messages = results.get('messages', [])
        emails = []

        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

            # Get body
            body = ""
            html_body = ""
            
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = decode_body(part)
                    elif part['mimeType'] == 'text/html':
                        html_body = decode_body(part)
            else:
                if message['payload'].get('mimeType') == 'text/html':
                    html_body = decode_body(message['payload'])
                else:
                    body = decode_body(message['payload'])
            
            # If we only have HTML, extract text from it
            if not body and html_body:
                body = extract_text_from_html(html_body)

            emails.append({
                'from': from_email,
                'subject': subject,
                'date': date,
                'body': body
            })

        return emails
    except Exception as e:
        return [{'error': f"Error reading emails: {str(e)}"}]

def get_attachments_info(message):
    """Extract attachment information from message"""
    attachments = []

    def process_parts(parts):
        for part in parts:
            if part.get('filename'):
                attachment_id = part['body'].get('attachmentId')
                if attachment_id:
                    attachments.append({
                        'filename': part['filename'],
                        'mimeType': part['mimeType'],
                        'attachmentId': attachment_id,
                        'size': part['body'].get('size', 0)
                    })

            # Recursively process nested parts
            if 'parts' in part:
                process_parts(part['parts'])

    if 'parts' in message['payload']:
        process_parts(message['payload']['parts'])

    return attachments

def download_attachment(message_id, attachment_id, filename, save_path=None):
    """Download an email attachment"""
    try:
        service = get_gmail_service()

        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()

        file_data = base64.urlsafe_b64decode(attachment['data'])

        if save_path is None:
            save_path = filename

        with open(save_path, 'wb') as f:
            f.write(file_data)

        return f"Attachment saved to {save_path}"
    except Exception as e:
        return f"Error downloading attachment: {str(e)}"

def search_emails(query, count=3):
    """Search emails with Gmail query syntax"""
    try:
        service = get_gmail_service()

        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=count
        ).execute()

        messages = results.get('messages', [])
        emails = []

        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

            # Get body
            body = ""
            html_body = ""

            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = decode_body(part)
                    elif part['mimeType'] == 'text/html':
                        html_body = decode_body(part)
            else:
                if message['payload'].get('mimeType') == 'text/html':
                    html_body = decode_body(message['payload'])
                else:
                    body = decode_body(message['payload'])

            # If we only have HTML, extract text from it
            if not body and html_body:
                body = extract_text_from_html(html_body)

            # Get attachments info
            attachments = get_attachments_info(message)

            emails.append({
                'from': from_email,
                'subject': subject,
                'date': date,
                'body': body,
                'message_id': msg['id'],
                'attachments': attachments
            })

        return emails
    except Exception as e:
        return [{'error': f"Error searching emails: {str(e)}"}]
