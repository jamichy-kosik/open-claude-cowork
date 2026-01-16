"""
Excel Management Skill Helper
Helper functions for working with Excel files - converting to CSV and performing column operations.

Installation:
    pip install pandas openpyxl xlrd

Environment:
    No special environment variables required
"""

import pandas as pd
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import os


def find_uploaded_file(filename: str) -> Optional[Path]:
    """
    Najde nahraný soubor podle názvu v .agent_uploads složce.
    
    Args:
        filename: Název souboru (např. "data.xlsx")
        
    Returns:
        Path: Cesta k souboru nebo None pokud není nalezen
    """
    # Detekce Docker prostředí vs lokální
    if Path("/app/.agent_uploads").exists():
        base_path = Path("/app/.agent_uploads")
    else:
        base_path = Path(".agent_uploads")
    
    # Hledání souboru
    matches = list(base_path.glob(f"**/{filename}"))
    
    if matches:
        return matches[0]  # Vrátí první nalezený
    return None


def excel_to_csv_by_filename(filename: str, sheet_name: Optional[str] = None) -> str:
    """
    Převede Excel na CSV podle názvu souboru (jednodušší než složité cesty).
    
    Args:
        filename: Název Excel souboru
        sheet_name: Název listu (None = první list)
        
    Returns:
        str: CSV text
        
    Example:
        >>> csv = excel_to_csv_by_filename("W43-44-2025.xlsx")
        >>> print(csv)
    """
    try:
        file_path = find_uploaded_file(filename)
        
        if not file_path:
            return f"Error: File '{filename}' not found in uploads"
        
        df = pd.read_excel(str(file_path), sheet_name=sheet_name or 0)
        csv_text = df.to_csv(index=False)
        return csv_text
    except Exception as e:
        return f"Error converting Excel to CSV: {str(e)}"


def get_excel_info_by_filename(filename: str) -> Dict[str, Any]:
    """
    Získá informace o Excel souboru podle názvu.
    
    Args:
        filename: Název Excel souboru
        
    Returns:
        dict: Metadata Excel včetně listů, řádků, sloupců
        
    Example:
        >>> info = get_excel_info_by_filename("data.xlsx")
        >>> print(f"Sheets: {info['sheets']}")
    """
    try:
        file_path = find_uploaded_file(filename)
        
        if not file_path:
            return {'error': f"File '{filename}' not found in uploads"}
        
        xl_file = pd.ExcelFile(str(file_path))
        
        sheets_info = {}
        for sheet_name in xl_file.sheet_names:
            df = xl_file.parse(sheet_name)
            sheets_info[sheet_name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            }
        
        return {
            'sheets': xl_file.sheet_names,
            'num_sheets': len(xl_file.sheet_names),
            'sheets_info': sheets_info,
            'file_size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
            'full_path': str(file_path)
        }
    except Exception as e:
        return {'error': str(e)}


def excel_to_csv(excel_path: str, sheet_name: Optional[str] = None) -> str:
    """
    Convert Excel file to CSV text for efficient LLM processing.
    
    Args:
        excel_path: Path to Excel file
        sheet_name: Sheet name (None = first sheet)
        
    Returns:
        str: CSV formatted text
        
    Example:
        >>> csv_text = excel_to_csv("sales.xlsx", "Q1 Sales")
        >>> print(csv_text)
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        csv_text = df.to_csv(index=False)
        return csv_text
    except Exception as e:
        return f"Error converting Excel to CSV: {str(e)}"


def get_excel_info(excel_path: str) -> Dict[str, Any]:
    """
    Get metadata and basic information about Excel workbook.
    
    Args:
        excel_path: Path to Excel file
        
    Returns:
        dict: Excel metadata including sheets, rows, columns
        
    Example:
        >>> info = get_excel_info("data.xlsx")
        >>> print(f"Sheets: {info['sheets']}")
    """
    try:
        xl_file = pd.ExcelFile(excel_path)
        
        sheets_info = {}
        for sheet_name in xl_file.sheet_names:
            df = xl_file.parse(sheet_name)
            sheets_info[sheet_name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            }
        
        return {
            'sheets': xl_file.sheet_names,
            'num_sheets': len(xl_file.sheet_names),
            'sheets_info': sheets_info,
            'file_size_mb': round(Path(excel_path).stat().st_size / (1024 * 1024), 2)
        }
    except Exception as e:
        return {'error': str(e)}


def get_columns(excel_path: str, sheet_name: Optional[str] = None) -> List[str]:
    """
    Get list of all column names.
    
    Args:
        excel_path: Path to Excel file
        sheet_name: Sheet name
        
    Returns:
        List[str]: List of column names
        
    Example:
        >>> columns = get_columns("data.xlsx")
        >>> print(f"Columns: {', '.join(columns)}")
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        return list(df.columns)
    except Exception as e:
        return [f"Error: {str(e)}"]


