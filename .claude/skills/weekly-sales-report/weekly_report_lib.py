#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Sales Report Library - Košík
Parametrizovaná knihovna funkcí pro generování týdenních reportů.

POUŽITÍ PRO AI AGENTY:
====================
Místo vytváření nových souborů VŽDY použij tento modul s parametry!

Příklad:
    from weekly_report_lib import WeeklySalesReport
    
    report = WeeklySalesReport(
        week_current="W52",
        week_previous="W51",
        csv_current="sales_sku_2025W52.csv",
        csv_previous="sales_sku_2025W51.csv"
    )
    
    # Analýza
    report.analyze()
    
    # PDF export
    report.generate_pdf("Weekly_Report_W52.pdf")
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ReportLab imports pro pokročilé PDF generování
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# POVINNÉ nastavení fontů pro české znaky
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.formatter.use_locale'] = False


@dataclass
class ReportConfig:
    """Konfigurace reportu - všechny parametry na jednom místě"""
    
    # Základní parametry
    week_current: str  # např. "W52"
    week_previous: str  # např. "W51"
    csv_current: str  # cesta k CSV
    csv_previous: str  # cesta k CSV
    
    # Výstupní soubory
    output_pdf: str = "Weekly_Sales_Report.pdf"
    output_dir: Path = field(default_factory=lambda: Path("."))
    
    # Filtry a thresholdy
    min_revenue_exceeders: float = 10_000  # Kč
    min_qty_exceeders: int = 5
    top_n_categories_l1: int = 15
    top_n_categories_l2: int = 20
    top_n_sku: int = 10
    
    # Mapování sloupců (pokud se liší názvy)
    column_mapping: Dict[str, str] = field(default_factory=lambda: {
        'Product Id Sap': 'SKU',
        'Product Name Web': 'Product_Name',
        'product category L1': 'L1',
        'product category L2': 'L2',
        'product category L3': 'L3',
        'Buy Price': 'Buy_Price',
        'Standard Price': 'Standard_Price',
        'Revenue': 'Revenue',
        'GM1 wo VAT': 'GM1',
        'Quantity Delivered': 'Qty',
        'Services': 'Services',
        'Brand Name': 'Brand',
        'Supplier Name': 'Supplier'
    })
    
    # PDF styling
    pdf_font: str = "Arial"
    pdf_colors: Dict[str, str] = field(default_factory=lambda: {
        'header_l1': '#4CAF50',
        'header_l2': '#2196F3',
        'header_exceeders': '#4CAF50',
        'header_underperf': '#F44336',
        'header_revenue': '#FF9800',
        'header_problems': '#F44336'
    })


