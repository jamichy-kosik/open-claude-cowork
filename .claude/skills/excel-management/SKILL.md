---
name: excel-management
description: Skill for working with Excel files - converting to CSV for efficient LLM processing, column operations, filtering, sorting, and data analysis.
---

# Excel Management Skill

## Overview
Skill pro práci s Excel soubory (.xlsx, .xls) - převod na CSV pro optimální zpracování LLM, operace se sloupci, filtrování, řazení a analýza dat.

## Prerequisites
- Python knihovny: `pandas`, `openpyxl`, `xlrd`
- Automaticky konvertuje Excel do CSV nebo Markdown formátu

## ⚡ Nové: Jednodušší načítání souborů podle názvu

### ✅ DOPORUČENO: By Filename (Simplest)
```python
# Jednoduše použij název souboru - automaticky ho najde
info = get_excel_info_by_filename("W43-44-2025.xlsx")
csv = excel_to_csv_by_filename("data.xlsx", "Sheet1")
```

**Pro AI agenty: Vždy preferuj funkce `*_by_filename()` - nepotřebuješ znát složitou cestu!**

## Functions

### `excel_to_csv_by_filename(filename: str, sheet_name: str = None) -> str`
**✅ DOPORUČENO** - Převede Excel na CSV podle názvu souboru.

**Parameters:**
- `filename`: Název Excel souboru (např. "W43-44-2025.xlsx")
- `sheet_name`: Název listu (None = první list)

**Returns:** CSV text

**Example:**
```python
from excel_helper import excel_to_csv_by_filename

csv = excel_to_csv_by_filename("W43-44-2025.xlsx")
print(csv)

# Specifický list
csv = excel_to_csv_by_filename("data.xlsx", "Q1 Sales")
```

### `get_excel_info_by_filename(filename: str) -> dict`
**✅ DOPORUČENO** - Získá informace o Excel souboru podle názvu.

**Parameters:**
- `filename`: Název Excel souboru

**Returns:** Dictionary s informacemi o listech, sloupcích, řádcích

**Example:**
```python
from excel_helper import get_excel_info_by_filename

info = get_excel_info_by_filename("W43-44-2025.xlsx")
print(f"Sheets: {info['sheets']}")
print(f"Rows: {info['sheets_info']['Sheet1']['rows']}")
print(f"Columns: {info['sheets_info']['Sheet1']['column_names']}")
```

### `excel_to_csv(excel_path: str, sheet_name: str = None) -> str`
Převede Excel soubor na CSV text pro efektivní zpracování LLM.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `sheet_name`: Název listu (None = první list)

**Returns:** CSV text s daty

**Example:**
```python
from excel_helper import excel_to_csv

csv_text = excel_to_csv(".agent_uploads/user_1/conv_5/sales.xlsx", "Q1 Sales")
print(csv_text)
```

### `get_columns(excel_path: str, sheet_name: str = None) -> List[str]`
Získá seznam všech názvů sloupců.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `sheet_name`: Název listu

**Returns:** Seznam názvů sloupců

**Example:**
```python
from excel_helper import get_columns

columns = get_columns("data.xlsx")
print(f"Sloupce: {', '.join(columns)}")
```

### `get_column_data(excel_path: str, column_name: str, sheet_name: str = None) -> List`
Získá všechna data z konkrétního sloupce.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `column_name`: Název sloupce
- `sheet_name`: Název listu

**Returns:** Seznam hodnot z sloupce

**Example:**
```python
from excel_helper import get_column_data

revenues = get_column_data("sales.xlsx", "Revenue")
print(f"Revenues: {revenues}")
```

### `get_column_summary(excel_path: str, column_name: str, sheet_name: str = None) -> dict`
Vypočítá statistiky pro číselný sloupec (sum, avg, min, max, count).

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `column_name`: Název číselného sloupce
- `sheet_name`: Název listu

**Returns:** Dictionary se statistikami

