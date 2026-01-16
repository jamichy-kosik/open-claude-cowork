---
name: weekly-sales-report
description: Skill pro generování profesionálních týdenních prodejních reportů z CSV/Excel dat s WoW analýzou, kategoriálním breakdown (L1/L2/L3), identifikací exceeders/underperformers, data quality auditom a exportem do PDF dle McKinsey standardů
---

# Weekly Sales Report - Košík

**Skill pro generování týdenních prodejních reportů dle McKinsey standardů**

## ⚠️ DŮLEŽITÉ PRO AI AGENTY

**🚨 KRITICKÁ PRAVIDLA - NIKDY NEPORUŠUJ:**

1. **NIKDY nevytvářej tyto soubory:**
   - ❌ `run_w*_vs_w*.py`
   - ❌ `analyze_*.py`
   - ❌ `generate_*.py`  
   - ❌ `custom_*.py`
   - ❌ Jakýkoliv nový Python soubor pro analýzu

2. **VŽDY použij jeden z těchto přístupů:**
   - ✅ CLI: `python cli_report.py W52 W51 data.csv prev.csv`
   - ✅ Knihovna: `from weekly_report_lib import quick_report`
   - ✅ Parametry: Změň jen čísla, ne kód

3. **POKUD uživatel řekne "analyzuj W50 vs W49":**
   ```bash
   # SPRÁVNĚ:
   python cli_report.py W50 W49 sales_w50.csv sales_w49.csv
   
   # ŠPATNĚ (NEVYTVÁŘEJ!):
   # create run_w50_vs_w49.py ...
   ```

---

### 🎯 ROZHODOVACÍ STROM pro agenty

```
Uživatel chce weekly report?
│
├─ ANO → Už existují CSV soubory?
│        │
│        ├─ ANO → Použij cli_report.py NEBO quick_report()
│        │        python cli_report.py W52 W51 data_w52.csv data_w51.csv
│        │
│        └─ NE → Zeptej se na cestu k souborům
│                Pak použij cli_report.py
│
└─ Chce změnit parametr (filtr, top N)?
         │
         ├─ Jen jeden parametr → cli_report.py s --flag
         │                        python cli_report.py ... --min-revenue 20000
         │
         └─ Více parametrů → Použij WeeklySalesReport s kwargs
                             report = WeeklySalesReport(..., min_revenue_exceeders=20000, top_n_sku=15)
```

---

### ❌ ZAKÁZANÉ VZORY (real examples z chyb)

**Vzor 1: Vytváření wrapper scriptu**
```python
# ❌ NIKDY NEDĚLEJ TOTO:
# create run_w50_vs_w49.py:
from weekly_report_lib import WeeklySalesReport
report = WeeklySalesReport(
    week_current="W50",
    week_previous="W49",
    csv_current="...",
    csv_previous="..."
)
report.analyze()
```

**✅ MÍSTO TOHO:**
```bash
python cli_report.py W50 W49 sales_w50.csv sales_w49.csv
```

---

**Vzor 2: Vytváření custom generátoru**
```python
# ❌ NIKDY NEDĚLAJ TOTO:
# create generate_report_w50.py:
import pandas as pd
# ... 200 řádků kódu ...
```

**✅ MÍSTO TOHO:**
```python
# Použij existující funkci
from weekly_report_lib import quick_report
quick_report("w50.csv", "w49.csv", "W50", "W49")
```

---

**Vzor 3: Vytváření PDF generátoru**
```python
# ❌ NIKDY NEDĚLEJ TOTO:
# create generate_pdf_w50.py:
from reportlab import ...
# ... PDF kód ...
```

**✅ MÍSTO TOHO:**
```bash
# CLI má PDF automaticky
python cli_report.py W50 W49 data.csv prev.csv

# Nebo programaticky
report = WeeklySalesReport(...)
report.analyze()
report.generate_pdf()
```

---

**VŽDY používej tento skill když:**
- Uživatel chce analyzovat týdenní prodejní data
- Má CSV/Excel soubory s SKU-level daty
- Chce WoW (week-over-week) porovnání
- Potřebuje PDF report s kategoriální analýzou
- Žádá o identifikaci exceeders/underperformers
- Chce data quality audit prodejních dat

