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

from config import * # Assicurati che config.py sia accessibile e contenga i colori PDF_CONFIG['colors']
from config import PDF_ISSUE_TYPE_LABELS # Import the new labels

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
        flowables.append(Spacer(1, 0.2 * inch))


        strengths, weaknesses = self._identify_strengths_weaknesses()

        table_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin

        # Define colors for striping from PDF_CONFIG or use defaults
        bg_color_even_hex = PDF_CONFIG['colors'].get('light_gray_alt', '#F0F4F7')
        bg_color_odd_hex = PDF_CONFIG['colors'].get('white', '#FFFFFF')
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
        data = [[Paragraph(h, self.styles['BodyText']) for h in ['Categoria', 'Punteggio', 'Stato']]]
        categories = {'Title Tags': self.analysis_results['title_analysis']['score'], 'Meta Descriptions': self.analysis_results['meta_description_analysis']['score'], 'Headings': self.analysis_results['headings_analysis']['score'], 'Immagini': self.analysis_results['images_analysis']['score'], 'Contenuto': self.analysis_results['content_analysis']['score'], 'Link Interni': self.analysis_results['links_analysis']['score'], 'Performance': self.analysis_results['performance_analysis']['score'], 'Aspetti Tecnici': self.analysis_results['technical_analysis']['score'], 'SSL': self.analysis_results['ssl_analysis']['score']}
        for category, score in categories.items():
            status_text = self._get_status_text(score)
            data.append([Paragraph(category, self.styles['BodyText']), Paragraph(f"{score}/100", self.styles['BodyText']), Paragraph(status_text, self.styles['BodyText'])])

        # Calculate available width for full-width table
        available_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        # Define relative column widths (e.g., 45% Categoria, 20% Punteggio, 35% Stato)
        col_widths = [available_width * 0.45, available_width * 0.20, available_width * 0.35]
        table = Table(data, colWidths=col_widths)

        COLOR_TABLE_HEADER_BG = PDF_CONFIG['colors'].get('primary_dark', '#004080') # Use from PDF_CONFIG
        COLOR_TABLE_ROW_BG_ODD = PDF_CONFIG['colors'].get('light_gray_alt', '#F0F4F7') # Use from PDF_CONFIG
        COLOR_TABLE_ROW_BG_EVEN = PDF_CONFIG['colors'].get('white', '#FFFFFF') # Use from PDF_CONFIG
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
        score_table_style.add('BOX', (0,0), (-1,-1), 1, HexColor(COLOR_BORDER))

        table.setStyle(score_table_style)
        flowables.append(table)
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
        flowables.append(Paragraph("Tabella Riepilogativa dei Problemi", self.styles['SectionHeading']))
        flowables.append(Spacer(1, 0.2 * inch))
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        all_issues_list = []
        issue_categories_to_process = ['errors', 'warnings', 'notices']
        for category_key in issue_categories_to_process:
            issues_in_category = detailed_issues.get(category_key, [])
            if isinstance(issues_in_category, list):
                for issue in issues_in_category:
                    # 'type' from these lists is the technical key
                    all_issues_list.append({'url': issue.get('url', 'N/A'),
                                            'type': issue.get('type', 'unknown_type'),
                                            'details': issue.get('image', issue.get('details', 'N/A')) }) # Prioritize 'image' for details if it exists

        # Fallback for other lists in detailed_issues (e.g., 'pages_without_title')
        # This part assumes that the 'issue_type' (key of the list, e.g. 'pages_without_title')
        # IS the technical key for the label.
        # And 'details' needs to be constructed or extracted.
        if not all_issues_list: # Only if the primary categories were empty or not found
            for issue_group_key, lst_issues in detailed_issues.items():
                if issue_group_key not in issue_categories_to_process and isinstance(lst_issues, list): # Avoid reprocessing
                    for item in lst_issues:
                        if isinstance(item, dict):
                            url = item.get('url', 'N/A')
                            # Determine detail: prioritize specific keys, then 'issue' field, then 'N/A'
                            detail_keys_order = ['src', 'image_src', 'image', 'tag', 'title', 'meta', 'issue']
                            detail_text = 'N/A'
                            for d_key in detail_keys_order:
                                if item.get(d_key):
                                    detail_text = item.get(d_key)
                                    break

                            all_issues_list.append({
                                'url': url,
                                'type': item.get('type', issue_group_key), # Use item's 'type' if present, else group key
                                'details': detail_text
                            })

        if not all_issues_list:
            flowables.append(Paragraph("Nessun problema specifico identificato.", self.styles['BodyText']))
            flowables.append(Spacer(1, 0.5 * inch))
            self.story.append(KeepTogether(flowables))
            return

        header_row = [
            Paragraph("Pagina URL", self.styles['SmallText']),
            Paragraph("Tipo di Problema", self.styles['SmallText']),
            Paragraph("Dettaglio/Elemento Coinvolto", self.styles['SmallText'])
        ]
        data = [header_row]

        for issue_item_dict in all_issues_list:
            technical_type = str(issue_item_dict.get('type', 'unknown_type'))
            user_friendly_label_template = PDF_ISSUE_TYPE_LABELS.get(technical_type, technical_type.replace('_', ' ').capitalize())

            specific_url = str(issue_item_dict.get('url', 'N/A'))
            specific_details = str(issue_item_dict.get('details', ''))

            # Placeholder substitution
            user_friendly_label = user_friendly_label_template.replace("{{url}}", specific_url)
            user_friendly_label = user_friendly_label.replace("{{pagina}}", specific_url) # Retrocompatibility
            user_friendly_label = user_friendly_label.replace("{{details}}", specific_details)
            user_friendly_label = user_friendly_label.replace("{{elemento}}", specific_details) # Retrocompatibility

            detail_content = str(issue_item_dict.get('details', 'N/A'))
            # Truncate if detail_content is a long URL (common for image src)
            # Also, ensure it's not the same as what might be in the label already if {{details}} was used.
            # For now, we just truncate as before.
            if "http" in detail_content and len(detail_content) > 70: # Simple heuristic
                detail_content = detail_content[:67] + "..."
            elif len(detail_content) > 100: # General truncation for very long details
                 detail_content = detail_content[:97] + "..."


            data.append([
                Paragraph(specific_url, self.styles['SmallText']), # Use specific_url directly for the URL column
                Paragraph(user_friendly_label, self.styles['SmallText']), # Formatted label
                Paragraph(detail_content, self.styles['SmallText'])
            ])

        # Calculate available width for full-width table
        available_width = A4[0] - self.doc.leftMargin - self.doc.rightMargin
        # Define relative column widths (e.g., 35% URL, 30% Tipo, 35% Dettaglio)
        col_widths = [available_width * 0.35, available_width * 0.30, available_width * 0.35]
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
        self.story.append(Paragraph("Analisi Dettagliata", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))
        detailed_issues = self.analysis_results.get('detailed_issues', {})

        def add_issue_table_subsection(section_title_text: str, issues: List[Dict], headers: List[str], data_keys: List[str], column_widths: List = None):
            if not issues: return
            flowables_subsection = [Paragraph(section_title_text, self.styles['BodyText']), Spacer(1, 0.1 * inch)]
            # Use SmallText for headers to match cell content style if not overridden by TableStyle FONTSIZE
            table_data = [[Paragraph(h, self.styles['SmallText']) for h in headers]]
            for issue_item in issues:
                row = []
                for key in data_keys:
                    full_url = str(issue_item.get(key, 'N/A')) # Full URL for href
                    display_text = full_url

                    # Truncate display_text if it's a long URL or very long string
                    if ("http" in display_text or "www" in display_text) and len(display_text) > 70: # Increased limit slightly for URLs
                        display_text = display_text[:67] + "..."
                    elif len(display_text) > 100: # General very long string truncation
                        display_text = display_text[:97] + "..."

                    cell_paragraph_style = self.styles['SmallText'] # Default style for cells

                    if key in ['url', 'image_src', 'href', 'link', 'src']: # Check if the key suggests it's a URL
                        # Ensure full_url is not 'N/A' before creating a link
                        if full_url != 'N/A' and "http" in full_url: # Basic check for a valid URL
                            link_color = PDF_CONFIG['colors'].get('link', 'blue') # Get link color from config or default to blue
                            cell_content = f'<a href="{full_url}" color="{link_color}">{display_text}</a>'
                        else:
                            cell_content = display_text # Non-linkable 'N/A' or invalid URL
                    else:
                        cell_content = display_text

                    row.append(Paragraph(cell_content, cell_paragraph_style))
                table_data.append(row)
            if column_widths is None:
                # Ensure total_width calculation is robust if page margins change
                page_width, _ = A4 # Standard A4 size, could get from self.doc.width if available before build
                # Ensure total_width calculation uses current document margins
                page_width_a4, _ = A4
                doc_margins = (self.doc.leftMargin + self.doc.rightMargin) if self.doc else (PDF_CONFIG['margin']['left'] + PDF_CONFIG['margin']['right']) * cm
                effective_page_width = page_width_a4 - doc_margins

                num_cols = len(headers)
                if num_cols > 0:
                    # Distribute width equally by default if specific column_widths not provided
                    column_widths = [effective_page_width / num_cols] * num_cols
                else:
                    column_widths = [] # Avoid division by zero
            table = Table(table_data, colWidths=column_widths) # Use dynamically calculated or passed column_widths

            # header_bg_color = PDF_CONFIG['colors'].get('secondary', '#005A9C') # Existing dark blue - replaced
            new_header_bg_color = colors.HexColor('#f5f5f5') # New light gray background
            header_outline_color = colors.HexColor('#FFCC00') # Amber/Yellow
            font_header_name = PDF_CONFIG.get('font_family_bold', 'Helvetica-Bold')
            font_header_size = PDF_CONFIG['font_sizes'].get('small', 9)

            font_body_name = PDF_CONFIG.get('font_family', 'Helvetica')
            font_body_size = PDF_CONFIG['font_sizes'].get('extra_small', 8.5)
            text_color_body = colors.HexColor(PDF_CONFIG['colors'].get('text_primary', '#000000'))

            bg_color_even = colors.white # Explicitly white for even rows
            bg_color_odd = colors.HexColor(PDF_CONFIG['colors'].get('light_gray', '#F0F0F0')) # Standard light gray for odd
            grid_color = colors.HexColor(PDF_CONFIG['colors'].get('border', '#CCCCCC'))

            style_cmds = [
                # Header Styling
                ('BACKGROUND', (0,0), (-1,0), new_header_bg_color), # New light gray background
                ('TEXTCOLOR', (0,0), (-1,0), colors.black), # Ensure black text
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), font_header_name),
                ('FONTSIZE', (0,0), (-1,0), font_header_size),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('TOPPADDING', (0,0), (-1,0), 6),
            ]
            # Add individual BOX for each header cell for #FFCC00 outline
            for col_idx in range(len(headers)):
                 style_cmds.append(('BOX', (col_idx,0), (col_idx,0), 1.5, header_outline_color))

            # Data Rows Styling
            style_cmds.extend([
                ('FONTNAME', (0,1), (-1,-1), font_body_name),
                ('FONTSIZE', (0,1), (-1,-1), font_body_size),
                ('TEXTCOLOR', (0,1), (-1,-1), text_color_body),
                ('ALIGN', (0,1), (-1,-1), 'LEFT'),
                ('VALIGN', (0,1), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, grid_color), # Grid for the whole table
                ('BOX', (0,0), (-1,-1), 1, grid_color), # Overall table border
            ])

            # Apply striping
            for i_row in range(1, len(table_data)): # Start from 1 (skip header)
                current_bg_color = bg_color_odd if i_row % 2 != 0 else bg_color_even
                style_cmds.append(('BACKGROUND', (0, i_row), (-1, i_row), current_bg_color))

            table.setStyle(TableStyle(style_cmds))
            flowables_subsection.append(table)
            # Reduced spacer height after each detailed issue table
            flowables_subsection.append(Spacer(1, 0.15 * inch))
            self.story.append(KeepTogether(flowables_subsection))

        # Calculate available_width once, assuming margins are set on self.doc
        page_width_a4, _ = A4
        doc_margins = (self.doc.leftMargin + self.doc.rightMargin) if self.doc else (PDF_CONFIG['margin']['left'] + PDF_CONFIG['margin']['right']) * cm
        available_width = page_width_a4 - doc_margins

        title_analysis = self.analysis_results['title_analysis']

        title_category_flowables = []
        title_category_flowables.append(Paragraph("Title Tags", self.styles['SectionHeading']))
        title_category_flowables.append(Spacer(1, 0.1*inch)) # Reduced spacer
        title_summary_items = [
            ("Pagine con Title", f"{title_analysis.get('pages_with_title', 0)}/{title_analysis.get('total_pages', 0)}"),
            ("Pagine senza Title", str(len(detailed_issues.get('pages_without_title', [])))),
            ("Title duplicati (istanze)", str(len(detailed_issues.get('duplicate_titles', [])))),
            ("Title troppo corti", str(len(title_analysis.get('too_short_titles', [])))),
            ("Title troppo lunghi", str(len(title_analysis.get('too_long_titles', [])))),
            ("Punteggio", f"{title_analysis.get('score', 'N/A')}/100")
        ]
        summary_table_title = self._create_summary_table_for_section(title_summary_items, available_width)
        if summary_table_title: title_category_flowables.append(summary_table_title)
        # Spacer after summary table before first detailed table is now handled by the spacer
        # at the start of add_issue_table_subsection or the one at its end.
        # self.story.append(Spacer(1, 0.2 * inch)) # Removed this explicit spacer
        self.story.append(KeepTogether(title_category_flowables))

        # Note: column_widths are now handled by add_issue_table_subsection if None is passed
        # The add_issue_table_subsection itself uses KeepTogether for its content.
        add_issue_table_subsection("Pagine senza Title", detailed_issues.get('pages_without_title', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'])
        add_issue_table_subsection("Title Duplicati", detailed_issues.get('duplicate_titles', []), headers=['Title Duplicato', 'URL Pagina Coinvolta', 'Conteggio'], data_keys=['title', 'url', 'duplicate_count'])
        add_issue_table_subsection(f"Title Troppo Corti (< {SEO_CONFIG.get('title_min_length', 30)} caratteri)", title_analysis.get('too_short_titles', []), headers=['URL Pagina', 'Title', 'Lunghezza'], data_keys=['url', 'title', 'length'])
        add_issue_table_subsection(f"Title Troppo Lunghi (> {SEO_CONFIG.get('title_max_length', 60)} caratteri)", title_analysis.get('too_long_titles', []), headers=['URL Pagina', 'Title', 'Lunghezza'], data_keys=['url', 'title', 'length'])
        self.story.append(PageBreak())

        meta_analysis = self.analysis_results['meta_description_analysis']
        meta_category_flowables = []
        meta_category_flowables.append(Paragraph("Meta Descriptions", self.styles['SectionHeading']))
        meta_category_flowables.append(Spacer(1, 0.1*inch))
        meta_summary_items = [
            ("Pagine con Meta Description", f"{meta_analysis.get('pages_with_meta',0)}/{meta_analysis.get('total_pages',0)}"),
            ("Pagine senza Meta Description", str(len(detailed_issues.get('pages_without_meta', [])))),
            ("Meta Description Duplicate (istanze)", str(len(detailed_issues.get('duplicate_meta_descriptions', [])))),
            ("Meta Description Troppo Corte", str(len(meta_analysis.get('too_short_metas',[])))),
            ("Meta Description Troppo Lunghe", str(len(meta_analysis.get('too_long_metas',[])))),
            ("Punteggio", f"{meta_analysis.get('score','N/A')}/100")
        ]
        summary_table_meta = self._create_summary_table_for_section(meta_summary_items, available_width)
        if summary_table_meta: meta_category_flowables.append(summary_table_meta)
        self.story.append(KeepTogether(meta_category_flowables))

        add_issue_table_subsection("Pagine senza Meta Description", detailed_issues.get('pages_without_meta', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'])
        add_issue_table_subsection("Meta Description Duplicate", detailed_issues.get('duplicate_meta_descriptions', []), headers=['Meta Description Duplicata', 'URL Pagina Coinvolta', 'Conteggio'], data_keys=['meta', 'url', 'duplicate_count'])
        add_issue_table_subsection(f"Meta Description Troppo Corte (< {SEO_CONFIG.get('meta_description_min_length', 50)} caratteri)", meta_analysis.get('too_short_metas',[]), headers=['URL Pagina', 'Meta Description', 'Lunghezza'], data_keys=['url', 'meta', 'length'])
        add_issue_table_subsection(f"Meta Description Troppo Lunghe (> {SEO_CONFIG.get('meta_description_max_length',160)} caratteri)", meta_analysis.get('too_long_metas',[]), headers=['URL Pagina', 'Meta Description', 'Lunghezza'], data_keys=['url', 'meta', 'length'])
        self.story.append(PageBreak())

        headings_analysis = self.analysis_results.get('headings_analysis', {})
        headings_category_flowables = []
        headings_category_flowables.append(Paragraph("Headings (H1, H2, H3)", self.styles['SectionHeading']))
        headings_category_flowables.append(Spacer(1, 0.1*inch))
        headings_summary_items = [
            ("Pagine senza H1", str(len(detailed_issues.get('missing_h1_pages', [])))),
            ("Pagine con H1 multipli", str(len(detailed_issues.get('multiple_h1_pages', [])))),
            ("Pagine senza H2", str(len(detailed_issues.get('missing_h2_pages', [])))),
            ("Pagine senza H3", str(len(detailed_issues.get('missing_h3_pages', [])))),
            ("Punteggio", f"{headings_analysis.get('score', 'N/A')}/100")
        ]
        summary_table_headings = self._create_summary_table_for_section(headings_summary_items, available_width)
        if summary_table_headings: headings_category_flowables.append(summary_table_headings)
        self.story.append(KeepTogether(headings_category_flowables))

        add_issue_table_subsection("Pagine senza H1", detailed_issues.get('missing_h1_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'])
        add_issue_table_subsection("Pagine con H1 Multipli", detailed_issues.get('multiple_h1_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'])
        add_issue_table_subsection("Pagine senza H2", detailed_issues.get('missing_h2_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'])
        add_issue_table_subsection("Pagine senza H3", detailed_issues.get('missing_h3_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'])
        self.story.append(PageBreak())

        images_analysis = self.analysis_results['images_analysis']
        images_category_flowables = []
        images_category_flowables.append(Paragraph("Immagini", self.styles['SectionHeading']))
        images_category_flowables.append(Spacer(1, 0.1*inch))
        images_summary_items = [
            ("Totale immagini analizzate", str(images_analysis.get('total_images',0))),
            ("Con ALT text (contenuto)", str(images_analysis.get('images_with_alt',0))),
            ("Senza attributo ALT HTML (istanze)", str(len(detailed_issues.get('images_without_alt',[])))),
            ("Con attributo ALT vuoto (istanze)", str(len(detailed_issues.get('images_with_empty_alt',[])))),
            ("Con attributo Title (contenuto)", str(images_analysis.get('images_with_title_attr',0))),
            ("Senza attributo Title HTML (istanze)", str(len(detailed_issues.get('images_without_title_attr',[])))),
            ("Con attributo Title vuoto (istanze)", str(len(detailed_issues.get('images_with_empty_title_attr',[])))),
            ("Immagini interrotte", str(len(detailed_issues.get('broken_images', [])))),
            ("Punteggio", f"{images_analysis.get('score','N/A')}/100")
        ]
        summary_table_images = self._create_summary_table_for_section(images_summary_items, available_width)
        if summary_table_images: images_category_flowables.append(summary_table_images)
        self.story.append(KeepTogether(images_category_flowables))

        img_headers = ['Pagina URL', 'URL Immagine', 'Problema']; img_data_keys = ['url', 'image_src', 'issue']
        add_issue_table_subsection("Immagini senza Attributo ALT HTML", detailed_issues.get('images_without_alt', []), headers=img_headers, data_keys=img_data_keys)
        add_issue_table_subsection("Immagini con Attributo ALT Vuoto", detailed_issues.get('images_with_empty_alt', []), headers=img_headers, data_keys=img_data_keys)
        add_issue_table_subsection("Immagini senza Attributo Title HTML", detailed_issues.get('images_without_title_attr', []), headers=img_headers, data_keys=img_data_keys)
        add_issue_table_subsection("Immagini con Attributo Title Vuoto", detailed_issues.get('images_with_empty_title_attr', []), headers=img_headers, data_keys=img_data_keys)
        add_issue_table_subsection("Immagini Interrotte", detailed_issues.get('broken_images', []), headers=img_headers, data_keys=img_data_keys)
        self.story.append(PageBreak())

        content_analysis = self.analysis_results.get('content_analysis', {})
        content_category_flowables = []
        content_category_flowables.append(Paragraph("Contenuto", self.styles['SectionHeading']))
        content_category_flowables.append(Spacer(1, 0.1*inch))
        content_summary_items = [
            ("Pagine con conteggio parole basso", str(len(detailed_issues.get('low_word_count_pages', [])))),
            ("Punteggio", f"{content_analysis.get('score', 'N/A')}/100")
        ]
        summary_table_content = self._create_summary_table_for_section(content_summary_items, available_width)
        if summary_table_content: content_category_flowables.append(summary_table_content)
        self.story.append(KeepTogether(content_category_flowables))

        add_issue_table_subsection(f"Pagine con Conteggio Parole Basso (< {SEO_CONFIG.get('min_word_count',200)} parole)", detailed_issues.get('low_word_count_pages', []), headers=['URL Pagina', 'Conteggio Parole', 'Problema'], data_keys=['url', 'word_count', 'issue'])
        self.story.append(PageBreak())

        links_analysis = self.analysis_results.get('links_analysis', {})
        links_category_flowables = []
        links_category_flowables.append(Paragraph("Link", self.styles['SectionHeading']))
        links_category_flowables.append(Spacer(1, 0.1*inch))
        links_summary_items = [ # Add more specific link metrics if available
            ("Punteggio Link Analysis", f"{links_analysis.get('score', 'N/A')}/100")
        ]
        summary_table_links = self._create_summary_table_for_section(links_summary_items, available_width)
        if summary_table_links: links_category_flowables.append(summary_table_links)
        self.story.append(KeepTogether(links_category_flowables))
        # Add specific link issue tables here if any (e.g., broken internal/external links)
        self.story.append(PageBreak())

        perf_analysis = self.analysis_results['performance_analysis']
        perf_category_flowables = []
        perf_category_flowables.append(Paragraph("Performance", self.styles['SectionHeading']))
        perf_category_flowables.append(Spacer(1, 0.1*inch))
        perf_summary_items = [
            ("Pagine considerate veloci", str(perf_analysis.get('fast_pages',0))),
            ("Pagine considerate lente (istanze)", str(len(detailed_issues.get('slow_pages',[])))),
            ("Tempo medio di risposta", f"{perf_analysis.get('average_response_time',0):.2f}s"),
            ("Dimensione media pagina", f"{perf_analysis.get('average_page_size',0)/1024:.1f} KB"),
            ("Pagine con HTML troppo grande", str(len(detailed_issues.get('large_html_pages', [])))),
            ("Punteggio", f"{perf_analysis.get('score','N/A')}/100")
        ]
        summary_table_perf = self._create_summary_table_for_section(perf_summary_items, available_width)
        if summary_table_perf: perf_category_flowables.append(summary_table_perf)
        self.story.append(KeepTogether(perf_category_flowables))

        add_issue_table_subsection(f"Pagine con Dimensioni HTML Troppo Grandi (> {SEO_CONFIG.get('max_page_size_mb', 2)} MB)", detailed_issues.get('large_html_pages', []), headers=['URL Pagina', 'Dimensione (MB)', 'Problema'], data_keys=['url', 'size_mb', 'issue'])
        add_issue_table_subsection(f"Pagine con Velocità di Caricamento Bassa (> {PERFORMANCE_CONFIG.get('max_response_time',3)}s)", detailed_issues.get('slow_pages', []), headers=['URL Pagina', 'Tempo (s)', 'Problema'], data_keys=['url', 'response_time', 'issue'])
        self.story.append(PageBreak())

        technical_analysis = self.analysis_results.get('technical_analysis', {})
        tech_category_flowables = []
        tech_category_flowables.append(Paragraph("Aspetti Tecnici", self.styles['SectionHeading']))
        tech_category_flowables.append(Spacer(1, 0.1*inch))
        tech_summary_items = []
        tech_issues_to_report_map = {
            'status_4xx_pages': "Pagine con Errori Client (4xx)",
            'status_5xx_pages': "Pagine con Errori Server (5xx)",
            'pages_without_canonical': "Pagine senza URL Canonico",
            'pages_without_lang': "Pagine senza Attributo Lingua",
            'pages_without_schema': "Pagine senza Schema Markup"
        }
        for key, text_label in tech_issues_to_report_map.items():
            tech_summary_items.append((text_label, str(len(detailed_issues.get(key, [])))))
        tech_summary_items.append(("Punteggio", f"{technical_analysis.get('score', 'N/A')}/100"))
        summary_table_tech = self._create_summary_table_for_section(tech_summary_items, available_width)
        if summary_table_tech: tech_category_flowables.append(summary_table_tech)
        self.story.append(KeepTogether(tech_category_flowables))

        tech_headers_default = ['URL Pagina', 'Problema Rilevato']; tech_data_keys_default = ['url', 'issue']
        for key, text_label in tech_issues_to_report_map.items():
            data_to_pass = detailed_issues.get(key, [])
            if key == 'status_4xx_pages' or key == 'status_5xx_pages':
                add_issue_table_subsection(text_label, data_to_pass, headers=['URL Pagina', 'Status Code', 'Problema'], data_keys=['url', 'status_code', 'issue'])
            else:
                add_issue_table_subsection(text_label, data_to_pass, headers=tech_headers_default, data_keys=tech_data_keys_default)
        self.story.append(PageBreak())

        ssl_analysis = self.analysis_results.get('ssl_analysis', {})
        ssl_category_flowables = []
        ssl_category_flowables.append(Paragraph("SSL / Sicurezza", self.styles['SectionHeading']))
        ssl_category_flowables.append(Spacer(1, 0.1*inch))
        ssl_summary_items = [
            ("Certificato SSL presente", 'Sì' if ssl_analysis.get('has_ssl') else 'No'),
            ("Certificato SSL valido", 'Sì' if ssl_analysis.get('ssl_valid') else 'No')
        ]
        if ssl_analysis.get('ssl_expires'):
            ssl_summary_items.append(("Scadenza Certificato SSL", str(ssl_analysis.get('ssl_expires'))))
        # Add Punteggio for SSL if available
        if 'score' in ssl_analysis:
             ssl_summary_items.append(("Punteggio", f"{ssl_analysis.get('score','N/A')}/100"))
        summary_table_ssl = self._create_summary_table_for_section(ssl_summary_items, available_width)
        if summary_table_ssl: ssl_category_flowables.append(summary_table_ssl)
        self.story.append(KeepTogether(ssl_category_flowables))
        # Add specific SSL issue tables here if any are generated by analyzer
        self.story.append(PageBreak())

    def _add_recommendations_section(self):
        main_title_flowables = [Paragraph("Raccomandazioni", self.styles['SectionHeading']), Spacer(1, 0.2 * inch)]
        recommendations = self.analysis_results['recommendations']
        if not recommendations:
            main_title_flowables.append(Paragraph("🎉 ECCELLENTE! Nessuna raccomandazione specifica identificata. Il sito presenta un'ottima ottimizzazione SEO.", self.styles['BodyText']))
            self.story.append(KeepTogether(main_title_flowables))
            return
        self.story.append(KeepTogether(main_title_flowables))

        def add_recommendation_table_subsection(title_text: str, recs: List[Dict]):
            if not recs: return
            flowables_subsection = [Paragraph(title_text, self.styles['BodyText']), Spacer(1, 0.1 * inch)]
            data = [[Paragraph(h, self.styles['BodyText']) for h in ['Categoria', 'Problema', 'Raccomandazione']]]
            for rec in recs: data.append([Paragraph(rec.get('category', 'N/A'), self.styles['BodyText']), Paragraph(rec.get('issue', 'N/A'), self.styles['BodyText']), Paragraph(rec.get('recommendation', 'N/A'), self.styles['BodyText'])])
            table = Table(data, colWidths=[4*cm, 6*cm, 7*cm])
            COLOR_TABLE_HEADER_BG = '#004080'; COLOR_TABLE_HEADER_TEXT = '#FFFFFF'; COLOR_TABLE_ROW_BG_ODD = '#F0F4F7'; COLOR_TABLE_ROW_BG_EVEN = '#FFFFFF'; COLOR_BORDER = '#CCCCCC'; FONT_FAMILY_TABLE_HEADER = 'Helvetica-Bold'; FONT_FAMILY_TABLE_BODY = 'Helvetica'; FONT_SIZE_TABLE_HEADER = 9; FONT_SIZE_TABLE_BODY = 9; COLOR_TEXT_PRIMARY_FOR_TABLE = '#222222'
            rec_table_style = TableStyle([('BACKGROUND', (0,0), (-1,0), HexColor(COLOR_TABLE_HEADER_BG)), ('TEXTCOLOR', (0,0), (-1,0), HexColor(COLOR_TABLE_HEADER_TEXT)), ('ALIGN', (0,0), (-1,0), 'CENTER'), ('FONTNAME', (0,0), (-1,0), FONT_FAMILY_TABLE_HEADER), ('FONTSIZE', (0,0), (-1,0), FONT_SIZE_TABLE_HEADER), ('BOTTOMPADDING', (0,0), (-1,0), 8), ('TOPPADDING', (0,0), (-1,0), 8), ('FONTNAME', (0,1), (-1,-1), FONT_FAMILY_TABLE_BODY), ('FONTSIZE', (0,1), (-1,-1), FONT_SIZE_TABLE_BODY), ('TEXTCOLOR', (0,1), (-1,-1), HexColor(COLOR_TEXT_PRIMARY_FOR_TABLE)), ('ALIGN', (0,1), (-1,-1), 'LEFT'), ('VALIGN', (0,1), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,1), (-1,-1), 5), ('TOPPADDING', (0,1), (-1,-1), 5), ('BACKGROUND', (0,1), (-1,-1), HexColor(COLOR_TABLE_ROW_BG_EVEN))])
            for i in range(1, len(data)):
                if i % 2 != 0: rec_table_style.add('BACKGROUND', (0,i), (-1,i), HexColor(COLOR_TABLE_ROW_BG_ODD))
            rec_table_style.add('GRID', (0,0), (-1,-1), 0.5, HexColor(COLOR_BORDER)); rec_table_style.add('BOX', (0,0), (-1,-1), 1, HexColor(COLOR_BORDER))
            table.setStyle(rec_table_style)
            flowables_subsection.append(table)
            flowables_subsection.append(Spacer(1, 0.3 * inch))
            self.story.append(KeepTogether(flowables_subsection))

        high_priority = [r for r in recommendations if r['priority'] == 'Alto']
        medium_priority = [r for r in recommendations if r['priority'] == 'Medio']
        low_priority = [r for r in recommendations if r['priority'] == 'Basso']
        add_recommendation_table_subsection("Priorità Alta", high_priority)
        add_recommendation_table_subsection("Priorità Media", medium_priority)
        add_recommendation_table_subsection("Priorità Bassa", low_priority)
        self.story.append(PageBreak())

    def _add_issue_details_appendix(self):
        main_title_flowables = [Paragraph("Descrizione Dettagliata dei Problemi Comuni", self.styles['SectionHeading']), Spacer(1, 0.2 * inch)]
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        unique_issue_types = set()
        issue_categories_to_process = ['errors', 'warnings', 'notices']
        for category_key in issue_categories_to_process:
            issues_in_category = detailed_issues.get(category_key, [])
            if isinstance(issues_in_category, list):
                for issue in issues_in_category:
                    if isinstance(issue, dict) and 'type' in issue: unique_issue_types.add(issue['type'])
        if not unique_issue_types: # Check if still empty after primary categories
            for issue_group_key, lst_issues in detailed_issues.items():
                if issue_group_key not in issue_categories_to_process and isinstance(lst_issues, list):
                    for item in lst_issues:
                        if isinstance(item, dict):
                             # Use item's 'type' field if it exists, otherwise the group key
                             unique_issue_types.add(item.get('type', issue_group_key))
        
        if not unique_issue_types:
            main_title_flowables.append(Paragraph("Nessun tipo di problema specifico da dettagliare.", self.styles['BodyText']))
            main_title_flowables.append(Spacer(1, 0.5 * inch))
            self.story.append(KeepTogether(main_title_flowables))
            return
        
        self.story.append(KeepTogether(main_title_flowables))

        issue_explanations = {'missing_title': "Ogni pagina dovrebbe avere un tag title univoco che ne descriva accuratamente il contenuto. È cruciale per la SEO.", 'duplicate_title': "Titoli duplicati confondono i motori di ricerca e possono danneggiare il ranking. Ogni pagina necessita di un titolo unico.", 'short_title': "Un titolo troppo corto potrebbe non fornire abbastanza informazioni ai motori di ricerca e agli utenti.", 'long_title': "Un titolo troppo lungo verrà troncato nei risultati di ricerca, riducendone l'efficacia.", 'missing_meta_description': "La meta description fornisce un riassunto della pagina nei risultati di ricerca. Anche se non è un fattore di ranking diretto, influenza il CTR.", 'duplicate_meta_description': "Meta description duplicate possono ridurre la specificità delle pagine agli occhi dei motori di ricerca.", 'short_meta_description': "Una meta description troppo corta potrebbe non essere abbastanza persuasiva per gli utenti.", 'long_meta_description': "Una meta description troppo lunga verrà troncata nei risultati di ricerca.", 'missing_h1': "Il tag H1 è il titolo principale della pagina e aiuta i motori di ricerca a comprenderne il contenuto. Ogni pagina dovrebbe avere un unico H1.", 'multiple_h1_tags': "Più tag H1 su una singola pagina possono confondere i motori di ricerca riguardo al focus principale del contenuto.", 'missing_h2': "I tag H2 aiutano a strutturare il contenuto e a definirne le sezioni principali. La loro assenza può rendere il contenuto meno leggibile per utenti e crawler.", 'missing_alt_attribute': "L'attributo ALT delle immagini è fondamentale per l'accessibilità (screen reader) e per la SEO (descrive l'immagine ai motori di ricerca).", 'empty_alt_attribute': "Un attributo ALT vuoto è tecnicamente presente ma non fornisce alcuna informazione, mancando i benefici per accessibilità e SEO.", 'broken_image': "Immagini interrotte danneggiano l'esperienza utente e possono indicare problemi di manutenzione del sito.", 'low_word_count': "Pagine con poco contenuto testuale (thin content) potrebbero essere considerate di bassa qualità dai motori di ricerca.", 'slow_page_load': "Pagine lente frustrano gli utenti e impattano negativamente il ranking sui motori di ricerca.", 'large_html_size': "Dimensioni HTML eccessive possono contribuire a tempi di caricamento lenti.", 'http_status_4xx': "Errori client (4xx, es. 404 Pagina Non Trovata) indicano problemi di accessibilità a risorse o pagine.", 'http_status_5xx': "Errori server (5xx) indicano problemi critici con il server che impediscono il caricamento della pagina.", 'no_canonical_tag': "Il tag canonical aiuta a prevenire problemi di contenuto duplicato specificando la versione preferita di una pagina.", 'missing_lang_attribute': "L'attributo 'lang' sull'elemento <html> aiuta i motori di ricerca e i browser a comprendere la lingua della pagina.", 'no_schema_markup': "Schema markup (dati strutturati) aiuta i motori di ricerca a comprendere meglio il contenuto e può abilitare rich snippet nei risultati di ricerca.", 'generic_issue': "Questo è un problema generico. Controllare i dettagli specifici forniti nella tabella dei problemi."}

        for issue_technical_key in sorted(list(unique_issue_types)):
            issue_display_name = PDF_ISSUE_TYPE_LABELS.get(issue_technical_key, issue_technical_key.replace('_', ' ').capitalize())
            explanation = issue_explanations.get(issue_technical_key, "Nessuna descrizione specifica disponibile per questo tipo di problema. Si prega di fare riferimento ai dettagli forniti e alle best practice SEO generali.")
            item_flowables = [Paragraph(f"<b>{issue_display_name}</b>", self.styles['BodyText']), Paragraph(explanation, self.styles['ListItem']), Spacer(1, 0.15 * inch)]
            self.story.append(KeepTogether(item_flowables))
        self.story.append(Spacer(1, 0.3 * inch))

    # _add_appendix method and its content are removed.
    # The _add_issue_details_appendix method and its content are removed.

    def _get_evaluation_text(self, score):
        methodology_text = """Questo report è stato generato utilizzando SEO Analyzer Pro, che esegue un'analisi completa del sito web basata sulle migliori pratiche SEO. L'analisi include:<ul><li>Crawling automatico del sito web</li><li>Verifica dei tag HTML principali (title, meta, headings)</li><li>Analisi delle immagini e degli alt text</li><li>Valutazione della qualità del contenuto</li><li>Test delle performance di caricamento</li><li>Controllo degli aspetti tecnici (SSL, canonical, etc.)</li></ul>Il punteggio finale è calcolato come media ponderata di tutti i fattori analizzati."""
        methodology_flowables.append(Paragraph(methodology_text, self.styles['BodyText']))
        methodology_flowables.append(Spacer(1, 0.2 * inch))
        self.story.append(KeepTogether(methodology_flowables))
        glossary_flowables = [Paragraph("Glossario", self.styles['BodyText']), Spacer(1, 0.1 * inch)]
        styled_glossary_data = [[Paragraph(h, self.styles['BodyText']) for h in ['Termine', 'Definizione']]]
        raw_glossary_entries = [
             ['Title Tag', 'Tag HTML che definisce il titolo della pagina mostrato nei risultati di ricerca'],
             ['Meta Description', 'Breve descrizione della pagina mostrata nei risultati di ricerca'],
             ['Alt Text', 'Testo alternativo per le immagini, importante per accessibilità e SEO'],
             ['Canonical URL', 'URL preferito per pagine con contenuto duplicato'],
             ['Schema Markup', 'Codice strutturato che aiuta i motori di ricerca a comprendere il contenuto'],
             ['Robots.txt', 'File che indica ai crawler quali parti del sito non devono essere indicizzate'],
             ['Sitemap.xml', 'File che elenca tutte le pagine importanti di un sito per i motori di ricerca'],
             ['Hreflang', 'Attributo HTML che specifica la lingua e la regione geografica di una pagina'],
             ['Mixed Content', 'Quando una pagina HTTPS carica risorse (immagini, script) tramite HTTP'],
             ['Viewport', 'Meta tag che controlla la larghezza della viewport su dispositivi mobili'],
             ['Core Web Vitals', 'Metriche di Google per valutare l\'esperienza utente di una pagina web (LCP, FID, CLS)'],
        ]
        for term, definition in raw_glossary_entries:
            styled_glossary_data.append([Paragraph(term, self.styles['BodyText']), Paragraph(definition, self.styles['BodyText'])])
        glossary_table = Table(styled_glossary_data, colWidths=[4*cm, 13*cm])
        COLOR_TABLE_HEADER_BG = '#004080'; COLOR_TABLE_HEADER_TEXT = '#FFFFFF'; COLOR_TABLE_ROW_BG_ODD = '#F0F4F7'; COLOR_TABLE_ROW_BG_EVEN = '#FFFFFF'; COLOR_BORDER = '#CCCCCC'; FONT_FAMILY_TABLE_HEADER = 'Helvetica-Bold'; FONT_FAMILY_TABLE_BODY = 'Helvetica'; FONT_SIZE_TABLE_HEADER = 9; FONT_SIZE_TABLE_BODY = 9; COLOR_TEXT_PRIMARY_FOR_TABLE = '#222222'
        glossary_style = TableStyle([('BACKGROUND', (0,0), (-1,0), HexColor(COLOR_TABLE_HEADER_BG)), ('TEXTCOLOR', (0,0), (-1,0), HexColor(COLOR_TABLE_HEADER_TEXT)), ('ALIGN', (0,0), (-1,0), 'CENTER'), ('FONTNAME', (0,0), (-1,0), FONT_FAMILY_TABLE_HEADER), ('FONTSIZE', (0,0), (-1,0), FONT_SIZE_TABLE_HEADER), ('BOTTOMPADDING', (0,0), (-1,0), 8), ('TOPPADDING', (0,0), (-1,0), 8), ('FONTNAME', (0,1), (-1,-1), FONT_FAMILY_TABLE_BODY), ('FONTSIZE', (0,1), (-1,-1), FONT_SIZE_TABLE_BODY), ('TEXTCOLOR', (0,1), (-1,-1), HexColor(COLOR_TEXT_PRIMARY_FOR_TABLE)), ('ALIGN', (0,1), (-1,-1), 'LEFT'), ('VALIGN', (0,1), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,1), (-1,-1), 5), ('TOPPADDING', (0,1), (-1,-1), 5), ('BACKGROUND', (0,1), (-1,-1), HexColor(COLOR_TABLE_ROW_BG_EVEN))])
        for i in range(1, len(styled_glossary_data)):
            if i % 2 != 0: glossary_style.add('BACKGROUND', (0,i), (-1,i), HexColor(COLOR_TABLE_ROW_BG_ODD))
        glossary_style.add('GRID', (0,0), (-1,-1), 0.5, HexColor(COLOR_BORDER)); glossary_style.add('BOX', (0,0), (-1,-1), 1, HexColor(COLOR_BORDER))
        glossary_table.setStyle(glossary_style)
        glossary_flowables.append(glossary_table)
        glossary_flowables.append(Spacer(1, 0.5*inch))
        self.story.append(KeepTogether(glossary_flowables))

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
