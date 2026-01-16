#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Wrapper pro Weekly Sales Report

POUŽITÍ PRO AI AGENTY:
======================
MÍSTO vytváření nových souborů VŽDY použij tento wrapper!

Příklady:
    # Základní report
    python cli_report.py W52 W51 sales_w52.csv sales_w51.csv
    
    # S vlastními parametry
    python cli_report.py W52 W51 sales_w52.csv sales_w51.csv --min-revenue 20000 --top-n 15
    
    # Pouze analýza, bez PDF
    python cli_report.py W52 W51 data.csv data_prev.csv --no-pdf
"""

import argparse
import sys
from pathlib import Path

# Add parent to path if needed
sys.path.insert(0, str(Path(__file__).parent))

from weekly_report_lib import WeeklySalesReport, ReportConfig
from pdf_generator_csv import create_beautiful_pdf


def main():
    parser = argparse.ArgumentParser(
        description='Weekly Sales Report Generator - Parametrizovaný wrapper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Příklady použití:
  
  Základní:
    %(prog)s W52 W51 sales_w52.csv sales_w51.csv
  
  S vlastním filtrem:
    %(prog)s W52 W51 data.csv prev.csv --min-revenue 20000
  
  Změna top N:
    %(prog)s W52 W51 data.csv prev.csv --top-n-sku 15 --top-n-l2 25
  
  Bez PDF (jen CSV):
    %(prog)s W52 W51 data.csv prev.csv --no-pdf
  
  Vlastní output dir:
    %(prog)s W52 W51 data.csv prev.csv --output-dir ./reports
        """
    )
    
    # Povinné argumenty
    parser.add_argument('week_current', help='Aktuální týden (např. W52)')
    parser.add_argument('week_previous', help='Předchozí týden (např. W51)')
    parser.add_argument('csv_current', help='Cesta k CSV aktuálního týdne')
    parser.add_argument('csv_previous', help='Cesta k CSV předchozího týdne')
    
    # Volitelné parametry
    parser.add_argument('--output-pdf', default=None, help='Název PDF (default: Weekly_Sales_Report.pdf)')
    parser.add_argument('--output-dir', default='.', help='Adresář pro výstupy (default: aktuální)')
    parser.add_argument('--min-revenue', type=float, default=10000, help='Min revenue pro exceeders (default: 10000)')
    parser.add_argument('--min-qty', type=int, default=5, help='Min qty pro exceeders (default: 5)')
    parser.add_argument('--top-n-l1', type=int, default=15, help='Top N L1 kategorií (default: 15)')
    parser.add_argument('--top-n-l2', type=int, default=20, help='Top N L2 kategorií (default: 20)')
    parser.add_argument('--top-n-sku', type=int, default=10, help='Top N SKU (default: 10)')
    parser.add_argument('--no-pdf', action='store_true', help='Přeskočit PDF generování')
    parser.add_argument('--no-summary', action='store_true', help='Přeskočit konzolový summary')
    parser.add_argument('--quiet', action='store_true', help='Tichý mód (min output)')
    parser.add_argument('--console-output', default=None, help='Uložit konzolový output do souboru pro PDF')
    
    args = parser.parse_args()
    
    # Vytvoř config
    output_pdf = args.output_pdf or f"Weekly_Sales_Report_{args.week_current}_vs_{args.week_previous}_2025.pdf"
    output_pdf_path = Path(args.output_dir) / output_pdf
    
    config = ReportConfig(
        week_current=args.week_current,
        week_previous=args.week_previous,
        csv_current=args.csv_current,
        csv_previous=args.csv_previous,
        output_pdf=str(output_pdf_path),
        output_dir=Path(args.output_dir),
        min_revenue_exceeders=args.min_revenue,
        min_qty_exceeders=args.min_qty,
        top_n_categories_l1=args.top_n_l1,
        top_n_categories_l2=args.top_n_l2,
        top_n_sku=args.top_n_sku
    )
    
    if not args.quiet:
        print(f"[CLI] Weekly Sales Report: {args.week_current} vs {args.week_previous}")
        print(f"[CLI] Current: {args.csv_current}")
        print(f"[CLI] Previous: {args.csv_previous}")
        print("-" * 80)
    
    # Vytvoř report
    report = WeeklySalesReport(config=config)
    
    # Analýza
    try:
        report.analyze()
    except Exception as e:
        print(f"[ERROR] Analýza selhala: {e}", file=sys.stderr)
        return 1
    
    # Summary - zachytíme do souboru pro PDF generování
    console_output_file = args.console_output
    if not args.no_pdf and not console_output_file:
        console_output_file = Path(args.output_dir) / f"console_output_{args.week_current}.txt"
    
    # Uložíme summary do souboru pokud generujeme PDF
    if console_output_file:
        original_stdout = sys.stdout
        try:
            with open(console_output_file, 'w', encoding='utf-8') as f:
                sys.stdout = f
                if not args.no_summary:
                    report.print_summary()
                    # Výpis detailních tabulek pro PDF
                    print_detailed_tables(report)
        finally:
            sys.stdout = original_stdout
        
        if not args.quiet:
            print(f"[INFO] Console output saved to: {console_output_file}")
    
    # Zobraz summary na konzoli (pokud není quiet)
    if not args.no_summary and not args.quiet:
        report.print_summary()
    
    # Ulož CSV
    try:
        report.save_results_csv()
    except Exception as e:
        print(f"[ERROR] CSV save selhal: {e}", file=sys.stderr)
        return 1
    
    # PDF - použij pokročilý generátor z weekly_report_lib
    if not args.no_pdf:
        try:
            if not console_output_file or not Path(console_output_file).exists():
                print(f"[WARNING] Console output nenalezen, PDF bude obsahovat pouze základní data")
                # Fallback na starý způsob
                report.generate_pdf()
            else:
                # Použij pokročilý PDF generátor z pdf_generator_improved
                if not args.quiet:
                    print(f"[PDF] Generating beautiful PDF from console output...")
                create_beautiful_pdf(console_output_file, output_pdf_path)
                if not args.quiet:
                    print(f"[OK] Beautiful PDF created: {output_pdf_path}")
        except Exception as e:
            print(f"[WARNING] PDF generation selhalo: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            print("[WARNING] CSV výstupy byly vytvořeny, PDF přeskočeno")
    
    if not args.quiet:
        print("\n" + "=" * 80)
        print("[OK] Report dokončen!")
        print(f"[FILES] CSV výstupy v: {args.output_dir}/")
        if not args.no_pdf:
            print(f"[FILES] PDF: {output_pdf_path}")
        if console_output_file and Path(console_output_file).exists():
            print(f"[FILES] Console log: {console_output_file}")
        print("=" * 80)
    
    return 0


def print_detailed_tables(report: WeeklySalesReport):
    """
    Vypíše detailní tabulky pro pokročilé PDF generování.
    Tento output je pak zpracován create_advanced_pdf_from_console() z weekly_report_lib
    """
    results = report.results
    
    if not results:
        return
    
    print("\n" + "="*80)
    print("KATEGORIE (L1/L2/L3) - W52")
    print("="*80)
    
    # L1 Categories
    if 'l1' in results and not results['l1'].empty:
        print("\nL1 kategorie: Top {}".format(len(results['l1'])))
        print("-" * 80)
        df = results['l1'].head(20)
        print(df.to_string(index=False))
    
    # L2 Categories
    if 'l2' in results and not results['l2'].empty:
        print("\nL2 kategorie: Top {}".format(len(results['l2'])))
        print("-" * 80)
        df = results['l2'].head(20)
        print(df.to_string(index=False))
    
    # L3 Categories
    if 'l3' in results and not results['l3'].empty:
        print("\nL3 kategorie: Top {}".format(len(results['l3'])))
        print("-" * 80)
        df = results['l3'].head(20)
        print(df.to_string(index=False))
    
    # Services
    if 'services' in results and not results['services'].empty:
        print("\n" + "="*80)
        print("SERVICES BREAKDOWN")
        print("="*80)
        print(results['services'].to_string(index=False))
    
    # Top lists WoW
    print("\n" + "="*80)
    print("TOP LISTY WoW")
    print("="*80)
    
    if 'exceeders' in results and not results['exceeders'].empty:
        print("\nTOP 10 Exceeders (WoW Revenue vzrostl > 10%)")
        print("-" * 80)
        print(results['exceeders'].head(10).to_string(index=False))
    
    if 'underperformers' in results and not results['underperformers'].empty:
        print("\nTOP 10 Underperformers (WoW Revenue poklesl > 10%)")
        print("-" * 80)
        print(results['underperformers'].head(10).to_string(index=False))
    
    # Top SKU
    if 'top_sku' in results and not results['top_sku'].empty:
        print("\n" + "="*80)
        print("TOP 10 SKU dle Revenue")
        print("="*80)
        print(results['top_sku'].head(10).to_string(index=False))
    
    # Problematic SKU
    if 'problematic' in results and not results['problematic'].empty:
        print("\n" + "="*80)
        print("TOP Problematické SKU")
        print("="*80)
        
        df_prob = results['problematic']
        
        # High Rev + Low Margin
        print("\nTOP 5 SKU: High Revenue + Low Margin (GM1 < 5%)")
        print("-" * 80)
        mask = df_prob['GM1_pct'] < 5
        print(df_prob[mask].head(5).to_string(index=False))
        
        # High Rev + Negative GM
        print("\nTOP 5 SKU: High Revenue + Negative GM1")
        print("-" * 80)
        mask = df_prob['GM1'] < 0
        print(df_prob[mask].head(5).to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