**NIKDY nepřepisuj již existující soubory:**
- ✅ VŽDY použij `weekly_report_lib.py` - parametrizovanou knihovnu
- ❌ NIKDY nevytvářej nové soubory `analyze_*.py` nebo `generate_*.py`
- ✅ Jen změň parametry při volání funkce

**PŘED vytvořením nových souborů:**
1. ✅ Použij `from weekly_report_lib import WeeklySalesReport`
2. ✅ Změň jen parametry (cesty, týdny, filtry)
3. ✅ Pokud chybí funkce, uprav `weekly_report_lib.py` pomocí `replace_string_in_file`

---

## 🚀 QUICK START pro AI agenty

### ⭐ NEJJEDNODUŠŠÍ - CLI Wrapper (DOPORUČENO)

```bash
# Základní použití (4 argumenty)
python cli_report.py W52 W51 sales_w52.csv sales_w51.csv

# S vlastním filtrem
python cli_report.py W52 W51 data.csv prev.csv --min-revenue 20000

# Změna top N
python cli_report.py W52 W51 data.csv prev.csv --top-n-sku 15 --top-n-l2 25

# Bez PDF (jen CSV analýza)
python cli_report.py W52 W51 data.csv prev.csv --no-pdf

# Tichý mód
python cli_report.py W52 W51 data.csv prev.csv --quiet
```

**Výhody CLI:**
- ✅ Žádné nové soubory
- ✅ Jeden příkaz = hotovo
- ✅ Automatické CSV + PDF
- ✅ Všechny parametry přes --flags

---

### Alternativa: Python knihovna

```python
from weekly_report_lib import quick_report

# Jen 4 parametry!
report = quick_report(
    csv_current="sales_sku_2025W52.csv",
    csv_previous="sales_sku_2025W51.csv",
    week_current="W52",
    week_previous="W51"
)

# Výstup: output_l1.csv, output_l2.csv, output_exceeders.csv, atd.
```

### Pokročilé použití (vlastní konfigurace)

```python
from weekly_report_lib import WeeklySalesReport, ReportConfig

# Vytvoř konfiguraci s vlastními parametry
config = ReportConfig(
    week_current="W52",
    week_previous="W51",
    csv_current="data/w52.csv",
    csv_previous="data/w51.csv",
    
    # Změň filtry
    min_revenue_exceeders=20_000,  # Default: 10_000
    top_n_sku=15,                   # Default: 10
    
    # Vlastní PDF název
    output_pdf="Custom_Report_W52.pdf"
)

# Vytvoř report
report = WeeklySalesReport(config=config)

# Spusť analýzu
report.analyze()

# Zobraz summary
report.print_summary()

# Ulož CSVs
report.save_results_csv()
```

### Změna jen jednoho parametru

```python
from weekly_report_lib import WeeklySalesReport

# Kwargs varianta (nejrychlejší pro jednu změnu)
report = WeeklySalesReport(
    week_current="W01",  # <-- ZMĚNA
    week_previous="W52",
    csv_current="sales_2026W01.csv",
    csv_previous="sales_2025W52.csv",
    min_revenue_exceeders=15_000  # <-- ZMĚNA filtru
)

report.analyze()
report.save_results_csv()
```

---

## 📋 DOSTUPNÉ PARAMETRY v ReportConfig

### Povinné parametry
- `week_current`: str - ID aktuálního týdne (např. "W52")
- `week_previous`: str - ID předchozího týdne (např. "W51")
- `csv_current`: str - cesta k CSV aktuálního týdne
- `csv_previous`: str - cesta k CSV předchozího týdne

### Volitelné parametry (s default hodnotami)
- `output_pdf`: str = "Weekly_Sales_Report.pdf"
- `output_dir`: Path = Path(".")
- `min_revenue_exceeders`: float = 10_000  # Kč
- `min_qty_exceeders`: int = 5
- `top_n_categories_l1`: int = 10
- `top_n_categories_l2`: int = 20
- `top_n_sku`: int = 10

### PDF styling (pokročilé)
- `pdf_font`: str = "Arial"
- `pdf_colors`: Dict s barvami pro různé sekce

---

