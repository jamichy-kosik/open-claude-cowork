#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Report Runner - Košík
Jednoduchý wrapper pro spuštění celého procesu
"""

import sys
import subprocess
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generuj weekly sales report')
    parser.add_argument('--w1', required=True, help='Cesta k CSV souboru pro týden W-1 (např. sales_sku_2025W51.csv)')
    parser.add_argument('--w2', required=True, help='Cesta k CSV souboru pro aktuální týden (např. sales_sku_2025W52.csv)')
    parser.add_argument('--output', default='Weekly_Sales_Report.pdf', help='Název výstupního PDF (default: Weekly_Sales_Report.pdf)')
    args = parser.parse_args()

    w1_path = Path(args.w1)
    w2_path = Path(args.w2)

    if not w1_path.exists():
        print(f"CHYBA: Soubor nenalezen: {w1_path}")
        sys.exit(1)

    if not w2_path.exists():
        print(f"CHYBA: Soubor nenalezen: {w2_path}")
        sys.exit(1)

    # Detekuj week ID z názvu souboru
    w1_id = extract_week_id(w1_path.name)
    w2_id = extract_week_id(w2_path.name)

    print(f"Zpracovávám: {w1_id} vs {w2_id}")
    print(f"Soubory: {w1_path} → {w2_path}")
    print("-" * 80)

    # Uprav analyze_weekly_sales.py aby bral argumenty
    console_output = f"weekly_report_{w2_id.lower()}_console.txt"

    # Vytvoř dočasný skript s dynamickými cestami
    temp_script = create_temp_script(w1_path, w2_path, w1_id, w2_id, console_output)

    # Spusť analýzu
    print("Krok 1/2: Spouštím analýzu dat...")
    result = subprocess.run([sys.executable, temp_script], capture_output=True, text=True)

    with open(console_output, 'w', encoding='utf-8') as f:
        f.write(result.stdout)

    if result.returncode != 0:
        print(f"CHYBA při analýze:\n{result.stderr}")
        sys.exit(1)

    print(f"   → Console output: {console_output}")

    # Generuj PDF
    print("Krok 2/2: Generuji PDF report...")
    pdf_script = create_pdf_script(console_output, args.output)
    result = subprocess.run([sys.executable, pdf_script], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"CHYBA při generování PDF:\n{result.stderr}")
        sys.exit(1)

    print(f"   → PDF vytvořeno: {args.output}")
    print("-" * 80)
    print("HOTOVO! Weekly report úspěšně vygenerován.")

    # Cleanup
    Path(temp_script).unlink()
    Path(pdf_script).unlink()

def extract_week_id(filename):
    """Extrahuj week ID z názvu souboru (např. 'W51' z 'sales_sku_2025W51.csv')"""
    import re
    match = re.search(r'W(\d+)', filename.upper())
    if match:
        return f"W{match.group(1)}"
    return "W??"

def create_temp_script(w1_path, w2_path, w1_id, w2_id, console_output):
    """Vytvoř dočasný skript s dynamickými cestami"""
    skill_dir = Path(__file__).parent
    base_script = skill_dir / "analyze_weekly_sales.py"

    with open(base_script, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nahraď hardcodované cesty
    content = content.replace(
        'w51_path = Path(r"C:\\Users\\JakubMichna\\WORK\\ai-agent-business-poc\\.agent_uploads\\user_1\\conv_118\\1\\sales_sku_2025W51.csv")',
        f'w51_path = Path(r"{w1_path.absolute()}")'
    )
    content = content.replace(
        'w52_path = Path(r"C:\\Users\\JakubMichna\\WORK\\ai-agent-business-poc\\.agent_uploads\\user_1\\conv_118\\1\\sales_sku_2025W52.csv")',
        f'w52_path = Path(r"{w2_path.absolute()}")'
    )
    content = content.replace('load_and_clean_data(w51_path, "W51")', f'load_and_clean_data(w51_path, "{w1_id}")')
    content = content.replace('load_and_clean_data(w52_path, "W52")', f'load_and_clean_data(w52_path, "{w2_id}")')

    temp_script = skill_dir / "_temp_analyze.py"
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(content)

    return str(temp_script)

def create_pdf_script(console_output, pdf_output):
    """Vytvoř dočasný PDF skript"""
    skill_dir = Path(__file__).parent
    base_script = skill_dir / "generate_pdf_report.py"

    with open(base_script, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nahraď výstupní cesty
    content = content.replace(
        'console_path = Path("weekly_report_w52_console.txt")',
        f'console_path = Path(r"{console_output}")'
    )
    content = content.replace(
        'pdf_path = Path("Weekly_Sales_Report_W52_2025.pdf")',
        f'pdf_path = Path(r"{pdf_output}")'
    )

    temp_script = skill_dir / "_temp_pdf.py"
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(content)

    return str(temp_script)

if __name__ == '__main__':
    main()
