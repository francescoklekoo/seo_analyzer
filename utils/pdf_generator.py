"""
Generatore di report PDF per l'analisi SEO
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, red, green, orange, blue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart # Not used, but good to have
from reportlab.graphics import renderPDF
from reportlab.lib import colors
import matplotlib
matplotlib.use('Agg') # Set backend BEFORE importing pyplot
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional # Added Tuple and Optional
import os

from config import (
    PDF_CONFIG, SEO_CONFIG, PERFORMANCE_CONFIG, # Existing partial imports
    CATEGORY_OCM, CATEGORY_SEO_AUDIT, AUDIT_CHECKS_CONFIG, PDF_ISSUE_DESCRIPTIONS,
    # PDF_ISSUE_TYPE_LABELS # This is now replaced by AUDIT_CHECKS_CONFIG and PDF_ISSUE_DESCRIPTIONS
)
# Make sure other necessary constants from config like FONT_FAMILY etc. are implicitly covered or explicitly imported if needed.
# For now, assuming PDF_CONFIG covers nested color/font needs.


class PDFGenerator:
    """
    Classe per generare report PDF professionali
    """
    
    def __init__(self, analysis_results: Dict, domain: str):
        self.analysis_results = analysis_results
        self.domain = domain
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        FONT_FAMILY = 'Helvetica'
        FONT_FAMILY_BOLD = 'Helvetica-Bold'
        COLOR_PRIMARY = '#005A9C'
        COLOR_TEXT_PRIMARY = '#222222'
        COLOR_TEXT_SECONDARY = '#555555'
        COLOR_SUCCESS = '#28A745'
        COLOR_WARNING = '#FFC107'
        COLOR_ERROR = '#DC3545'
        FONT_SIZE_TITLE = 20
        FONT_SIZE_HEADING = 15
        FONT_SIZE_BODY = 10
        FONT_SIZE_SMALL = 8

        style_name = 'CustomTitle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_TITLE, leading=FONT_SIZE_TITLE * 1.2, alignment=TA_CENTER, textColor=HexColor(COLOR_PRIMARY), spaceAfter=12))
        style_name = 'CustomSubtitle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_HEADING, leading=FONT_SIZE_HEADING * 1.2, alignment=TA_CENTER, textColor=HexColor(COLOR_TEXT_SECONDARY), spaceAfter=6))
        style_name = 'SectionHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_HEADING, leading=FONT_SIZE_HEADING * 1.2, spaceAfter=8, textColor=HexColor(COLOR_PRIMARY)))
        style_name = 'SectionSubHeadingStyle' # New Style
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=12, leading=12 * 1.2, spaceAfter=6, textColor=HexColor(COLOR_TEXT_PRIMARY)))
        style_name = 'SpecificProblemHeadingStyle' # New Style for specific problem types in weaknesses
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_BODY, leading=FONT_SIZE_BODY * 1.2, spaceBefore=4, spaceAfter=2, leftIndent=10, textColor=HexColor(COLOR_TEXT_PRIMARY)))
        style_name = 'IssueDetailItemStyle' # New Style for issue details under specific problems
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], leftIndent=20, spaceAfter=2, bulletIndent=10)) # Smaller leftIndent than ListItem

        # Styles for the Weaknesses Table
        style_name = 'TableMacroCategoryStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_BODY, leading=FONT_SIZE_BODY * 1.2, textColor=HexColor(COLOR_TEXT_PRIMARY), spaceBefore=6, spaceAfter=4))
        style_name = 'TableSpecificProblemStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_BODY, textColor=HexColor(COLOR_TEXT_SECONDARY), leftIndent=0, spaceAfter=2)) # Indent managed by cell padding
        style_name = 'TableDetailURLStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_PRIMARY), leftIndent=0))
        style_name = 'TableDetailStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_SECONDARY), leftIndent=0))
        style_name = 'TableRecommendationStyle' # New style for recommendations in table
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_SECONDARY), leftIndent=5, spaceBefore=2, spaceAfter=2, bulletIndent=0, firstLineIndent=0))


        style_name = 'BodyText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_BODY, leading=FONT_SIZE_BODY * 1.4, spaceAfter=6, textColor=HexColor(COLOR_TEXT_PRIMARY)))
        style_name = 'ListItem'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], leftIndent=30, spaceAfter=4, bulletIndent=20)) # Increased indent for general list items
        style_name = 'SmallText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, leading=FONT_SIZE_SMALL * 1.2, alignment=TA_CENTER, textColor=HexColor(COLOR_TEXT_SECONDARY)))
        score_parent_style = self.styles['BodyText']
        style_name = 'ScoreExcellent'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_SUCCESS), fontName=FONT_FAMILY_BOLD))
        style_name = 'ScoreGood'
        if style_name not in self.styles:
             self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_PRIMARY), fontName=FONT_FAMILY_BOLD))
        style_name = 'ScoreWarning'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_WARNING), fontName=FONT_FAMILY_BOLD))
        style_name = 'ScoreCritical'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_ERROR), fontName=FONT_FAMILY_BOLD))

        # Styles for new Executive Summary
        style_name = 'OCMSectionHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['SectionHeading'], spaceBefore=12, textColor=HexColor(PDF_CONFIG['colors'].get('primary', '#336699'))))
        style_name = 'SEOAuditSectionHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['SectionHeading'], spaceBefore=12, textColor=HexColor(PDF_CONFIG['colors'].get('secondary_dark', '#556677')))) # Example different color

        style_name = 'ErrorSubHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=11, leading=11 * 1.2, spaceBefore=8, spaceAfter=4, textColor=HexColor(COLOR_ERROR)))
        style_name = 'WarningSubHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=11, leading=11 * 1.2, spaceBefore=8, spaceAfter=4, textColor=HexColor(COLOR_WARNING))) # Ensure COLOR_WARNING is defined
        style_name = 'NoticeSubHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=11, leading=11 * 1.2, spaceBefore=8, spaceAfter=4, textColor=HexColor(COLOR_TEXT_SECONDARY))) # Example color for Notice

        style_name = 'IssueDescriptionText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], leftIndent=10, spaceBefore=2, spaceAfter=4, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_SECONDARY)))
        
    def _add_header(self):
        self.story.append(Paragraph("Report di Audit del Sito", self.styles['CustomTitle'])) # First line
        self.story.append(Paragraph(self.domain, self.styles['CustomSubtitle']))      # Second line (domain name)
        self.story.append(Spacer(1, 0.2 * inch))
        current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.story.append(Paragraph(f"Generato il: {current_datetime}", self.styles['SmallText']))
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_chart_and_counts_section(self):
        section_flowables = []

        # Get Chart
        chart_image = self._get_site_health_chart_flowable()
        if chart_image:
            section_flowables.append(chart_image)
            section_flowables.append(Spacer(1, 0.1 * inch)) # Reduced spacer after chart

        # --- New Categorized Summary Boxes ---
        categorized_issues = self.analysis_results.get('categorized_issues', {})
        ocm_errors_count = len(categorized_issues.get(CATEGORY_OCM, {}).get('ERROR', []))
        ocm_warnings_count = len(categorized_issues.get(CATEGORY_OCM, {}).get('WARNING', []))
        ocm_notices_count = len(categorized_issues.get(CATEGORY_OCM, {}).get('NOTICE', []))

        seo_errors_count = len(categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get('ERROR', []))
        seo_warnings_count = len(categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get('WARNING', []))
        seo_notices_count = len(categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get('NOTICE', []))

        # Define colors for boxes
        COLOR_RED_BOX = colors.HexColor(PDF_CONFIG['colors'].get('error', '#DC3545'))
        COLOR_ORANGE_BOX = colors.HexColor(PDF_CONFIG['colors'].get('warning', '#FFC107'))
        COLOR_BLUE_BOX = colors.HexColor(PDF_CONFIG['colors'].get('info', '#17A2B8')) # Using info from PDF_CONFIG or a default

        # Styles for text in boxes
        count_style = ParagraphStyle(
            name='BoxCountStyle',
            fontSize=20, # Increased font size for count
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER,
            leading=22
        )
        label_style = ParagraphStyle(
            name='BoxLabelStyle',
            fontSize=9, # Standard label size
            fontName='Helvetica',
            textColor=colors.white,
            alignment=TA_CENTER,
            leading=10,
            spaceBefore=4 # Add a bit of space between count and label
        )

        # Content for OCM boxes
        ocm_error_content = [Paragraph(f"{ocm_errors_count}", count_style), Paragraph("Errori OCM", label_style)]
        ocm_warning_content = [Paragraph(f"{ocm_warnings_count}", count_style), Paragraph("Avvert. OCM", label_style)] # Abbreviated for space
        ocm_notice_content = [Paragraph(f"{ocm_notices_count}", count_style), Paragraph("Avvisi OCM", label_style)]

        # Content for SEO Audit boxes
        seo_error_content = [Paragraph(f"{seo_errors_count}", count_style), Paragraph("Errori SEO", label_style)]
        seo_warning_content = [Paragraph(f"{seo_warnings_count}", count_style), Paragraph("Avvert. SEO", label_style)] # Abbreviated for space
        seo_notice_content = [Paragraph(f"{seo_notices_count}", count_style), Paragraph("Avvisi SEO", label_style)]

        # Calculate column width for 3 boxes per row
        page_content_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        box_col_width = (page_content_width - 2 * (0.1 * inch)) / 3 # Small gap (0.1 inch) on each side of the middle box, effectively spacing between boxes

        # OCM Row Table
        row1_data = [ocm_error_content, ocm_warning_content, ocm_notice_content]
        table_row1 = Table([row1_data], colWidths=[box_col_width, box_col_width, box_col_width], rowHeights=[0.8*inch]) # Adjusted height
        table_row1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), COLOR_RED_BOX),
            ('BACKGROUND', (1,0), (1,0), COLOR_ORANGE_BOX),
            ('BACKGROUND', (2,0), (2,0), COLOR_BLUE_BOX),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10), # Increased padding
            ('BOTTOMPADDING', (0,0), (-1,-1), 10), # Increased padding
            # ('BOX', (0,0), (-1,-1), 0.5, colors.darkgrey), # Optional: border around all boxes in the row
            # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey) # Optional: inner lines
        ]))
        section_flowables.append(table_row1)
        section_flowables.append(Spacer(1, 0.15 * inch)) # Space between the two rows of boxes

        # SEO Audit Row Table
        row2_data = [seo_error_content, seo_warning_content, seo_notice_content]
        table_row2 = Table([row2_data], colWidths=[box_col_width, box_col_width, box_col_width], rowHeights=[0.8*inch]) # Adjusted height
        table_row2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), COLOR_RED_BOX),
            ('BACKGROUND', (1,0), (1,0), COLOR_ORANGE_BOX),
            ('BACKGROUND', (2,0), (2,0), COLOR_BLUE_BOX),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10), # Increased padding
            ('BOTTOMPADDING', (0,0), (-1,-1), 10), # Increased padding
        ]))
        section_flowables.append(table_row2)
        # --- End of New Categorized Summary Boxes ---


        # The old summary box code is removed as per plan.
        # old_color_error_hex = PDF_CONFIG['colors'].get('error', '#DC3545')
        # old_color_warning_hex = PDF_CONFIG['colors'].get('warning', '#FFC107')
        # old_color_notice_hex = PDF_CONFIG['colors'].get('info', PDF_CONFIG['colors'].get('secondary', '#17A2B8'))
        # ... (rest of old code was here) ...
        # issue_counts_table.setStyle(counts_table_style)
        # section_flowables.append(issue_counts_table)

        if section_flowables:
            self.story.append(KeepTogether(section_flowables))
            self.story.append(Spacer(1, 0.3 * inch)) # Spacer after the whole section (chart + boxes)

    def _add_executive_summary(self):
        flowables = []
        flowables.append(Paragraph("Riassunto Esecutivo", self.styles['SectionHeading'])) # Already Italian
        flowables.append(Spacer(1, 0.2 * inch))

        overall_score = self.analysis_results.get('overall_score', 0)
        evaluation = self._get_evaluation_text(overall_score)

        categorized_issues_data = self.analysis_results.get('categorized_issues', {})
        num_errors = sum(len(lst) for cat in categorized_issues_data.values() for sev, lst in cat.items() if sev == 'ERROR')
        num_warnings = sum(len(lst) for cat in categorized_issues_data.values() for sev, lst in cat.items() if sev == 'WARNING')
        num_notices = sum(len(lst) for cat in categorized_issues_data.values() for sev, lst in cat.items() if sev == 'NOTICE')

        issue_parts = []
        if num_errors > 0: issue_parts.append(f"<b>{num_errors}</b> Errori") # Already Italian
        if num_warnings > 0: issue_parts.append(f"<b>{num_warnings}</b> Avvertimenti") # Already Italian
        if num_notices > 0: issue_parts.append(f"<b>{num_notices}</b> Avvisi") # Already Italian

        issues_string = ""
        if not issue_parts:
            issues_string = "non rilevando problemi significativi" # Already Italian
        elif len(issue_parts) == 1:
            issues_string = f"identificando {issue_parts[0]}" # Already Italian
        elif len(issue_parts) == 2:
            issues_string = f"identificando {issue_parts[0]} e {issue_parts[1]}" # Already Italian
        else:
            issues_string = f"identificando {issue_parts[0]}, {issue_parts[1]} e {issue_parts[2]}" # Already Italian

        total_pages_analyzed = self.analysis_results.get('summary', {}).get('total_pages_analyzed', len(self.analysis_results.get('pages_data', [])))

        summary_text = f"""L'analisi SEO del sito <b>{self.domain}</b> ha rivelato un punteggio complessivo di <font color="{self._get_score_color_hex(overall_score)}"><b>{overall_score}/100</b></font>. Valutazione: <b>{evaluation}</b>. Sono state analizzate <b>{total_pages_analyzed}</b> pagine, {issues_string}.""" # Already Italian

        summary_paragraph = Paragraph(summary_text, self.styles['BodyText'])
        flowables.append(summary_paragraph)
        flowables.append(Spacer(1, 0.2 * inch))

        categorized_issues = self.analysis_results.get('categorized_issues', {})

        if CATEGORY_OCM in categorized_issues:
            flowables.append(Paragraph(CATEGORY_OCM, self.styles['OCMSectionHeading']))
            for severity in ['ERROR', 'WARNING', 'NOTICE']: # ERROR, WARNING, NOTICE will be translated to Errori, Avvertimenti, Avvisi
                issues_list = categorized_issues.get(CATEGORY_OCM, {}).get(severity, [])
                if issues_list:
                    severity_style_name = f"{severity.capitalize()}SubHeading"
                    # Translate severity names for display
                    severity_display_name = {
                        'ERROR': 'Errori', 'WARNING': 'Avvertimenti', 'NOTICE': 'Avvisi'
                    }.get(severity, severity.capitalize())
                    flowables.append(Paragraph(f"{severity_display_name} ({len(issues_list)})", self.styles.get(severity_style_name, self.styles['SectionSubHeadingStyle'])))
                    for issue in issues_list:
                        check_config = AUDIT_CHECKS_CONFIG.get(issue['key'], {})
                        description = PDF_ISSUE_DESCRIPTIONS.get(check_config.get('description_key'), "N/D") # N/A to N/D

                        flowables.append(Paragraph(f"<b>{issue.get('label', 'N/D')}</b>", self.styles['BodyText'])) # N/A to N/D
                        if issue.get('url') and issue.get('url') != self.domain :
                            flowables.append(Paragraph(f"URL: {issue['url']}", self.styles['SmallText']))
                        flowables.append(Paragraph(f"Dettagli: {issue.get('details', 'N/D')}", self.styles['SmallText'])) # N/A to N/D
                        flowables.append(Paragraph(f"Impatto SEO: {description}", self.styles['IssueDescriptionText'])) # Already Italian
                        flowables.append(Spacer(1, 0.1 * inch))
            flowables.append(Spacer(1, 0.1 * inch))

        if CATEGORY_SEO_AUDIT in categorized_issues:
            flowables.append(Paragraph(CATEGORY_SEO_AUDIT, self.styles['SEOAuditSectionHeading'])) # Already Italian
            for severity in ['ERROR', 'WARNING', 'NOTICE']: # ERROR, WARNING, NOTICE will be translated
                issues_list = categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get(severity, [])
                if issues_list:
                    severity_style_name = f"{severity.capitalize()}SubHeading"
                    severity_display_name = {
                        'ERROR': 'Errori', 'WARNING': 'Avvertimenti', 'NOTICE': 'Avvisi'
                    }.get(severity, severity.capitalize())
                    flowables.append(Paragraph(f"{severity_display_name} ({len(issues_list)})", self.styles.get(severity_style_name, self.styles['SectionSubHeadingStyle'])))
                    for issue in issues_list:
                        check_config = AUDIT_CHECKS_CONFIG.get(issue['key'], {})
                        description = PDF_ISSUE_DESCRIPTIONS.get(check_config.get('description_key'), "N/D") # N/A to N/D

                        flowables.append(Paragraph(f"<b>{issue.get('label', 'N/D')}</b>", self.styles['BodyText'])) # N/A to N/D
                        if issue.get('url') and issue.get('url') != self.domain:
                            flowables.append(Paragraph(f"URL: {issue['url']}", self.styles['SmallText']))
                        flowables.append(Paragraph(f"Dettagli: {issue.get('details', 'N/D')}", self.styles['SmallText'])) # N/A to N/D
                        flowables.append(Paragraph(f"Impatto SEO: {description}", self.styles['IssueDescriptionText'])) # Already Italian
                        flowables.append(Spacer(1, 0.1 * inch))
            flowables.append(Spacer(1, 0.1 * inch))

        if overall_score >= 80:
            flowables.append(Paragraph("Punti di Forza Generali:", self.styles['SectionSubHeadingStyle'])) # Already Italian
            flowables.append(Paragraph(f"Il punteggio generale di {overall_score}/100 indica una buona performance complessiva.", self.styles['BodyText'])) # Already Italian

        flowables.append(Spacer(1, 0.5 * inch))
        self.story.append(KeepTogether(flowables))

    def _add_score_overview(self):
        flowables = []
        flowables.append(Paragraph("Panoramica dei Punteggi", self.styles['SectionHeading'])) # "Panoramica Punteggi" to "Panoramica dei Punteggi"
        flowables.append(Spacer(1, 0.2 * inch))

        overall_score = self.analysis_results.get('overall_score', 'N/D') # N/A to N/D
        score_text = f"Punteggio SEO Complessivo: {overall_score}/100" # Already Italian
        flowables.append(Paragraph(score_text, self.styles['BodyText']))

        # data = [[Paragraph(h, self.styles['BodyText']) for h in ['Categoria', 'Punteggio', 'Stato']]] # Already Italian
        # categories = {'Title Tags': self.analysis_results['title_analysis']['score'], 'Meta Descriptions': self.analysis_results['meta_description_analysis']['score'], 'Headings': self.analysis_results['headings_analysis']['score'], 'Immagini': self.analysis_results['images_analysis']['score'], 'Contenuto': self.analysis_results['content_analysis']['score'], 'Link Interni': self.analysis_results['links_analysis']['score'], 'Performance': self.analysis_results['performance_analysis']['score'], 'Aspetti Tecnici': self.analysis_results['technical_analysis']['score'], 'SSL': self.analysis_results['ssl_analysis']['score']}
        # The category names 'Title Tags', 'Meta Descriptions' etc. should be translated if this section is uncommented and used.
        # For now, this part is commented out in the original code.
        # Example translations if needed:
        # 'Title Tags': 'Tag Title',
        # 'Meta Descriptions': 'Meta Description',
        # 'Headings': 'Intestazioni',
        # 'Immagini': 'Immagini', # Already Italian
        # 'Contenuto': 'Contenuto', # Already Italian
        # 'Link Interni': 'Link Interni', # Already Italian
        # 'Performance': 'Prestazioni',
        # 'Aspetti Tecnici': 'Aspetti Tecnici', # Already Italian
        # 'SSL': 'SSL' # Already Italian
        # for category, score in categories.items():
        #     status_text = self._get_status_text(score)
        #     data.append([Paragraph(category, self.styles['BodyText']), Paragraph(f"{score}/100", self.styles['BodyText']), Paragraph(status_text, self.styles['BodyText'])])

        # # Calculate available width for full-width table
        # available_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        # # Define relative column widths (e.g., 45% Categoria, 20% Punteggio, 35% Stato)
        # col_widths = [available_width * 0.45, available_width * 0.20, available_width * 0.35]
        # table = Table(data, colWidths=col_widths)

        # COLOR_TABLE_HEADER_BG = PDF_CONFIG['colors'].get('primary_dark', '#004080') # Use from PDF_CONFIG
        # COLOR_TABLE_ROW_ODD = PDF_CONFIG['colors'].get('light_gray_alt', '#F0F4F7') # Use from PDF_CONFIG
        # COLOR_TABLE_ROW_BG_EVEN = PDF_CONFIG['colors'].get('white', '#FFFFFF') # Use from PDF_CONFIG
        # COLOR_BORDER = PDF_CONFIG['colors'].get('border', '#CCCCCC') # Use from PDF_CONFIG
        # FONT_FAMILY_TABLE_HEADER = PDF_CONFIG.get('font_family_bold', 'Helvetica-Bold')
        # FONT_FAMILY_TABLE_BODY = PDF_CONFIG.get('font_family', 'Helvetica')
        # FONT_SIZE_TABLE_HEADER = PDF_CONFIG['font_sizes'].get('small', 9)
        # FONT_SIZE_TABLE_BODY = PDF_CONFIG['font_sizes'].get('small', 9) # Consistent small size
        # COLOR_TEXT_PRIMARY_FOR_TABLE = PDF_CONFIG['colors'].get('text_primary', '#222222')
        # HEADER_OUTLINE_COLOR = colors.HexColor('#FFCC00') # Amber/Yellow
        # NEW_HEADER_BG_COLOR = colors.HexColor('#f5f5f5')

        # score_table_style_cmds = [
            # Header Styling
            # ('BACKGROUND', (0, 0), (-1, 0), NEW_HEADER_BG_COLOR), # New light gray background
            # ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), # Ensure black text
            # ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            # ('FONTNAME', (0, 0), (-1, 0), FONT_FAMILY_TABLE_HEADER),
            # ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_TABLE_HEADER),
            # ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Individual BOX for each header cell for #FFCC00 outline
            # ('BOX', (0,0), (0,0), 1.5, HEADER_OUTLINE_COLOR),
            # ('BOX', (1,0), (1,0), 1.5, HEADER_OUTLINE_COLOR),
            # ('BOX', (2,0), (2,0), 1.5, HEADER_OUTLINE_COLOR),

            # Data Rows Styling
            # ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY_TABLE_BODY),
            # ('FONTSIZE', (0, 1), (-1, -1), FONT_SIZE_TABLE_BODY),
            # ('TEXTCOLOR', (0, 1), (-1, -1), HexColor(COLOR_TEXT_PRIMARY_FOR_TABLE)),
            # ('ALIGN', (0, 1), (-1, -1), 'LEFT'), # Categoria left aligned
            # ('ALIGN', (1, 1), (1, -1), 'CENTER'), # Punteggio center aligned
            # ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Stato left aligned
            # ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            # ('BOTTOMPADDING', (0, 1), (-1, -1), 6), # Adjusted padding for data rows
            # ('TOPPADDING', (0, 1), (-1, -1), 6),   # Adjusted padding for data rows
            # ('BACKGROUND', (0, 1), (-1, -1), HexColor(COLOR_TABLE_ROW_BG_EVEN)), # Default for even data rows
        # ]

        # score_table_style = TableStyle(score_table_style_cmds)

        # Apply odd row striping
        # for i in range(1, len(data)): # Start from 1 to skip header
            # if i % 2 != 0: # Odd rows (1st, 3rd, 5th data row)
                # score_table_style.add('BACKGROUND', (0, i), (-1, i), HexColor(COLOR_TABLE_ROW_BG_ODD))

        # General table grid (applied first, header BOXes will draw over it for header cells)
        # score_table_style.add('GRID', (0,0), (-1,-1), 0.5, HexColor(COLOR_BORDER))
        # Overall table border (can be same as grid or slightly thicker)
        # score_table_style.add('BOX', (0,0), (-1,-1), 1, HexColor(COLOR_BORDER))

        # table.setStyle(score_table_style)
        # flowables.append(table)
        flowables.append(Spacer(1, 0.5 * inch))
        self.story.append(KeepTogether(flowables))

    def _get_site_health_chart_flowable(self):
        """
        Crea un grafico a ciambella (donut chart) che mostra la percentuale di salute del sito,
         suddivisa in Sano, Avvertimenti, e Problemi, con legenda in basso.
        Restituisce l'oggetto Image di ReportLab.
        """
        try:
            # Ensure overall_score is float and defaults to 0 if not found or None
            raw_overall_score = self.analysis_results.get('overall_score')
            if raw_overall_score is None:
                print("WARNING: 'overall_score' not found in analysis_results for chart generation. Defaulting to 0.")
                overall_score = 0.0
            else:
                overall_score = float(raw_overall_score)

            detailed_issues = self.analysis_results.get('detailed_issues', {})
            num_errors = len(detailed_issues.get('errors', []))
            num_warnings = len(detailed_issues.get('warnings', []))

            sano_percentage = overall_score

            # Calculate the portion that is NOT healthy
            non_sano_percentage = 100.0 - sano_percentage

            # Initialize problemi and avvertimenti percentages
            problemi_percentage = 0.0
            avvertimenti_percentage = 0.0

            total_critical_issues = num_errors + num_warnings

            if non_sano_percentage > 0:
                if total_critical_issues > 0:
                    problemi_percentage = (num_errors / total_critical_issues) * non_sano_percentage
                    avvertimenti_percentage = (num_warnings / total_critical_issues) * non_sano_percentage
                else:
                    # If overall_score < 100 but no errors/warnings, attribute the non_sano part to "Problemi" by default.
                    problemi_percentage = non_sano_percentage
            else:
                # if sano_percentage is 100 (or more, though score should be capped at 100),
                # then non_sano is 0 or negative, so problemi and avvertimenti are 0.
                pass

            # Normalize percentages to ensure they sum to 100 due to potential float precision issues
            # and ensure segments are not negative.
            sano_percentage = max(0.0, sano_percentage)
            problemi_percentage = max(0.0, problemi_percentage)
            avvertimenti_percentage = max(0.0, avvertimenti_percentage)

            # Recalculate total based on potentially capped values
            # This step is crucial if sano_percentage could be > 100 initially or if any part becomes < 0
            # For example, if overall_score was > 100, non_sano_percentage would be < 0.
            # The max(0, ...) calls handle this by clamping.
            # Now, ensure the sum is 100.

            # If overall_score was > 100, sano_percentage is capped at 100 (or whatever it was if <100).
            # If overall_score was < 0, sano_percentage is capped at 0.
            # The sum of the three should ideally be 100.
            # If sano_percentage alone is already > 100 (e.g. score was 105), it should be capped at 100
            # and other percentages should be 0.
            if sano_percentage >= 100.0:
                sano_percentage = 100.0
                problemi_percentage = 0.0
                avvertimenti_percentage = 0.0
            else: # sano_percentage is < 100.0
                  # problemi_percentage and avvertimenti_percentage were derived from (100 - sano_percentage)
                  # The sum should naturally be 100 unless non_sano_percentage was <=0 initially.
                  # If non_sano_percentage was <=0 (i.e. score >=100), problemi and avvertimenti are already 0.
                  # The main adjustment needed is if the sum is slightly off due to floating point arithmetic.
                  current_total = sano_percentage + problemi_percentage + avvertimenti_percentage
                  if abs(current_total - 100.0) > 0.01 and current_total > 0: # Check if adjustment is needed
                      # Simple scaling adjustment
                      scale_factor = 100.0 / current_total
                      sano_percentage *= scale_factor
                      problemi_percentage *= scale_factor
                      avvertimenti_percentage *= scale_factor
                      # Re-cap largest to ensure sum is exactly 100 after scaling, preventing over/undershoot
                      # This is a bit redundant if scaling worked perfectly, but good as a final guard.
                      final_total = sano_percentage + problemi_percentage + avvertimenti_percentage
                      if abs(final_total - 100.0) > 0.001: # Small tolerance for float comparison
                          diff = 100.0 - final_total
                          # Add difference to the largest segment, or sano if all are similar
                          if sano_percentage >= problemi_percentage and sano_percentage >= avvertimenti_percentage:
                              sano_percentage += diff
                          elif problemi_percentage >= sano_percentage and problemi_percentage >= avvertimenti_percentage:
                              problemi_percentage += diff
                          else:
                              avvertimenti_percentage += diff

            # Final clamp to ensure no negative percentages after adjustments
            sano_percentage = max(0.0, round(sano_percentage, 1)) # Round to 1 decimal place for neater values
            problemi_percentage = max(0.0, round(problemi_percentage, 1))
            avvertimenti_percentage = max(0.0, round(avvertimenti_percentage, 1))

            # Due to rounding, sum might be slightly off 100. Adjust largest to compensate.
            rounded_sum = sano_percentage + problemi_percentage + avvertimenti_percentage
            if abs(rounded_sum - 100.0) > 0.01 and rounded_sum > 0: # if sum is like 99.9 or 100.1
                diff = 100.0 - rounded_sum
                if sano_percentage >= problemi_percentage and sano_percentage >= avvertimenti_percentage:
                    sano_percentage += diff
                elif problemi_percentage >= sano_percentage and problemi_percentage >= avvertimenti_percentage:
                    problemi_percentage += diff
                else: # avvertimenti_percentage is largest or they are equal
                    avvertimenti_percentage += diff
                # Re-round and re-clamp after this final adjustment
                sano_percentage = max(0.0, round(sano_percentage, 1))
                problemi_percentage = max(0.0, round(problemi_percentage, 1))
                avvertimenti_percentage = max(0.0, round(avvertimenti_percentage, 1))


            # Define colors and font (ensure these are loaded from PDF_CONFIG as intended)
            COLOR_GREEN = PDF_CONFIG['colors'].get('success', '#28A745')
            COLOR_ORANGE = PDF_CONFIG['colors'].get('warning', '#FFC107')
            COLOR_RED = PDF_CONFIG['colors'].get('error', '#DC3545')
            FONT_FAMILY_CHART = PDF_CONFIG.get('font_family', 'Arial')

            chart_segments_data = []
            chart_segments_colors = []
            legend_elements = []

            # Order: Green, Orange, Red for legend consistency
            if sano_percentage > 0.1:
                chart_segments_data.append(sano_percentage)
                chart_segments_colors.append(COLOR_GREEN)
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_GREEN, markersize=10, label=f'Sano ({sano_percentage:.0f}%)'))

            if avvertimenti_percentage > 0.1: # Orange for Warnings
                chart_segments_data.append(avvertimenti_percentage)
                chart_segments_colors.append(COLOR_ORANGE)
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_ORANGE, markersize=10, label=f'Avvertimenti ({avvertimenti_percentage:.0f}%)'))

            if problemi_percentage > 0.1: # Red for Problems
                chart_segments_data.append(problemi_percentage)
                chart_segments_colors.append(COLOR_RED)
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_RED, markersize=10, label=f'Problemi ({problemi_percentage:.0f}%)'))

            # Fallback if all percentages are effectively zero
            if not chart_segments_data:
                # This case implies overall_score was 0 or very close, and no specific errors/warnings pushed other segments above 0.1
                # Display 100% Problemi for a score of 0.
                chart_segments_data = [100.0]
                chart_segments_colors = [COLOR_RED] # Red for "Problemi"
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_RED, markersize=10, label=f'Problemi (100%)'))
                # Display 0% in the center if we defaulted to 100% problemi chart.
                # This ensures consistency if overall_score was, for example, 0.01 but all segments ended up <0.1.
                # However, the main text displays the original overall_score.
                # For the purpose of the chart's central text, if it's all red, it should show the score that led to this (likely 0).
                # The original overall_score (raw_overall_score or the float version) is used for the center text.
                # The `int(overall_score)` in ax.text will use the potentially adjusted overall_score from the top of the function.
                # Let's ensure the displayed score in center text is the original `overall_score` before any normalization logic specific to chart segments.
                # No, `overall_score` at the top is already the one to use.
                # If `overall_score` was >0 but chart is 100% red due to tiny segments, this is fine.
                pass


            fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor='white')
            ax.set_facecolor('white')

            # Create the pie chart (donut style)
            wedges, _ = ax.pie(chart_segments_data, colors=chart_segments_colors, startangle=90,
                               counterclock=False, wedgeprops=dict(width=0.35))

            # Centered text for overall score and title
            # Use the initial overall_score (after float conversion and None check) for the center text.
            display_score_in_center = int(round(overall_score)) # Round to nearest int for display
            ax.text(0, 0.1, f'{display_score_in_center}%',
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=36, fontweight='bold', color=PDF_CONFIG['colors'].get('primary', '#005A9C'),
                    fontfamily=FONT_FAMILY_CHART)
            ax.text(0, -0.15, 'Salute del Sito',
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=14, color=PDF_CONFIG['colors'].get('text_primary', '#222222'),
                    fontfamily=FONT_FAMILY_CHART)

            if legend_elements:
                fig.legend(handles=legend_elements, loc='lower center', ncol=len(legend_elements),
                           fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.08))

            ax.set_aspect('equal')
            ax.axis('off')

            # Adjust subplot to make space for legend
            plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.20 if legend_elements else 0.05) # Keep bottom padding for legend

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            img_buffer.seek(0)

            chart_image = RLImage(img_buffer, width=3*inch, height=3*inch)

            plt.close(fig)
            return chart_image
        except Exception as e:
            print(f"ERROR in _get_site_health_chart_flowable: Errore durante la generazione del grafico Site Health: {e}")
            import traceback
            traceback.print_exc()
            return None


    def _add_issues_table_section(self):
        flowables = []
        flowables.append(Paragraph("Tabelle Dati Dettagliate", self.styles['SectionHeading'])) # Updated Title
        flowables.append(Spacer(1, 0.2 * inch))

        # Define severity styles locally for colored text
        # Base style for severity text - ensure SmallText is defined in _setup_custom_styles
        base_severity_style = self.styles.get('SmallText', ParagraphStyle(name='DefaultSmallText', fontSize=8, fontName='Helvetica'))

        # It's better to define these colors once if they are used in multiple places, e.g., in __init__ or _setup_custom_styles
        # For now, defining them here for clarity of this method's scope.
        color_error = HexColor(PDF_CONFIG['colors'].get('error', '#DC3545'))
        color_warning = HexColor(PDF_CONFIG['colors'].get('warning', '#FFC107'))
        color_notice = HexColor(PDF_CONFIG['colors'].get('info', '#17A2B8')) # Matches COLOR_BLUE_BOX

        severity_error_style = ParagraphStyle(name='SeverityError', parent=base_severity_style, textColor=color_error, alignment=TA_LEFT)
        severity_warning_style = ParagraphStyle(name='SeverityWarning', parent=base_severity_style, textColor=color_warning, alignment=TA_LEFT)
        severity_notice_style = ParagraphStyle(name='SeverityNotice', parent=base_severity_style, textColor=color_notice, alignment=TA_LEFT)

        severity_text_map = {'ERROR': "ERRORE", 'WARNING': "AVVERTIMENTO", 'NOTICE': "AVVISO"}
        severity_style_map = {
            'ERROR': severity_error_style,
            'WARNING': severity_warning_style,
            'NOTICE': severity_notice_style
        }

        categorized_issues = self.analysis_results.get('categorized_issues', {})
        all_issues_for_table = []

        for category_key, severities in categorized_issues.items():
            # Assuming category_key is something like CATEGORY_OCM or CATEGORY_SEO_AUDIT which are already Italian
            categoria_text = category_key
            for severity_level_key, issues_list in severities.items():
                gravita_text_key = severity_level_key # 'ERROR', 'WARNING', 'NOTICE'

                for issue in issues_list:
                    tipo_problema_text = issue.get('label', 'N/D')

                    url_text = issue.get('url', '')
                    details_text = issue.get('details', 'N/D')
                    url_dettagli_text = ""
                    if url_text and url_text != self.domain: # Only show URL if it's specific and not the main domain
                        url_dettagli_text += f"URL: {url_text}\n"
                    url_dettagli_text += f"Dettagli: {details_text}"
                    url_dettagli_text = url_dettagli_text.strip()
                    if not url_dettagli_text: # Fallback if both were empty
                        url_dettagli_text = "N/D"


                    valore_misurato_text = issue.get('value', issue.get('measured_value', 'N/D'))

                    all_issues_for_table.append({
                        'categoria': categoria_text,
                        'gravita_key': gravita_text_key,
                        'tipo_problema': tipo_problema_text,
                        'url_dettagli': url_dettagli_text,
                        'valore_misurato': valore_misurato_text
                    })

        if not all_issues_for_table:
            flowables.append(Paragraph("Nessun problema specifico identificato.", self.styles['BodyText']))
            flowables.append(Spacer(1, 0.5 * inch))
            self.story.append(KeepTogether(flowables))
            return

        header_style = self.styles.get('SmallText', ParagraphStyle(name='TableHeaderSmall', fontSize=9, fontName=PDF_CONFIG['font_family_bold'], alignment=TA_CENTER))
        header_row_text = ["Categoria", "Gravità", "Tipo di Problema", "URL/Dettagli Specifici", "Valore Misurato"]
        header_row = [Paragraph(text, header_style) for text in header_row_text]

        data_rows = [header_row]

        # Use a smaller font for data cells to fit more content
        data_cell_style = self.styles.get('SmallText', ParagraphStyle(name='DataCellSmall', fontSize=8, fontName=PDF_CONFIG['font_family'], alignment=TA_LEFT))
        data_cell_style_center = ParagraphStyle(name='DataCellSmallCenter', parent=data_cell_style, alignment=TA_CENTER)


        for item in all_issues_for_table:
            row = [
                Paragraph(item['categoria'], data_cell_style),
                Paragraph(severity_text_map.get(item['gravita_key'], item['gravita_key']), severity_style_map.get(item['gravita_key'], data_cell_style)),
                Paragraph(item['tipo_problema'], data_cell_style),
                Paragraph(item['url_dettagli'].replace("\n", "<br/>"), data_cell_style), # Allow line breaks
                Paragraph(str(item['valore_misurato']), data_cell_style_center) # Ensure value is string
            ]
            data_rows.append(row)

        available_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        col_widths = [
            available_width * 0.15, # Categoria
            available_width * 0.15, # Gravità
            available_width * 0.25, # Tipo di Problema
            available_width * 0.35, # URL/Dettagli Specifici
            available_width * 0.10  # Valore Misurato
        ]

        table = Table(data_rows, colWidths=col_widths)

        # Styling
        new_header_bg_color = colors.HexColor('#f5f5f5') # Light gray for header
        color_row_odd_bg = colors.HexColor(PDF_CONFIG['colors'].get('light_gray_alt', '#E8EFF5'))
        color_row_even_bg = colors.white
        grid_color = colors.HexColor(PDF_CONFIG['colors'].get('border_light', '#B0C4DE'))
        text_color_body = colors.HexColor(PDF_CONFIG['colors'].get('text_primary', '#222222'))

        table_style_cmds = [
            ('BACKGROUND', (0,0), (-1,0), new_header_bg_color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black), # Header text black
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), PDF_CONFIG.get('font_family_bold', 'Helvetica-Bold')), # Ensure bold font for header
            ('FONTSIZE', (0,0), (-1,0), PDF_CONFIG['font_sizes'].get('small', 9)),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),

            # Data Rows General Styling
            ('TEXTCOLOR', (0,1), (-1,-1), text_color_body),
            ('FONTNAME', (0,1), (-1,-1), PDF_CONFIG.get('font_family', 'Helvetica')),
            ('FONTSIZE', (0,1), (-1,-1), PDF_CONFIG['font_sizes'].get('extra_small', 8)),
            ('VALIGN', (0,1), (-1,-1), 'TOP'), # Top align content in cells

            # Specific Column Alignments for data rows
            ('ALIGN', (0,1), (0,-1), 'LEFT'),   # Categoria
            ('ALIGN', (1,1), (1,-1), 'LEFT'),   # Gravità (text part, style handles color)
            ('ALIGN', (2,1), (2,-1), 'LEFT'),   # Tipo di Problema
            ('ALIGN', (3,1), (3,-1), 'LEFT'),   # URL/Dettagli
            ('ALIGN', (4,1), (4,-1), 'CENTER'), # Valore Misurato

            # Padding for all data cells
            ('LEFTPADDING', (0,1), (-1,-1), 5),
            ('RIGHTPADDING', (0,1), (-1,-1), 5),
            ('TOPPADDING', (0,1), (-1,-1), 5),
            ('BOTTOMPADDING', (0,1), (-1,-1), 5),

            # Grid and Borders
            ('GRID', (0,0), (-1,-1), 0.5, grid_color),
            ('BOX', (0,0), (-1,-1), 1, grid_color), # Thicker border for the whole table
        ]

        # Row striping
        for i in range(1, len(data_rows)): # Start from 1 to skip header
            bg_color = color_row_even_bg if i % 2 == 0 else color_row_odd_bg
            table_style_cmds.append(('BACKGROUND', (0,i), (-1,i), bg_color))

        table.setStyle(TableStyle(table_style_cmds))

        flowables.append(table)
        flowables.append(Spacer(1, 0.5 * inch))
        self.story.append(KeepTogether(flowables))

    def _create_summary_table_for_section(self, items: List[Tuple[str, str]], available_width: float) -> Table:
        """
        Creates a striped, full-width table for summary data of an analysis section.
        items: List of (Metric Name, Metric Value) tuples.
        available_width: The calculated available width for the table.
        """
        if not items:
            return None

        # Define header and data rows
        header_row = [Paragraph("Parametro", self.styles['BodyText']), Paragraph("Valore", self.styles['BodyText'])] # Already Italian
        table_data = [header_row] # Add header row first

        for name, value in items: # 'name' could be English here if items come from English keys
            # If 'name' is from a fixed set of English keys, it should be translated here.
            # Example: name_translated = {'Metric Name': 'Nome Parametro'}.get(name, name)
            # For now, assuming 'name' is already being passed in Italian or is a general term.
            table_data.append([
                Paragraph(name, self.styles['BodyText']),
                Paragraph(str(value), self.styles['BodyText'])
            ])

        # Define column widths (e.g., 60% for name, 40% for value)
        col_widths = [available_width * 0.6, available_width * 0.4]
        summary_table = Table(table_data, colWidths=col_widths)

        # Styling elements
        new_header_bg_color = colors.HexColor('#f5f5f5')
        header_outline_color = colors.HexColor('#FFCC00')
        font_header_name = PDF_CONFIG.get('font_family_bold', 'Helvetica-Bold') # Using BodyText's font but bold for header
        font_header_size = PDF_CONFIG['font_sizes'].get('body', 10) # BodyText size for header

        bg_color_even_hex = PDF_CONFIG['colors'].get('white', '#FFFFFF')
        bg_color_odd_hex = PDF_CONFIG['colors'].get('light_gray_alt', '#F0F4F7')
        grid_color = colors.HexColor(PDF_CONFIG['colors'].get('border', '#CCCCCC'))

        table_style_cmds = [
            # Header Styling
            ('BACKGROUND', (0,0), (-1,0), new_header_bg_color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), font_header_name),
            ('FONTSIZE', (0,0), (-1,0), font_header_size),
            ('BOTTOMPADDING', (0,0), (-1,0), 5), # Adjusted padding for header
            ('TOPPADDING', (0,0), (-1,0), 5),
            ('BOX', (0,0), (0,0), 1.5, header_outline_color), # Outline for first header cell
            ('BOX', (1,0), (1,0), 1.5, header_outline_color), # Outline for second header cell

            # General Data Row Styling (starts from row 1 now)
            ('VALIGN', (0,1), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,1), (-1,-1), 5),
            ('RIGHTPADDING', (0,1), (-1,-1), 5),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, grid_color), # Grid for the whole table
        ]

        # Striping for data rows (starting from row 1)
        for i in range(1, len(table_data)): # i is the actual row index in table_data
            if (i-1) % 2 == 0: # Even data row (i=1, 3, 5...) -> (i-1) = 0, 2, 4...
                table_style_cmds.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor(bg_color_even_hex)))
            else: # Odd data row (i=2, 4, 6...) -> (i-1) = 1, 3, 5...
                table_style_cmds.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor(bg_color_odd_hex)))

        summary_table.setStyle(TableStyle(table_style_cmds))
        return summary_table

    def _create_section_header_with_list_items(self, section_title_str: str, list_item_texts: List[str]) -> KeepTogether:
        # This method will be phased out or significantly changed.
        # For now, keeping it to avoid breaking existing calls until they are all refactored.
        flowables = [Paragraph(section_title_str, self.styles['SectionHeading'])]
        for item_text in list_item_texts:
            flowables.append(Paragraph(item_text, self.styles['ListItem']))
        flowables.append(Spacer(1, 0.1 * inch))
        return KeepTogether(flowables)

    def _add_detailed_analysis_section(self):
        self.story.append(Paragraph("Analisi Dettagliata per Categoria", self.styles['SectionHeading'])) # Already Italian
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Analisi dettagliata per categoria in fase di revisione.", self.styles['BodyText'])) # Already Italian
        self.story.append(Spacer(1, 0.5 * inch))
        # Comment out the previous content generation for this section
        # detailed_issues = self.analysis_results.get('detailed_issues', {})
        # ... (rest of the original method content commented out) ...
        # self.story.append(PageBreak())

    def _add_recommendations_section(self):
        self.story.append(Paragraph("Raccomandazioni", self.styles['SectionHeading'])) # Already Italian
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Sezione raccomandazioni in fase di revisione. Le raccomandazioni principali sono ora integrate nel Riassunto Esecutivo.", self.styles['BodyText'])) # Already Italian
        self.story.append(Spacer(1, 0.5 * inch))
        # Comment out the previous content generation for this section
        # recommendations = self.analysis_results['recommendations']
        # ... (rest of the original method content commented out) ...
        # self.story.append(PageBreak())

    def _add_issue_details_appendix(self):
        # This method might be removed or significantly changed later.
        # For now, let's add a placeholder similar to other sections.
        self.story.append(Paragraph("Descrizione Dettagliata dei Problemi Comuni", self.styles['SectionHeading'])) # Already Italian
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Sezione appendice descrizioni problemi in fase di revisione.", self.styles['BodyText'])) # Already Italian
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_core_web_vitals_section(self):
        self.story.append(PageBreak())
        self.story.append(Paragraph("Metriche Core Web Vitals", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))
        # These values should ideally come from self.analysis_results
        # Using placeholders as per the plan for now.
        self.story.append(Paragraph("Interaction to Next Paint (INP): <b>600ms</b>", self.styles['BodyText']))
        self.story.append(Paragraph("Cumulative Layout Shift (CLS): <b>0.3</b>", self.styles['BodyText']))
        self.story.append(Paragraph("Tempo di risposta server: <b>809ms</b>", self.styles['BodyText']))
        self.story.append(Spacer(1, 0.3 * inch))

    def _add_seo_content_analysis_section(self):
        self.story.append(PageBreak())
        self.story.append(Paragraph("Analisi Contenuti SEO", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        self.story.append(Paragraph("Analisi Thin Content", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Elenco delle pagine con contenuto scarso o duplicato.", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph("Analisi Meta Description", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Pagine con meta description mancanti, troppo corte o troppo lunghe.", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph("Stato Implementazione Schema Markup", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Verifica degli schema markup implementati (es. FAQ, Video, LocalBusiness, Product) e potenziali errori.", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.3 * inch))

    def _add_security_performance_section(self):
        self.story.append(PageBreak())
        self.story.append(Paragraph("Sicurezza e Performance Aggiuntive", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        self.story.append(Paragraph("Stato Content Security Policy (CSP)", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Verifica dell'implementazione e della corretta configurazione della Content Security Policy.", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph("Configurazione X-Frame-Options", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Controllo delle intestazioni X-Frame-Options per la protezione contro il clickjacking.", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph("Analisi Segnali E-E-A-T", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Valutazione preliminare dei segnali di Esperienza, Competenza, Autorevolezza e Affidabilità (E-E-A-T).", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.3 * inch))

    def _add_priority_recommendations_section(self):
        self.story.append(PageBreak())
        self.story.append(Paragraph("Raccomandazioni Prioritarie", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        self.story.append(Paragraph("Priorità Alta", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Elenco delle azioni ad alta priorità da intraprendere immediatamente. Timeline stimata: [timeline].", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph("Priorità Media", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Azioni a media priorità. Timeline stimata: [timeline].", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph("Priorità Bassa", self.styles['SectionSubHeadingStyle']))
        self.story.append(Paragraph("Azioni a bassa priorità. Timeline stimata: [timeline].", self.styles['BodyText'])) # Placeholder
        self.story.append(Spacer(1, 0.3 * inch))

    def _get_evaluation_text(self, score): # Already Italian
        if score >= 90: return "Eccellente"
        elif score >= 70: return "Buono"
        elif score >= 50: return "Da Migliorare"
        else: return "Critico"
    
    def _get_status_text(self, score): # Already Italian
        if score >= 90: return "✓ Eccellente"
        elif score >= 70: return "⚠ Buono"
        elif score >= 50: return "⚠ Da Migliorare"
        else: return "✗ Critico"
    
    def _get_score_color_hex(self, score): # No text here
        if score >= 90: return '#28A745'
        elif score >= 70: return '#005A9C'
        elif score >= 50: return '#FFC107'
        else: return '#DC3545'

    def _identify_strengths_weaknesses(self):
        strengths = []
        # Strengths identification remains the same
        # categories = {'Title Tags': self.analysis_results['title_analysis']['score'], 'Meta Descriptions': self.analysis_results['meta_description_analysis']['score'], 'Immagini': self.analysis_results['images_analysis']['score'], 'Contenuto': self.analysis_results['content_analysis']['score'], 'Performance': self.analysis_results['performance_analysis']['score'], 'SSL': self.analysis_results['ssl_analysis']['score'], 'Link Interni': self.analysis_results['links_analysis']['score'], 'Aspetti Tecnici': self.analysis_results['technical_analysis']['score']}
        # Simplified list of categories for strengths, based on available analysis results keys
        # This avoids KeyError if some analyses were not run or 'score' is missing.
        strength_candidate_categories = { # Dictionary for mapping keys to Italian names
            'title_analysis': 'Analisi Titoli',
            'meta_description_analysis': 'Analisi Meta Description',
            'images_analysis': 'Analisi Immagini',
            'content_analysis': 'Analisi Contenuto',
            'performance_analysis': 'Analisi delle Prestazioni', # Changed "Analisi Prestazioni"
            'ssl_analysis': 'Analisi SSL',
            'links_analysis': 'Analisi Link Interni',
            'technical_analysis': 'Analisi Tecnica'
        }
        for cat_key, category_name_it in strength_candidate_categories.items(): # Iterate through dict
            category_analysis = self.analysis_results.get(cat_key)
            if category_analysis and isinstance(category_analysis, dict):
                score = category_analysis.get('score')
                # Use the Italian name from the dictionary
                if score is not None and score >= 80: # Assuming 80 is the threshold for a strength
                    strengths.append(f"{category_name_it} ottimizzato correttamente (punteggio: {score}/100)") # Already Italian format

        weaknesses_structured = {
            'errors': {}, # These keys 'errors', 'warnings', 'notices' are internal; display names are handled by severity_display_name
            'warnings': {},
            'notices': {}
        }
        # Ensure detailed_issues and its sub-keys exist and are lists
        detailed_issues_data = self.analysis_results.get('detailed_issues', {})
        if not isinstance(detailed_issues_data, dict):
            detailed_issues_data = {} # Fallback to empty dict if not a dict

        macro_map = {
            'errors': 'errors', # Key in weaknesses_structured : key in detailed_issues_data
            'warnings': 'warnings',
            'notices': 'notices'
        }

        for macro_key, detailed_issue_list_key in macro_map.items():
            issues_list = detailed_issues_data.get(detailed_issue_list_key, [])
            if not isinstance(issues_list, list): # Ensure it's a list
                continue

            for issue in issues_list:
                if not isinstance(issue, dict): # Ensure each issue is a dict
                    continue

                specific_type_key = issue.get('type', 'tipo_sconosciuto') # 'unknown_type' to 'tipo_sconosciuto'
                # Attempt to get label from PDF_ISSUE_TYPE_LABELS; if missing, create a fallback.
                # This part is tricky because PDF_ISSUE_TYPE_LABELS was removed/restructured.
                # The new structure AUDIT_CHECKS_CONFIG maps a technical key to a dict with 'label'.
                # This old weaknesses logic might not map directly anymore.
                # For now, let's try to find a label from AUDIT_CHECKS_CONFIG if possible, or fallback.

                # Fallback label generation if direct mapping is not found
                # Assuming issue.get('label') is the primary source now, or AUDIT_CHECKS_CONFIG provides it.
                user_friendly_label = issue.get('label') # Prioritize given label
                if not user_friendly_label:
                    # Fallback to a generic label if specific_type_key is also not very descriptive
                    user_friendly_label = specific_type_key.replace('_', ' ').capitalize()
                    check_config = AUDIT_CHECKS_CONFIG.get(issue.get('key')) # issue['key'] is the new standard
                    if check_config:
                        user_friendly_label = check_config.get('label', user_friendly_label)
                    elif 'PDF_ISSUE_TYPE_LABELS' in globals(): # Should not exist, but as a safeguard
                         user_friendly_label = PDF_ISSUE_TYPE_LABELS.get(specific_type_key, user_friendly_label)


                details_text = issue.get('image', issue.get('details', issue.get('issue', 'N/D'))) # N/A to N/D
                issue_entry = {
                    'url': issue.get('url', 'N/D'), # N/A to N/D
                    'details': details_text,
                    'type': specific_type_key
                }

                if user_friendly_label not in weaknesses_structured[macro_key]:
                    weaknesses_structured[macro_key][user_friendly_label] = {
                        'type': specific_type_key, # This is an internal key, not directly displayed
                        'instances': []
                    }
                weaknesses_structured[macro_key][user_friendly_label]['instances'].append(issue_entry)

        # Clean up empty categories/labels as before
        weaknesses_structured = {k: v for k, v in weaknesses_structured.items() if v}
        for mk in list(weaknesses_structured.keys()):
            for pl_key in list(weaknesses_structured[mk].keys()):
                if not weaknesses_structured[mk][pl_key]['instances']:
                    del weaknesses_structured[mk][pl_key]
            if not weaknesses_structured[mk]:
                del weaknesses_structured[mk]

        return strengths, weaknesses_structured
        
    def generate_pdf(self, filename: str) -> bool:
        try:
            self.doc = SimpleDocTemplate(filename, pagesize=A4,
                                         leftMargin=PDF_CONFIG['margin']['left']*cm,
                                         rightMargin=PDF_CONFIG['margin']['right']*cm,
                                         topMargin=PDF_CONFIG['margin']['top']*cm,
                                         bottomMargin=PDF_CONFIG['margin']['bottom']*cm)
            self.story = []
            self._add_header()
            self._add_chart_and_counts_section() # NEWLY ADDED CALL
            self._add_executive_summary()
            self._add_score_overview()
            self.story.append(PageBreak())
            self._add_issues_table_section()

            # New sections added here
            self._add_core_web_vitals_section()
            self._add_seo_content_analysis_section()
            self._add_security_performance_section()
            self._add_priority_recommendations_section()

            # Existing sections that were marked "in fase di revisione"
            self._add_detailed_analysis_section()
            self._add_recommendations_section() # This was the old general recommendations

            # self.story.append(PageBreak()) # Optional Page break
            # Removed sections:
            # self._add_issue_details_appendix()
            # self._add_appendix()
            self.doc.build(self.story)
            return True
        except Exception as e:
            print(f"Errore durante la generazione del PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