## 🔧 CO DĚLAT KDYŽ...

### Uživatel chce změnit filtr (např. min_revenue)
❌ **NESPRÁVNĚ:**
```python
# Vytvoř nový soubor analyze_weekly_sales_v2.py...
```

✅ **SPRÁVNĚ:**
```python
from weekly_report_lib import WeeklySalesReport

report = WeeklySalesReport(
    week_current="W52",
    week_previous="W51", 
    csv_current="data.csv",
    csv_previous="data_prev.csv",
    min_revenue_exceeders=20_000  # <-- JEN ZMĚNA PARAMETRU
)
report.analyze()
```

### Uživatel chce jinou kategorii (L3 místo L2)
✅ **SPRÁVNĚ:**
```python
report = WeeklySalesReport(...)
report.analyze()

# Zavolej specifickou funkci
l3_data = report._analyze_category('L3', top_n=15)
print(l3_data)
```

### Uživatel chce vlastní logic (např. top 20 místo 10)
✅ **SPRÁVNĚ:**
```python
report = WeeklySalesReport(
    ...,
    top_n_categories_l2=20  # <-- PARAMETR
)
```

### Chybí funkce v knihovně
✅ **SPRÁVNĚ:**
1. Použij `replace_string_in_file` na `weekly_report_lib.py`
2. Přidej novou metodu do třídy `WeeklySalesReport`
3. Zachovej parametrizaci

❌ **NESPRÁVNĚ:**
- Vytvoř nový soubor `custom_analysis.py`

---

## Účel
Automatizovaná analýza týdenních prodejních dat z CSV/Excel souborů a tvorba strukturovaného PDF reportu s důrazem na:
- Data quality check
- Executive summary (top kategorie, drivery, akce)
- Kategoriální breakdown (L1/L2/L3)
- Services split (sklady HP/regiony)
- Top listy (exceeders/underperformers WoW)
- Problematické SKU (GM1<0, nízké marže, extrémní ceny)
- Data issues (max 5 priorit)

## Kdy použít
- Týdenní reporting prodejů
- Analýza week-over-week změn
- Identifikace obchodních příležitostí a rizik
- Data quality audit

## Prerekvizity
```bash
pip install pandas numpy reportlab matplotlib
```

## Požadovaná struktura CSV dat

**Povinné sloupce:**
- Services, Product Id Sap, Product Name Web
- product category L1/L2/L3/L4
- Buy Price, Standard Price, Revenue, GM1 wo VAT
- Quantity Delivered

**DŮLEŽITÉ**: Čísla s čárkou jako tisícový oddělovač (např. `1,735.00`) jsou automaticky detekovány.

## Struktura reportu

### DATA CHECK
- Týden, počet řádků, SKU, SKU sold
- Control totals (Revenue, GM1, Qty)
- KPI sanity check (avg price)
- Missing categories (% + dopad)
- Duplicity (Week+SKU+Services)
- GM1 < 0 (počet SKU + dopad, top 5)
- Extrémy (GM1=Revenue, GM1%>80%)

### EXECUTIVE SUMMARY (8-12 vět)
- Prodej Košíku za týden + WoW delta
- Top 3 L1 kategorie + share
- Top 5 L2 kategorie + share
- 3-5 driverů růstu (SKU s nejvyšším WoW %)
- 3-5 doporučených akcí

### KATEGORIE
- **L1**: Revenue, share, GM1, GM1%, #SKU
- **L2**: Top 20 + řádek "Ostatní"
- **L3**: Top 20 (pokud existuje)
- Řazení: vždy podle Revenue desc

### SERVICES BREAKDOWN
- HP vs Regions
- Revenue, share, GM1, GM1%, #SKU, Qty

### TOP LISTY
- **TOP 10 Exceeders** (WoW % růst)
- **TOP 10 Underperformers** (WoW % pokles)
- Filtr: Revenue >= 10k, Qty >= 5

### TOP SKU REVENUE
- TOP 10 SKU dle absolutní Revenue

### PROBLEMATICKÉ SKU
1. TOP 5 s GM1 < 0
2. TOP 5 s GM1% < 10% (ale >= 0)
3. TOP 5 s extrémní odchylkou ceny od Buy Price

