# Weekly Sales Report Skill - Košík

**Automatizovaný týdenní prodejní reporting dle McKinsey standardů**

## 🚀 Quick Start (CLI - NEJJEDNODUŠŠÍ pro AI agenty)

### ✅ DOPORUČENO: CLI Wrapper

```bash
# Základní použití
python cli_report.py W52 W51 sales_w52.csv sales_w51.csv

# Výstup:
# - output_l1.csv, output_l2.csv, output_exceeders.csv, ...
# - Weekly_Sales_Report_W52_vs_W51_2025.pdf

# S vlastními parametry
python cli_report.py W52 W51 data.csv prev.csv --min-revenue 20000 --top-n-sku 15

# Jen CSV (bez PDF)
python cli_report.py W52 W51 data.csv prev.csv --no-pdf

# Všechny možnosti
python cli_report.py --help
```

**Proč CLI?**
- ✅ 1 příkaz = hotovo (žádné nové soubory)
- ✅ Automatická detekce encoding (UTF-16, UTF-8)
- ✅ Všechny parametry přes --flags
- ✅ CSV + PDF automaticky

---

## 🐍 Alternativa: Python knihovna

### Quick funkce (4 parametry)

```python
from weekly_report_lib import quick_report

# Jen 4 parametry!
report = quick_report(
    csv_current="sales_sku_2025W52.csv",
    csv_previous="sales_sku_2025W51.csv",
    week_current="W52",
    week_previous="W51"
)
```

**Výsledek:** `output_l1.csv`, `output_l2.csv`, `output_exceeders.csv`, atd.

### Pokročilé použití s vlastní konfigurací

```python
from weekly_report_lib import WeeklySalesReport, ReportConfig

config = ReportConfig(
    week_current="W52",
    week_previous="W51",
    csv_current="w52.csv",
    csv_previous="w51.csv",
    min_revenue_exceeders=20_000,  # změna filtru
    top_n_sku=15                    # změna top N
)

report = WeeklySalesReport(config=config)
report.analyze()
report.print_summary()
report.save_results_csv()
```

### ⚠️ Legacy způsob (zastaralý)

```bash
# STARÝ způsob - stále funguje, ale není doporučený
python run_weekly_report.py --w1 sales_sku_2025W51.csv --w2 sales_sku_2025W52.csv
```

## Co dostaneš

