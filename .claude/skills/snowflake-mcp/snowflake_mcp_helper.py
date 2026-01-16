"""
Snowflake MCP Helper Functions
Provides functions to interact with Snowflake MCP server via JSON-RPC
"""
import os
import json
import requests
from typing import Any, Dict, List
from pathlib import Path

# MCP Server Configuration
MCP_URL = "https://lvourab-yr02508.snowflakecomputing.com/api/v2/databases/KOSIK/schemas/ML_REPORTING/mcp-servers/KOSIK_ML_REPORTING_MCP"

def get_snowflake_token_from_db() -> str:
    """
    Načte Snowflake token z databáze pro aktuálního uživatele
    Používá AGENT_USER_ID environment variable nastavené agent_service.py
    
    Returns:
        Snowflake MCP token z databáze
        
    Raises:
        ValueError: Pokud není nastavený AGENT_USER_ID nebo uživatel nemá token
    """
    user_id = os.getenv('AGENT_USER_ID')
    if not user_id:
        raise ValueError("AGENT_USER_ID not set in environment")
    
    try:
        # Nastavíme DATABASE_URL pro Docker prostředí před importem
        if os.path.exists("/app/data/agent_app.db"):
            os.environ['DATABASE_URL'] = 'sqlite:////app/data/agent_app.db'
        
        # Import zde aby fungovalo i mimo agent context
        import sys
        # Pro Docker: /app je přímo backend root
        if os.path.exists("/app/app/core/database.py"):
            sys.path.insert(0, "/app")
        else:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'agent-web-app' / 'backend'))
        
        from app.core.database import SessionLocal
        from app.services.oauth_service import get_snowflake_token
        
        db = SessionLocal()
        try:
            token = get_snowflake_token(int(user_id), db)
            return token
        finally:
            db.close()
    except Exception as e:
        raise ValueError(f"Failed to load Snowflake token from database: {str(e)}")

def get_headers() -> Dict[str, str]:
    """
    Get headers with auth token
    Priorita:
    1. Token z databáze (pokud je nastaven AGENT_USER_ID)
    2. Token z environment variable SNOWFLAKE_MCP_TOKEN
    """
    token = None
    
    # Pokusit se načíst token z databáze pokud běží v agent contextu
    if os.getenv('AGENT_USER_ID'):
        try:
            token = get_snowflake_token_from_db()
        except Exception as e:
            # Logovat error ale pokračovat - fallback na env variable
            print(f"Warning: Failed to load token from database: {e}")
    
    # Fallback na environment variable
    if not token:
        token = os.getenv('SNOWFLAKE_MCP_TOKEN', '')
    
    if not token:
        raise ValueError(
            "Snowflake token not found. Please either:\n"
            "1. Set your token in the application settings (for logged in users)\n"
            "2. Set SNOWFLAKE_MCP_TOKEN environment variable"
        )
    
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

def call_mcp_method(method: str, params: Dict[str, Any] = None) -> Any:
    """
    Call MCP server JSON-RPC method
    
    Args:
        method: JSON-RPC method name (e.g., 'tools/list', 'tools/call')
        params: Method parameters
    
    Returns:
        Result from MCP server
    """
    if params is None:
        params = {}
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    try:
        response = requests.post(MCP_URL, json=payload, headers=get_headers(), timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if 'error' in result:
            return {'error': result['error']}
        
        return result.get('result', {})
    except requests.exceptions.RequestException as e:
        return {'error': f'Request failed: {str(e)}'}
    except json.JSONDecodeError as e:
        return {'error': f'Invalid JSON response: {str(e)}'}

def list_mcp_tools() -> List[Dict[str, Any]]:
    """
    List all available tools from MCP server
    
    Returns:
        List of available tools with their descriptions
    """
    result = call_mcp_method('tools/list')
    if 'error' in result:
        return [{'error': result['error']}]
    
    tools = result.get('tools', [])
    return tools

def execute_sql_query(sql: str) -> Any:
    """
    Execute SQL query using MCP ml_reporting_sql tool
    
    Args:
        sql: SQL query to execute
    
    Returns:
        Query results
    """
    params = {
        "name": "ml_reporting_sql",
        "arguments": {
            "sql": sql
        }
    }
    
    result = call_mcp_method('tools/call', params)
    
    if 'error' in result:
        return {'error': result['error']}
    
    # Parse the response
    content = result.get('content', [])
    if content and len(content) > 0:
        return content[0].get('text', '')
    
    return result

def search_feedback(query: str) -> Any:
    """
    Search ML feedback using MCP ml_feedback_sum_search tool
    
    Args:
        query: Search query
    
    Returns:
        Search results
    """
    params = {
        "name": "ml_feedback_sum_search",
        "arguments": {
            "query": query
        }
    }
    
    result = call_mcp_method('tools/call', params)
    
    if 'error' in result:
        return {'error': result['error']}
    
    # Parse the response
    content = result.get('content', [])
    if content and len(content) > 0:
        return content[0].get('text', '')
    
    return result

def call_feedback_agent(input_text: str) -> Any:
    """
    Call feedback agent using MCP feedback_agent tool
    
    Args:
        input_text: Input text for the agent
    
    Returns:
        Agent response
    """
    params = {
        "name": "feedback_agent",
        "arguments": {
            "input": input_text
        }
    }
    
    result = call_mcp_method('tools/call', params)
    
    if 'error' in result:
        return {'error': result['error']}
    
    # Parse the response
    content = result.get('content', [])
    if content and len(content) > 0:
        return content[0].get('text', '')
    
    return result

# Main function for testing
if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    
    print("Testing Snowflake MCP Helper...")
    print("\n1. Listing available tools:")
    tools = list_mcp_tools()
    print(json.dumps(tools, indent=2))
    
    print("\n2. Testing SQL query:")
    result = execute_sql_query("SHOW TABLES IN SCHEMA KOSIK.ML_REPORTING LIMIT 5")
    print(result)