### DATA ISSUES (max 5)
- Problém + dopad + fix
- Příklady: záporné GM1, missing categories, volatilita, nízká rotace

## Mapování sloupců

V `ReportConfig` můžeš přepsat mapování sloupců pomocí `column_mapping`:

```python
config = ReportConfig(
    ...,
    column_mapping={
        'Product Id Sap': 'SKU',
        'Product Name Web': 'Product_Name',
        'product category L1': 'L1',
        'product category L2': 'L2',
        'Buy Price': 'Buy_Price',
        'Standard Price': 'Standard_Price',
        'Revenue': 'Revenue',
        'GM1 wo VAT': 'GM1',
        'Quantity Delivered': 'Qty',
        'Services': 'Services'
    }
)
```

**Pro nestandardní sloupce:**
```python
config = ReportConfig(
    ...,
    column_mapping={
        'SKU_ID': 'SKU',
        'Product_Title': 'Product_Name',
        'Category_Level_1': 'L1',
        # ... atd
    }
)
```

Chybějící sloupce jsou hlášeny v Data check.

## Parametry (konzistence)

### Top listy filtr
```python
Revenue >= 10_000  # Kč
Qty >= 5
```

### Kategorie
- Řazení: vždy Revenue desc
- L2/L3: max 20 řádků + "Ostatní"

### SKU sold
```python
Revenue > 0  # fallback: Qty > 0
```

### WoW comparison
- Week ber z názvu souboru nebo sloupce Week/Date
- Pokud chybí W-1, explicitně uvádí "WoW nelze"

## Formátování (CZ)

### Čísla
```python
format_cz_number(12345.67, 2)  # → "12 345,67"
format_cz_percent(14.2, 1)     # → "14,2 %"
```

### Text
- Nikdy "trh", vždy "Prodej Košíku"
- Podíly: "share X,X %"
- SKU anomálie: vždy SKU ID + název + číslo dopadu

### PDF a matplotlib - ČESKÉ ZNAKY

⚠️ **KRITICKÉ: VŽDY nastav Arial font na začátku skriptu!**

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# POVINNÉ pro české znaky (č, ř, š, ž, ý, á, atd.)
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.formatter.use_locale'] = False
```

**Proč Arial?**
- Windows má Arial vždy dostupný v `C:\Windows\Fonts\arial.ttf`
- Podporuje plnou českou diakritiku (ěščřžýáíé)
- DejaVu Sans jako fallback pro Linux

**Časté chyby:**
❌ Zapomenuté nastavení → výsledek: "Po■et ■ádků" místo "Počet řádků"
❌ Použití default fontu → ReportLab/matplotlib použije Helvetica (bez diakritiky)
❌ Encoding UTF-8 v CSV ale ne v matplotlib → mixed problémy

**Správný workflow:**
```python
# 1. Nastav font PŘED jakýmkoliv plt.figure()
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

# 2. Load data s UTF-8
df = pd.read_csv('data.csv', encoding='utf-8-sig')

# 3. Vytvoř grafy
fig, ax = plt.subplots()
ax.set_title('Počet řádků')  # ✅ Funguje
```

**ReportLab PDF:**
- Velikost: A4 (8.27 x 11.69 inch)
- Font: Registruj Arial přes TTFont (viz pdf-management skill)
- Tabulky: max 20 řádků, fontsize=7-8pt
- Barvy: Material Design paleta (viz pdf-management SKILL.md)

## 🐛 TROUBLESHOOTING

### Problém 1: Agent vytváří nové soubory

**Symptom:**
```
Agent vytvořil: run_w50_vs_w49.py
Agent vytvořil: generate_report_w50.py
Agent vytvořil: generate_pdf_w50.py
```

**Důvod:** Agent ignoroval instrukce v SKILL.md

**Fix:**
```bash
# PŘED jakoukoliv prací spusť validaci
python validate_approach.py

# Použij CLI místo vytváření souborů
python cli_report.py W50 W49 sales_w50.csv sales_w49.csv
```

---

### Problém 2: UnicodeEncodeError v Windows konzoli

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

**Důvod:** Windows console nepodporuje emoji (✅❌⚠️)

**Fix:** Už opraveno v `weekly_report_lib.py` - používá [OK], [ERROR], [WARNING]

---

### Problém 3: CSV encoding error

**Symptom:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte ...
```

