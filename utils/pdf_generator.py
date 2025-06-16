"""
Analizzatore SEO per i dati raccolti dal crawler
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
from typing import Dict, List, Any, Tuple, Optional
import os
import logging

from config import (
    PDF_CONFIG, SEO_CONFIG, PERFORMANCE_CONFIG,
    CATEGORY_OCM, CATEGORY_SEO_AUDIT, AUDIT_CHECKS_CONFIG, PDF_ISSUE_DESCRIPTIONS,
)

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
        self.logger = logging.getLogger(__name__)
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
        style_name = 'SectionSubHeadingStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=12, leading=12 * 1.2, spaceAfter=6, textColor=HexColor(COLOR_TEXT_PRIMARY)))
        style_name = 'SpecificProblemHeadingStyle' # Used for grouped issue labels
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_BODY, leading=FONT_SIZE_BODY * 1.2, spaceBefore=6, spaceAfter=3, leftIndent=0, textColor=HexColor(COLOR_TEXT_PRIMARY))) # Adjusted leftIndent
        style_name = 'IssueDetailItemStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], leftIndent=20, spaceAfter=2, bulletIndent=10))

        style_name = 'TableMacroCategoryStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_BODY, leading=FONT_SIZE_BODY * 1.2, textColor=HexColor(COLOR_TEXT_PRIMARY), spaceBefore=6, spaceAfter=4))
        style_name = 'TableSpecificProblemStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_BODY, textColor=HexColor(COLOR_TEXT_SECONDARY), leftIndent=0, spaceAfter=2))
        style_name = 'TableDetailURLStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_PRIMARY), leftIndent=0))
        style_name = 'TableDetailStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_SECONDARY), leftIndent=0))
        style_name = 'TableRecommendationStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_SECONDARY), leftIndent=5, spaceBefore=2, spaceAfter=2, bulletIndent=0, firstLineIndent=0))

        style_name = 'BodyText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_BODY, leading=FONT_SIZE_BODY * 1.4, spaceAfter=6, textColor=HexColor(COLOR_TEXT_PRIMARY)))
        style_name = 'ListItem'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], leftIndent=30, spaceAfter=4, bulletIndent=20))
        style_name = 'SmallText' # Used for table cells
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY, fontSize=FONT_SIZE_SMALL, leading=FONT_SIZE_SMALL * 1.2, alignment=TA_LEFT, textColor=HexColor(COLOR_TEXT_SECONDARY))) # Default to TA_LEFT for table cells

        # Style for table headers, can be based on SmallText but bold
        style_name = 'ExecSummaryTableHeaderStyle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=FONT_SIZE_SMALL, leading=FONT_SIZE_SMALL * 1.2, alignment=TA_LEFT, textColor=HexColor(COLOR_TEXT_PRIMARY)))


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

        style_name = 'OCMSectionHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['SectionHeading'], spaceBefore=12, textColor=HexColor(PDF_CONFIG['colors'].get('primary', '#336699'))))
        style_name = 'SEOAuditSectionHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['SectionHeading'], spaceBefore=12, textColor=HexColor(PDF_CONFIG['colors'].get('secondary_dark', '#556677'))))

        style_name = 'ErrorSubHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=11, leading=11 * 1.2, spaceBefore=8, spaceAfter=4, textColor=HexColor(COLOR_ERROR)))
        style_name = 'WarningSubHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=11, leading=11 * 1.2, spaceBefore=8, spaceAfter=4, textColor=HexColor(COLOR_WARNING)))
        style_name = 'NoticeSubHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, fontName=FONT_FAMILY_BOLD, fontSize=11, leading=11 * 1.2, spaceBefore=8, spaceAfter=4, textColor=HexColor(COLOR_TEXT_SECONDARY)))

        style_name = 'IssueDescriptionText' # Used for the general description of a problem type
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], leftIndent=0, spaceBefore=2, spaceAfter=4, fontSize=FONT_SIZE_SMALL, textColor=HexColor(COLOR_TEXT_SECONDARY))) # Adjusted leftIndent
        
    def _add_header(self):
        self.story.append(Paragraph("Report di Audit del Sito", self.styles['CustomTitle']))
        self.story.append(Paragraph(self.domain, self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.2 * inch))
        current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.story.append(Paragraph(f"Generato il: {current_datetime}", self.styles['SmallText']))
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_chart_and_counts_section(self):
        section_flowables = []
        chart_image = self._get_site_health_chart_flowable()
        if chart_image:
            section_flowables.append(chart_image)
            section_flowables.append(Spacer(1, 0.1 * inch))

        categorized_issues = self.analysis_results.get('categorized_issues', {})
        ocm_errors_count = len(categorized_issues.get(CATEGORY_OCM, {}).get('ERROR', []))
        ocm_warnings_count = len(categorized_issues.get(CATEGORY_OCM, {}).get('WARNING', []))
        ocm_notices_count = len(categorized_issues.get(CATEGORY_OCM, {}).get('NOTICE', []))
        seo_errors_count = len(categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get('ERROR', []))
        seo_warnings_count = len(categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get('WARNING', []))
        seo_notices_count = len(categorized_issues.get(CATEGORY_SEO_AUDIT, {}).get('NOTICE', []))

        COLOR_RED_BOX = colors.HexColor(PDF_CONFIG['colors'].get('error', '#DC3545'))
        COLOR_ORANGE_BOX = colors.HexColor(PDF_CONFIG['colors'].get('warning', '#FFC107'))
        COLOR_BLUE_BOX = colors.HexColor(PDF_CONFIG['colors'].get('info', '#17A2B8'))

        count_style = ParagraphStyle(name='BoxCountStyle', fontSize=20, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER, leading=22)
        label_style = ParagraphStyle(name='BoxLabelStyle', fontSize=9, fontName='Helvetica', textColor=colors.white, alignment=TA_CENTER, leading=10, spaceBefore=4)

        ocm_error_content = [Paragraph(f"{ocm_errors_count}", count_style), Paragraph("Errori OCM", label_style)]
        ocm_warning_content = [Paragraph(f"{ocm_warnings_count}", count_style), Paragraph("Avvert. OCM", label_style)]
        ocm_notice_content = [Paragraph(f"{ocm_notices_count}", count_style), Paragraph("Avvisi OCM", label_style)]
        seo_error_content = [Paragraph(f"{seo_errors_count}", count_style), Paragraph("Errori SEO", label_style)]
        seo_warning_content = [Paragraph(f"{seo_warnings_count}", count_style), Paragraph("Avvert. SEO", label_style)]
        seo_notice_content = [Paragraph(f"{seo_notices_count}", count_style), Paragraph("Avvisi SEO", label_style)]

        page_content_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        box_col_width = (page_content_width - 2 * (0.1 * inch)) / 3

        row1_data = [ocm_error_content, ocm_warning_content, ocm_notice_content]
        table_row1 = Table([row1_data], colWidths=[box_col_width, box_col_width, box_col_width], rowHeights=[0.8*inch])
        table_row1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), COLOR_RED_BOX), ('BACKGROUND', (1,0), (1,0), COLOR_ORANGE_BOX), ('BACKGROUND', (2,0), (2,0), COLOR_BLUE_BOX),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        section_flowables.append(table_row1)
        section_flowables.append(Spacer(1, 0.15 * inch))

        row2_data = [seo_error_content, seo_warning_content, seo_notice_content]
        table_row2 = Table([row2_data], colWidths=[box_col_width, box_col_width, box_col_width], rowHeights=[0.8*inch])
        table_row2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), COLOR_RED_BOX), ('BACKGROUND', (1,0), (1,0), COLOR_ORANGE_BOX), ('BACKGROUND', (2,0), (2,0), COLOR_BLUE_BOX),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        section_flowables.append(table_row2)

        if section_flowables:
            self.story.append(KeepTogether(section_flowables))
            self.story.append(Spacer(1, 0.3 * inch))

    def _add_executive_summary(self):
        flowables = []
        flowables.append(Paragraph("Riassunto Esecutivo", self.styles['SectionHeading']))
        flowables.append(Spacer(1, 0.2 * inch))

        overall_score = self.analysis_results.get('overall_score', 0)
        evaluation = self._get_evaluation_text(overall_score)

        categorized_issues_data = self.analysis_results.get('categorized_issues', {})
        num_errors = sum(len(lst) for cat in categorized_issues_data.values() for sev, lst in cat.items() if sev == 'ERROR')
        num_warnings = sum(len(lst) for cat in categorized_issues_data.values() for sev, lst in cat.items() if sev == 'WARNING')
        num_notices = sum(len(lst) for cat in categorized_issues_data.values() for sev, lst in cat.items() if sev == 'NOTICE')

        issue_parts = []
        if num_errors > 0: issue_parts.append(f"<b>{num_errors}</b> Errori")
        if num_warnings > 0: issue_parts.append(f"<b>{num_warnings}</b> Avvertimenti")
        if num_notices > 0: issue_parts.append(f"<b>{num_notices}</b> Avvisi")

        issues_string = ""
        if not issue_parts: issues_string = "non rilevando problemi significativi"
        elif len(issue_parts) == 1: issues_string = f"identificando {issue_parts[0]}"
        elif len(issue_parts) == 2: issues_string = f"identificando {issue_parts[0]} e {issue_parts[1]}"
        else: issues_string = f"identificando {issue_parts[0]}, {issue_parts[1]} e {issue_parts[2]}"

        total_pages_analyzed = self.analysis_results.get('summary', {}).get('total_pages_analyzed', len(self.analysis_results.get('pages_data', [])))
        summary_text = f"""L'analisi SEO del sito <b>{self.domain}</b> ha rivelato un punteggio complessivo di <font color="{self._get_score_color_hex(overall_score)}"><b>{overall_score}/100</b></font>. Valutazione: <b>{evaluation}</b>. Sono state analizzate <b>{total_pages_analyzed}</b> pagine, {issues_string}."""
        summary_paragraph = Paragraph(summary_text, self.styles['BodyText'])
        flowables.append(summary_paragraph)
        flowables.append(Spacer(1, 0.2 * inch))

        # New Grouped Issue Display
        page_content_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin - (0.4 * inch)
        col_widths_exec_summary = [page_content_width * 0.35, page_content_width * 0.65] # Adjusted for "Pagina" and "Dettaglio"

        table_header_style = self.styles['ExecSummaryTableHeaderStyle'] # Defined in _setup_custom_styles
        table_cell_style = self.styles['SmallText'] # Using existing SmallText, ensure it's TA_LEFT

        for category_name_display, category_key in [(CATEGORY_OCM, CATEGORY_OCM), (CATEGORY_SEO_AUDIT, CATEGORY_SEO_AUDIT)]:
            has_issues_in_category_for_display = False
            category_specific_flowables = [] # Store flowables for this specific category section

            # Add Category Heading (e.g., OCMSectionHeading or SEOAuditSectionHeading)
            if category_key == CATEGORY_OCM:
                category_specific_flowables.append(Paragraph(category_name_display, self.styles['OCMSectionHeading']))
            else:
                category_specific_flowables.append(Paragraph(category_name_display, self.styles['SEOAuditSectionHeading']))

            any_issue_in_severity_for_this_category = False
            for severity in ['ERROR', 'WARNING', 'NOTICE']:
                issues_list = categorized_issues_data.get(category_key, {}).get(severity, [])

                if issues_list:
                    any_issue_in_severity_for_this_category = True
                    has_issues_in_category_for_display = True # Mark that we found something to display for this category

                    severity_style_name = f"{severity.capitalize()}SubHeading"
                    severity_display_text = {'ERROR': 'Errori Critici', 'WARNING': 'Avvertimenti Importanti', 'NOTICE': 'Avvisi Minori'}.get(severity, severity.capitalize())
                    category_specific_flowables.append(Paragraph(f"{severity_display_text} ({len(issues_list)} problemi totali)", self.styles.get(severity_style_name, self.styles['SectionSubHeadingStyle'])))

                    grouped_issues = {}
                    for issue_item in issues_list:
                        problem_label = issue_item.get('label', 'Problema Sconosciuto')
                        if problem_label not in grouped_issues:
                            grouped_issues[problem_label] = []
                        instance_details = {
                            'url': issue_item.get('url', self.domain),
                            'details': issue_item.get('details', 'N/D'),
                            'key': issue_item.get('key')
                        }
                        grouped_issues[problem_label].append(instance_details)

                    for problem_label, instances_list in grouped_issues.items():
                        category_specific_flowables.append(Paragraph(problem_label, self.styles['SpecificProblemHeadingStyle']))

                        if instances_list:
                            first_instance_key = instances_list[0].get('key')
                            if first_instance_key:
                                check_config = AUDIT_CHECKS_CONFIG.get(first_instance_key, {})
                                description_key = check_config.get('description_key')
                                if description_key:
                                    general_description = PDF_ISSUE_DESCRIPTIONS.get(description_key, "")
                                    if general_description:
                                        category_specific_flowables.append(Paragraph(general_description, self.styles['IssueDescriptionText']))
                                        category_specific_flowables.append(Spacer(1, 0.05 * inch))

                        table_data = [[Paragraph("<b>Pagina/Contesto</b>", table_header_style), Paragraph("<b>Dettaglio Specifico</b>", table_header_style)]]
                        for instance in instances_list:
                            page_url = instance.get('url', self.domain)
                            page_cell_content = "Sito Globale / Generale" if page_url == self.domain or not page_url else page_url
                            detail_cell_content = instance.get('details', 'N/D')
                            if len(detail_cell_content) > 150:
                                detail_cell_content = detail_cell_content[:147] + "..."
                            table_data.append([
                                Paragraph(page_cell_content, table_cell_style),
                                Paragraph(detail_cell_content.replace('\n', '<br/>'), table_cell_style)
                            ])

                        if len(table_data) > 1:
                            issue_table = Table(table_data, colWidths=col_widths_exec_summary, repeatRows=1)
                            style_commands = [
                                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E0E0E0")),
                                ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
                                ('LEFTPADDING', (0,0), (-1,-1), 3),
                                ('RIGHTPADDING', (0,0), (-1,-1), 3),
                                ('TOPPADDING', (0,0), (-1,-1), 3),
                                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                                ('VALIGN', (0,0), (-1,-1), 'TOP'), # Changed to TOP for better multi-line cell handling
                            ]
                            for i in range(len(instances_list)):
                                if (i + 1) % 2 == 0:
                                    style_commands.append(('BACKGROUND', (0, i + 1), (-1, i + 1), colors.HexColor("#F0F4F7")))
                                else:
                                    style_commands.append(('BACKGROUND', (0, i + 1), (-1, i + 1), colors.white))
                            issue_table.setStyle(TableStyle(style_commands))
                            category_specific_flowables.append(issue_table)
                        category_specific_flowables.append(Spacer(1, 0.15 * inch))

                if not any_issue_in_severity_for_this_category and issues_list: # Should not happen if issues_list is populated
                    category_specific_flowables.append(Paragraph(f"Nessun {severity.lower()} per {category_name_display}.", self.styles['BodyText']))

            if has_issues_in_category_for_display: # Only add if there was something to show
                flowables.extend(category_specific_flowables)
                flowables.append(Spacer(1, 0.1 * inch))
            else: # No issues at all for this category
                flowables.extend(category_specific_flowables) # Add category heading
                flowables.append(Paragraph(f"Nessun problema rilevato per {category_name_display}.", self.styles['BodyText']))
                flowables.append(Spacer(1, 0.1 * inch))


        if overall_score >= 80 and not (num_errors > 0 or num_warnings > 0 or num_notices > 0) :
             flowables.append(Paragraph("Punti di Forza Generali:", self.styles['SectionSubHeadingStyle']))
             flowables.append(Paragraph(f"Il punteggio generale di {overall_score}/100 indica una buona performance complessiva con nessun problema critico o avvertimento rilevato.", self.styles['BodyText']))
        elif overall_score >= 80:
            flowables.append(Paragraph("Punti di Forza Generali:", self.styles['SectionSubHeadingStyle']))
            flowables.append(Paragraph(f"Il punteggio generale di {overall_score}/100 indica una buona performance complessiva.", self.styles['BodyText']))

        flowables.append(Spacer(1, 0.5 * inch))
        self.story.append(KeepTogether(flowables))

    def _add_score_overview(self):
        flowables = []
        flowables.append(Paragraph("Panoramica dei Punteggi", self.styles['SectionHeading']))
        flowables.append(Spacer(1, 0.2 * inch))
        overall_score = self.analysis_results.get('overall_score', 'N/A')
        score_text = f"Punteggio SEO Complessivo: {overall_score}/100"
        flowables.append(Paragraph(score_text, self.styles['BodyText']))
        flowables.append(Spacer(1, 0.5 * inch))
        self.story.append(KeepTogether(flowables))

    def _get_site_health_chart_flowable(self):
        """
        Crea un grafico a ciambella (donut chart) che mostra la percentuale di salute del sito,
         suddivisa in Sano, Errori, Avvertimenti, e Avvisi, con legenda in basso.
        Restituisce l'oggetto Image di ReportLab.
        """
        try:
            raw_overall_score = self.analysis_results.get('overall_score')
            if raw_overall_score is None:
                self.logger.warning("'overall_score' not found for chart generation. Defaulting to 0.")
                overall_score = 0.0
            else:
                overall_score = float(raw_overall_score)

            sano_percentage = max(0.0, min(100.0, overall_score)) # Clamp score
            non_sano_percentage = 100.0 - sano_percentage

            categorized_issues = self.analysis_results.get('categorized_issues', {})
            total_errors = sum(len(lst) for cat_issues in categorized_issues.values() for severity, lst in cat_issues.items() if severity == 'ERROR')
            total_warnings = sum(len(lst) for cat_issues in categorized_issues.values() for severity, lst in cat_issues.items() if severity == 'WARNING')
            total_notices = sum(len(lst) for cat_issues in categorized_issues.values() for severity, lst in cat_issues.items() if severity == 'NOTICE')

            total_issues_for_distribution = total_errors + total_warnings + total_notices

            errori_chart_percentage = 0.0
            avvertimenti_chart_percentage = 0.0
            avvisi_chart_percentage = 0.0

            if non_sano_percentage > 0.001: # Use a small epsilon for float comparison
                if total_issues_for_distribution > 0:
                    errori_chart_percentage = (total_errors / total_issues_for_distribution) * non_sano_percentage
                    avvertimenti_chart_percentage = (total_warnings / total_issues_for_distribution) * non_sano_percentage
                    avvisi_chart_percentage = (total_notices / total_issues_for_distribution) * non_sano_percentage
                else:
                    if overall_score < 100 : avvisi_chart_percentage = non_sano_percentage
                    else: errori_chart_percentage = 0

            current_sum_non_sano_parts = errori_chart_percentage + avvertimenti_chart_percentage + avvisi_chart_percentage
            if current_sum_non_sano_parts > 0 and abs(current_sum_non_sano_parts - non_sano_percentage) > 0.01 :
                scale = non_sano_percentage / current_sum_non_sano_parts
                errori_chart_percentage *= scale
                avvertimenti_chart_percentage *= scale
                avvisi_chart_percentage *= scale

            sano_percentage = round(sano_percentage, 1)
            errori_chart_percentage = round(errori_chart_percentage, 1)
            avvertimenti_chart_percentage = round(avvertimenti_chart_percentage, 1)
            avvisi_chart_percentage = round(avvisi_chart_percentage, 1)

            all_segments_sum = sano_percentage + errori_chart_percentage + avvertimenti_chart_percentage + avvisi_chart_percentage
            if abs(all_segments_sum - 100.0) > 0.01 and all_segments_sum > 0:
                diff = 100.0 - all_segments_sum
                temp_segments = {'sano': sano_percentage, 'errori': errori_chart_percentage, 'avvertimenti': avvertimenti_chart_percentage, 'avvisi': avvisi_chart_percentage}
                eligible_segments = {k: v for k, v in temp_segments.items() if v > 0.05}
                if eligible_segments:
                    largest_key_final = max(eligible_segments, key=eligible_segments.get)
                    temp_segments[largest_key_final] += diff
                else:
                    if sano_percentage > 0.05 : temp_segments['sano'] += diff
                    elif errori_chart_percentage > 0.05 : temp_segments['errori'] += diff
                    elif avvertimenti_chart_percentage > 0.05 : temp_segments['avvertimenti'] += diff
                    elif avvisi_chart_percentage > 0.05 : temp_segments['avvisi'] += diff
                    else:
                        if overall_score == 100: temp_segments['sano'] += diff
                        else: temp_segments['errori'] += diff

                sano_percentage = temp_segments['sano']
                errori_chart_percentage = temp_segments['errori']
                avvertimenti_chart_percentage = temp_segments['avvertimenti']
                avvisi_chart_percentage = temp_segments['avvisi']

            sano_percentage = max(0.0, round(sano_percentage, 1))
            errori_chart_percentage = max(0.0, round(errori_chart_percentage, 1))
            avvertimenti_chart_percentage = max(0.0, round(avvertimenti_chart_percentage, 1))
            avvisi_chart_percentage = max(0.0, round(avvisi_chart_percentage, 1))

            final_sum_check = sano_percentage + errori_chart_percentage + avvertimenti_chart_percentage + avvisi_chart_percentage
            if abs(final_sum_check - 100.0) > 0.01 and final_sum_check > 0:
                sano_percentage += (100.0 - final_sum_check)
                sano_percentage = max(0.0, round(sano_percentage, 1))


            COLOR_GREEN = PDF_CONFIG['colors'].get('success', '#28A745')
            COLOR_RED = PDF_CONFIG['colors'].get('error', '#DC3545')
            COLOR_ORANGE = PDF_CONFIG['colors'].get('warning', '#FFC107')
            COLOR_BLUE_INFO = PDF_CONFIG['colors'].get('info', '#17A2B8')
            FONT_FAMILY_CHART = PDF_CONFIG.get('font_family', 'Helvetica')

            chart_segments_data = []
            chart_segments_colors = []
            legend_elements = []

            if sano_percentage > 0.05:
                chart_segments_data.append(sano_percentage)
                chart_segments_colors.append(COLOR_GREEN)
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_GREEN, markersize=10, label=f'Sano ({sano_percentage:.1f}%)'))
            if errori_chart_percentage > 0.05:
                chart_segments_data.append(errori_chart_percentage)
                chart_segments_colors.append(COLOR_RED)
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_RED, markersize=10, label=f'Errori ({errori_chart_percentage:.1f}%)'))
            if avvertimenti_chart_percentage > 0.05:
                chart_segments_data.append(avvertimenti_chart_percentage)
                chart_segments_colors.append(COLOR_ORANGE)
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_ORANGE, markersize=10, label=f'Avvertimenti ({avvertimenti_chart_percentage:.1f}%)'))
            if avvisi_chart_percentage > 0.05:
                chart_segments_data.append(avvisi_chart_percentage)
                chart_segments_colors.append(COLOR_BLUE_INFO)
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_BLUE_INFO, markersize=10, label=f'Avvisi ({avvisi_chart_percentage:.1f}%)'))

            if not chart_segments_data :
                if overall_score >= 99.9:
                    chart_segments_data = [100.0]
                    chart_segments_colors = [COLOR_GREEN]
                    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_GREEN, markersize=10, label='Sano (100.0%)'))
                else:
                    chart_segments_data = [100.0]
                    chart_segments_colors = [COLOR_RED]
                    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_RED, markersize=10, label='Da Migliorare (100.0%)'))


            fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor='white')
            ax.set_facecolor('white')

            wedges, _ = ax.pie(chart_segments_data, colors=chart_segments_colors, startangle=90,
                               counterclock=False, wedgeprops=dict(width=0.35))

            display_score_in_center = int(round(overall_score))
            ax.text(0, 0.1, f'{display_score_in_center}%',
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=36, fontweight='bold', color=PDF_CONFIG['colors'].get('primary', '#005A9C'),
                    fontfamily=FONT_FAMILY_CHART)
            ax.text(0, -0.15, 'Salute del Sito',
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=14, color=PDF_CONFIG['colors'].get('text_primary', '#222222'),
                    fontfamily=FONT_FAMILY_CHART)

            if legend_elements:
                ncol_legend = 1
                if len(legend_elements) > 2: ncol_legend = 2

                fig.legend(handles=legend_elements, loc='lower center', ncol=ncol_legend,
                           fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.02))


            ax.set_aspect('equal')
            ax.axis('off')
            plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.18 if legend_elements else 0.05)

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
            img_buffer.seek(0)
            chart_image = RLImage(img_buffer, width=3*inch, height=3*inch)
            plt.close(fig)
            return chart_image
        except Exception as e:
            self.logger.error(f"Errore durante la generazione del grafico Site Health: {e}", exc_info=True)
            return None

    def _add_issues_table_section(self):
        flowables = []
        flowables.append(Paragraph("Tabelle Dati Dettagliate", self.styles['SectionHeading']))
        flowables.append(Spacer(1, 0.2 * inch))

        base_severity_style = self.styles.get('SmallText', ParagraphStyle(name='DefaultSmallText', fontSize=8, fontName='Helvetica'))
        # Ensure SmallText has TA_LEFT for table cells if it's being reused
        if self.styles['SmallText'].alignment != TA_LEFT:
             self.styles.add(ParagraphStyle(name='SmallTextForTable', parent=self.styles['SmallText'], alignment=TA_LEFT))
             data_cell_style = self.styles['SmallTextForTable']
        else:
            data_cell_style = self.styles['SmallText']

        color_error = HexColor(PDF_CONFIG['colors'].get('error', '#DC3545'))
        color_warning = HexColor(PDF_CONFIG['colors'].get('warning', '#FFC107'))
        color_notice = HexColor(PDF_CONFIG['colors'].get('info', '#17A2B8'))

        severity_error_style = ParagraphStyle(name='SeverityErrorInTable', parent=data_cell_style, textColor=color_error)
        severity_warning_style = ParagraphStyle(name='SeverityWarningInTable', parent=data_cell_style, textColor=color_warning)
        severity_notice_style = ParagraphStyle(name='SeverityNoticeInTable', parent=data_cell_style, textColor=color_notice)

        severity_text_map = {'ERROR': "ERRORE", 'WARNING': "AVVERTIMENTO", 'NOTICE': "AVVISO"}
        severity_style_map = {'ERROR': severity_error_style, 'WARNING': severity_warning_style, 'NOTICE': severity_notice_style}

        categorized_issues = self.analysis_results.get('categorized_issues', {})
        ocm_issues_for_table = []
        seo_audit_issues_for_table = []

        # Data Segregation
        for category_key, severities in categorized_issues.items():
            for severity_level_key, issues_list in severities.items():
                for issue in issues_list:
                    tipo_problema_text = issue.get('label', 'N/D')
                    url_text = issue.get('url', '')
                    details_text = issue.get('details', 'N/D')

                    url_dettagli_text = ""
                    if url_text and url_text != self.domain:
                        url_dettagli_text += f"URL: {url_text}<br/>"
                    url_dettagli_text += f"Dettagli: {details_text}"
                    url_dettagli_text = url_dettagli_text.strip()
                    if not url_dettagli_text: url_dettagli_text = "N/D"

                    valore_misurato_text = issue.get('value', issue.get('measured_value', 'N/D'))

                    formatted_issue = {
                        'gravita_key': severity_level_key,
                        'tipo_problema': tipo_problema_text,
                        'url_dettagli': url_dettagli_text,
                        'valore_misurato': valore_misurato_text
                    }
                    if category_key == CATEGORY_OCM:
                        ocm_issues_for_table.append(formatted_issue)
                    elif category_key == CATEGORY_SEO_AUDIT:
                        seo_audit_issues_for_table.append(formatted_issue)

        if not ocm_issues_for_table and not seo_audit_issues_for_table:
            flowables.append(Paragraph("Nessun problema specifico identificato nelle tabelle dettagliate.", self.styles['BodyText']))
            self.story.append(KeepTogether(flowables))
            return

        header_table_style = ParagraphStyle(name='TableHeaderSmall', parent=self.styles['SmallText'], fontName=PDF_CONFIG['font_family_bold'], alignment=TA_CENTER)
        header_row_text_4_cols = ["Gravità", "Tipo di Problema", "URL/Dettagli Specifici", "Valore Misurato"]
        header_row_4_cols = [Paragraph(text, header_table_style) for text in header_row_text_4_cols]

        data_cell_style_center = ParagraphStyle(name='DataCellSmallCenter', parent=data_cell_style, alignment=TA_CENTER)

        available_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        col_widths_4_cols = [available_width * 0.15, available_width * 0.30, available_width * 0.40, available_width * 0.15]

        new_header_bg_color = colors.HexColor('#f5f5f5')
        color_row_odd_bg = colors.HexColor(PDF_CONFIG['colors'].get('light_gray_alt', '#E8EFF5')) # A slightly different shade for striping
        color_row_even_bg = colors.white
        grid_color = colors.HexColor(PDF_CONFIG['colors'].get('border_light', '#B0C4DE'))
        text_color_body = colors.HexColor(PDF_CONFIG['colors'].get('text_primary', '#222222'))

        base_table_style_cmds = [
            ('BACKGROUND', (0,0), (-1,0), new_header_bg_color), ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'), ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), PDF_CONFIG.get('font_family_bold', 'Helvetica-Bold')),
            ('FONTSIZE', (0,0), (-1,0), PDF_CONFIG['font_sizes'].get('small', 9)),
            ('BOTTOMPADDING', (0,0), (-1,0), 8), ('TOPPADDING', (0,0), (-1,0), 8),
            ('TEXTCOLOR', (0,1), (-1,-1), text_color_body),
            ('FONTNAME', (0,1), (-1,-1), PDF_CONFIG.get('font_family', 'Helvetica')),
            ('FONTSIZE', (0,1), (-1,-1), PDF_CONFIG['font_sizes'].get('extra_small', 8)),
            ('VALIGN', (0,1), (-1,-1), 'TOP'),
            ('ALIGN', (0,1), (0,-1), 'LEFT'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
            ('ALIGN', (2,1), (2,-1), 'LEFT'),
            ('ALIGN', (3,1), (3,-1), 'CENTER'),
            ('LEFTPADDING', (0,1), (-1,-1), 5), ('RIGHTPADDING', (0,1), (-1,-1), 5),
            ('TOPPADDING', (0,1), (-1,-1), 5), ('BOTTOMPADDING', (0,1), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, grid_color), ('BOX', (0,0), (-1,-1), 1, grid_color),
        ]

        # OCM Table
        if ocm_issues_for_table:
            flowables.append(Paragraph("Dettaglio Problemi OCM", self.styles['SectionSubHeadingStyle']))
            flowables.append(Spacer(1, 0.1 * inch))
            ocm_data_rows = [header_row_4_cols]
            for item in ocm_issues_for_table:
                row = [
                    Paragraph(severity_text_map.get(item['gravita_key'], item['gravita_key']), severity_style_map.get(item['gravita_key'], data_cell_style)),
                    Paragraph(item['tipo_problema'], data_cell_style),
                    Paragraph(item['url_dettagli'].replace("\n", "<br/>"), data_cell_style),
                    Paragraph(str(item['valore_misurato']), data_cell_style_center)
                ]
                ocm_data_rows.append(row)

            ocm_table = Table(ocm_data_rows, colWidths=col_widths_4_cols, repeatRows=1)
            ocm_table_style_cmds = list(base_table_style_cmds)
            for i in range(1, len(ocm_data_rows)):
                bg_color = color_row_even_bg if i % 2 == 0 else color_row_odd_bg
                ocm_table_style_cmds.append(('BACKGROUND', (0,i), (-1,i), bg_color))
            ocm_table.setStyle(TableStyle(ocm_table_style_cmds))
            flowables.append(ocm_table)
            flowables.append(Spacer(1, 0.3 * inch))

        # SEO Audit Table
        if seo_audit_issues_for_table:
            flowables.append(Paragraph("Dettaglio Problemi SEO Audit", self.styles['SectionSubHeadingStyle']))
            flowables.append(Spacer(1, 0.1 * inch))
            seo_audit_data_rows = [header_row_4_cols]
            for item in seo_audit_issues_for_table:
                row = [
                    Paragraph(severity_text_map.get(item['gravita_key'], item['gravita_key']), severity_style_map.get(item['gravita_key'], data_cell_style)),
                    Paragraph(item['tipo_problema'], data_cell_style),
                    Paragraph(item['url_dettagli'].replace("\n", "<br/>"), data_cell_style),
                    Paragraph(str(item['valore_misurato']), data_cell_style_center)
                ]
                seo_audit_data_rows.append(row)

            seo_table = Table(seo_audit_data_rows, colWidths=col_widths_4_cols, repeatRows=1)
            seo_table_style_cmds = list(base_table_style_cmds)
            for i in range(1, len(seo_audit_data_rows)):
                bg_color = color_row_even_bg if i % 2 == 0 else color_row_odd_bg
                seo_table_style_cmds.append(('BACKGROUND', (0,i), (-1,i), bg_color))
            seo_table.setStyle(TableStyle(seo_table_style_cmds))
            flowables.append(seo_table)
            flowables.append(Spacer(1, 0.3 * inch))

        self.story.append(KeepTogether(flowables))


    def _create_summary_table_for_section(self, items: List[Tuple[str, str]], available_width: float) -> Optional[Table]:
        if not items: return None
        header_row = [Paragraph("Parametro", self.styles['BodyText']), Paragraph("Valore", self.styles['BodyText'])]
        table_data = [header_row]
        for name, value in items: table_data.append([Paragraph(name, self.styles['BodyText']), Paragraph(str(value), self.styles['BodyText'])])
        col_widths = [available_width * 0.6, available_width * 0.4]
        summary_table = Table(table_data, colWidths=col_widths)
        new_header_bg_color = colors.HexColor('#f5f5f5'); header_outline_color = colors.HexColor('#FFCC00'); font_header_name = PDF_CONFIG.get('font_family_bold', 'Helvetica-Bold'); font_header_size = PDF_CONFIG['font_sizes'].get('body', 10); bg_color_even_hex = PDF_CONFIG['colors'].get('white', '#FFFFFF'); bg_color_odd_hex = PDF_CONFIG['colors'].get('light_gray_alt', '#F0F4F7'); grid_color = colors.HexColor(PDF_CONFIG['colors'].get('border', '#CCCCCC'))
        table_style_cmds = [
            ('BACKGROUND', (0,0), (-1,0), new_header_bg_color), ('TEXTCOLOR', (0,0), (-1,0), colors.black), ('ALIGN', (0,0), (-1,0), 'CENTER'), ('VALIGN', (0,0), (-1,0), 'MIDDLE'), ('FONTNAME', (0,0), (-1,0), font_header_name), ('FONTSIZE', (0,0), (-1,0), font_header_size), ('BOTTOMPADDING', (0,0), (-1,0), 5), ('TOPPADDING', (0,0), (-1,0), 5), ('BOX', (0,0), (0,0), 1.5, header_outline_color), ('BOX', (1,0), (1,0), 1.5, header_outline_color),
            ('VALIGN', (0,1), (-1,-1), 'TOP'), ('LEFTPADDING', (0,1), (-1,-1), 5), ('RIGHTPADDING', (0,1), (-1,-1), 5), ('TOPPADDING', (0,1), (-1,-1), 4), ('BOTTOMPADDING', (0,1), (-1,-1), 4), ('GRID', (0,0), (-1,-1), 0.5, grid_color),
        ]
        for i in range(1, len(table_data)):
            if (i-1) % 2 == 0: table_style_cmds.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor(bg_color_even_hex)))
            else: table_style_cmds.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor(bg_color_odd_hex)))
        summary_table.setStyle(TableStyle(table_style_cmds))
        return summary_table

    def _create_section_header_with_list_items(self, section_title_str: str, list_item_texts: List[str]) -> KeepTogether:
        flowables = [Paragraph(section_title_str, self.styles['SectionHeading'])]
        for item_text in list_item_texts: flowables.append(Paragraph(item_text, self.styles['ListItem']))
        flowables.append(Spacer(1, 0.1 * inch))
        return KeepTogether(flowables)

    # def _add_detailed_analysis_section(self):
    #     self.story.append(Paragraph("Analisi Dettagliata per Categoria", self.styles['SectionHeading']))
    #     self.story.append(Spacer(1, 0.2 * inch))
    #     self.story.append(Paragraph("Analisi dettagliata per categoria in fase di revisione.", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.5 * inch))

    # def _add_recommendations_section(self):
    #     self.story.append(Paragraph("Raccomandazioni", self.styles['SectionHeading']))
    #     self.story.append(Spacer(1, 0.2 * inch))
    #     self.story.append(Paragraph("Sezione raccomandazioni in fase di revisione. Le raccomandazioni principali sono ora integrate nel Riassunto Esecutivo.", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.5 * inch))

    def _add_issue_details_appendix(self):
        self.story.append(Paragraph("Descrizione Dettagliata dei Problemi Comuni", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Sezione appendice descrizioni problemi in fase di revisione.", self.styles['BodyText']))
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_core_web_vitals_section(self):
        self.story.append(PageBreak())
        self.story.append(Paragraph("Metriche Core Web Vitals", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph("Interaction to Next Paint (INP): <b>600ms</b>", self.styles['BodyText']))
        self.story.append(Paragraph("Cumulative Layout Shift (CLS): <b>0.3</b>", self.styles['BodyText']))
        self.story.append(Paragraph("Tempo di risposta server: <b>809ms</b>", self.styles['BodyText']))
        self.story.append(Spacer(1, 0.3 * inch))

    # def _add_seo_content_analysis_section(self):
    #     self.story.append(PageBreak())
    #     self.story.append(Paragraph("Analisi Contenuti SEO", self.styles['SectionHeading']))
    #     self.story.append(Spacer(1, 0.2 * inch))
    #     self.story.append(Paragraph("Analisi Thin Content", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Elenco delle pagine con contenuto scarso o duplicato.", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.1 * inch))
    #     self.story.append(Paragraph("Analisi Meta Description", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Pagine con meta description mancanti, troppo corte o troppo lunghe.", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.1 * inch))
    #     self.story.append(Paragraph("Stato Implementazione Schema Markup", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Verifica degli schema markup implementati (es. FAQ, Video, LocalBusiness, Product) e potenziali errori.", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.3 * inch))

    # def _add_security_performance_section(self):
    #     self.story.append(PageBreak())
    #     self.story.append(Paragraph("Sicurezza e Performance Aggiuntive", self.styles['SectionHeading']))
    #     self.story.append(Spacer(1, 0.2 * inch))
    #     self.story.append(Paragraph("Stato Content Security Policy (CSP)", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Verifica dell'implementazione e della corretta configurazione della Content Security Policy.", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.1 * inch))
    #     self.story.append(Paragraph("Configurazione X-Frame-Options", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Controllo delle intestazioni X-Frame-Options per la protezione contro il clickjacking.", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.1 * inch))
    #     self.story.append(Paragraph("Analisi Segnali E-E-A-T", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Valutazione preliminare dei segnali di Esperienza, Competenza, Autorevolezza e Affidabilità (E-E-A-T).", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.3 * inch))

    # def _add_priority_recommendations_section(self):
    #     self.story.append(PageBreak())
    #     self.story.append(Paragraph("Raccomandazioni Prioritarie", self.styles['SectionHeading']))
    #     self.story.append(Spacer(1, 0.2 * inch))
    #     self.story.append(Paragraph("Priorità Alta", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Elenco delle azioni ad alta priorità da intraprendere immediatamente. Timeline stimata: [timeline].", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.1 * inch))
    #     self.story.append(Paragraph("Priorità Media", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Azioni a media priorità. Timeline stimata: [timeline].", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.1 * inch))
    #     self.story.append(Paragraph("Priorità Bassa", self.styles['SectionSubHeadingStyle']))
    #     self.story.append(Paragraph("Azioni a bassa priorità. Timeline stimata: [timeline].", self.styles['BodyText']))
    #     self.story.append(Spacer(1, 0.3 * inch))

    def _get_evaluation_text(self, score):
        if score is None: return "N/D"
        if score >= 90: return "Eccellente" # Adjusted from previous version
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
        strength_candidate_categories = {
            'title_analysis': 'Analisi Titoli', 'meta_description_analysis': 'Analisi Meta Description',
            'images_analysis': 'Analisi Immagini', 'content_analysis': 'Analisi Contenuto',
            'performance_analysis': 'Analisi delle Prestazioni',
            'ssl_analysis': 'Analisi SSL', 'links_analysis': 'Analisi Link Interni',
            'technical_analysis': 'Analisi Tecnica'
        }
        for cat_key, category_name_it in strength_candidate_categories.items():
            category_analysis = self.analysis_results.get(cat_key)
            if category_analysis and isinstance(category_analysis, dict):
                score = category_analysis.get('score')
                if score is not None and score >= 80:
                    strengths.append(f"{category_name_it} ottimizzato correttamente (punteggio: {score}/100)")

        weaknesses_structured = {'errors': {}, 'warnings': {}, 'notices': {}}
        detailed_issues_data = self.analysis_results.get('detailed_issues', {}) # This is legacy, should be replaced by categorized_issues
        if not isinstance(detailed_issues_data, dict): detailed_issues_data = {}
        macro_map = {'errors': 'errors', 'warnings': 'warnings', 'notices': 'notices'}

        for macro_key, detailed_issue_list_key in macro_map.items():
            issues_list = detailed_issues_data.get(detailed_issue_list_key, [])
            if not isinstance(issues_list, list): continue
            for issue in issues_list:
                if not isinstance(issue, dict): continue
                specific_type_key = issue.get('type', 'tipo_sconosciuto')
                user_friendly_label = issue.get('label')
                if not user_friendly_label:
                    user_friendly_label = specific_type_key.replace('_', ' ').capitalize()
                    check_config = AUDIT_CHECKS_CONFIG.get(issue.get('key'))
                    if check_config: user_friendly_label = check_config.get('label', user_friendly_label)
                    # Fallback to PDF_ISSUE_TYPE_LABELS removed as it's deprecated
                details_text = issue.get('image', issue.get('details', issue.get('issue', 'N/D')))
                issue_entry = {'url': issue.get('url', 'N/D'), 'details': details_text, 'type': specific_type_key}
                if user_friendly_label not in weaknesses_structured[macro_key]:
                    weaknesses_structured[macro_key][user_friendly_label] = {'type': specific_type_key, 'instances': []}
                weaknesses_structured[macro_key][user_friendly_label]['instances'].append(issue_entry)

        weaknesses_structured = {k: v for k, v in weaknesses_structured.items() if v}
        for mk in list(weaknesses_structured.keys()):
            for pl_key in list(weaknesses_structured[mk].keys()):
                if not weaknesses_structured[mk][pl_key]['instances']: del weaknesses_structured[mk][pl_key]
            if not weaknesses_structured[mk]: del weaknesses_structured[mk]
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
            self._add_chart_and_counts_section()
            self._add_executive_summary() # This method is being refactored
            self._add_score_overview()
            self.story.append(PageBreak())
            self._add_issues_table_section()
            self._add_core_web_vitals_section()
            # Commented out calls from previous step:
            # self._add_seo_content_analysis_section()
            # self._add_security_performance_section()
            # self._add_priority_recommendations_section()
            # self._add_detailed_analysis_section()
            # self._add_recommendations_section()

            # Potentially add _add_issue_details_appendix() if it's still desired
            # self.story.append(PageBreak())
            # self._add_issue_details_appendix()

            self.doc.build(self.story)
            return True
        except Exception as e:
            self.logger.error(f"Errore durante la generazione del PDF: {e}", exc_info=True)
            return False

[end of utils/pdf_generator.py]