### Console Output
Kompletní textový report s:
- **DATA CHECK**: Kontrolní součty, missing data, duplicity, GM1<0, extrémy
- **EXECUTIVE SUMMARY**: Top 3 L1, Top 5 L2, top drivery, akce (8-12 vět)
- **KATEGORIE**: L1/L2/L3 breakdown (Revenue, share, GM1, GM1%, #SKU)
- **SERVICES**: HP vs Regions split
- **TOP LISTY**: Top 10 exceeders/underperformers WoW
- **TOP SKU**: Top 10 dle Revenue
- **PROBLEMATICKÉ SKU**: GM1<0, nízké marže, extrémní ceny
- **DATA ISSUES**: Max 5 priorit (problém+dopad+fix)

### PDF Report
Profesionálně naformátovaný A4 dokument s:
- Strukturované sekce
- Tabulky s auto-šířkou sloupců
- České formátování čísel (tisíce mezerou, desetiny čárkou)
- DejaVu Sans font (podpora češtiny)

## Struktura dat (požadavky)

CSV/Excel soubory musí obsahovat tyto sloupce:

**Povinné:**
- `Services` (HP/Regions/jiné)
- `Product Id Sap` (SKU identifikátor)
- `Product Name Web` (název produktu)
- `product category L1` (hlavní kategorie)
- `product category L2` (subkategorie)
- `Revenue` (tržby)
- `GM1 wo VAT` (hrubá marže bez DPH)
- `Quantity Delivered` (dodané množství)

**Doporučené:**
- `product category L3/L4`
- `Brand Name`
- `Supplier Name`
- `Buy Price` (nákupní cena)
- `Standard Price` (standardní cena)
- `VAT` (DPH sazba)

**DŮLEŽITÉ**: Čísla mohou mít čárku jako tisícový oddělovač (např. `1,735.00` znamená 1 735). Skript automaticky detekuje a normalizuje.

## Parametry analýzy

### Top listy filtr
```
Revenue >= 10 000 Kč
Qty >= 5 ks
```

### SKU sold definice
```
Revenue > 0 (fallback: Qty > 0)
```

### WoW comparison
- Automatická detekce week ID z názvu souboru
- Pokud chybí W-1, explicitně uvede "WoW nelze"

### Kategorie
- Řazení: vždy podle Revenue desc
- L2/L3: max 20 řádků + řádek "Ostatní"

## Příklady výstupů

### Executive Summary
```
Prodej Košíku za W52: 75 748 200 Kč, WoW -14,2 % (-12 494 139 Kč).

Top 3 kategorie L1:
  - Nápoje: 15 954 305 Kč, share 21,1 %
  - Mléčné a chlazené: 13 911 224 Kč, share 18,4 %
  - Trvanlivé: 11 684 140 Kč, share 15,4 %

Top 5 driverů růstu (WoW % + absolutní delta):
  - SKU 1009854 Segafredo Espresso 1kg: +2866,3 %, +188 342 Kč
  - SKU 1144321 Varta AA 12ks: +1381,1 %, +17 001 Kč
  ...
```

### Data Issues
```
1. PROBLÉM: 239 SKU se záporným GM1
   DOPAD: Ztráta 1 127 727 Kč revenue s negativní marží
   FIX: Revize nákupních cen u dodavatelů, případně delistování

2. PROBLÉM: Missing L2 kategorie u 0,7 % řádků
   DOPAD: Ztráta 616 013 Kč v reporting granularity
   FIX: Doplnit kategorizaci L2 v master data, automatizace z L1
```

## Známá omezení

1. **UTF-16 encoding**: Pokud soubor používá UTF-16 s TAB separátory (typické pro Excel export), automaticky detekováno
2. **Long product names**: V PDF zkráceno na 40-50 znaků
3. **Console encoding**: Windows může mít problémy s UTF-8 → skript nastavuje `sys.stdout` na UTF-8
4. **Pie charts**: Pokud reportlab nemá nástroj, fallback na textový přehled

## Customizace

### Změna top lists filtru
Uprav v `analyze_weekly_sales.py`:
```python
# Aktuálně:
filtered = merged[(merged['Revenue'] >= 10000) & (merged['Qty'] >= 5)]

# Změň na:
filtered = merged[(merged['Revenue'] >= 5000) & (merged['Qty'] >= 3)]
```

### Přidání nové kategorie L5
1. Přidej do `col_map`:
   ```python
   'product category L5': 'L5'
   ```
2. Přidej sekci do `category_analysis()`:
   ```python
   if 'L5' in df.columns and df['L5'].notna().any():
       # ... stejná logika jako L3
   ```

### Vlastní formát čísel
Uprav funkce `format_cz_number()` a `format_cz_percent()`.

## Troubleshooting

### "Nepodařilo se načíst CSV"
- Zkontroluj encoding: UTF-16 nebo UTF-8?
- Zkontroluj delimiter: TAB nebo čárka?
- Ujisti se, že první řádek obsahuje hlavičky

### "GM1 < 0 pro mnoho SKU"
- Normální pro loss leaders nebo promo kampaně
- Pokud >10% SKU, zkontroluj Buy Price v master data

### "WoW volatilita >200%"
- Běžné pro nové SKU nebo po stockoutu v W-1
- Filtr v `data_issues()` lze upravit

### PDF nefunguje
- Chybí font DejaVu Sans? Automatický fallback na Helvetica
- Chybí reportlab? `pip install reportlab`

## Dependencies

```bash
pip install pandas numpy reportlab
```

Optional:
```bash
pip install openpyxl  # Pro přímý import z Excel
```

## Struktura souborů

```
weekly-sales-report/
├── SKILL.md                      # Detailní dokumentace
├── README.md                     # Tento soubor
├── run_weekly_report.py          # Hlavní runner script
├── analyze_weekly_sales.py       # Core analýza
└── examples/
    ├── sales_sku_2025W51.csv     # (example data)
    └── sales_sku_2025W52.csv     # (example data)
```

## Best Practices

1. **Pojmenuj soubory konzistentně**: `sales_sku_YYYYWXX.csv` (např. `sales_sku_2025W52.csv`)
2. **Kontroluj data před uploadem**: Ověř, že všechny povinné sloupce existují
3. **Archive old reports**: Přesuň staré PDF do `archive/` poygenerování nového
4. **Review data issues**: Prioritizuj top 3 issues z reportu pro následující týden
5. **Monitor WoW trends**: Pokud volatilita >100% častá, zváž seasonality adjustment

## Support

Pro další info viz `SKILL.md` nebo kontaktuj autora.

---

**Vytvořeno**: 2026-01-02
**Verze**: 1.0
**Licence**: Internal use only