def get_column_data(excel_path: str, column_name: str, sheet_name: Optional[str] = None) -> List:
    """
    Get all data from specific column.
    
    Args:
        excel_path: Path to Excel file
        column_name: Column name
        sheet_name: Sheet name
        
    Returns:
        List: List of values from column
        
    Example:
        >>> revenues = get_column_data("sales.xlsx", "Revenue")
        >>> print(f"Revenues: {revenues}")
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        if column_name not in df.columns:
            return [f"Error: Column '{column_name}' not found. Available columns: {', '.join(df.columns)}"]
        return df[column_name].tolist()
    except Exception as e:
        return [f"Error: {str(e)}"]


def get_column_summary(excel_path: str, column_name: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate statistics for numeric column (sum, avg, min, max, count).
    
    Args:
        excel_path: Path to Excel file
        column_name: Numeric column name
        sheet_name: Sheet name
        
    Returns:
        dict: Statistics dictionary
        
    Example:
        >>> stats = get_column_summary("sales.xlsx", "Revenue")
        >>> print(f"Total: ${stats['sum']:,.2f}")
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        
        if column_name not in df.columns:
            return {'error': f"Column '{column_name}' not found"}
        
        col_data = df[column_name]
        
        # Try to convert to numeric
        if not pd.api.types.is_numeric_dtype(col_data):
            col_data = pd.to_numeric(col_data, errors='coerce')
        
        return {
            'sum': float(col_data.sum()),
            'avg': float(col_data.mean()),
            'min': float(col_data.min()),
            'max': float(col_data.max()),
            'count': int(col_data.count()),
            'null_count': int(col_data.isna().sum())
        }
    except Exception as e:
        return {'error': str(e)}


def filter_by_column(excel_path: str, column_name: str, operator: str, value: Any, 
                    sheet_name: Optional[str] = None) -> str:
    """
    Filter rows by column value and return as CSV.
    
    Args:
        excel_path: Path to Excel file
        column_name: Column name for filtering
        operator: Operator - "==", "!=", ">", "<", ">=", "<=", "contains"
        value: Value for comparison
        sheet_name: Sheet name
        
    Returns:
        str: CSV text with filtered data
        
    Example:
        >>> high_sales = filter_by_column("sales.xlsx", "Revenue", ">", 10000)
        >>> print(high_sales)
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        # Apply filter
        if operator == "==":
            filtered_df = df[df[column_name] == value]
        elif operator == "!=":
            filtered_df = df[df[column_name] != value]
        elif operator == ">":
            filtered_df = df[df[column_name] > value]
        elif operator == "<":
            filtered_df = df[df[column_name] < value]
        elif operator == ">=":
            filtered_df = df[df[column_name] >= value]
        elif operator == "<=":
            filtered_df = df[df[column_name] <= value]
        elif operator == "contains":
            filtered_df = df[df[column_name].astype(str).str.contains(str(value), case=False, na=False)]
        else:
            return f"Error: Unknown operator '{operator}'"
        
        return filtered_df.to_csv(index=False)
    except Exception as e:
        return f"Error filtering data: {str(e)}"


