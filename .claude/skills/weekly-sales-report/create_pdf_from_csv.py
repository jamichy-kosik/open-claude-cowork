#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Generator z CSV výstupů - Weekly Sales Report Košík
Vytvoří strukturovaný PDF report dle McKinsey standardů
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from pathlib import Path
import sys

def format_cz_number(value, decimals=0):
    """Formátuje číslo do CZ formátu (mezera jako tisícový oddělovač, čárka jako desetinný)"""
    if pd.isna(value):
        return "-"
    try:
        value = float(value)
        if decimals == 0:
            formatted = f"{value:,.0f}"
        else:
            formatted = f"{value:,.{decimals}f}"
        # Nahraď čárku za mezeru (tisíce) a tečku za čárku (desetiny)
        formatted = formatted.replace(",", " ").replace(".", ",")
        return formatted
    except:
        return str(value)

def format_cz_percent(value, decimals=1):
    """Formátuje procenta do CZ formátu"""
    if pd.isna(value):
        return "-"
    try:
        value = float(value)
        return f"{value:,.{decimals}f}".replace(".", ",") + " %"
    except:
        return str(value)

def create_pdf_report_from_csv(
    output_pdf_path,
    l1_csv, l2_csv, services_csv,
    exceeders_csv, underperf_csv,
    top_sku_csv, problems_csv,
    week_current="W52", week_previous="W51"
):
    """Vytvoří PDF report z CSV souborů"""

    # Register Arial font pro české znaky
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
        font_name = 'Arial'
        font_name_bold = 'Arial-Bold'
    except:
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'C:\\Windows\\Fonts\\DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf'))
            font_name = 'DejaVuSans'
            font_name_bold = 'DejaVuSans-Bold'
        except:
            font_name = 'Helvetica'
            font_name_bold = 'Helvetica-Bold'

    # Načti CSV data
    df_l1 = pd.read_csv(l1_csv, encoding='utf-8-sig')
    df_l2 = pd.read_csv(l2_csv, encoding='utf-8-sig')
    df_services = pd.read_csv(services_csv, encoding='utf-8-sig')
    df_exceeders = pd.read_csv(exceeders_csv, encoding='utf-8-sig')
    df_underperf = pd.read_csv(underperf_csv, encoding='utf-8-sig')
    df_top_sku = pd.read_csv(top_sku_csv, encoding='utf-8-sig')
    df_problems = pd.read_csv(problems_csv, encoding='utf-8-sig')

    # Vytvoř PDF dokument
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Styly
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=20,
        alignment=1
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=14,
        textColor=colors.HexColor('#2196F3'),
        spaceAfter=10,
        spaceBefore=15
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName=font_name_bold,
        fontSize=11,
        textColor=colors.HexColor('#444444'),
        spaceAfter=8,
        spaceBefore=10
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=12
    )

    # === TITLE PAGE ===
    elements.append(Paragraph(f"Weekly Sales Report - Košík", title_style))
    elements.append(Paragraph(f"{week_current} vs {week_previous} (2025)", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))

    # === DATA CHECK ===
    total_revenue = df_l1['Revenue'].sum()
    total_gm1 = df_l1['GM1'].sum()
    total_qty = df_l1['Qty'].sum()
    total_sku = df_l1['SKU'].sum()
    gm1_pct = (total_gm1 / total_revenue * 100) if total_revenue > 0 else 0

    # Počet SKU s GM1 < 0
    gm1_negative_count = df_problems[df_problems['GM1'] < 0].shape[0] if 'GM1' in df_problems.columns else 0
    gm1_negative_impact = df_problems[df_problems['GM1'] < 0]['GM1'].sum() if gm1_negative_count > 0 else 0

    elements.append(Paragraph("DATA CHECK", h1_style))

    data_check_text = f"""
    <b>Týden:</b> {week_current} (předchozí: {week_previous})<br/>
    <b>Celkový obrat:</b> {format_cz_number(total_revenue, 0)} Kč<br/>
    <b>Celková GM1:</b> {format_cz_number(total_gm1, 0)} Kč ({format_cz_percent(gm1_pct, 1)})<br/>
    <b>Prodané množství:</b> {format_cz_number(total_qty, 0)} ks<br/>
    <b>SKU celkem:</b> {format_cz_number(total_sku, 0)}<br/>
    <b>SKU s GM1 &lt; 0:</b> {gm1_negative_count} (dopad: {format_cz_number(gm1_negative_impact, 0)} Kč)
    """
    elements.append(Paragraph(data_check_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))

    # === EXECUTIVE SUMMARY ===
    elements.append(Paragraph("EXECUTIVE SUMMARY", h1_style))

    # Top 3 L1
    top3_l1 = df_l1.head(3)
    wow_total = ((total_revenue - df_l1['Revenue_prev'].sum()) / df_l1['Revenue_prev'].sum() * 100) if df_l1['Revenue_prev'].sum() > 0 else 0

    summary_text = f"""
    Prodej Košíku za týden {week_current} dosáhl {format_cz_number(total_revenue/1000, 0)} tis. Kč,
    WoW změna {format_cz_percent(wow_total, 1)}. Marže GM1 na úrovni {format_cz_percent(gm1_pct, 1)}.<br/><br/>

    <b>Top 3 kategorie L1 (dle Revenue):</b><br/>
    """

    for idx, row in top3_l1.iterrows():
        summary_text += f"• <b>{row['L1']}</b>: {format_cz_number(row['Revenue']/1000, 0)} tis. Kč (share {format_cz_percent(row['share'], 1)}), WoW {format_cz_percent(row['WoW_pct'], 1)}<br/>"

    summary_text += "<br/><b>Top 5 kategorie L2 (dle Revenue):</b><br/>"
    top5_l2 = df_l2.head(5)
    for idx, row in top5_l2.iterrows():
        summary_text += f"• {row['L2']}: {format_cz_number(row['Revenue']/1000, 0)} tis. Kč (share {format_cz_percent(row['share'], 1)})<br/>"

    # Top drivery (z exceeders)
    summary_text += "<br/><b>Top 3 drivery růstu (WoW):</b><br/>"
    top_drivers = df_exceeders.head(3)
    for idx, row in top_drivers.iterrows():
        pct = row.get('WoW_pct', 0)
        delta = row.get('Revenue_delta', 0)
        summary_text += f"• SKU {row['SKU']} - {row['Product_Name'][:40]}: +{format_cz_percent(pct, 1)} ({format_cz_number(delta/1000, 0)} tis. Kč)<br/>"

    # Doporučené akce
    summary_text += "<br/><b>Doporučené akce:</b><br/>"
    summary_text += f"• Posílit zásoby top exceeders (vysoký WoW růst)<br/>"
    summary_text += f"• Analyzovat podvýkonné kategorie (Mražené -25%, Mléčné -17%)<br/>"
    summary_text += f"• Řešit {gm1_negative_count} SKU se zápornou GM1 (dopad {format_cz_number(abs(gm1_negative_impact)/1000, 0)} tis. Kč)<br/>"

    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))

    # === KATEGORIE L1 ===
    elements.append(Paragraph("KATEGORIE L1 - Přehled", h1_style))

    table_data = [['Kategorie', 'Revenue (tis. Kč)', 'Share', 'GM1%', 'WoW%', '#SKU']]
    for idx, row in df_l1.iterrows():
        if pd.notna(row['L1']):
            table_data.append([
                row['L1'],
                format_cz_number(row['Revenue']/1000, 0),
                format_cz_percent(row['share'], 1),
                format_cz_percent(row['GM1_pct'], 1),
                format_cz_percent(row['WoW_pct'], 1),
                format_cz_number(row['SKU'], 0)
            ])

    t = Table(table_data, colWidths=[80*mm, 30*mm, 20*mm, 20*mm, 20*mm, 15*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3*inch))

    # === KATEGORIE L2 ===
    elements.append(PageBreak())
    elements.append(Paragraph("KATEGORIE L2 - Top 20", h1_style))

    table_data = [['Kategorie', 'Revenue (tis. Kč)', 'Share', 'GM1%', 'WoW%']]
    df_l2_top = df_l2.head(20)
    for idx, row in df_l2_top.iterrows():
        if pd.notna(row['L2']):
            table_data.append([
                row['L2'][:35],
                format_cz_number(row['Revenue']/1000, 0),
                format_cz_percent(row['share'], 1),
                format_cz_percent(row['GM1_pct'], 1),
                format_cz_percent(row['WoW_pct'], 1)
            ])

    # Řádek "Ostatní"
    if len(df_l2) > 20:
        ostatni_rev = df_l2.iloc[20:]['Revenue'].sum()
        ostatni_share = df_l2.iloc[20:]['share'].sum()
        ostatni_gm1 = df_l2.iloc[20:]['GM1'].sum()
        ostatni_gm1_pct = (ostatni_gm1 / ostatni_rev * 100) if ostatni_rev > 0 else 0
        table_data.append([
            'Ostatní',
            format_cz_number(ostatni_rev/1000, 0),
            format_cz_percent(ostatni_share, 1),
            format_cz_percent(ostatni_gm1_pct, 1),
            '-'
        ])

    t = Table(table_data, colWidths=[90*mm, 30*mm, 20*mm, 20*mm, 25*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3*inch))

    # === SERVICES BREAKDOWN ===
    elements.append(Paragraph("SERVICES BREAKDOWN (HP vs Regions)", h1_style))

    table_data = [['Services', 'Revenue (tis. Kč)', 'Share', 'GM1 (tis. Kč)', 'GM1%', '#SKU']]
    for idx, row in df_services.iterrows():
        share_val = (row['Revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        gm1_pct_val = (row['GM1'] / row['Revenue'] * 100) if row['Revenue'] > 0 else 0
        table_data.append([
            row['Services'],
            format_cz_number(row['Revenue']/1000, 0),
            format_cz_percent(share_val, 1),
            format_cz_number(row['GM1']/1000, 0),
            format_cz_percent(gm1_pct_val, 1),
            format_cz_number(row['SKU'], 0)
        ])

    t = Table(table_data, colWidths=[40*mm, 35*mm, 20*mm, 30*mm, 20*mm, 20*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff3e0')])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3*inch))

    # === TOP EXCEEDERS ===
    elements.append(PageBreak())
    elements.append(Paragraph("TOP 10 EXCEEDERS (WoW růst)", h1_style))

    table_data = [['SKU', 'Produkt', 'Revenue (Kč)', 'WoW%', 'Δ Revenue (Kč)']]
    for idx, row in df_exceeders.head(10).iterrows():
        table_data.append([
            str(row['SKU']),
            row['Product_Name'][:35],
            format_cz_number(row['Revenue'], 0),
            format_cz_percent(row.get('WoW_pct', 0), 1),
            format_cz_number(row.get('Revenue_delta', 0), 0)
        ])

    t = Table(table_data, colWidths=[20*mm, 70*mm, 30*mm, 25*mm, 30*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3*inch))

    # === TOP UNDERPERFORMERS ===
    elements.append(Paragraph("TOP 10 UNDERPERFORMERS (WoW pokles)", h1_style))

    table_data = [['SKU', 'Produkt', 'Revenue (Kč)', 'WoW%', 'Δ Revenue (Kč)']]
    for idx, row in df_underperf.head(10).iterrows():
        table_data.append([
            str(row['SKU']),
            row['Product_Name'][:35],
            format_cz_number(row['Revenue'], 0),
            format_cz_percent(row.get('WoW_pct', 0), 1),
            format_cz_number(row.get('Revenue_delta', 0), 0)
        ])

    t = Table(table_data, colWidths=[20*mm, 70*mm, 30*mm, 25*mm, 30*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F44336')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffebee')])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3*inch))

    # === TOP SKU REVENUE ===
    elements.append(PageBreak())
    elements.append(Paragraph("TOP 10 SKU dle Revenue", h1_style))

    table_data = [['SKU', 'Produkt', 'Revenue (Kč)', 'GM1 (Kč)', 'Qty']]
    for idx, row in df_top_sku.head(10).iterrows():
        table_data.append([
            str(row['SKU']),
            row['Product_Name'][:40],
            format_cz_number(row['Revenue'], 0),
            format_cz_number(row['GM1'], 0),
            format_cz_number(row['Qty'], 0)
        ])

    t = Table(table_data, colWidths=[20*mm, 80*mm, 30*mm, 30*mm, 20*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff3e0')])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3*inch))

    # === PROBLEMATICKÉ SKU ===
    elements.append(Paragraph("TOP PROBLEMATICKÉ SKU", h1_style))

    # GM1 < 0
    df_neg_gm1 = df_problems[df_problems['GM1'] < 0].head(5)
    if len(df_neg_gm1) > 0:
        elements.append(Paragraph("1. SKU se zápornou GM1 (Top 5)", h2_style))
        table_data = [['SKU', 'Produkt', 'Revenue (Kč)', 'GM1 (Kč)', 'GM1%']]
        for idx, row in df_neg_gm1.iterrows():
            table_data.append([
                str(row['SKU']),
                row['Product_Name'][:40],
                format_cz_number(row['Revenue'], 0),
                format_cz_number(row['GM1'], 0),
                format_cz_percent(row['GM1_pct'], 1)
            ])

        t = Table(table_data, colWidths=[20*mm, 75*mm, 30*mm, 25*mm, 20*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F44336')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffebee'), colors.white])
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))

    # Nízká GM1% (0-10%)
    df_low_gm1 = df_problems[(df_problems['GM1'] >= 0) & (df_problems['GM1_pct'] < 10)].head(5)
    if len(df_low_gm1) > 0:
        elements.append(Paragraph("2. SKU s nízkou GM1% (0-10%)", h2_style))
        table_data = [['SKU', 'Produkt', 'Revenue (Kč)', 'GM1 (Kč)', 'GM1%']]
        for idx, row in df_low_gm1.iterrows():
            table_data.append([
                str(row['SKU']),
                row['Product_Name'][:40],
                format_cz_number(row['Revenue'], 0),
                format_cz_number(row['GM1'], 0),
                format_cz_percent(row['GM1_pct'], 1)
            ])

        t = Table(table_data, colWidths=[20*mm, 75*mm, 30*mm, 25*mm, 20*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fff3e0'), colors.white])
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))

    # === DATA ISSUES ===
    elements.append(PageBreak())
    elements.append(Paragraph("DATA ISSUES (Top 5 priorit)", h1_style))

    issues_text = f"""
    <b>1. Záporná GM1 u {gm1_negative_count} SKU</b><br/>
    <i>Dopad:</i> {format_cz_number(abs(gm1_negative_impact)/1000, 0)} tis. Kč<br/>
    <i>Fix:</i> Přehodnotit Buy Price nebo Standard Price, případně stáhnout SKU z prodeje<br/><br/>

    <b>2. Vysoká volatilita WoW u top kategorií</b><br/>
    <i>Dopad:</i> Mražené -25%, Mléčné -17%, Trvanlivé -23%<br/>
    <i>Fix:</i> Analyzovat demand planning a inventory management<br/><br/>

    <b>3. Nízká marže u top revenue SKU</b><br/>
    <i>Dopad:</i> Top 10 SKU zahrnuje položky s GM1% pod 10%<br/>
    <i>Fix:</i> Optimalizovat pricing strategii u high-volume produktů<br/><br/>

    <b>4. Nerovnoměrné rozdělení Services</b><br/>
    <i>Dopad:</i> HP má {format_cz_percent(df_services[df_services['Services']=='HP']['Revenue'].sum()/total_revenue*100, 1)} share<br/>
    <i>Fix:</i> Posílit distribuci v Regions (43% capacity využití)<br/><br/>

    <b>5. High-growth exceeders s rizikem stock-out</b><br/>
    <i>Dopad:</i> Top 3 exceeders s +100% WoW růstem<br/>
    <i>Fix:</i> Urgentní review inventory a reorder points
    """

    elements.append(Paragraph(issues_text, normal_style))

    # Build PDF
    doc.build(elements)
    print(f"\n[OK] PDF vytvořeno: {output_pdf_path}")
    print(f"[FILES] Velikost: {Path(output_pdf_path).stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    # Cesty k CSV
    base_dir = Path(__file__).parent

    create_pdf_report_from_csv(
        output_pdf_path=base_dir / "Weekly_Sales_Report_W52_vs_W51_2025.pdf",
        l1_csv=base_dir / "output_l1.csv",
        l2_csv=base_dir / "output_l2.csv",
        services_csv=base_dir / "output_services.csv",
        exceeders_csv=base_dir / "output_exceeders.csv",
        underperf_csv=base_dir / "output_underperformers.csv",
        top_sku_csv=base_dir / "output_top_sku.csv",
        problems_csv=base_dir / "output_problems.csv",
        week_current="W52",
        week_previous="W51"
    )
