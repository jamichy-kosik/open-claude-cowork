#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validační script pro AI agenty - Self-check před vytvořením nového souboru

POUŽITÍ:
    python validate_approach.py

Tento script zkontroluje, zda agent postupuje správně a neporušuje pravidla.
"""

import sys
from pathlib import Path

# Check 1: Existuje cli_report.py?
cli_path = Path(__file__).parent / "cli_report.py"
lib_path = Path(__file__).parent / "weekly_report_lib.py"

print("=" * 80)
print("VALIDACE WEEKLY SALES REPORT WORKFLOW")
print("=" * 80)

errors = []
warnings = []
ok_checks = []

# Check CLI
if cli_path.exists():
    ok_checks.append("[OK] cli_report.py existuje")
else:
    errors.append("[ERROR] cli_report.py CHYBÍ - agent nemůže použít CLI!")

# Check knihovna
if lib_path.exists():
    ok_checks.append("[OK] weekly_report_lib.py existuje")
else:
    errors.append("[ERROR] weekly_report_lib.py CHYBÍ - základní knihovna!")

# Check zakázané soubory
forbidden_patterns = [
    "run_w*_vs_w*.py",
    "analyze_w*.py",
    "generate_report_w*.py",
    "generate_pdf_w*.py",
    "custom_*.py"
]

found_forbidden = []
for pattern in forbidden_patterns:
    matches = list(Path(__file__).parent.glob(pattern))
    if matches:
        for match in matches:
            if match.name not in ['weekly_report_lib.py', 'cli_report.py', 'example_usage.py', 'validate_approach.py']:
                found_forbidden.append(match.name)

if found_forbidden:
    warnings.append(f"[WARNING] Nalezeny podezřelé soubory (možná legacy): {', '.join(found_forbidden)}")
    warnings.append("[WARNING] Tyto soubory by NEMĚLY být vytvářeny agenty!")
else:
    ok_checks.append("[OK] Žádné zakázané soubory nenalezeny")

# Check example_usage.py
example_path = Path(__file__).parent / "example_usage.py"
if example_path.exists():
    ok_checks.append("[OK] example_usage.py existuje (reference pro agenty)")
else:
    warnings.append("[WARNING] example_usage.py CHYBÍ - agent nemá příklady!")

# Print results
print("\n✅ ÚSPĚŠNÉ KONTROLY:")
for check in ok_checks:
    print(f"  {check}")

if warnings:
    print("\n⚠️  VAROVÁNÍ:")
    for warn in warnings:
        print(f"  {warn}")

if errors:
    print("\n❌ CHYBY:")
    for error in errors:
        print(f"  {error}")
    print("\n[RESULT] VALIDACE SELHALA - oprav chyby!")
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("DOPORUČENÝ WORKFLOW PRO AI AGENTY:")
print("=" * 80)
print("""
1. Uživatel chce weekly report?
   → python cli_report.py W52 W51 data_w52.csv data_w51.csv

2. Uživatel chce změnit filtr?
   → python cli_report.py ... --min-revenue 20000

3. Uživatel chce programatické použití?
   → from weekly_report_lib import quick_report
   → quick_report("w52.csv", "w51.csv", "W52", "W51")

❌ NIKDY NEVYTVÁŘEJ:
   - run_w*_vs_w*.py
   - analyze_*.py
   - generate_*.py
   - custom_*.py
""")
print("=" * 80)

if warnings:
    print("\n[RESULT] VALIDACE PROŠLA S VAROVÁNÍMI")
    sys.exit(0)
else:
    print("\n[RESULT] VALIDACE ÚSPĚŠNÁ - workflow je správný!")
    sys.exit(0)
