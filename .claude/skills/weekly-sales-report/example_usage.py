#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Jak správně použít weekly_report_lib.py

Pro AI agenty: KOPÍRUJ TENTO PATTERN, nevytvářej nové soubory!
"""

from weekly_report_lib import WeeklySalesReport, ReportConfig, quick_report

# ============================================================================
# PŘÍKLAD 1: Nejjednodušší použití
# ============================================================================
def example_quick():
    """Nejrychlejší způsob - 4 parametry"""
    print("="*80)
    print("EXAMPLE 1: Quick Report")
    print("="*80)
    
    report = quick_report(
        csv_current="sales_sku_2025W52.csv",
        csv_previous="sales_sku_2025W51.csv",
        week_current="W52",
        week_previous="W51"
    )
    
    print("✅ Done! Check output_*.csv files\n")
    return report


# ============================================================================
# PŘÍKLAD 2: S vlastní konfigurací
# ============================================================================
def example_custom_config():
    """Pokročilé použití s custom parametry"""
    print("="*80)
    print("EXAMPLE 2: Custom Configuration")
    print("="*80)
    
    # Vytvoř config s vlastními parametry
    config = ReportConfig(
        week_current="W52",
        week_previous="W51",
        csv_current="sales_sku_2025W52.csv",
        csv_previous="sales_sku_2025W51.csv",
        
        # ZMĚNA: Vyšší threshold pro exceeders
        min_revenue_exceeders=20_000,  # místo default 10_000
        min_qty_exceeders=10,          # místo default 5
        
        # ZMĚNA: Více top SKU
        top_n_sku=15,  # místo default 10
        
        # ZMĚNA: Vlastní název PDF
        output_pdf="Custom_Weekly_Report_W52.pdf"
    )
    
    # Vytvoř report s config
    report = WeeklySalesReport(config=config)
    
    # Spusť analýzu
    report.analyze()
    
    # Zobraz summary
    report.print_summary()
    
    # Ulož výsledky
    report.save_results_csv()
    
    print("✅ Custom report done!\n")
    return report


# ============================================================================
# PŘÍKLAD 3: Jen změna jednoho parametru (kwargs)
# ============================================================================
def example_kwargs():
    """Nejrychlejší pro změnu 1-2 parametrů"""
    print("="*80)
    print("EXAMPLE 3: Kwargs (změna jen revenue filtru)")
    print("="*80)
    
    report = WeeklySalesReport(
        week_current="W52",
        week_previous="W51",
        csv_current="sales_sku_2025W52.csv",
        csv_previous="sales_sku_2025W51.csv",
        min_revenue_exceeders=15_000  # <-- JEDINÁ ZMĚNA!
    )
    
    report.analyze()
    report.save_results_csv()
    
    print("✅ Kwargs report done!\n")
    return report


# ============================================================================
# PŘÍKLAD 4: Vlastní analýza (použití interních metod)
# ============================================================================
def example_custom_analysis():
    """Pokročilé: volání specifických metod"""
    print("="*80)
    print("EXAMPLE 4: Custom Analysis (jen L3 kategorie)")
    print("="*80)
    
    report = WeeklySalesReport(
        week_current="W52",
        week_previous="W51",
        csv_current="sales_sku_2025W52.csv",
        csv_previous="sales_sku_2025W51.csv"
    )
    
    # Load data
    report.load_data()
    
    # Spusť jen specifickou analýzu
    l3_data = report._analyze_category('L3', top_n=15)
    
    print("\nTop 15 L3 categories:")
    print(l3_data[['L3', 'Revenue', 'share', 'WoW_pct']].head(15))
    
    # Ulož jen L3
    l3_data.to_csv('output_l3_custom.csv', index=False, encoding='utf-8-sig')
    
    print("\n✅ Custom L3 analysis done!\n")
    return report


# ============================================================================
# PŘÍKLAD 5: Batch processing (více týdnů)
# ============================================================================
def example_batch():
    """Zpracování více týdnů najednou"""
    print("="*80)
    print("EXAMPLE 5: Batch Processing (W50, W51, W52)")
    print("="*80)
    
    weeks = [
        ("W50", "W49", "sales_sku_2025W50.csv", "sales_sku_2025W49.csv"),
        ("W51", "W50", "sales_sku_2025W51.csv", "sales_sku_2025W50.csv"),
        ("W52", "W51", "sales_sku_2025W52.csv", "sales_sku_2025W51.csv"),
    ]
    
    reports = []
    for week_curr, week_prev, csv_curr, csv_prev in weeks:
        print(f"\n📊 Processing {week_curr} vs {week_prev}...")
        
        try:
            report = quick_report(
                csv_current=csv_curr,
                csv_previous=csv_prev,
                week_current=week_curr,
                week_previous=week_prev,
                output_pdf=f"Report_{week_curr}.pdf"
            )
            reports.append(report)
            print(f"   ✅ {week_curr} done")
        except FileNotFoundError as e:
            print(f"   ⚠️ {week_curr} skipped: {e}")
    
    print(f"\n✅ Batch done! Processed {len(reports)} weeks\n")
    return reports


# ============================================================================
# MAIN: Spusť příklady
# ============================================================================
if __name__ == "__main__":
    import sys
    
    examples = {
        '1': ('Quick report', example_quick),
        '2': ('Custom config', example_custom_config),
        '3': ('Kwargs (single param change)', example_kwargs),
        '4': ('Custom analysis (L3 only)', example_custom_analysis),
        '5': ('Batch processing', example_batch)
    }
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        if choice in examples:
            name, func = examples[choice]
            print(f"\n🚀 Running example: {name}\n")
            func()
        else:
            print(f"Unknown example: {choice}")
            print(f"Available: {', '.join(examples.keys())}")
    else:
        print("Usage: python example_usage.py <example_number>")
        print("\nAvailable examples:")
        for key, (name, _) in examples.items():
            print(f"  {key}: {name}")
        print("\nExample: python example_usage.py 1")
