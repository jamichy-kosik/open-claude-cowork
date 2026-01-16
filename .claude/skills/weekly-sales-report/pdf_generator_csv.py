#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF generátor pro Weekly Sales Report - načítá data z CSV souborů
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import pandas as pd
import os
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def create_beautiful_pdf(console_output_path, pdf_output_path):
    """
    Vytvoří PDF z CSV souborů místo parsování textu
    """
    # Získej složku kde jsou CSV soubory (stejná jako console output)
    csv_dir = os.path.dirname(console_output_path) if os.path.dirname(console_output_path) else '.'
    
    # Register fonts
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
        font_name = 'Arial'
        font_name_bold = 'Arial-Bold'
        print("[OK] Arial fonty nacteny pro ceskou diakritiku")
    except:
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
        print("[WARNING] Pouzije se Helvetica")

    # Create PDF
    doc = SimpleDocTemplate(str(pdf_output_path), pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=50, bottomMargin=40)

    elements = []
    styles = getSampleStyleSheet()

    # Colors
    COLOR_PRIMARY = colors.HexColor('#3498db')
    COLOR_SUCCESS = colors.HexColor('#27ae60')
    COLOR_DANGER = colors.HexColor('#e74c3c')
    COLOR_PURPLE = colors.HexColor('#9b59b6')
    COLOR_ORANGE = colors.HexColor('#e67e22')
    COLOR_DARK = colors.HexColor('#2c3e50')
    COLOR_LIGHT_BG = colors.HexColor('#ecf0f1')
    COLOR_ALT_ROW = colors.HexColor('#f8f9fa')

    # Styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
        fontName=font_name_bold, fontSize=24, textColor=COLOR_DARK,
        spaceAfter=8, alignment=1, leading=28)
    
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontName=font_name, fontSize=12, textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=30, alignment=1)
    
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
        fontName=font_name_bold, fontSize=13, textColor=COLOR_DARK,
        spaceAfter=10, spaceBefore=12)
    
    section_style = ParagraphStyle('Section', parent=styles['Heading1'],
        fontName=font_name_bold, fontSize=14, textColor=colors.white,
        leftIndent=0)

    # Header
    elements.append(Paragraph("Weekly Sales Report", title_style))
    elements.append(Paragraph("Košík.cz", subtitle_style))
    
    report_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    date_style = ParagraphStyle('Date', parent=styles['Normal'], 
                               fontName=font_name, fontSize=9, 
                               textColor=colors.HexColor('#95a5a6'), alignment=1)
    elements.append(Paragraph(f"Vygenerováno: {report_date}", date_style))
    elements.append(Spacer(1, 0.3*inch))

    # Načti data pro Executive Summary
    try:
        # Načti CSV soubory
        df_l1 = pd.read_csv(os.path.join(csv_dir, 'output_l1.csv'))
        df_l2 = pd.read_csv(os.path.join(csv_dir, 'output_l2.csv'))
        df_exceeders = pd.read_csv(os.path.join(csv_dir, 'output_exceeders.csv'))
        df_underperf = pd.read_csv(os.path.join(csv_dir, 'output_underperformers.csv'))
        df_problems = pd.read_csv(os.path.join(csv_dir, 'output_problems.csv'))
        
        # Parsuj základní metriky z console outputu
        with open(console_output_path, 'r', encoding='utf-8') as f:
            console_lines = f.readlines()
        
        week = total_revenue = total_gm1 = sku_sold = gm1_negative = None
        for line in console_lines:
            if 'Week:' in line:
                week = line.split(':', 1)[1].strip()
            elif 'Total Revenue:' in line:
                total_revenue = line.split(':', 1)[1].strip()
            elif 'Total GM1:' in line:
                total_gm1 = line.split(':', 1)[1].strip()
            elif 'SKU sold:' in line:
                sku_sold = line.split(':', 1)[1].strip()
            elif 'GM1 < 0:' in line:
                gm1_negative = line.split(':', 1)[1].strip()
        
        # Vygeneruj plný executive summary
        add_section_header(elements, "EXECUTIVE SUMMARY", COLOR_PRIMARY, section_style)
        add_executive_summary_content(elements, week, total_revenue, total_gm1, sku_sold, gm1_negative,
                                     df_l1, df_l2, df_exceeders, df_underperf, df_problems,
                                     font_name, font_name_bold)
        elements.append(Spacer(1, 0.25*inch))
        
    except Exception as e:
        print(f"Varování: Nepodařilo se vygenerovat executive summary: {e}")
        import traceback
        traceback.print_exc()

    # Kategorie L1
    try:
        df_l1 = pd.read_csv(os.path.join(csv_dir, 'output_l1.csv'))
        add_section_header(elements, "KATEGORIE L1 - TOP 15", COLOR_PURPLE, section_style)
        
        # Přidej koláčový graf
        pie_chart_path = create_pie_chart(df_l1.head(15), csv_dir)
        if pie_chart_path:
            img = Image(pie_chart_path, width=5*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.15*inch))
        
        add_dataframe_table(elements, df_l1.head(15), 'L1', font_name, font_name_bold,
                          COLOR_PURPLE, COLOR_LIGHT_BG, COLOR_ALT_ROW)
        elements.append(Spacer(1, 0.25*inch))
    except Exception as e:
        print(f"Varování: Nepodařilo se načíst L1: {e}")

    # Kategorie L2
    try:
        df_l2 = pd.read_csv(os.path.join(csv_dir, 'output_l2.csv'))
        add_section_header(elements, "KATEGORIE L2 - TOP 10", COLOR_PURPLE, section_style)
        add_dataframe_table(elements, df_l2.head(10), 'L2', font_name, font_name_bold,
                          COLOR_PURPLE, COLOR_LIGHT_BG, COLOR_ALT_ROW)
        elements.append(Spacer(1, 0.25*inch))
    except Exception as e:
        print(f"Varování: Nepodařilo se načíst L2: {e}")

    # Services
    try:
        df_services = pd.read_csv(os.path.join(csv_dir, 'output_services.csv'))
        add_section_header(elements, "SERVICES BREAKDOWN", colors.HexColor('#16a085'), section_style)
        add_dataframe_table(elements, df_services, 'services', font_name, font_name_bold,
                          colors.HexColor('#16a085'), COLOR_LIGHT_BG, COLOR_ALT_ROW)
        elements.append(Spacer(1, 0.25*inch))
    except Exception as e:
        print(f"Varování: Nepodařilo se načíst services: {e}")

    # TOP LISTY WoW
    add_section_header(elements, "TOP LISTY WoW", COLOR_ORANGE, section_style)
    
    # Exceeders
    try:
        df_exceeders = pd.read_csv(os.path.join(csv_dir, 'output_exceeders.csv'))
        elements.append(Paragraph("TOP 10 Exceeders (WoW Revenue vzrostl > 10%)", h2_style))
        add_dataframe_table(elements, df_exceeders.head(10), 'exceeders', font_name, font_name_bold,
                          COLOR_SUCCESS, COLOR_LIGHT_BG, COLOR_ALT_ROW)
        elements.append(Spacer(1, 0.15*inch))
    except Exception as e:
        print(f"Varování: Nepodařilo se načíst exceeders: {e}")

    # Underperformers
    try:
        df_underperf = pd.read_csv(os.path.join(csv_dir, 'output_underperformers.csv'))
        elements.append(Paragraph("TOP 10 Underperformers (WoW Revenue poklesl > 10%)", h2_style))
        add_dataframe_table(elements, df_underperf.head(10), 'underperformers', font_name, font_name_bold,
                          COLOR_DANGER, COLOR_LIGHT_BG, COLOR_ALT_ROW)
        elements.append(Spacer(1, 0.25*inch))
    except Exception as e:
        print(f"Varování: Nepodařilo se načíst underperformers: {e}")

    # TOP SKU
    try:
        df_top_sku = pd.read_csv(os.path.join(csv_dir, 'output_top_sku.csv'))
        add_section_header(elements, "TOP 10 SKU dle Revenue", COLOR_DARK, section_style)
        add_dataframe_table(elements, df_top_sku.head(10), 'top_sku', font_name, font_name_bold,
                          COLOR_DARK, COLOR_LIGHT_BG, COLOR_ALT_ROW)
    except Exception as e:
        print(f"Varování: Nepodařilo se načíst top SKU: {e}")

    # Build PDF
    doc.build(elements)
    print(f"[OK] PDF vytvoreno z CSV souboru: {pdf_output_path}")