**Důvod:** CSV je UTF-16 s TAB delimiterem

**Fix:** Už opraveno v `_load_csv()` - automatická detekce UTF-16/UTF-8

---

### Problém 4: Agent chce vytvořit "custom_analysis.py"

**Prevence:**
1. Zkontroluj `python validate_approach.py`
2. Přečti SKILL.md sekci "ZAKÁZANÉ VZORY"
3. Použij místo toho:
   ```python
   # Vlastní analýza - SPRÁVNĚ
   from weekly_report_lib import WeeklySalesReport
   
   report = WeeklySalesReport(...)
   report.load_data()
   
   # Custom logic
   custom_data = report.df_current[report.df_current['L3'] == 'Specifická kategorie']
   # ... vlastní zpracování ...
   ```

---

## ✅ SELF-CHECK pro agenty (před začátkem práce)

Spusť tento checklist PŘED vytvořením jakéhokoliv souboru:

```bash
# 1. Validace workflow
python validate_approach.py

# 2. Existuje cli_report.py?
ls cli_report.py  # ANO → použij ho!

# 3. Existuje weekly_report_lib.py?
ls weekly_report_lib.py  # ANO → použij ho!

# 4. Přečti příklady
python example_usage.py 1  # Spusť příklad
```

**Pokud validace OK:**
- ✅ Použij `python cli_report.py ...`
- ✅ NEBO `from weekly_report_lib import quick_report`
- ❌ NEVYTVÁŘEJ nové soubory!

**Pokud validace selže:**
- 🔧 Oprav chybějící soubory
- 📖 Přečti SKILL.md znovu
- 🚫 NEPOKRAČUJ bez opraveného workflow

---

## Struktura souborů

**✅ POUŽIJ TYTO (parametrizovaná knihovna):**
```
.
├── weekly_report_lib.py       # HLAVNÍ knihovna (VŽDY použij!)
├── cli_report.py              # CLI wrapper
├── example_usage.py           # Příklady použití
└── validate_approach.py       # Self-check validace
```

## Maintenance

### Přidání nového sloupce
1. Uprav `col_map` v `load_and_clean_data()`
2. Přidej do `numeric_cols` pokud je číselný
3. Uprav `data_check()` pro validaci

### Nová sekce v reportu
1. Přidej novou metodu do `WeeklySalesReport` třídy v `weekly_report_lib.py`
2. Použij `replace_string_in_file` pro úpravu knihovny
3. ❌ **NIKDY nevytvářej** `generate_*.py` soubory!

## Známá omezení

1. **Encoding**: Windows console může mít problémy s UTF-8 → skript nastavuje `sys.stdout` na UTF-8
2. **Pie charts**: Pokud reportlab nemá nástroj, fallback na "Top 5 L1 + Ostatní" jako text
3. **Long product names**: V PDF tabulkách zkráceno na 40-50 znaků
4. **Services**: Pokud sloupec chybí, skip Services breakdown

## Style guidelines

- **Věcné, bez omáčky**: Executive summary max 8-12 vět
- **Nikdy nepiš "chyba nástroje"**: Vždy dej fallback
- **Konzistence**: všechny sekce používají stejný formát čísel/procent
- **Akce-orientovanost**: Data issues vždy s fix návrhem

---

**Vytvořeno**: 2026-01-02  
**Verze**: 2.0 (parametrizovaná knihovna)  
**Autor**: Claude (McKinsey-style reporting specialist)

---

## 📚 Výstupní soubory

- `output_l1.csv`, `output_l2.csv` - Kategorie L1/L2
- `output_exceeders.csv`, `output_underperformers.csv` - WoW top/bottom
- `output_services.csv` - HP/Regions breakdown
- `output_top_sku.csv` - Top revenue SKU
- `output_problems.csv` - Problematické SKU
- `output_data_check.csv` - Data quality
- `Weekly_Sales_Report_W*.pdf` - Finální PDF

---

**Verze**: 2.1 | **Vytvořeno**: 2026-01-05 | **Autor**: Claude
