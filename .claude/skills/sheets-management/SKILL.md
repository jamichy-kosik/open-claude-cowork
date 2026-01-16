---
name: sheets-management
description: Manages Google Sheets operations including reading sheet data and appending new rows to spreadsheets.
---

# Google Sheets Management Skill

This skill provides Google Sheets operations through the Google Sheets API.

## Important: Working Directory

**Always run commands from the skill directory:**
```bash
cd "../../.claude/skills/sheets-management"
```

## Available Functions

### 1. Read Sheet Data
Reads data from a specified range in a Google Sheets spreadsheet.

```bash
cd "../../.claude/skills/sheets-management" && python -c "from sheets_helper import read_sheet_data; print(read_sheet_data('SPREADSHEET_ID', 'Sheet1', 'A1', 'C10'))"
```

Or in Python:
```python
from sheets_helper import read_sheet_data

# Read data from spreadsheet
spreadsheet_id = "1abc...xyz"  # Found in URL between /d/ and /edit
sheet_name = "List1"
start_range = "A1"
end_range = "C10"

result = read_sheet_data(spreadsheet_id, sheet_name, start_range, end_range)
print(result)

# Read entire sheet (no range specified)
result = read_sheet_data(spreadsheet_id, "List1")
print(result)

# Read specific columns (entire column range)
result = read_sheet_data(spreadsheet_id, "List1", "B", "D")
print(result)

# Read from specific cell to end of data
result = read_sheet_data(spreadsheet_id, "List1", "A1")
print(result)
```

**Spreadsheet ID Format:**
- Found in the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- Example: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

**Parameters:**
- `spreadsheet_id`: The spreadsheet ID from URL
- `sheet_name`: Name of the sheet (e.g., 'Sheet1', '52.week')
- `start_range`: Starting cell (e.g., 'A1', 'B') - optional
- `end_range`: Ending cell (e.g., 'C10', 'D') - optional

Returns pipe-separated text format:
```
Header1 | Header2 | Header3
Value1 | Value2 | Value3
Value4 | Value5 | Value6
```

### 2. Update Row
Writes values to specific cells in a given row.

```bash
cd "../../.claude/skills/sheets-management" && python -c "from sheets_helper import update_row; print(update_row('SPREADSHEET_ID', 'Sheet1', 5, 'A', ['Value1', 'Value2', 'Value3']))"
```

Or in Python:
```python
from sheets_helper import update_row

# Write values to row 5, starting at column A
spreadsheet_id = "1abc...xyz"
sheet_name = "List1"
row_number = 5
values = ["2025-12-01", "Coffee", "85 CZK"]

result = update_row(spreadsheet_id, sheet_name, row_number, start_column='A', values=values)
print(result)

# Write to specific columns (e.g., columns N, O, P in row 10)
values = ["12345", "Product Name", "Active"]
result = update_row(spreadsheet_id, "52.week", 10, start_column='N', values=values)
print(result)
```

**Parameters:**
- `spreadsheet_id`: The spreadsheet ID
- `sheet_name`: Name of the sheet (e.g., 'Sheet1', '52.week')
- `row_number`: Row number to update (1-based, e.g., 1 for first row)
- `start_column`: Starting column letter (e.g., 'A', 'N', 'AA')
- `values`: List of values to write

### 3. Append Row
Appends a new row by finding the first empty row and updating it.

```bash
cd "../../.claude/skills/sheets-management" && python -c "from sheets_helper import append_row; print(append_row('SPREADSHEET_ID', 'Sheet1', ['Value1', 'Value2', 'Value3'], 'A', 'A'))"
```

Or in Python:
```python
from sheets_helper import append_row

# Add new row with data (checks column A for empty cells)
spreadsheet_id = "1abc...xyz"
sheet_name = "List1"
values = ["2025-12-01", "Oběd", "200 CZK"]

result = append_row(spreadsheet_id, sheet_name, values, start_column='A')
print(result)

# Write to columns N-AG, but check column N for empty rows
values = ["12345", "Product", "25.50", "2025-01-01", "2025-12-31"]
result = append_row(spreadsheet_id, "52.week", values, start_column='N', check_column='N')
print(result)

# Add multiple rows
for data in [["Row1", "Data1"], ["Row2", "Data2"], ["Row3", "Data3"]]:
    result = append_row(spreadsheet_id, "Sheet1", data, start_column='A')
    print(result)
```