**Example:**
```python
from excel_helper import get_column_summary

stats = get_column_summary("sales.xlsx", "Revenue")
print(f"Total: ${stats['sum']:,.2f}")
print(f"Average: ${stats['avg']:,.2f}")
```

### `filter_by_column(excel_path: str, column_name: str, operator: str, value: Any, sheet_name: str = None) -> str`
Filtruje řádky podle hodnoty ve sloupci a vrátí jako CSV.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `column_name`: Název sloupce pro filtrování
- `operator`: Operátor - "==", "!=", ">", "<", ">=", "<=", "contains"
- `value`: Hodnota pro porovnání
- `sheet_name`: Název listu

**Returns:** CSV text s vyfiltrovanými daty

**Example:**
```python
from excel_helper import filter_by_column

# Najdi všechny high-value sales
high_sales = filter_by_column("sales.xlsx", "Revenue", ">", 10000)
print(high_sales)

# Najdi konkrétní produkt
product_a = filter_by_column("sales.xlsx", "Product", "==", "Product A")
```

### `sort_by_column(excel_path: str, column_name: str, ascending: bool = True, limit: int = None, sheet_name: str = None) -> str`
Seřadí data podle sloupce a vrátí jako CSV.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `column_name`: Název sloupce pro řazení
- `ascending`: True = vzestupně, False = sestupně
- `limit`: Maximální počet řádků (None = všechny)
- `sheet_name`: Název listu

**Returns:** CSV text se seřazenými daty

**Example:**
```python
from excel_helper import sort_by_column

# Top 10 produktů podle ratingu
top_products = sort_by_column("products.xlsx", "Rating", ascending=False, limit=10)
print(top_products)
```

### `select_columns(excel_path: str, columns: List[str], sheet_name: str = None) -> str`
Vybere jen určité sloupce a vrátí jako CSV.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `columns`: Seznam názvů sloupců k výběru
- `sheet_name`: Název listu

**Returns:** CSV text s vybranými sloupci

**Example:**
```python
from excel_helper import select_columns

# Export jen důležitých sloupců
report = select_columns("full_data.xlsx", ["Name", "Revenue", "Status"])
print(report)
```

### `get_unique_values(excel_path: str, column_name: str, sheet_name: str = None) -> List`
Získá unikátní hodnoty ve sloupci.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `column_name`: Název sloupce
- `sheet_name`: Název listu

**Returns:** Seznam unikátních hodnot

**Example:**
```python
from excel_helper import get_unique_values

categories = get_unique_values("products.xlsx", "Category")
print(f"Kategorie: {', '.join(categories)}")
```

### `count_values(excel_path: str, column_name: str, sheet_name: str = None) -> dict`
Spočítá výskyty jednotlivých hodnot ve sloupci.

**Parameters:**
- `excel_path`: Cesta k Excel souboru
- `column_name`: Název sloupce
- `sheet_name`: Název listu

**Returns:** Dictionary {hodnota: počet}

**Example:**
```python
from excel_helper import count_values

product_counts = count_values("orders.xlsx", "Product")
print("Počet objednávek podle produktu:")
for product, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {product}: {count}")
```

## Typical Workflows

### 1. Rychlý přehled Excel souboru
```python
from excel_helper import get_excel_info, get_columns, excel_to_csv

# Metadata
info = get_excel_info("data.xlsx")
print(f"Listy: {info['sheets']}")

# Sloupce prvního listu
columns = get_columns("data.xlsx")
print(f"Sloupce: {columns}")

# Preview prvních 10 řádků
csv_preview = excel_to_csv("data.xlsx")
lines = csv_preview.split('\n')[:11]  # header + 10 rows
print('\n'.join(lines))
```

