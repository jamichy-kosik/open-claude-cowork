"""
Google Sheets Helper Functions
Provides Python functions for Google Sheets operations via Google Sheets API.
"""

import os
import sys
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


def get_sheets_service():
    """
    Authenticates and returns Google Sheets API service from database.
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
            # Zkusíme nejprve 'sheets', pokud neexistuje, použijeme 'google_drive' credentials
            # (Drive API má automaticky přístup i k Sheets)
            try:
                creds = get_user_credentials(user_id, 'sheets', db)
            except ValueError:
                try:
                    creds = get_user_credentials(user_id, 'google_drive', db)
                except ValueError:
                    raise OAuthRequiredException('sheets')
            
            if not creds:
                raise OAuthRequiredException('sheets')
            
            return build('sheets', 'v4', credentials=creds)
        except ValueError:
            raise OAuthRequiredException('sheets')
        finally:
            db.close()
    
    except OAuthRequiredException:
        raise
    except ImportError as e:
        raise Exception(f"Failed to import database services: {str(e)}. Make sure the agent-web-app backend is available.")
    except Exception as e:
        raise Exception(f"Failed to get Sheets service: {str(e)}")


def read_sheet_data(spreadsheet_id: str, sheet_name: str, start_range: str = None, end_range: str = None) -> str:
    """
    Reads data from a Google Sheets spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in URL between /d/ and /edit)
                       Example: '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
        sheet_name: Name of the sheet (e.g., 'Sheet1', '52.week')
        start_range: Starting cell (e.g., 'A1'). Optional - if not provided, reads entire sheet
        end_range: Ending cell (e.g., 'C10'). Optional - if not provided, reads from start to end of data
    
    Returns:
        Pipe-separated text format with rows on separate lines
    """
    service = get_sheets_service()
    sheet = service.spreadsheets()
    
    # Construct range_name with ! separator
    if start_range and end_range:
        range_name = f"{sheet_name}!{start_range}:{end_range}"
    elif start_range:
        range_name = f"{sheet_name}!{start_range}"
    else:
        range_name = sheet_name
    
    try:
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        values = result.get('values', [])
        
        if not values:
            return "Žádná data nebyla nalezena."
        
        # Convert to simple text format with pipe separators
        output = []
        for row in values:
            # Pad short rows with empty strings
            output.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(output)
    
    except Exception as e:
        return f"❌ Chyba čtení: {str(e)}"


def update_row(spreadsheet_id: str, sheet_name: str, row_number: int, start_column: str, values: list) -> str:
    """
    Updates specific cells in a given row.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: Name of the sheet (e.g., 'Sheet1', '52.week')
        row_number: Row number to update (1-based, e.g., 1 for first row)
        start_column: Starting column letter (e.g., 'A', 'N')
        values: List of values to write
    
    Returns:
        Success message or error message
    """
    service = get_sheets_service()
    
    # Calculate end column based on number of values
    start_col_index = ord(start_column.upper()) - ord('A')
    end_col_index = start_col_index + len(values) - 1
    
    # Convert column index back to letter
    if end_col_index < 26:
        end_column = chr(ord('A') + end_col_index)
    else:
        # Handle columns beyond Z (AA, AB, etc.)
        first_letter = chr(ord('A') + (end_col_index // 26) - 1)
        second_letter = chr(ord('A') + (end_col_index % 26))
        end_column = first_letter + second_letter
    
    range_name = f"{sheet_name}!{start_column}{row_number}:{end_column}{row_number}"
    
    body = {'values': [values]}
    
    try:
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        updated_cells = result.get('updatedCells', 0)
        return f"✅ Řádek {row_number} aktualizován. Aktualizováno {updated_cells} buněk."
    
    except Exception as e:
        return f"❌ Chyba zápisu: {str(e)}"


def append_row(spreadsheet_id: str, sheet_name: str, values: list, start_column: str = 'A', check_column: str = None) -> str:
    """
    Appends a new row by finding the first empty row and updating it.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: Name of the sheet (e.g., 'Sheet1', '52.week')
        values: List of values for the columns
               Example: ['2025-01-01', 'Coffee', '85 CZK']
        start_column: Starting column letter where values will be written (default: 'A')
        check_column: Column to check for empty cells to find next row (default: same as start_column)
                     Example: 'N' - checks column N for empty cells
    
    Returns:
        Success message with row number, or error message
    """
    service = get_sheets_service()
    
    # Use start_column as check_column if not specified
    if check_column is None:
        check_column = start_column
    
    try:
        # Read the check column to find first empty row
        # Read a large range to ensure we get all data
        range_name = f"{sheet_name}!{check_column}:{check_column}"
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        existing_values = result.get('values', [])
        
        # Find first empty row (row number is 1-based)
        next_row = len(existing_values) + 1
        
        # Check if last few rows are actually empty
        for i in range(len(existing_values) - 1, -1, -1):
            if not existing_values[i] or not existing_values[i][0] or str(existing_values[i][0]).strip() == '':
                next_row = i + 1
            else:
                break
        
        # Use update_row to write to the specific row
        return update_row(spreadsheet_id, sheet_name, next_row, start_column, values)
    
    except Exception as e:
        return f"❌ Chyba při hledání prázdného řádku: {str(e)}"