**Parameters:**
- `spreadsheet_id`: The spreadsheet ID
- `sheet_name`: Name of the sheet (e.g., 'Sheet1', '52.week')
- `values`: List of values for the columns
- `start_column`: Starting column letter where values will be written (default: 'A')
- `check_column`: Column to check for empty cells to find next row (optional, defaults to start_column)
                 Example: If writing to columns N-AG but want to check column N for empty rows

**How it works:**
1. Reads the `check_column` to find all existing values
2. Finds the first empty row (where check_column is empty)
3. Writes values starting at `start_column` in that row
4. Returns the row number where data was written

**Value Input Options:**
- Values are automatically formatted using `USER_ENTERED` mode
- Numbers are recognized as numbers
- Dates are parsed if in valid format
- Formulas starting with `=` are evaluated

## Authentication

This skill requires:
- `credentials.json` - OAuth client credentials
- `token_sheets.json` - User authentication token (auto-generated on first run)

Both files must be present in the skill directory.

## Error Handling

All functions include comprehensive error handling:
- Missing credentials → Clear error message
- Invalid spreadsheet ID → Returns error description
- Invalid range → Returns range format requirements
- Permission errors → Detailed access error info
- Network issues → Timeout and connection error messages

## Usage Examples

**Example 1: Read and display expense tracker**
```python
from sheets_helper import read_sheet_data

# Read expense data
spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
expenses = read_sheet_data(spreadsheet_id, "Expenses", "A1", "D100")
print("📊 Expense Tracker:")
print(expenses)
```

**Example 2: Add new expense entry**
```python
from sheets_helper import append_row, read_sheet_data
from datetime import date

# Add today's expense
spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
today = date.today().strftime("%Y-%m-%d")
new_expense = [today, "Coffee", "85 CZK", "Food"]

result = append_row(spreadsheet_id, "Expenses", new_expense, start_column='A', check_column='A')
print(result)

# Verify it was added
recent = read_sheet_data(spreadsheet_id, "Expenses", "A1", "D10")
print("\nRecent expenses:")
print(recent)
```

**Example 3: Log multiple entries**
```python
from sheets_helper import append_row

spreadsheet_id = "1abc...xyz"
transactions = [
    ["2025-12-01", "Groceries", "450 CZK"],
    ["2025-12-01", "Transport", "120 CZK"],
    ["2025-12-01", "Dinner", "380 CZK"]
]

for transaction in transactions:
    result = append_row(spreadsheet_id, "Sheet1", transaction, start_column='A', check_column='A')
    print(result)
```

**Example 4: Read and analyze data**
```python
from sheets_helper import read_sheet_data

# Read sales data
spreadsheet_id = "1abc...xyz"
data = read_sheet_data(spreadsheet_id, "Sales", "A", "E")

# Parse and display
lines = data.split('\n')
print(f"Total rows: {len(lines)}")
print(f"Headers: {lines[0]}")
print(f"\nFirst 5 entries:")
for line in lines[1:6]:
    print(line)
```

## Data Format Guidelines

**Reading Data:**
- Empty cells appear as empty strings in output
- Numbers are returned as formatted strings
- Dates are returned in the format set in the sheet
- Formulas return their calculated values

**Appending Data:**
- Pass values as list of strings
- Numbers can be strings like "123" or "45.67"
- Dates should be in format "YYYY-MM-DD"
- Formulas must start with "=" (e.g., "=SUM(A1:A10)")

## Limitations

- Only works with spreadsheets the authenticated user has access to
- No support for batch updates (use multiple append_row calls)
- No support for cell formatting (bold, colors, etc.)
- No support for inserting rows at specific positions (only append)
- No support for deleting rows or columns
- No support for creating new spreadsheets

For these advanced features, use the Google Sheets API directly or extend the skill.

## Finding Spreadsheet ID

1. Open your Google Sheet in browser
2. Look at the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
   ```
3. Copy the long string between `/d/` and `/edit`
4. That's your `spreadsheet_id`

Example URL:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
```

Spreadsheet ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
