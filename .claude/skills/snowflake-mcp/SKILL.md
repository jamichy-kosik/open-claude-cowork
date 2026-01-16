---
name: snowflake-mcp
description: Provides access to Snowflake ML Reporting database via MCP server. Use for executing SQL queries, searching ML feedback, and interacting with feedback agent. Only for KOSIK ML_REPORTING schema.
---

# Snowflake MCP Management Skill

## Overview

This skill provides access to Snowflake ML Reporting database through the MCP (Model Context Protocol) server. It enables SQL queries, feedback search, and agent interactions.

## Available Tools

The MCP server provides three main tools:
1. **ml_reporting_sql** - Execute SQL queries
2. **ml_feedback_sum_search** - Search ML feedback summaries
3. **feedback_agent** - Interact with feedback analysis agent

## Prerequisites

- **Token Storage**: Snowflake MCP token is stored in the database per-user
  - For logged-in users: Token is automatically loaded from database
  - For manual testing: Set `SNOWFLAKE_MCP_TOKEN` environment variable
  - Users can set their token through the application Settings page
- Python package: `requests`
- Access to Snowflake MCP server at KOSIK.ML_REPORTING schema

## Authentication

The helper automatically loads the Snowflake token using this priority:
1. **Database (preferred)**: When running through the agent, token is loaded from the user's database credentials
2. **Environment variable (fallback)**: `SNOWFLAKE_MCP_TOKEN` for manual testing

The agent automatically sets `AGENT_USER_ID` which enables database token loading.

## Important: Working Directory

**Always run commands from the skill directory:**
```bash
cd "../../.claude/skills/snowflake-mcp"
```

The helper automatically loads `.env` from the project root.

## Functions

### 1. List Available MCP Tools

Get list of all available tools from the MCP server.

**Usage:**
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import list_mcp_tools; import json; print(json.dumps(list_mcp_tools(), indent=2))"
```

**Returns:**
List of tools with their names, descriptions, and input schemas.

### 2. Execute SQL Query

Execute SQL queries on Snowflake ML_REPORTING schema.

**Usage:**
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import execute_sql_query; print(execute_sql_query('SHOW TABLES IN SCHEMA KOSIK.ML_REPORTING'))"
```

**Parameters:**
- `sql` (string): SQL query to execute

**Examples:**
```bash
# List tables
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import execute_sql_query; print(execute_sql_query('SHOW TABLES IN SCHEMA KOSIK.ML_REPORTING'))"

# Count rows
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import execute_sql_query; print(execute_sql_query('SELECT COUNT(*) FROM KOSIK.ML_REPORTING.TABLE_NAME'))"

# Select data
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import execute_sql_query; print(execute_sql_query('SELECT * FROM KOSIK.ML_REPORTING.TABLE_NAME LIMIT 10'))"
```

### 3. Search ML Feedback

Search through ML feedback summaries using semantic search.

**Usage:**
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import search_feedback; print(search_feedback('customer complaints about product quality'))"
```

**Parameters:**
- `query` (string): Search query for feedback

**Example:**
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import search_feedback; print(search_feedback('delivery issues'))"
```

### 4. Call Feedback Agent

Interact with the feedback analysis agent for insights and analysis.

**Usage:**
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import call_feedback_agent; print(call_feedback_agent('Analyze recent negative feedback trends'))"
```

**Parameters:**
- `input_text` (string): Question or task for the agent

**Example:**
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import call_feedback_agent; print(call_feedback_agent('What are the main customer complaints this month?'))"
```

## Configuration

Required environment variable in `.env` file:
```
SNOWFLAKE_MCP_TOKEN=your_bearer_token_here
```

## Security

- All requests use Bearer token authentication
- Token is read from environment variable
- Only executes queries through MCP server (server-side security applies)

## Error Handling

All functions return error information if something fails:
```json
{
  "error": "Error description"
}
```

## Examples

### Example 1: List all tables
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import execute_sql_query; print(execute_sql_query('SHOW TABLES IN SCHEMA KOSIK.ML_REPORTING'))"
```

### Example 2: Get table structure
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import execute_sql_query; print(execute_sql_query('DESCRIBE TABLE KOSIK.ML_REPORTING.YOUR_TABLE'))"
```

### Example 3: Query data
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import execute_sql_query; print(execute_sql_query('SELECT * FROM KOSIK.ML_REPORTING.YOUR_TABLE LIMIT 5'))"
```

### Example 4: Search feedback
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import search_feedback; print(search_feedback('product quality issues'))"
```

### Example 5: Ask feedback agent
```bash
cd "../../.claude/skills/snowflake-mcp" && python -c "from snowflake_mcp_helper import call_feedback_agent; print(call_feedback_agent('Summarize top 5 customer concerns'))"
```

## Notes

- MCP server URL: `https://lvourab-yr02508.snowflakecomputing.com/api/v2/databases/KOSIK/schemas/ML_REPORTING/mcp-servers/KOSIK_ML_REPORTING_MCP`
- Database: KOSIK
- Schema: ML_REPORTING
- Uses JSON-RPC 2.0 protocol