class WeeklySalesReport:
    """Hlavní třída pro generování týdenních reportů"""
    
    def __init__(self, config: Optional[ReportConfig] = None, **kwargs):
        """
        Inicializace reportu.
        
        Args:
            config: ReportConfig objekt, nebo None pro použití kwargs
            **kwargs: Parametry pro vytvoření ReportConfig
        
        Příklady:
            # S config objektem
            cfg = ReportConfig(week_current="W52", ...)
            report = WeeklySalesReport(config=cfg)
            
            # S kwargs (jednodušší)
            report = WeeklySalesReport(
                week_current="W52",
                week_previous="W51",
                csv_current="data_w52.csv",
                csv_previous="data_w51.csv"
            )
        """
        if config is None:
            config = ReportConfig(**kwargs)
        self.config = config
        
        self.df_current = None
        self.df_previous = None
        self.results = {}  # Ukládání mezivýsledků
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Načte a očistí CSV data"""
        print(f"[LOAD] Loading {self.config.csv_current}...")
        
        # Detekce encoding a delimiter
        self.df_current = self._load_csv(self.config.csv_current, self.config.week_current)
        self.df_previous = self._load_csv(self.config.csv_previous, self.config.week_previous)
        
        print(f"[OK] Loaded: {len(self.df_current)} rows (current), {len(self.df_previous)} rows (previous)")
        return self.df_current, self.df_previous
    
    def _load_csv(self, path: str, week_id: str) -> pd.DataFrame:
        """Pomocná funkce pro načtení jednoho CSV"""
        # Detekce encoding: priorita UTF-16 + TAB, pak UTF-8
        try:
            df = pd.read_csv(path, encoding='utf-16', sep='\t')
        except (UnicodeError, pd.errors.ParserError):
            try:
                df = pd.read_csv(path, encoding='utf-8-sig', sep=',')
            except:
                df = pd.read_csv(path, encoding='utf-8-sig', sep=';')

        # Rename columns
        df = df.rename(columns=self.config.column_mapping)

        # Add Week column
        if 'Week' not in df.columns:
            df['Week'] = week_id

        # Detect thousand separator (comma in numbers like "1,735.00")
        numeric_cols = ['Revenue', 'GM1', 'Qty', 'Buy_Price', 'Standard_Price']
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == object:
                    # Remove thousand separators (comma) and convert
                    df[col] = df[col].astype(str).str.replace(',', '').replace('', '0')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df
    
    def analyze(self) -> Dict:
        """
        Hlavní analýza - spustí všechny sub-analýzy.
        
        Returns:
            Dict s výsledky analýzy
        """
        if self.df_current is None:
            self.load_data()
        
        print("[ANALYZE] Starting analysis...")
        
        # Data quality check
        self.results['data_check'] = self._data_check()
        
        # Kategoriální analýza
        self.results['l1'] = self._analyze_category('L1', self.config.top_n_categories_l1)
        self.results['l2'] = self._analyze_category('L2', self.config.top_n_categories_l2)
        
        # WoW comparison
        self.results['exceeders'] = self._find_exceeders()
        self.results['underperformers'] = self._find_underperformers()
        
        # Services breakdown
        if 'Services' in self.df_current.columns:
            self.results['services'] = self._analyze_services()
        
        # Top SKU
        self.results['top_sku'] = self._top_sku_revenue()
        
        # Problematické SKU
        self.results['problems'] = self._problematic_sku()
        
        print("[OK] Analysis complete")
        return self.results
    
    def _data_check(self) -> Dict:
        """Data quality check"""
        df = self.df_current
        
        return {
            'rows': len(df),
            'sku_count': df['SKU'].nunique() if 'SKU' in df.columns else 0,
            'sku_sold': len(df[df['Revenue'] > 0]) if 'Revenue' in df.columns else 0,
            'total_revenue': df['Revenue'].sum() if 'Revenue' in df.columns else 0,
            'total_gm1': df['GM1'].sum() if 'GM1' in df.columns else 0,
            'total_qty': df['Qty'].sum() if 'Qty' in df.columns else 0,
            'gm1_negative_count': len(df[df['GM1'] < 0]) if 'GM1' in df.columns else 0,
            'gm1_negative_impact': df[df['GM1'] < 0]['GM1'].sum() if 'GM1' in df.columns else 0
        }
    
    def _analyze_category(self, level: str, top_n: int) -> pd.DataFrame:
        """Analýza kategorie (L1/L2/L3)"""
        if level not in self.df_current.columns:
            return pd.DataFrame()
        
        # Agregace current week
        agg_current = self.df_current.groupby(level).agg({
            'Revenue': 'sum',
            'GM1': 'sum',
            'Qty': 'sum',
            'SKU': 'nunique'
        }).reset_index()
        
        # WoW comparison
        if self.df_previous is not None and level in self.df_previous.columns:
            agg_previous = self.df_previous.groupby(level)['Revenue'].sum()
            agg_current['Revenue_prev'] = agg_current[level].map(agg_previous).fillna(0)
            agg_current['WoW_pct'] = ((agg_current['Revenue'] - agg_current['Revenue_prev']) / 
                                      agg_current['Revenue_prev'].replace(0, np.nan) * 100)
        
        # Share calculation
        total_revenue = agg_current['Revenue'].sum()
        agg_current['share'] = agg_current['Revenue'] / total_revenue * 100
        
        # GM1%
        agg_current['GM1_pct'] = (agg_current['GM1'] / agg_current['Revenue'].replace(0, np.nan) * 100)
        
        # Sort and return top N
        return agg_current.sort_values('Revenue', ascending=False).head(top_n)
    
    def _find_exceeders(self) -> pd.DataFrame:
        """Find top WoW performers"""
        if self.df_previous is None:
            return pd.DataFrame()
        
        # AGREGACE: Sečti podle SKU (bez Services, Sales Condition, Promo)
        current_agg = self.df_current.groupby('SKU').agg({
            'Product_Name': 'first',
            'Revenue': 'sum',
            'Qty': 'sum'
        }).reset_index()
        
        previous_agg = self.df_previous.groupby('SKU').agg({
            'Revenue': 'sum'
        }).reset_index()
        
        # Merge aggregated data
        merged = pd.merge(
            current_agg,
            previous_agg,
            on='SKU',
            how='left',
            suffixes=('', '_prev')
        )
        
        # Filter
        merged = merged[
            (merged['Revenue'] >= self.config.min_revenue_exceeders) &
            (merged['Qty'] >= self.config.min_qty_exceeders) &
            (merged['Revenue_prev'] > 0)
        ]
        
        # Calculate WoW%
        merged['WoW_pct'] = ((merged['Revenue'] - merged['Revenue_prev']) / merged['Revenue_prev'] * 100)
        merged['Revenue_delta'] = merged['Revenue'] - merged['Revenue_prev']
        
        # Filtruj pouze růsty (WoW > 10%) a seřaď podle největšího růstu
        merged = merged[merged['WoW_pct'] > 10]
        
        return merged.sort_values('WoW_pct', ascending=False).head(self.config.top_n_sku)
    
    def _find_underperformers(self) -> pd.DataFrame:
        """Find top WoW decliners"""
        if self.df_previous is None:
            return pd.DataFrame()
        
        # AGREGACE: Sečti podle SKU (bez Services, Sales Condition, Promo)
        current_agg = self.df_current.groupby('SKU').agg({
            'Product_Name': 'first',
            'Revenue': 'sum',
            'Qty': 'sum'
        }).reset_index()
        
        previous_agg = self.df_previous.groupby('SKU').agg({
            'Revenue': 'sum'
        }).reset_index()
        
        # Merge aggregated data
        merged = pd.merge(
            current_agg,
            previous_agg,
            on='SKU',
            how='left',
            suffixes=('', '_prev')
        )
        
        # Filter - produkty s poklesem
        merged = merged[
            (merged['Revenue'] >= self.config.min_revenue_exceeders) &
            (merged['Qty'] >= self.config.min_qty_exceeders) &
            (merged['Revenue_prev'] > 0)
        ]
        
        # Calculate WoW%
        merged['WoW_pct'] = ((merged['Revenue'] - merged['Revenue_prev']) / merged['Revenue_prev'] * 100)
        merged['Revenue_delta'] = merged['Revenue'] - merged['Revenue_prev']
        
        # Filtruj pouze poklesy (WoW < -10%) a seřaď podle největšího poklesu
        merged = merged[merged['WoW_pct'] < -10]
        
        return merged.sort_values('WoW_pct', ascending=True).head(self.config.top_n_sku)
    
    def _analyze_services(self) -> pd.DataFrame:
        """Services breakdown"""
        if 'Services' not in self.df_current.columns:
            return pd.DataFrame()
        
        return self.df_current.groupby('Services').agg({
            'Revenue': 'sum',
            'GM1': 'sum',
            'Qty': 'sum',
            'SKU': 'nunique'
        }).reset_index()
    
    def _top_sku_revenue(self) -> pd.DataFrame:
        """Top SKU by absolute revenue"""
        # AGREGACE: Sečti podle SKU (bez Services, Sales Condition, Promo)
        agg = self.df_current.groupby('SKU').agg({
            'Product_Name': 'first',
            'Revenue': 'sum',
            'GM1': 'sum',
            'Qty': 'sum'
        }).reset_index()
        
        return agg.nlargest(self.config.top_n_sku, 'Revenue')[[
            'SKU', 'Product_Name', 'Revenue', 'GM1', 'Qty'
        ]]
    
    def _problematic_sku(self) -> pd.DataFrame:
        """SKU s GM1 < 0 nebo nízkou marží"""
        # AGREGACE: Sečti podle SKU (bez Services, Sales Condition, Promo)
        agg = self.df_current.groupby('SKU').agg({
            'Product_Name': 'first',
            'Revenue': 'sum',
            'GM1': 'sum'
        }).reset_index()
        
        agg['GM1_pct'] = agg['GM1'] / agg['Revenue'].replace(0, np.nan) * 100
        
        # Filter problematic
        problematic = agg[
            (agg['GM1'] < 0) | 
            ((agg['GM1_pct'] < 10) & (agg['GM1_pct'] >= 0))
        ]
        
        return problematic.nlargest(self.config.top_n_sku, 'Revenue')[
            ['SKU', 'Product_Name', 'Revenue', 'GM1', 'GM1_pct']
        ]
    
    def save_results_csv(self, output_dir: Optional[Path] = None):
        """Uloží všechny výsledky do CSV souborů"""
        if output_dir is None:
            output_dir = self.config.output_dir
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Save individual CSVs
        for key, df in self.results.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                filepath = output_dir / f"output_{key}.csv"
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                print(f"[OK] Saved: {filepath}")
    
    def generate_pdf(self, output_path: Optional[str] = None):
        """
        Vygeneruj PDF report.
        
        Args:
            output_path: Cesta k výstupnímu PDF (nebo použij config.output_pdf)
        """
        if output_path is None:
            output_path = self.config.output_pdf
        
        print(f"[PDF] Generating {output_path}...")
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            print("[ERROR] ReportLab not installed. Run: pip install reportlab")
            return
        
        # Register Arial font
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
        except:
            print("[WARNING] Arial font not found, using default")
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                     fontSize=18, textColor=colors.HexColor('#2C3E50'),
                                     fontName='Arial-Bold')
        header_style = ParagraphStyle('CustomHeader', parent=styles['Heading2'],
                                      fontSize=14, textColor=colors.HexColor('#34495E'),
                                      fontName='Arial-Bold')
        
        # Title
        story.append(Paragraph(f"Weekly Sales Report - Košík", title_style))
        story.append(Paragraph(f"Week {self.config.week_current} vs {self.config.week_previous}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        dc = self.results.get('data_check', {})
        story.append(Paragraph("Executive Summary", header_style))
        
        summary_data = [
            ["Metric", "Value"],
            ["Total Revenue", f"{dc.get('total_revenue', 0):,.0f} Kč"],
            ["Total GM1", f"{dc.get('total_gm1', 0):,.0f} Kč"],
            ["SKU Sold", f"{dc.get('sku_sold', 0):,}"],
            ["GM1 < 0 SKU", f"{dc.get('gm1_negative_count', 0)} ({dc.get('gm1_negative_impact', 0):,.0f} Kč)"]
        ]
        
        t = Table(summary_data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))
        
        # L1 Categories
        if 'l1' in self.results and not self.results['l1'].empty:
            story.append(Paragraph("Top L1 Categories", header_style))
            df_l1 = self.results['l1'].head(15)
            
            table_data = [["Category", "Revenue (Kč)", "Share %", "WoW %", "GM1 %"]]
            for _, row in df_l1.iterrows():
                table_data.append([
                    str(row.get('L1', 'N/A'))[:30],
                    f"{row.get('Revenue', 0):,.0f}",
                    f"{row.get('share', 0):.1f}",
                    f"{row.get('WoW_pct', 0):.1f}",
                    f"{row.get('GM1_pct', 0):.1f}"
                ])
            
            t = Table(table_data, colWidths=[2*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
            ]))
            story.append(t)
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        print(f"[OK] PDF created: {output_path}")
        
    def print_summary(self):
        """Vypíše executive summary do konzole"""
        if not self.results:
            print("[WARNING] No results available. Run analyze() first.")
            return
        
        dc = self.results.get('data_check', {})
        
        print("\n" + "="*80)
        print("EXECUTIVE SUMMARY")
        print("="*80)
        print(f"Week: {self.config.week_current} (previous: {self.config.week_previous})")
        print(f"Total Revenue: {dc.get('total_revenue', 0):,.0f} Kč")
        print(f"Total GM1: {dc.get('total_gm1', 0):,.0f} Kč")
        print(f"SKU sold: {dc.get('sku_sold', 0):,}")
        print(f"GM1 < 0: {dc.get('gm1_negative_count', 0)} SKU (impact: {dc.get('gm1_negative_impact', 0):,.0f} Kč)")
        
        # Top L1
        if 'l1' in self.results and not self.results['l1'].empty:
            print("\nTop 3 L1 categories:")
            for idx, row in self.results['l1'].head(3).iterrows():
                print(f"  {idx+1}. {row.get('L1', 'N/A')}: {row.get('Revenue', 0):,.0f} Kč (share {row.get('share', 0):.1f}%)")
        
        print("="*80 + "\n")


    def generate_pdf_advanced(self, console_output_path: Optional[str] = None, pdf_output_path: Optional[str] = None):
        """
        Vygeneruje pokročilé PDF z console outputu pomocí ReportLab.
        
        Args:
            console_output_path: Cesta k textovému souboru s console výstupem
            pdf_output_path: Cesta k výstupnímu PDF (default z config)
        """
        if pdf_output_path is None:
            pdf_output_path = self.config.output_pdf
        
        if console_output_path is None:
            # Vytvoř console output
            console_output_path = self.config.output_dir / f"console_output_{self.config.week_current}.txt"
            self._save_console_output(console_output_path)
        
        create_pdf_from_console(console_output_path, pdf_output_path)
    
    
    def _save_console_output(self, output_path: Path):
        """Uloží console output do souboru"""
        import sys
        from io import StringIO
        
        # Zachytit console output
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        
        try:
            self.print_summary()
            self._print_detailed_tables()
        finally:
            sys.stdout = old_stdout
        
        # Ulož do souboru
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(buffer.getvalue())
    
    
    def _print_detailed_tables(self):
        """Vypíše detailní tabulky pro pokročilé PDF generování"""
        results = self.results
        
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


def create_pdf_from_console(console_output_path, pdf_output_path):
    """Vytvoří pokročilé PDF z console outputu"""

    # Register DejaVu fonts for Czech characters
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'C:\\Windows\\Fonts\\DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf'))
        font_name = 'DejaVuSans'
        font_name_bold = 'DejaVuSans-Bold'
    except:
        # Fallback to Helvetica
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'

    # Create PDF
    doc = SimpleDocTemplate(str(pdf_output_path), pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=40, bottomMargin=30)

    # Container for 'Flowable' objects
    elements = []

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=1  # Center
    )

    h1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=10,
        spaceBefore=15
    )

    h2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name_bold,
        fontSize=11,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8,
        spaceBefore=10
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=12
    )

    # Title
    elements.append(Paragraph("Weekly Sales Report - Košík", title_style))
    elements.append(Paragraph("2025", h2_style))
    elements.append(Spacer(1, 0.3*inch))

    # Read console output
    with open(console_output_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_section = None
    content = []

    for line in lines:
        line = line.rstrip()

        if '=' * 40 in line:
            # Section divider
            if content:
                # Process previous section
                _add_section_to_pdf(elements, current_section, content, h1_style, h2_style, normal_style, font_name)
                content = []
            continue

        # Detect section headers
        if line.startswith('['):
            continue
        elif 'DATA CHECK' in line:
            current_section = 'DATA CHECK: ' + line.split('-')[-1].strip()
        elif 'EXECUTIVE SUMMARY' in line:
            current_section = 'EXECUTIVE SUMMARY'
        elif 'KATEGORIE' in line and 'W52' in line:
            current_section = 'KATEGORIE (L1/L2/L3)'
        elif 'SERVICES' in line:
            current_section = 'SERVICES BREAKDOWN'
        elif 'TOP LISTY' in line:
            current_section = 'TOP LISTY WoW'
        elif 'TOP 10 SKU dle Revenue' in line:
            current_section = 'TOP SKU REVENUE'
        elif 'TOP Problematické SKU' in line:
            current_section = 'PROBLEMATICKÉ SKU'
        elif 'DATA ISSUES' in line:
            current_section = 'DATA ISSUES'
        elif 'WEEKLY REPORT COMPLETE' in line:
            break
        else:
            if line.strip():
                content.append(line)

    # Last section
    if content:
        _add_section_to_pdf(elements, current_section, content, h1_style, h2_style, normal_style, font_name)

    # Build PDF
    doc.build(elements)
    print(f"PDF vytvořeno: {pdf_output_path}")


def _add_section_to_pdf(elements, section_name, content, h1_style, h2_style, normal_style, font_name):
    """Přidá sekci do PDF"""
    if not section_name:
        return

    # Add section header
    elements.append(Paragraph(section_name, h1_style))
    elements.append(Spacer(1, 0.1*inch))

    # Parse content
    if 'DATA CHECK' in section_name:
        _add_data_check(elements, content, normal_style)
    elif 'EXECUTIVE SUMMARY' in section_name:
        _add_executive_summary(elements, content, h2_style, normal_style)
    elif 'KATEGORIE' in section_name:
        _add_categories(elements, content, h2_style, normal_style, font_name)
    elif 'SERVICES' in section_name:
        _add_services(elements, content, normal_style, font_name)
    elif 'TOP LISTY' in section_name:
        _add_top_lists(elements, content, h2_style, normal_style, font_name)
    elif 'TOP SKU' in section_name:
        _add_top_sku(elements, content, normal_style, font_name)
    elif 'PROBLEMATICKÉ' in section_name:
        _add_problematic(elements, content, h2_style, normal_style, font_name)
    elif 'DATA ISSUES' in section_name:
        _add_data_issues(elements, content, normal_style)

    elements.append(Spacer(1, 0.2*inch))


def _add_data_check(elements, content, normal_style):
    """Data check section"""
    for line in content:
        elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 0.1*inch))


def _add_executive_summary(elements, content, h2_style, normal_style):
    """Executive summary"""
    for line in content:
        if line.startswith('Top ') or line.startswith('Doporučené'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
        else:
            elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 0.1*inch))


def _add_categories(elements, content, h2_style, normal_style, font_name):
    """Category tables"""
    current_table = []
    table_type = None

    for line in content:
        if 'L1 kategorie:' in line or 'L2 kategorie' in line or 'L3 kategorie' in line:
            if current_table:
                _create_table(elements, current_table, table_type, font_name)
                current_table = []
            table_type = 'L1' if 'L1' in line else ('L2' if 'L2' in line else 'L3')
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            continue

        if line.strip().startswith('Kategorie') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        _create_table(elements, current_table, table_type, font_name)


def _add_services(elements, content, normal_style, font_name):
    """Services table"""
    table_data = []
    for line in content:
        if line.strip().startswith('Services') or line.strip().startswith('-'):
            continue
        if line.strip():
            table_data.append(line)

    if table_data:
        _create_table(elements, table_data, 'services', font_name)


def _add_top_lists(elements, content, h2_style, normal_style, font_name):
    """Top lists"""
    current_table = []
    table_type = None

    for line in content:
        if 'TOP 10 Exceeders' in line or 'TOP 10 Underperformers' in line:
            if current_table:
                _create_table(elements, current_table, table_type, font_name)
                current_table = []
            table_type = 'exceeders' if 'Exceeders' in line else 'underperformers'
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            continue

        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        _create_table(elements, current_table, table_type, font_name)


def _add_top_sku(elements, content, normal_style, font_name):
    """Top SKU by revenue"""
    table_data = []
    for line in content:
        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue
        if line.strip():
            table_data.append(line)

    if table_data:
        _create_table(elements, table_data, 'top_sku', font_name)


def _add_problematic(elements, content, h2_style, normal_style, font_name):
    """Problematic SKU"""
    current_table = []
    table_type = None

    for line in content:
        if 'TOP 5 SKU' in line:
            if current_table:
                _create_table(elements, current_table, table_type, font_name)
                current_table = []
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            table_type = 'problematic'
            continue

        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        _create_table(elements, current_table, table_type, font_name)


def _add_data_issues(elements, content, normal_style):
    """Data issues"""
    for line in content:
        if line.strip().startswith(tuple('12345')):
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
        else:
            elements.append(Paragraph(line, normal_style))


def _create_table(elements, data, table_type, font_name):
    """Create table from parsed data"""
    if not data:
        return

    # Parse fixed-width table data
    table_data_parsed = []
    for line in data[:20]:  # Max 20 rows
        # Split by multiple spaces
        parts = [p.strip() for p in line.split('  ') if p.strip()]
        if len(parts) >= 2:
            table_data_parsed.append(parts[:6])  # Max 6 columns

    if not table_data_parsed:
        return

    # Create table
    table = Table(table_data_parsed, repeatRows=0)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.1*inch))


# ============================================================================
# POKROČILÉ PDF GENEROVÁNÍ Z CONSOLE OUTPUTU
# ============================================================================

def create_advanced_pdf_from_console(console_output_path, pdf_output_path):
    """
    Vytvoří pokročilé PDF z console outputu s tabulkami a formátováním.
    Vylepšená verze s lepším vizuálním designem.
    """
    # Register DejaVu fonts for Czech characters
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'C:\\Windows\\Fonts\\DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf'))
        font_name = 'DejaVuSans'
        font_name_bold = 'DejaVuSans-Bold'
    except:
        # Fallback to Helvetica
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'

    # Create PDF
    doc = SimpleDocTemplate(str(pdf_output_path), pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=50, bottomMargin=40)

    # Container for 'Flowable' objects
    elements = []

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=22,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        alignment=1  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=30,
        alignment=1  # Center
    )

    h1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        borderPadding=8,
        leftIndent=0
    )

    h2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name_bold,
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=12
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2c3e50')
    )
    
    metric_style = ParagraphStyle(
        'MetricStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#2c3e50')
    )

    # Title with subtitle
    elements.append(Paragraph("Weekly Sales Report - Košík", title_style))
    from datetime import datetime
    report_date = datetime.now().strftime("%d.%m.%Y")
    elements.append(Paragraph(f"Vygenerováno: {report_date}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))

    # Read console output
    with open(console_output_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_section = None
    content = []

    for line in lines:
        line = line.rstrip()

        if '=' * 40 in line:
            # Section divider
            if content:
                # Process previous section
                _add_section_to_pdf(elements, current_section, content, h1_style, h2_style, normal_style, font_name)
                content = []
            continue

        # Detect section headers
        if line.startswith('['):
            continue
        elif 'DATA CHECK' in line:
            current_section = 'DATA CHECK: ' + line.split('-')[-1].strip()
        elif 'EXECUTIVE SUMMARY' in line:
            current_section = 'EXECUTIVE SUMMARY'
        elif 'KATEGORIE' in line and 'W52' in line:
            current_section = 'KATEGORIE (L1/L2/L3)'
        elif 'SERVICES' in line:
            current_section = 'SERVICES BREAKDOWN'
        elif 'TOP LISTY' in line:
            current_section = 'TOP LISTY WoW'
        elif 'TOP 10 SKU dle Revenue' in line:
            current_section = 'TOP SKU REVENUE'
        elif 'TOP Problematické SKU' in line:
            current_section = 'PROBLEMATICKÉ SKU'
        elif 'DATA ISSUES' in line:
            current_section = 'DATA ISSUES'
        elif 'WEEKLY REPORT COMPLETE' in line:
            break
        else:
            if line.strip():
                content.append(line)

    # Last section
    if content:
        _add_section_to_pdf(elements, current_section, content, h1_style, h2_style, normal_style, font_name)

    # Build PDF
    doc.build(elements)
    print(f"PDF vytvořeno: {pdf_output_path}")


def _add_section_to_pdf(elements, section_name, content, h1_style, h2_style, normal_style, font_name):
    """Přidá sekci do PDF"""
    if not section_name:
        return

    # Add section header
    elements.append(Paragraph(section_name, h1_style))
    elements.append(Spacer(1, 0.1*inch))

    # Parse content
    if 'DATA CHECK' in section_name:
        _add_data_check(elements, content, normal_style)
    elif 'EXECUTIVE SUMMARY' in section_name:
        _add_executive_summary(elements, content, h2_style, normal_style)
    elif 'KATEGORIE' in section_name:
        _add_categories(elements, content, h2_style, normal_style, font_name)
    elif 'SERVICES' in section_name:
        _add_services(elements, content, normal_style, font_name)
    elif 'TOP LISTY' in section_name:
        _add_top_lists(elements, content, h2_style, normal_style, font_name)
    elif 'TOP SKU' in section_name:
        _add_top_sku(elements, content, normal_style, font_name)
    elif 'PROBLEMATICKÉ' in section_name:
        _add_problematic(elements, content, h2_style, normal_style, font_name)
    elif 'DATA ISSUES' in section_name:
        _add_data_issues(elements, content, normal_style)

    elements.append(Spacer(1, 0.2*inch))


def _add_data_check(elements, content, normal_style):
    """Data check section"""
    for line in content:
        elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 0.1*inch))


def _add_executive_summary(elements, content, h2_style, normal_style):
    """Executive summary"""
    for line in content:
        if line.startswith('Top ') or line.startswith('Doporučené'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
        else:
            elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 0.1*inch))


def _add_categories(elements, content, h2_style, normal_style, font_name):
    """Category tables"""
    current_table = []
    table_type = None

    for line in content:
        if 'L1 kategorie:' in line or 'L2 kategorie' in line or 'L3 kategorie' in line:
            if current_table:
                _create_pdf_table(elements, current_table, table_type, font_name)
                current_table = []
            table_type = 'L1' if 'L1' in line else ('L2' if 'L2' in line else 'L3')
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            continue

        if line.strip().startswith('Kategorie') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        _create_pdf_table(elements, current_table, table_type, font_name)


def _add_services(elements, content, normal_style, font_name):
    """Services table"""
    table_data = []
    for line in content:
        if line.strip().startswith('Services') or line.strip().startswith('-'):
            continue
        if line.strip():
            table_data.append(line)

    if table_data:
        _create_pdf_table(elements, table_data, 'services', font_name)


def _add_top_lists(elements, content, h2_style, normal_style, font_name):
    """Top lists"""
    current_table = []
    table_type = None

    for line in content:
        if 'TOP 10 Exceeders' in line or 'TOP 10 Underperformers' in line:
            if current_table:
                _create_pdf_table(elements, current_table, table_type, font_name)
                current_table = []
            table_type = 'exceeders' if 'Exceeders' in line else 'underperformers'
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            continue

        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        _create_pdf_table(elements, current_table, table_type, font_name)


def _add_top_sku(elements, content, normal_style, font_name):
    """Top SKU by revenue"""
    table_data = []
    for line in content:
        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue
        if line.strip():
            table_data.append(line)

    if table_data:
        _create_pdf_table(elements, table_data, 'top_sku', font_name)


def _add_problematic(elements, content, h2_style, normal_style, font_name):
    """Problematic SKU"""
    current_table = []
    table_type = None

    for line in content:
        if 'TOP 5 SKU' in line:
            if current_table:
                _create_pdf_table(elements, current_table, table_type, font_name)
                current_table = []
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            table_type = 'problematic'
            continue

        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        _create_pdf_table(elements, current_table, table_type, font_name)


def _add_data_issues(elements, content, normal_style):
    """Data issues"""
    for line in content:
        if line.strip().startswith(tuple('12345')):
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
        else:
            elements.append(Paragraph(line, normal_style))


def _create_pdf_table(elements, data, table_type, font_name):
    """Create table from parsed data"""
    if not data:
        return

    # Parse fixed-width table data
    table_data_parsed = []
    for line in data[:20]:  # Max 20 rows
        # Split by multiple spaces
        parts = [p.strip() for p in line.split('  ') if p.strip()]
        if len(parts) >= 2:
            table_data_parsed.append(parts[:6])  # Max 6 columns

    if not table_data_parsed:
        return

    # Create table
    table = Table(table_data_parsed, repeatRows=0)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.1*inch))


# ============================================================================
# HELPER FUNCTIONS pro rychlé použití
# ============================================================================

def quick_report(csv_current: str, csv_previous: str, 
                 week_current: str = "W52", week_previous: str = "W51",
                 output_pdf: str = "Weekly_Report.pdf"):
    """
    Jednoduchá funkce pro rychlé vygenerování reportu.
    
    Příklad:
        quick_report(
            csv_current="sales_w52.csv",
            csv_previous="sales_w51.csv",
            week_current="W52",
            week_previous="W51"
        )
    """
    report = WeeklySalesReport(
        week_current=week_current,
        week_previous=week_previous,
        csv_current=csv_current,
        csv_previous=csv_previous,
        output_pdf=output_pdf
    )
    
    report.analyze()
    report.print_summary()
    report.save_results_csv()
    
    return report


if __name__ == "__main__":
    # Příklad použití
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python weekly_report_lib.py <csv_current> <csv_previous> [week_current] [week_previous]")
        sys.exit(1)
    
    csv_current = sys.argv[1]
    csv_previous = sys.argv[2]
    week_current = sys.argv[3] if len(sys.argv) > 3 else "W52"
    week_previous = sys.argv[4] if len(sys.argv) > 4 else "W51"
    
    report = quick_report(csv_current, csv_previous, week_current, week_previous)
    print("\n✅ Report complete! Check output_*.csv files")