def create_pie_chart(df_l1, output_dir):
    """Vytvoří koláčový graf L1 kategorií podle Revenue"""
    try:
        # Příprava dat
        if df_l1.empty or 'Revenue' not in df_l1.columns:
            return None
        
        # Vezmi top 10 kategorií + agreguj zbytek jako "Ostatní"
        top_n = 10
        if len(df_l1) > top_n:
            top_categories = df_l1.head(top_n).copy()
            others_revenue = df_l1.iloc[top_n:]['Revenue'].sum()
            if others_revenue > 0:
                others_row = pd.DataFrame({
                    'L1': ['Ostatní'],
                    'Revenue': [others_revenue]
                })
                chart_data = pd.concat([top_categories[['L1', 'Revenue']], others_row], ignore_index=True)
            else:
                chart_data = top_categories[['L1', 'Revenue']]
        else:
            chart_data = df_l1[['L1', 'Revenue']].copy()
        
        # Vytvoř graf
        plt.figure(figsize=(8, 6))
        
        # Barvy - moderní paleta
        colors_list = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
                      '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085', '#7f8c8d']
        
        # Koláčový graf
        wedges, texts, autotexts = plt.pie(
            chart_data['Revenue'],
            labels=chart_data['L1'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_list[:len(chart_data)],
            textprops={'fontsize': 9, 'weight': 'bold'}
        )
        
        # Styling
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
        
        plt.title('Rozdělení Revenue podle L1 kategorií', fontsize=14, weight='bold', pad=20)
        plt.axis('equal')
        
        # Uložení
        chart_path = os.path.join(output_dir, 'l1_pie_chart.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"[OK] Koláčový graf vytvořen: {chart_path}")
        return chart_path
        
    except Exception as e:
        print(f"[WARNING] Nepodařilo se vytvořit koláčový graf: {e}")
        import traceback
        traceback.print_exc()
        return None


def add_executive_summary_content(elements, week, total_revenue, total_gm1, sku_sold, gm1_negative,
                                  df_l1, df_l2, df_exceeders, df_underperf, df_problems,
                                  font_name, font_name_bold):
    """Generuje plný executive summary podle specifikace"""
    
    normal_style = ParagraphStyle('SummaryNormal', fontName=font_name, fontSize=10, leading=16, 
                                  alignment=4, spaceAfter=6)  # 4 = justify
    bold_style = ParagraphStyle('SummaryBold', fontName=font_name_bold, fontSize=10, leading=16,
                               alignment=4, spaceAfter=6)
    
    # 1. Úvodní věta - Prodej Košíku
    intro = f"Prodej Košíku {week}: {total_revenue}, GM1 {total_gm1} "
    if 'Revenue_prev' in df_l1.columns and not df_l1.empty:
        total_prev = df_l1['Revenue_prev'].sum()
        total_curr = df_l1['Revenue'].sum()
        wow_change = ((total_curr - total_prev) / total_prev * 100) if total_prev > 0 else 0
        intro += f"(WoW {wow_change:+.1f}%, {sku_sold} SKU)."
    else:
        intro += f"({sku_sold} SKU)."
    
    elements.append(Paragraph(intro, bold_style))
    
    # 2. Top 3 L1 kategorie
    if not df_l1.empty and len(df_l1) >= 3:
        top3_l1 = df_l1.head(3)
        l1_text = "Top 3 L1 kategorie: "
        l1_parts = []
        for idx, row in top3_l1.iterrows():
            name = row['L1']
            rev = f"{int(row['Revenue']):,}".replace(',', ' ')
            share = row.get('share', 0)
            wow = f"{row['WoW_pct']:+.1f}%" if 'WoW_pct' in row and pd.notna(row['WoW_pct']) else ""
            
            if wow:
                l1_parts.append(f"{name} {rev} Kč (share {share:.1f}%, WoW {wow})")
            else:
                l1_parts.append(f"{name} {rev} Kč (share {share:.1f}%)")
        
        l1_text += "; ".join(l1_parts) + "."
        elements.append(Paragraph(l1_text, normal_style))
    
    # 3. Top 5 L2 kategorie
    if not df_l2.empty and len(df_l2) >= 5:
        top5_l2 = df_l2.head(5)
        l2_text = "Top 5 L2 kategorie: "
        l2_parts = []
        for idx, row in top5_l2.iterrows():
            name = row['L2']
            rev = f"{int(row['Revenue']):,}".replace(',', ' ')
            share = row.get('share', 0)
            
            l2_parts.append(f"{name} {rev} Kč (share {share:.1f}%)")
        
        l2_text += "; ".join(l2_parts) + "."
        elements.append(Paragraph(l2_text, normal_style))
    
    # 4. Top 3-5 driverů růstu (exceeders)
    if not df_exceeders.empty:
        # Vyfiltruj extrémní hodnoty (WoW > 1000% jsou pravděpodobně data issues)
        df_exc_filtered = df_exceeders[df_exceeders['WoW_pct'] < 1000].head(5)
        
        if len(df_exc_filtered) > 0:
            drivers_text = f"Hlavní drivery růstu WoW: "
            driver_parts = []
            for idx, row in df_exc_filtered.head(3).iterrows():
                sku = row['SKU']
                name = row['Product_Name'][:40] + '...' if len(row['Product_Name']) > 40 else row['Product_Name']
                delta = f"{int(row['Revenue_delta']):,}".replace(',', ' ')
                wow = row['WoW_pct']
                
                driver_parts.append(f"{name} (SKU {sku}) +{delta} Kč ({wow:+.1f}% WoW)")
            
            drivers_text += "; ".join(driver_parts) + "."
            elements.append(Paragraph(drivers_text, normal_style))
    
    # 5. Top 3-5 problémů (underperformers + problematic SKU)
    problems_text = "Hlavní problémy: "
    problem_parts = []
    
    # Underperformers
    if not df_underperf.empty:
        for idx, row in df_underperf.head(2).iterrows():
            sku = row['SKU']
            name = row['Product_Name'][:40] + '...' if len(row['Product_Name']) > 40 else row['Product_Name']
            delta = f"{int(row['Revenue_delta']):,}".replace(',', ' ')
            wow = row['WoW_pct']
            
            problem_parts.append(f"{name} (SKU {sku}) {delta} Kč ({wow:.1f}% WoW)")
    
    # GM1 < 0 problém
    if gm1_negative:
        problem_parts.append(gm1_negative)
    
    # Problematic SKU
    if not df_problems.empty and len(df_problems) > 0:
        prob_row = df_problems.iloc[0]
        if 'SKU' in prob_row and 'Product_Name' in prob_row and 'GM1' in prob_row:
            sku = prob_row['SKU']
            name = prob_row['Product_Name'][:35] + '...' if len(prob_row['Product_Name']) > 35 else prob_row['Product_Name']
            gm1 = f"{int(prob_row['GM1']):,}".replace(',', ' ')
            problem_parts.append(f"záporné GM1 u {name} (SKU {sku}, dopad {gm1} Kč)")
    
    if problem_parts:
        problems_text += "; ".join(problem_parts[:5]) + "."
        elements.append(Paragraph(problems_text, normal_style))
    
    # 6. Doporučené akce (3-5)
    actions_text = "Doporučené akce: "
    actions = []
    
    # Akce 1: Focus na top performery
    if not df_l1.empty:
        top_l1 = df_l1.iloc[0]
        if 'WoW_pct' in top_l1 and pd.notna(top_l1['WoW_pct']) and top_l1['WoW_pct'] > 5:
            actions.append(f"udržet momentum u {top_l1['L1']} (+{top_l1['WoW_pct']:.1f}% WoW)")
    
    # Akce 2: Fix problematické kategorie
    if not df_l1.empty:
        for idx, row in df_l1.iterrows():
            if 'WoW_pct' in row and pd.notna(row['WoW_pct']) and row['WoW_pct'] < -10:
                actions.append(f"analyzovat pokles u {row['L1']} ({row['WoW_pct']:.1f}% WoW)")
                break
    
    # Akce 3: Fix GM1 < 0
    if gm1_negative and '(' in gm1_negative:
        actions.append("opravit pricing u SKU s GM1 < 0")
    
    # Akce 4: Optimalizace top SKU
    if not df_exceeders.empty:
        actions.append("kontrolovat dostupnost top rostoucích SKU")
    
    # Akce 5: Data quality
    if not df_exceeders.empty:
        extreme_count = len(df_exceeders[df_exceeders['WoW_pct'] > 500])
        if extreme_count > 0:
            actions.append(f"ověřit data kvalitu u {extreme_count} SKU s extrémním WoW% (možná missing prev data)")
    
    if actions:
        actions_text += "; ".join(actions[:5]) + "."
        elements.append(Paragraph(actions_text, normal_style))


def add_section_header(elements, title, bg_color, section_style):
    """Přidá sekční hlavičku"""
    section_para = Paragraph(f"<b>{title}</b>", section_style)
    header_table = Table([[section_para]], colWidths=[7.3*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.15*inch))


def add_dataframe_table(elements, df, table_type, font_name, font_name_bold,
                       header_color, bg_color, alt_row_color):
    """Vytvoří tabulku z pandas DataFrame"""
    if df.empty:
        return
    
    # Vyber sloupce podle typu tabulky
    if table_type in ['L1', 'L2', 'L3']:
        # Chceme: název kategorie, Revenue, GM1, Qty, SKU count, WoW%
        cols_to_show = []
        for col in [table_type, 'Revenue', 'GM1', 'Qty', 'SKU', 'WoW_pct']:
            if col in df.columns:
                cols_to_show.append(col)
        df = df[cols_to_show]
    elif table_type in ['exceeders', 'underperformers']:
        # SKU, Product_Name, Revenue, Qty, WoW_pct
        cols_to_show = []
        for col in ['SKU', 'Product_Name', 'Revenue', 'Qty', 'WoW_pct']:
            if col in df.columns:
                cols_to_show.append(col)
        df = df[cols_to_show]
    elif table_type == 'services':
        cols_to_show = []
        for col in ['Services', 'Revenue', 'GM1', 'Qty', 'SKU']:
            if col in df.columns:
                cols_to_show.append(col)
        df = df[cols_to_show]
    elif table_type == 'top_sku':
        cols_to_show = []
        for col in ['SKU', 'Product_Name', 'Revenue', 'GM1', 'Qty']:
            if col in df.columns:
                cols_to_show.append(col)
        df = df[cols_to_show]
    
    # Formátuj čísla
    df_formatted = df.copy()
    for col in df_formatted.columns:
        if col in ['Revenue', 'GM1', 'Revenue_prev', 'Revenue_delta']:
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{int(x):,}".replace(',', ' ') if pd.notna(x) and abs(x) >= 1 else str(x))
        elif col in ['Qty', 'SKU']:
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{int(x):,}".replace(',', ' ') if pd.notna(x) else str(x))
        elif col == 'WoW_pct':
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
        elif col == 'share':
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
        elif col == 'GM1_pct':
            df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
        elif col == 'Product_Name':
            # Zkrať dlouhé názvy
            df_formatted[col] = df_formatted[col].apply(lambda x: x[:50] + '...' if isinstance(x, str) and len(x) > 50 else x)
    
    # Vytvoř data pro tabulku
    table_data = [df_formatted.columns.tolist()] + df_formatted.values.tolist()
    
    # Převeď na string a wrap v Paragraph
    cell_style = ParagraphStyle('Cell', fontName=font_name, fontSize=8, leading=10, alignment=1)
    first_col_style = ParagraphStyle('FirstCol', fontName=font_name, fontSize=8, leading=10, alignment=0)
    header_cell_style = ParagraphStyle('HeaderCell', fontName=font_name_bold, fontSize=9, leading=11, textColor=colors.white, alignment=1)
    
    wrapped_data = []
    for idx, row in enumerate(table_data):
        wrapped_row = []
        for col_idx, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else ''
            if idx == 0:
                # Header
                wrapped_row.append(Paragraph(cell_str, header_cell_style))
            else:
                # Data - první sloupec vlevo, ostatní vpravo
                if col_idx == 0 or col_idx == 1:  # SKU + názvy vlevo
                    wrapped_row.append(Paragraph(cell_str, first_col_style))
                else:
                    wrapped_row.append(Paragraph(cell_str, cell_style))
        wrapped_data.append(wrapped_row)
    
    # Šířky sloupců
    total_width = 7.3 * inch
    num_cols = len(wrapped_data[0])
    
    if table_type in ['exceeders', 'underperformers']:
        # SKU 10%, Název 40%, ostatní rovnoměrně
        col_widths = [total_width * 0.10, total_width * 0.40] + [total_width * 0.50 / max(1, num_cols - 2)] * (num_cols - 2)
    elif table_type in ['L1', 'L2', 'L3']:
        # Název 35%, ostatní rovnoměrně
        col_widths = [total_width * 0.35] + [total_width * 0.65 / max(1, num_cols - 1)] * (num_cols - 1)
    elif table_type == 'top_sku':
        # SKU 10%, Název 35%, ostatní rovnoměrně
        col_widths = [total_width * 0.10, total_width * 0.35] + [total_width * 0.55 / max(1, num_cols - 2)] * (num_cols - 2)
    else:
        col_widths = [total_width / num_cols] * num_cols
    
    # Vytvoř tabulku
    table = Table(wrapped_data, colWidths=col_widths, repeatRows=1)
    
    # Styling
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('PADDING', (0, 0), (-1, 0), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.white),
        ('PADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#95a5a6')),
        ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor('#bdc3c7')),
    ]
    
    # Alternující barvy řádků
    for i in range(1, len(wrapped_data)):
        if i % 2 == 0:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), alt_row_color))
        else:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), bg_color))
    
    table.setStyle(TableStyle(style_commands))
    elements.append(table)
    elements.append(Spacer(1, 0.12*inch))


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        create_beautiful_pdf(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python pdf_generator_csv.py <console_output.txt> <output.pdf>")