### 2. Analýza prodejních dat
```python
from excel_helper import get_column_summary, sort_by_column, filter_by_column

# Celkové statistiky
revenue_stats = get_column_summary("sales.xlsx", "Revenue")
print(f"Celkové tržby: ${revenue_stats['sum']:,.2f}")
print(f"Průměrná transakce: ${revenue_stats['avg']:,.2f}")

# Top 5 nejlepších sales
top_sales = sort_by_column("sales.xlsx", "Revenue", ascending=False, limit=5)
print("\nTop 5 sales:")
print(top_sales)

# High-value transactions
high_value = filter_by_column("sales.xlsx", "Revenue", ">", 50000)
print(f"\nHigh-value transactions:\n{high_value}")
```

### 3. Filtrování a export dat
```python
from excel_helper import filter_by_column, select_columns

# Najdi všechny aktivní zákazníky
active = filter_by_column("customers.xlsx", "Status", "==", "Active")

# Vytvoř report jen s důležitými sloupci
report = select_columns("customers.xlsx", ["Name", "Email", "Revenue", "Status"])

# Kombinace: active customers + jen důležité sloupce
# (můžeš uložit filtered data do temp souboru a pak select columns)
```

### 4. Agregace a seskupování
```python
from excel_helper import count_values, get_unique_values

# Kolik objednávek podle produktu
product_counts = count_values("orders.xlsx", "Product")
print("Top 3 produkty:")
for product, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"  {product}: {count} objednávek")

# Všechny unikátní kategorie
categories = get_unique_values("products.xlsx", "Category")
print(f"\nDostupné kategorie: {', '.join(categories)}")
```

### 5. Hledání a analýza konkrétních dat
```python
from excel_helper import search_in_excel, filter_by_column, get_column_data

# Najdi všechny výskyty konkrétního zákazníka
results = search_in_excel("transactions.xlsx", "John Doe")
print(f"Nalezeno {len(results)} transakcí pro John Doe")

# Filtruj podle více kritérií (postupně)
# 1. Filtruj podle kategorie
category_data = filter_by_column("products.xlsx", "Category", "==", "Electronics")
# 2. Ulož do temp souboru a filtruj znovu podle ceny
# (nebo použij pandas přímo v Bash nástroji)
```

### 6. Export pro další zpracování
```python
from excel_helper import excel_to_csv, select_columns

# Převeď celý Excel na CSV pro bulk zpracování
csv_data = excel_to_csv("large_dataset.xlsx")

# Nebo jen relevantní sloupce
minimal_csv = select_columns("large_dataset.xlsx", ["ID", "Name", "Value"])

# Můžeš pak zpracovat CSV v Bash nebo uložit:
# with open("output.csv", "w") as f:
#     f.write(minimal_csv)
```

## Best Practices

### 1. Použij CSV převod pro velké datasety
```python
# Místo čtení celého Excel do paměti:
csv_text = excel_to_csv("big_file.xlsx")
# CSV je kompaktnější a rychlejší pro LLM zpracování
```

### 2. Filtruj před exportem
```python
# Místo exportu všeho a pak filtrování:
filtered_csv = filter_by_column("data.xlsx", "Status", "==", "Active")
# Menší data = rychlejší zpracování
```

### 3. Používej column selection pro relevantní data
```python
# Místo všech sloupců:
relevant_data = select_columns("full_data.xlsx", ["Name", "Revenue"])
# Méně tokenů pro LLM
```

### 4. Kombinuj funkce pro komplexní queries
```python
# 1. Filtruj
active_customers = filter_by_column("customers.xlsx", "Status", "==", "Active")

# 2. Seřaď podle revenue
sorted_customers = sort_by_column("customers.xlsx", "Revenue", ascending=False)

# 3. Vezmi top 10
top_10 = sort_by_column("customers.xlsx", "Revenue", ascending=False, limit=10)
```

## Notes
- **CSV formát je efektivnější** pro LLM než JSON nebo Markdown pro velké datasety
- **Pandas automaticky detekuje typy** - čísla, datumy, text
- **Podporuje .xlsx i .xls** soubory
- **Zachovává prázdné buňky** jako prázdné stringy v CSV
