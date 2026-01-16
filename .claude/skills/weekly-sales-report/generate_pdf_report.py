#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Weekly Report Generator - Košík
Vytvoří PDF report z konzolového výstupu
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import sys

def create_pdf_report(console_output_path, pdf_output_path):
    """Vytvoří PDF z console outputu"""

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
    elements.append(Paragraph("W52 vs W51 (2025)", h2_style))
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
                add_section_to_pdf(elements, current_section, content, h1_style, h2_style, normal_style, font_name)
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
        add_section_to_pdf(elements, current_section, content, h1_style, h2_style, normal_style, font_name)

    # Build PDF
    doc.build(elements)
    print(f"PDF vytvořeno: {pdf_output_path}")

def add_section_to_pdf(elements, section_name, content, h1_style, h2_style, normal_style, font_name):
    """Přidá sekci do PDF"""
    if not section_name:
        return

    # Add section header
    elements.append(Paragraph(section_name, h1_style))
    elements.append(Spacer(1, 0.1*inch))

    # Parse content
    if 'DATA CHECK' in section_name:
        add_data_check(elements, content, normal_style)
    elif 'EXECUTIVE SUMMARY' in section_name:
        add_executive_summary(elements, content, h2_style, normal_style)
    elif 'KATEGORIE' in section_name:
        add_categories(elements, content, h2_style, normal_style, font_name)
    elif 'SERVICES' in section_name:
        add_services(elements, content, normal_style, font_name)
    elif 'TOP LISTY' in section_name:
        add_top_lists(elements, content, h2_style, normal_style, font_name)
    elif 'TOP SKU' in section_name:
        add_top_sku(elements, content, normal_style, font_name)
    elif 'PROBLEMATICKÉ' in section_name:
        add_problematic(elements, content, h2_style, normal_style, font_name)
    elif 'DATA ISSUES' in section_name:
        add_data_issues(elements, content, normal_style)

    elements.append(Spacer(1, 0.2*inch))

def add_data_check(elements, content, normal_style):
    """Data check section"""
    for line in content:
        elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 0.1*inch))

def add_executive_summary(elements, content, h2_style, normal_style):
    """Executive summary"""
    for line in content:
        if line.startswith('Top ') or line.startswith('Doporučené'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
        else:
            elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 0.1*inch))

def add_categories(elements, content, h2_style, normal_style, font_name):
    """Category tables"""
    current_table = []
    table_type = None

    for line in content:
        if 'L1 kategorie:' in line or 'L2 kategorie' in line or 'L3 kategorie' in line:
            if current_table:
                create_table(elements, current_table, table_type, font_name)
                current_table = []
            table_type = 'L1' if 'L1' in line else ('L2' if 'L2' in line else 'L3')
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            continue

        if line.strip().startswith('Kategorie') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        create_table(elements, current_table, table_type, font_name)

def add_services(elements, content, normal_style, font_name):
    """Services table"""
    table_data = []
    for line in content:
        if line.strip().startswith('Services') or line.strip().startswith('-'):
            continue
        if line.strip():
            table_data.append(line)

    if table_data:
        create_table(elements, table_data, 'services', font_name)

def add_top_lists(elements, content, h2_style, normal_style, font_name):
    """Top lists"""
    current_table = []
    table_type = None

    for line in content:
        if 'TOP 10 Exceeders' in line or 'TOP 10 Underperformers' in line:
            if current_table:
                create_table(elements, current_table, table_type, font_name)
                current_table = []
            table_type = 'exceeders' if 'Exceeders' in line else 'underperformers'
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            continue

        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        create_table(elements, current_table, table_type, font_name)

def add_top_sku(elements, content, normal_style, font_name):
    """Top SKU by revenue"""
    table_data = []
    for line in content:
        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue
        if line.strip():
            table_data.append(line)

    if table_data:
        create_table(elements, table_data, 'top_sku', font_name)

def add_problematic(elements, content, h2_style, normal_style, font_name):
    """Problematic SKU"""
    current_table = []
    table_type = None

    for line in content:
        if 'TOP 5 SKU' in line:
            if current_table:
                create_table(elements, current_table, table_type, font_name)
                current_table = []
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            table_type = 'problematic'
            continue

        if line.strip().startswith('SKU') or line.strip().startswith('-'):
            continue

        if line.strip():
            current_table.append(line)

    if current_table:
        create_table(elements, current_table, table_type, font_name)

def add_data_issues(elements, content, normal_style):
    """Data issues"""
    for line in content:
        if line.strip().startswith(tuple('12345')):
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph(f"<b>{line}</b>", normal_style))
        else:
            elements.append(Paragraph(line, normal_style))

def create_table(elements, data, table_type, font_name):
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

def main():
    console_path = Path("weekly_report_w52_console.txt")
    pdf_path = Path("Weekly_Sales_Report_W52_2025.pdf")

    if not console_path.exists():
        print(f"Console output nenalezen: {console_path}")
        return

    create_pdf_report(console_path, pdf_path)

if __name__ == '__main__':
    main()