def sort_by_column(excel_path: str, column_name: str, ascending: bool = True, 
                  limit: Optional[int] = None, sheet_name: Optional[str] = None) -> str:
    """
    Sort data by column and return as CSV.
    
    Args:
        excel_path: Path to Excel file
        column_name: Column name for sorting
        ascending: True = ascending, False = descending
        limit: Maximum rows to return (None = all)
        sheet_name: Sheet name
        
    Returns:
        str: CSV text with sorted data
        
    Example:
        >>> top_products = sort_by_column("products.xlsx", "Rating", ascending=False, limit=10)
        >>> print(top_products)
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        sorted_df = df.sort_values(by=column_name, ascending=ascending)
        
        if limit:
            sorted_df = sorted_df.head(limit)
        
        return sorted_df.to_csv(index=False)
    except Exception as e:
        return f"Error sorting data: {str(e)}"


def select_columns(excel_path: str, columns: List[str], sheet_name: Optional[str] = None) -> str:
    """
    Select specific columns and return as CSV.
    
    Args:
        excel_path: Path to Excel file
        columns: List of column names to select
        sheet_name: Sheet name
        
    Returns:
        str: CSV text with selected columns
        
    Example:
        >>> report = select_columns("data.xlsx", ["Name", "Revenue", "Status"])
        >>> print(report)
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        
        # Check if all columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            return f"Error: Columns not found: {', '.join(missing_cols)}"
        
        selected_df = df[columns]
        return selected_df.to_csv(index=False)
    except Exception as e:
        return f"Error selecting columns: {str(e)}"


def get_unique_values(excel_path: str, column_name: str, sheet_name: Optional[str] = None) -> List:
    """
    Get unique values in column.
    
    Args:
        excel_path: Path to Excel file
        column_name: Column name
        sheet_name: Sheet name
        
    Returns:
        List: List of unique values
        
    Example:
        >>> categories = get_unique_values("products.xlsx", "Category")
        >>> print(f"Categories: {', '.join(categories)}")
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        
        if column_name not in df.columns:
            return [f"Error: Column '{column_name}' not found"]
        
        unique_vals = df[column_name].dropna().unique().tolist()
        return [str(val) for val in unique_vals]
    except Exception as e:
        return [f"Error: {str(e)}"]


def count_values(excel_path: str, column_name: str, sheet_name: Optional[str] = None) -> Dict[str, int]:
    """
    Count occurrences of each value in column.
    
    Args:
        excel_path: Path to Excel file
        column_name: Column name
        sheet_name: Sheet name
        
    Returns:
        dict: Dictionary {value: count}
        
    Example:
        >>> product_counts = count_values("orders.xlsx", "Product")
        >>> for product, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True):
        ...     print(f"{product}: {count}")
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        
        if column_name not in df.columns:
            return {'error': f"Column '{column_name}' not found"}
        
        value_counts = df[column_name].value_counts().to_dict()
        return {str(k): int(v) for k, v in value_counts.items()}
    except Exception as e:
        return {'error': str(e)}


def search_in_excel(excel_path: str, query: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for text in Excel file and return matches with context.
    
    Args:
        excel_path: Path to Excel file
        query: Search query text
        sheet_name: Sheet name
        
    Returns:
        List[dict]: List of matches with row, column, and value
        
    Example:
        >>> results = search_in_excel("data.xlsx", "John Doe")
        >>> print(f"Found {len(results)} matches")
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        results = []
        
        for col in df.columns:
            matches = df[df[col].astype(str).str.contains(query, case=False, na=False)]
            for idx, row in matches.iterrows():
                results.append({
                    'row': int(idx) + 2,  # +2 because Excel is 1-indexed and has header
                    'column': col,
                    'value': str(row[col]),
                    'full_row': row.to_dict()
                })
        
        return results
    except Exception as e:
        return [{'error': str(e)}]


def excel_to_markdown_table(excel_path: str, sheet_name: Optional[str] = None, max_rows: int = 100) -> str:
    """
    Convert Excel to Markdown table format (for smaller datasets).
    
    Args:
        excel_path: Path to Excel file
        sheet_name: Sheet name
        max_rows: Maximum rows to include
        
    Returns:
        str: Markdown formatted table
        
    Example:
        >>> markdown = excel_to_markdown_table("small_data.xlsx", max_rows=20)
        >>> print(markdown)
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name or 0)
        
        if len(df) > max_rows:
            df = df.head(max_rows)
            truncated_note = f"\n\n*(Showing first {max_rows} of {len(df)} rows)*"
        else:
            truncated_note = ""
        
        markdown = df.to_markdown(index=False)
        return markdown + truncated_note
    except Exception as e:
        return f"Error converting to Markdown: {str(e)}"
