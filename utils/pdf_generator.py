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
        self.story.append(Paragraph("Site Audit Report", self.styles['CustomTitle'])) # First line
        self.story.append(Paragraph(self.domain, self.styles['CustomSubtitle']))      # Second line (domain name)
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph(f"Generato in data: {self.analysis_results['summary']['analysis_date']}", self.styles['SmallText']))
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_chart_and_counts_section(self):
        section_flowables = []

        # Get Chart
        chart_image = self._get_site_health_chart_flowable()
        if chart_image:
            section_flowables.append(chart_image)
            section_flowables.append(Spacer(1, 0.3 * inch))

        # Issue Counts Logic
        # Ensure analysis_results and detailed_issues are available, or pass them if needed.
        # Assuming they are available via self.analysis_results as in _add_executive_summary
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        num_errors = len(detailed_issues.get('errors', []))
        num_warnings = len(detailed_issues.get('warnings', []))
        num_notices = len(detailed_issues.get('notices', []))

        color_error_hex = PDF_CONFIG['colors'].get('error', '#DC3545')
        color_warning_hex = PDF_CONFIG['colors'].get('warning', '#FFC107')
        color_notice_hex = PDF_CONFIG['colors'].get('info', PDF_CONFIG['colors'].get('secondary', '#17A2B8'))

        # Use self.styles.get to safely access 'Normal' or fallback to 'BodyText'
        parent_style = self.styles.get('Normal', self.styles['BodyText'])
        count_box_base_style = ParagraphStyle(
            name='CountBoxBaseStyle',
            parent=parent_style,
            alignment=TA_CENTER,
            leading=14
        )
        error_text_style = ParagraphStyle(
            name='ErrorCountBoxStyle', parent=count_box_base_style,
            textColor=colors.HexColor(color_error_hex)
        )
        warning_text_style = ParagraphStyle(
            name='WarningCountBoxStyle', parent=count_box_base_style,
            textColor=colors.HexColor(color_warning_hex)
        )
        notice_text_style = ParagraphStyle(
            name='NoticeCountBoxStyle', parent=count_box_base_style,
            textColor=colors.HexColor(color_notice_hex)
        )

        error_p = Paragraph(f"<font size='16'><b>{num_errors}</b></font><br/><font size='10'>Errori</font>", error_text_style)
        warning_p = Paragraph(f"<font size='16'><b>{num_warnings}</b></font><br/><font size='10'>Avvertimenti</font>", warning_text_style)
        notice_p = Paragraph(f"<font size='16'><b>{num_notices}</b></font><br/><font size='10'>Avvisi</font>", notice_text_style)

        box_data = [[error_p, warning_p, notice_p]]

        # Ensure self.doc is available for margins, or use fixed values if called before self.doc init
        # This method is called from generate_pdf after self.doc is initialized.
        page_content_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        col_width = (page_content_width - 2 * 0.1*inch) / 3 # Allowing 0.1 inch gap on each side of middle box

        issue_counts_table = Table(box_data, colWidths=[col_width, col_width, col_width], rowHeights=[0.8*inch])

        counts_table_style = TableStyle([
            ('BOX', (0,0), (0,0), 1.5, colors.HexColor(color_error_hex)),
            ('BOX', (1,0), (1,0), 1.5, colors.HexColor(color_warning_hex)),
            ('BOX', (2,0), (2,0), 1.5, colors.HexColor(color_notice_hex)),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ])
        issue_counts_table.setStyle(counts_table_style)
        section_flowables.append(issue_counts_table)

        if section_flowables:
            self.story.append(KeepTogether(section_flowables))
            self.story.append(Spacer(1, 0.3 * inch)) # Spacer after the whole section

    def _add_executive_summary(self):
        flowables = []
        flowables.append(Paragraph("Riassunto Esecutivo", self.styles['SectionHeading']))
        flowables.append(Spacer(1, 0.2 * inch))

        # chart_image = self._get_site_health_chart_flowable() # REMOVED

        overall_score = self.analysis_results['overall_score']
        evaluation = self._get_evaluation_text(overall_score)
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        num_errors = len(detailed_issues.get('errors', []))
        num_warnings = len(detailed_issues.get('warnings', []))
        num_notices = len(detailed_issues.get('notices', []))
        issue_parts = []
        if num_errors > 0: issue_parts.append(f"<b>{num_errors}</b> Errori")
        if num_warnings > 0: issue_parts.append(f"<b>{num_warnings}</b> Avvertimenti")
        if num_notices > 0: issue_parts.append(f"<b>{num_notices}</b> Avvisi")
        issues_string = ""
        if not issue_parts:
            issues_string = "non rilevando problemi significativi" if self.analysis_results['summary']['total_issues'] == 0 else f"identificando <b>{self.analysis_results['summary']['total_issues']}</b> problemi complessivi"
        elif len(issue_parts) == 1: issues_string = f"identificando {issue_parts[0]}"
        elif len(issue_parts) == 2: issues_string = f"identificando {issue_parts[0]} e {issue_parts[1]}"
        else: issues_string = f"identificando {issue_parts[0]}, {issue_parts[1]} e {issue_parts[2]}"
        summary_text = f"""L'analisi SEO del sito <b>{self.domain}</b> ha rivelato un punteggio complessivo di <font color="{self._get_score_color_hex(overall_score)}"><b>{overall_score}/100</b></font>. Valutazione: <b>{evaluation}</b>. Sono state analizzate <b>{self.analysis_results['summary']['total_pages_analyzed']}</b> pagine, {issues_string} e generando <b>{self.analysis_results['summary']['total_recommendations']}</b> raccomandazioni per il miglioramento."""
        summary_paragraph = Paragraph(summary_text, self.styles['BodyText'])

        # chart_image and chart_summary_table logic REMOVED
        # issue_counts_table and related logic REMOVED
        flowables.append(summary_paragraph) # Appending the main summary text directly.
                                            # The chart and counts are in _add_chart_and_counts_section

        # Spacing after summary_paragraph if needed, or rely on paragraph's spaceAfter
        # flowables.append(Spacer(1, 0.2 * inch)) # This was the original spacer after summary text.
                                                 # The new structure has a spacer after the chart/counts section.
                                                 # And another spacer after the summary_paragraph (now this one)
                                                 # before Strengths/Weaknesses.
                                                 # Let's keep a spacer here for now.
        flowables.append(Spacer(1, 0.2 * inch)) # Spacer after summary text

        # --- New Executive Summary Content ---
        categorized_issues = self.analysis_results.get('categorized_issues', {})

        # OCM Section
        flowables.append(Paragraph(CATEGORY_OCM, self.styles['OCMSectionHeading']))
        for severity in ['ERROR', 'WARNING', 'NOTICE']:
            issues_list = categorized_issues.get(CATEGORY_OCM, {}).get(severity, [])
            severity_style_name = f"{severity.capitalize()}SubHeading" # ErrorSubHeading, WarningSubHeading, etc.
            if severity_style_name not in self.styles: # Fallback if style not defined
                severity_style_name = 'SectionSubHeadingStyle'

            flowables.append(Paragraph(f"{severity.capitalize()}S", self.styles.get(severity_style_name, self.styles['BodyText'])))

            if issues_list:
                for issue in issues_list:
                    check_config = AUDIT_CHECKS_CONFIG.get(issue['key'], {})
                    description = PDF_ISSUE_DESCRIPTIONS.get(check_config.get('description_key'), "N/A")

                    flowables.append(Paragraph(f"<b>{issue['label']}</b>", self.styles['BodyText']))
                    if issue.get('url') and issue.get('url') != self.domain : # Show URL if page-specific
                        flowables.append(Paragraph(f"URL: {issue['url']}", self.styles['SmallText']))
                    flowables.append(Paragraph(f"Dettagli: {issue.get('details', 'N/A')}", self.styles['SmallText']))
                    flowables.append(Paragraph(f"Impatto SEO: {description}", self.styles['IssueDescriptionText']))
                    flowables.append(Spacer(1, 0.1 * inch))
            else:
                flowables.append(Paragraph("Nessun problema rilevato in questa categoria di severità.", self.styles['BodyText']))
            flowables.append(Spacer(1, 0.1 * inch))

        # SEO Audit Section
        flowables.append(Paragraph(CATEGORY_SEO_AUDIT, self.styles['SEOAuditSectionHeading']))
        for severity in ['ERROR', 'WARNING', 'NOTICE']:
            issues_list = categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get(severity, [])
            severity_style_name = f"{severity.capitalize()}SubHeading"
            if severity_style_name not in self.styles:
                severity_style_name = 'SectionSubHeadingStyle'

            flowables.append(Paragraph(f"{severity.capitalize()}S", self.styles.get(severity_style_name, self.styles['BodyText'])))

            if issues_list:
                for issue in issues_list:
                    check_config = AUDIT_CHECKS_CONFIG.get(issue['key'], {})
                    description = PDF_ISSUE_DESCRIPTIONS.get(check_config.get('description_key'), "N/A")

                    flowables.append(Paragraph(f"<b>{issue['label']}</b>", self.styles['BodyText']))
                    if issue.get('url') and issue.get('url') != self.domain: # Show URL if page-specific
                        flowables.append(Paragraph(f"URL: {issue['url']}", self.styles['SmallText']))
                    flowables.append(Paragraph(f"Dettagli: {issue.get('details', 'N/A')}", self.styles['SmallText']))
                    flowables.append(Paragraph(f"Impatto SEO: {description}", self.styles['IssueDescriptionText']))
                    flowables.append(Spacer(1, 0.1 * inch))
            else:
                flowables.append(Paragraph("Nessun problema rilevato in questa categoria di severità.", self.styles['BodyText']))
            flowables.append(Spacer(1, 0.1 * inch))

        # Simplified Strengths
        if overall_score >= 80: # Example threshold for "good score"
            flowables.append(Paragraph("Punti di Forza Generali:", self.styles['SectionSubHeadingStyle']))
            flowables.append(Paragraph(f"Il punteggio generale di {overall_score}/100 indica una buona performance complessiva.", self.styles['BodyText']))

        # --- End of New Executive Summary Content ---

        # Old strengths/weaknesses table logic is removed.
        # strengths, weaknesses = self._identify_strengths_weaknesses()
        # table_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin

        # Define colors for striping from PDF_CONFIG or use defaults (Commented out as old tables are removed)
        # bg_color_even_hex = PDF_CONFIG['colors'].get('light_gray_alt', '#F0F4F7')
        # bg_color_odd_hex = PDF_CONFIG['colors'].get('white', '#FFFFFF')
        bg_color_even = colors.HexColor(bg_color_even_hex)
        bg_color_odd = colors.HexColor(bg_color_odd_hex)

        base_table_style_cmds = [
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]

        # Strengths Section
        flowables.append(Paragraph("Punti di Forza:", self.styles['SectionSubHeadingStyle']))
        if strengths:
            strengths_data = [[Paragraph(s, self.styles['BodyText'])] for s in strengths]
            strengths_table = Table(strengths_data, colWidths=[table_width])

            current_strengths_style_cmds = list(base_table_style_cmds) # Copy base
            for i, _ in enumerate(strengths):
                color = bg_color_even if i % 2 == 0 else bg_color_odd
                current_strengths_style_cmds.append(('BACKGROUND', (0,i), (0,i), color))
            strengths_table.setStyle(TableStyle(current_strengths_style_cmds))
            flowables.append(strengths_table)
        else:
            flowables.append(Paragraph("Nessun punto di forza specifico identificato.", self.styles['ListItem']))

        flowables.append(Spacer(1, 0.1 * inch))

        # Weaknesses Section - New structure with multiple small tables
        flowables.append(Paragraph("Aree di Miglioramento:", self.styles['SectionSubHeadingStyle']))
        flowables.append(Spacer(1, 0.1 * inch)) # Space after main title

        has_any_weakness_to_show = False

        if weaknesses and isinstance(weaknesses, dict):
            macro_order_map = {
                'errors': 'Errori Critici',
                'warnings': 'Avvertimenti Importanti',
                'notices': 'Avvisi e Ottimizzazioni Minori'
            }

            # Define colors for striping from PDF_CONFIG or use defaults for table
            bg_color_even_hex_table = PDF_CONFIG['colors'].get('light_gray', '#F0F0F0')
            bg_color_odd_hex_table = PDF_CONFIG['colors'].get('white', '#FFFFFF')
            bg_color_even_table = colors.HexColor(bg_color_even_hex_table)
            bg_color_odd_table = colors.HexColor(bg_color_odd_hex_table)

            # Specific problem title background
            specific_problem_title_bg_hex = PDF_CONFIG['colors'].get('secondary_light', '#E4EAF1') # A light neutral color
            specific_problem_title_bg = colors.HexColor(specific_problem_title_bg_hex)

            for macro_key, macro_display_name in macro_order_map.items():
                if macro_key in weaknesses and weaknesses[macro_key]:
                    if not has_any_weakness_to_show: # First time we find a macro category with issues
                        has_any_weakness_to_show = True

                    # Add Macro Category Title as a standalone Paragraph
                    flowables.append(Paragraph(macro_display_name, self.styles['TableMacroCategoryStyle']))
                    # flowables.append(Spacer(1, 0.05 * inch)) # Small space after macro title

                    specific_problems_dict = weaknesses[macro_key] # This is now a dict of dicts
                    for problem_label, problem_data in specific_problems_dict.items():
                        technical_issue_type = problem_data['type']
                        problem_instances = problem_data['instances']

                        flowables.append(Spacer(1, 0.15 * inch)) # Space BEFORE each specific problem table

                        table_data_specific = []
                        table_style_specific_cmds = [
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('LEFTPADDING', (0,0), (-1,-1), 3),
                            ('RIGHTPADDING', (0,0), (-1,-1), 3),
                            ('TOPPADDING', (0,0), (-1,-1), 3),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor(PDF_CONFIG['colors'].get('border', '#CCCCCC'))),
                        ]

                        # Specific Problem Title Row
                        table_data_specific.append([Paragraph(problem_label, self.styles['TableSpecificProblemStyle'])])
                        table_style_specific_cmds.extend([
                            ('SPAN', (0,0), (1,0)), # Span title row
                            ('BACKGROUND', (0,0), (1,0), specific_problem_title_bg),
                            ('TEXTCOLOR', (0,0), (1,0), colors.black),
                            ('TOPPADDING', (0,0), (1,0), 5),
                            ('BOTTOMPADDING', (0,0), (1,0), 5),
                        ])

                        # Issue Detail Rows
                        for i, instance in enumerate(problem_instances):
                            details_display = instance['details']
                            if len(details_display) > 120: # Truncate for cell
                                details_display = details_display[:117] + "..."

                            url_text = instance['url']
                            if len(url_text) > 80: # Truncate for cell
                                url_text = url_text[:77] + "..."

                            row_items = [Paragraph(url_text, self.styles['TableDetailURLStyle'])]
                            if details_display != 'N/A' and details_display != instance['url']:
                                row_items.append(Paragraph(details_display, self.styles['TableDetailStyle']))
                            else:
                                row_items.append(Paragraph('-', self.styles['TableDetailStyle']))
                            table_data_specific.append(row_items)

                            # Striping for detail rows (i+1 because title is row 0)
                            current_bg_color = bg_color_even_table if i % 2 == 0 else bg_color_odd_table
                            table_style_specific_cmds.append(('BACKGROUND', (0, i+1), (1, i+1), current_bg_color))

                            # Individual recommendation rows are REMOVED from here

                        if table_data_specific: # Should always be true if problem_instances is not empty due to title row
                            page_width, _ = A4
                            available_width = page_width - self.doc.leftMargin - self.doc.rightMargin - (0.2 * inch) # Ensure it fits
                            col_widths_specific = [available_width * 0.5, available_width * 0.5]

                            specific_problem_table = Table(table_data_specific, colWidths=col_widths_specific)
                            specific_problem_table.setStyle(TableStyle(table_style_specific_cmds))
                            flowables.append(specific_problem_table)

                            # Add single recommendation paragraph after the table for this specific problem (for warnings/notices)
                            if macro_key in ['warnings', 'notices']:
                                recommendation_text = PDF_ISSUE_RECOMMENDATIONS.get(
                                    technical_issue_type,
                                    PDF_ISSUE_RECOMMENDATIONS.get('generic_seo_tip', "Consultare le best practice SEO.")
                                )
                                specific_content_flowables = [specific_problem_table]
                                specific_content_flowables.append(Spacer(1, 0.05 * inch)) # Small spacer before recommendation
                                rec_paragraph_text = f"<b>Raccomandazione:</b> {recommendation_text}"
                                specific_content_flowables.append(Paragraph(rec_paragraph_text, self.styles['TableRecommendationStyle']))
                                specific_content_flowables.append(Spacer(1, 0.05 * inch)) # Small spacer after recommendation
                                flowables.append(KeepTogether(specific_content_flowables))
                            else: # If not warning/notice, just add the table
                                flowables.append(specific_problem_table)

                    # Removed the Spacer(1, 0.1 * inch) that was here to avoid double spacing
                    # as spacers are now inside the KeepTogether or around it.

        if not has_any_weakness_to_show:
            flowables.append(Paragraph("Nessuna area di miglioramento critica identificata.", self.styles['ListItem']))

        flowables.append(Spacer(1, 0.5 * inch)) # Final spacer for the section
        self.story.append(KeepTogether(flowables))

    def _add_score_overview(self):
        flowables = []
        flowables.append(Paragraph("Panoramica Punteggi", self.styles['SectionHeading']))
        flowables.append(Spacer(1, 0.2 * inch))

        overall_score = self.analysis_results.get('overall_score', 'N/A')
        score_text = f"Punteggio SEO Complessivo: {overall_score}/100"
        flowables.append(Paragraph(score_text, self.styles['BodyText']))

        # data = [[Paragraph(h, self.styles['BodyText']) for h in ['Categoria', 'Punteggio', 'Stato']]]
        # categories = {'Title Tags': self.analysis_results['title_analysis']['score'], 'Meta Descriptions': self.analysis_results['meta_description_analysis']['score'], 'Headings': self.analysis_results['headings_analysis']['score'], 'Immagini': self.analysis_results['images_analysis']['score'], 'Contenuto': self.analysis_results['content_analysis']['score'], 'Link Interni': self.analysis_results['links_analysis']['score'], 'Performance': self.analysis_results['performance_analysis']['score'], 'Aspetti Tecnici': self.analysis_results['technical_analysis']['score'], 'SSL': self.analysis_results['ssl_analysis']['score']}
        # for category, score in categories.items():
        #     status_text = self._get_status_text(score)
        #     data.append([Paragraph(category, self.styles['BodyText']), Paragraph(f"{score}/100", self.styles['BodyText']), Paragraph(status_text, self.styles['BodyText'])])

        # # Calculate available width for full-width table
        # available_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        # # Define relative column widths (e.g., 45% Categoria, 20% Punteggio, 35% Stato)
        # col_widths = [available_width * 0.45, available_width * 0.20, available_width * 0.35]
        # table = Table(data, colWidths=col_widths)

        # COLOR_TABLE_HEADER_BG = PDF_CONFIG['colors'].get('primary_dark', '#004080') # Use from PDF_CONFIG
        # COLOR_TABLE_ROW_BG_ODD = PDF_CONFIG['colors'].get('light_gray_alt', '#F0F4F7') # Use from PDF_CONFIG
        # COLOR_TABLE_ROW_BG_EVEN = PDF_CONFIG['colors'].get('white', '#FFFFFF') # Use from PDF_CONFIG
        COLOR_BORDER = PDF_CONFIG['colors'].get('border', '#CCCCCC') # Use from PDF_CONFIG
        FONT_FAMILY_TABLE_HEADER = PDF_CONFIG.get('font_family_bold', 'Helvetica-Bold')
        FONT_FAMILY_TABLE_BODY = PDF_CONFIG.get('font_family', 'Helvetica')
        FONT_SIZE_TABLE_HEADER = PDF_CONFIG['font_sizes'].get('small', 9)
        FONT_SIZE_TABLE_BODY = PDF_CONFIG['font_sizes'].get('small', 9) # Consistent small size
        COLOR_TEXT_PRIMARY_FOR_TABLE = PDF_CONFIG['colors'].get('text_primary', '#222222')
        HEADER_OUTLINE_COLOR = colors.HexColor('#FFCC00') # Amber/Yellow
        NEW_HEADER_BG_COLOR = colors.HexColor('#f5f5f5')

        score_table_style_cmds = [
            # Header Styling
            ('BACKGROUND', (0, 0), (-1, 0), NEW_HEADER_BG_COLOR), # New light gray background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), # Ensure black text
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_FAMILY_TABLE_HEADER),
            ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_TABLE_HEADER),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Individual BOX for each header cell for #FFCC00 outline
            ('BOX', (0,0), (0,0), 1.5, HEADER_OUTLINE_COLOR),
            ('BOX', (1,0), (1,0), 1.5, HEADER_OUTLINE_COLOR),
            ('BOX', (2,0), (2,0), 1.5, HEADER_OUTLINE_COLOR),

            # Data Rows Styling
            ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY_TABLE_BODY),
            ('FONTSIZE', (0, 1), (-1, -1), FONT_SIZE_TABLE_BODY),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor(COLOR_TEXT_PRIMARY_FOR_TABLE)),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'), # Categoria left aligned
            ('ALIGN', (1, 1), (1, -1), 'CENTER'), # Punteggio center aligned
            ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Stato left aligned
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6), # Adjusted padding for data rows
            ('TOPPADDING', (0, 1), (-1, -1), 6),   # Adjusted padding for data rows
            ('BACKGROUND', (0, 1), (-1, -1), HexColor(COLOR_TABLE_ROW_BG_EVEN)), # Default for even data rows
        ]

        score_table_style = TableStyle(score_table_style_cmds)

        # Apply odd row striping
        for i in range(1, len(data)): # Start from 1 to skip header
            if i % 2 != 0: # Odd rows (1st, 3rd, 5th data row)
                score_table_style.add('BACKGROUND', (0, i), (-1, i), HexColor(COLOR_TABLE_ROW_BG_ODD))

        # General table grid (applied first, header BOXes will draw over it for header cells)
        score_table_style.add('GRID', (0,0), (-1,-1), 0.5, HexColor(COLOR_BORDER))
        # Overall table border (can be same as grid or slightly thicker)
        # score_table_style.add('BOX', (0,0), (-1,-1), 1, HexColor(COLOR_BORDER))

        # table.setStyle(score_table_style)
        # flowables.append(table)
        flowables.append(Spacer(1, 0.5 * inch))
        self.story.append(KeepTogether(flowables))

    def _get_site_health_chart_flowable(self):
        """
        Crea un grafico a ciambella (donut chart) che mostra la percentuale di salute del sito
        con un cerchio di completamento esterno e la percentuale al centro.
        Restituisce l'oggetto Image di ReportLab.
        """
        try:
            # Ottieni il punteggio complessivo
            try:
                overall_score = self.analysis_results['overall_score']
            except KeyError:
                # Consider logging this warning instead of printing directly if a logging system is in place
                print("WARNING: 'overall_score' not found in analysis_results for chart generation.")
                return None

            health_percentage = overall_score
            problem_percentage = 100 - overall_score

            # Colori e stili
            COLOR_SUCCESS_CHART = '#28A745' # Renamed to avoid conflict if other COLOR_SUCCESS exists
            COLOR_ERROR_CHART = '#DC3545'   # Renamed for clarity
            FONT_FAMILY_CHART = 'Arial'     # Renamed for clarity

            fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor='white') # Changed from (5,5)
            ax.set_facecolor('white')

            sizes = [health_percentage, problem_percentage]
            chart_colors = [COLOR_SUCCESS_CHART, COLOR_ERROR_CHART] # Use renamed variables

            wedges, texts = ax.pie(sizes, colors=chart_colors, startangle=90,
                                counterclock=False, wedgeprops=dict(width=0.3))

            for text_obj in texts: # Renamed variable to avoid conflict
                text_obj.set_visible(False)

            circle_outer = plt.Circle((0, 0), 0.85, fill=False, linewidth=8,
                                    color=COLOR_SUCCESS_CHART, alpha=0.3)
            ax.add_patch(circle_outer)

            theta1 = 90
            theta2 = 90 - (health_percentage * 360 / 100)

            angles = np.linspace(np.radians(theta1), np.radians(theta2), 100)
            x_outer = 0.85 * np.cos(angles)
            y_outer = 0.85 * np.sin(angles)

            ax.plot(x_outer, y_outer, linewidth=8, color=COLOR_SUCCESS_CHART, solid_capstyle='round')

            ax.text(0, 0.1, f'{int(health_percentage)}%',
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=36, fontweight='bold', color='#005A9C', fontfamily=FONT_FAMILY_CHART)

            ax.text(0, -0.15, 'Site Health',
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=14, color='#222222', fontfamily=FONT_FAMILY_CHART)

            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_SUCCESS_CHART,
                        markersize=12, label=f'Sano ({health_percentage:.0f}%)'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_ERROR_CHART,
                        markersize=12, label=f'Problemi ({problem_percentage:.0f}%)')
            ]

            ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1),
                    fontsize=10, frameon=False)

            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-1.2, 1.2)
            ax.set_aspect('equal')
            ax.axis('off')

            plt.tight_layout()

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            img_buffer.seek(0)

            # RLImage is already imported as Image, so just use Image
            chart_image = RLImage(img_buffer, width=2.5*inch, height=2.5*inch) # Removed keepAspectRatio

            plt.close(fig) # Assicura che la figura sia chiusa
            return chart_image
        except Exception as e:
            # Consider logging this error instead of printing directly if a logging system is in place
            print(f"ERROR in _get_site_health_chart_flowable: Errore durante la generazione del grafico Site Health: {e}")
            import traceback
            traceback.print_exc() # This is useful for debugging but might be removed for production
            return None


    def _add_issues_table_section(self):
        flowables = []
        flowables.append(Paragraph("Tabella Riepilogativa dei Problemi (Nuova Struttura)", self.styles['SectionHeading']))
        flowables.append(Spacer(1, 0.2 * inch))

        categorized_issues = self.analysis_results.get('categorized_issues', {})
        all_issues_flat = []
        for category_name, severities in categorized_issues.items():
            for severity_level, issues_list in severities.items():
                for issue in issues_list:
                    all_issues_flat.append({
                        'category_main': category_name,
                        'severity': severity_level,
                        'label': issue.get('label', 'N/A'),
                        'url_details': f"{issue.get('url', self.domain)} - {issue.get('details', 'N/A')}"
                    })

        if not all_issues_flat:
            flowables.append(Paragraph("Nessun problema specifico identificato nella nuova struttura.", self.styles['BodyText']))
            flowables.append(Spacer(1, 0.5 * inch))
            self.story.append(KeepTogether(flowables))
            return

        header_row = [
            Paragraph("Categoria", self.styles['SmallText']),
            Paragraph("Gravità", self.styles['SmallText']),
            Paragraph("Problema", self.styles['SmallText']),
            Paragraph("URL/Dettagli", self.styles['SmallText'])
        ]
        data = [header_row]

        for issue_item in all_issues_flat:
            data.append([
                Paragraph(issue_item['category_main'], self.styles['SmallText']),
                Paragraph(issue_item['severity'], self.styles['SmallText']),
                Paragraph(issue_item['label'], self.styles['SmallText']),
                Paragraph(issue_item['url_details'], self.styles['SmallText'])
            ])

        # Calculate available width for full-width table
        available_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        # Define relative column widths
        col_widths = [available_width * 0.25, available_width * 0.15, available_width * 0.30, available_width * 0.30]
        table = Table(data, colWidths=col_widths)

        # Define colors and fonts from PDF_CONFIG for clarity and consistency
        color_header_bg = PDF_CONFIG['colors'].get('primary_dark', '#004080')
        # color_header_text = PDF_CONFIG['colors'].get('white', '#FFFFFF') # Will be changed to black
        color_row_odd = PDF_CONFIG['colors'].get('light_gray_alt', '#E8EFF5')
        color_row_even = PDF_CONFIG['colors'].get('white', '#FFFFFF')
        color_border = PDF_CONFIG['colors'].get('border_light', '#B0C4DE')
        font_header = PDF_CONFIG['font_family_bold']
        font_body = PDF_CONFIG['font_family']
        fontsize_header = PDF_CONFIG['font_sizes'].get('small', 9)
        fontsize_body = PDF_CONFIG['font_sizes'].get('extra_small', 8) # Matches SmallText style
        color_text_body = PDF_CONFIG['colors'].get('text_primary', '#222222')

        HEADER_OUTLINE_COLOR = colors.HexColor('#FFCC00') # Amber/Yellow
        NEW_HEADER_BG_COLOR = colors.HexColor('#f5f5f5')

        issues_table_style_cmds = [
            # Header Row Styling
            ('BACKGROUND', (0, 0), (-1, 0), NEW_HEADER_BG_COLOR), # New light gray background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), # Ensure black text
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), font_header),
            ('FONTSIZE', (0, 0), (-1, 0), fontsize_header),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Individual BOX for each header cell for #FFCC00 outline
            ('BOX', (0,0), (0,0), 1.5, HEADER_OUTLINE_COLOR),
            ('BOX', (1,0), (1,0), 1.5, HEADER_OUTLINE_COLOR),
            ('BOX', (2,0), (2,0), 1.5, HEADER_OUTLINE_COLOR),

            # Data Rows Styling
            ('FONTNAME', (0, 1), (-1, -1), font_body),
            ('FONTSIZE', (0, 1), (-1, -1), fontsize_body),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor(color_text_body)),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor(color_row_even)), # Default for even data rows
        ]

        issues_table_style = TableStyle(issues_table_style_cmds)

        # Apply odd row striping
        for i in range(1, len(data)): # Start from 1 to skip header
            if i % 2 != 0:
                issues_table_style.add('BACKGROUND', (0, i), (-1, i), HexColor(color_row_odd))

        # General table grid (applied first, header BOXes will draw over it for header cells)
        issues_table_style.add('GRID', (0,0), (-1,-1), 0.5, HexColor(color_border))
        # Overall table border (can be same as grid or slightly thicker)
        issues_table_style.add('BOX', (0,0), (-1,-1), 1, HexColor(color_border))

        table.setStyle(issues_table_style)
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
        header_row = [Paragraph("Parametro", self.styles['BodyText']), Paragraph("Valore", self.styles['BodyText'])]
        table_data = [header_row] # Add header row first

        for name, value in items:
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
        self.story.append(Paragraph("Analisi Dettagliata per Categoria", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Analisi dettagliata per categoria in fase di revisione.", self.styles['BodyText']))
        self.story.append(Spacer(1, 0.5 * inch))
        # Comment out the previous content generation for this section
        # detailed_issues = self.analysis_results.get('detailed_issues', {})
        # ... (rest of the original method content commented out) ...
        # self.story.append(PageBreak())

    def _add_recommendations_section(self):
        self.story.append(Paragraph("Raccomandazioni", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Sezione raccomandazioni in fase di revisione. Le raccomandazioni principali sono ora integrate nel Riassunto Esecutivo.", self.styles['BodyText']))
        self.story.append(Spacer(1, 0.5 * inch))
        # Comment out the previous content generation for this section
        # recommendations = self.analysis_results['recommendations']
        # ... (rest of the original method content commented out) ...
        # self.story.append(PageBreak())

    def _add_issue_details_appendix(self):
        # This method might be removed or significantly changed later.
        # For now, let's add a placeholder similar to other sections.
        self.story.append(Paragraph("Descrizione Dettagliata dei Problemi Comuni", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Sezione appendice descrizioni problemi in fase di revisione.", self.styles['BodyText']))
        self.story.append(Spacer(1, 0.5 * inch))

    def _get_evaluation_text(self, score):
        if score >= 90: return "Eccellente"
        elif score >= 70: return "Buono"
        elif score >= 50: return "Da Migliorare"
        else: return "Critico"
    
    def _get_status_text(self, score):
        if score >= 90: return "✓ Eccellente"
        elif score >= 70: return "⚠ Buono"
        elif score >= 50: return "⚠ Da Migliorare"
        else: return "✗ Critico"
    
    def _get_score_color_hex(self, score):
        if score >= 90: return '#28A745'
        elif score >= 70: return '#005A9C'
        elif score >= 50: return '#FFC107'
        else: return '#DC3545'

    def _identify_strengths_weaknesses(self):
        strengths = []
        # Strengths identification remains the same
        categories = {'Title Tags': self.analysis_results['title_analysis']['score'], 'Meta Descriptions': self.analysis_results['meta_description_analysis']['score'], 'Immagini': self.analysis_results['images_analysis']['score'], 'Contenuto': self.analysis_results['content_analysis']['score'], 'Performance': self.analysis_results['performance_analysis']['score'], 'SSL': self.analysis_results['ssl_analysis']['score'], 'Link Interni': self.analysis_results['links_analysis']['score'], 'Aspetti Tecnici': self.analysis_results['technical_analysis']['score']}
        for category, score in categories.items():
            if score >= 80: strengths.append(f"{category} ottimizzato correttamente (punteggio: {score}/100)")
            # Weaknesses based on scores are not included here anymore, as per new structure focusing on detailed_issues

        weaknesses_structured = {
            'errors': {},
            'warnings': {},
            'notices': {}
        }
        detailed_issues = self.analysis_results.get('detailed_issues', {})

        macro_map = {
            'errors': 'errors',
            'warnings': 'warnings',
            'notices': 'notices'
        }

        for macro_key, detailed_issue_list_key in macro_map.items():
            issues_list = detailed_issues.get(detailed_issue_list_key, [])
            if not isinstance(issues_list, list):
                continue

            for issue in issues_list:
                if not isinstance(issue, dict):
                    continue

                specific_type_key = issue.get('type', 'unknown_type')
                # Get user-friendly label or create a fallback
                user_friendly_label = PDF_ISSUE_TYPE_LABELS.get(specific_type_key, specific_type_key.replace('_', ' ').capitalize())

                # Prepare issue details for presentation
                # Prioritize 'image' for details if it exists, then 'details', then 'issue' field or 'N/A'
                details_text = issue.get('image', issue.get('details', issue.get('issue', 'N/A')))

                issue_entry = {
                    'url': issue.get('url', 'N/A'),
                    'details': details_text,
                    'type': specific_type_key  # Ensure original type is passed
                }

                if user_friendly_label not in weaknesses_structured[macro_key]:
                    weaknesses_structured[macro_key][user_friendly_label] = {
                        'type': specific_type_key, # Store the technical type for the group
                        'instances': []
                    }
                weaknesses_structured[macro_key][user_friendly_label]['instances'].append(issue_entry)

        # Remove macro categories if they are empty
        weaknesses_structured = {key: val for key, val in weaknesses_structured.items() if val}
        # Further filter out specific problem groups if they somehow ended up with no instances
        for macro_key in list(weaknesses_structured.keys()):
            for problem_label in list(weaknesses_structured[macro_key].keys()):
                if not weaknesses_structured[macro_key][problem_label]['instances']:
                    del weaknesses_structured[macro_key][problem_label]
            if not weaknesses_structured[macro_key]: # If macro category became empty
                del weaknesses_structured[macro_key]

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
            self._add_detailed_analysis_section()
            self._add_recommendations_section()
            # self.story.append(PageBreak()) # Page break might be desired before recommendations, or not, depending on flow. Let's keep it for now.
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
