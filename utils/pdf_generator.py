"""
Generatore di report PDF per l'analisi SEO
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, red, green, orange, blue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart # Not used, but good to have
from reportlab.graphics import renderPDF
from reportlab.lib import colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from datetime import datetime
from typing import Dict, List, Any
import os

from config import * # Assicurati che config.py sia accessibile e contenga i colori PDF_CONFIG['colors']

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
        # Chiamiamo _setup_custom_styles solo una volta per classe o in modo condizionale
        # per evitare l'errore "Style already defined".
        # Un approccio più robusto è usare un flag di classe o controllare l'esistenza dello stile.
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configura gli stili personalizzati"""
        # CONCEPTUAL PDF_CONFIG (assuming updated in config.py)
        # For demonstration, using direct values here. In practice, these would come from PDF_CONFIG.
        FONT_FAMILY = 'Helvetica'
        FONT_FAMILY_BOLD = 'Helvetica-Bold'
        
        COLOR_PRIMARY = '#005A9C'         # Dark Blue
        COLOR_TEXT_PRIMARY = '#222222'   # Very Dark Gray / Off-black
        COLOR_TEXT_SECONDARY = '#555555' # Medium Gray
        COLOR_SUCCESS = '#28A745'
        COLOR_WARNING = '#FFC107' # Amber
        COLOR_ERROR = '#DC3545' # Red
        
        FONT_SIZE_TITLE = 20
        FONT_SIZE_HEADING = 15
        FONT_SIZE_BODY = 10
        FONT_SIZE_SMALL = 8

        # Stile titolo principale
        style_name = 'CustomTitle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                fontName=FONT_FAMILY_BOLD,
                fontSize=FONT_SIZE_TITLE,
                leading=FONT_SIZE_TITLE * 1.2,
                alignment=TA_CENTER,
                textColor=HexColor(COLOR_PRIMARY),
                spaceAfter=12
            ))
        
        # Stile sottotitolo
        style_name = 'CustomSubtitle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                fontName=FONT_FAMILY,
                fontSize=FONT_SIZE_HEADING,
                leading=FONT_SIZE_HEADING * 1.2,
                alignment=TA_CENTER,
                textColor=HexColor(COLOR_TEXT_SECONDARY),
                spaceAfter=6
            ))

        # Stile per le sezioni
        style_name = 'SectionHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                fontName=FONT_FAMILY_BOLD,
                fontSize=FONT_SIZE_HEADING,
                leading=FONT_SIZE_HEADING * 1.2,
                spaceAfter=8, # Increased space after heading
                textColor=HexColor(COLOR_PRIMARY)
            ))

        # Stile per il testo normale
        style_name = 'BodyText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                fontName=FONT_FAMILY,
                fontSize=FONT_SIZE_BODY,
                leading=FONT_SIZE_BODY * 1.4, # Increased line spacing
                spaceAfter=6,
                textColor=HexColor(COLOR_TEXT_PRIMARY)
            ))

        # Stile per i punti elenco
        style_name = 'ListItem'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                parent=self.styles['BodyText'], # Inherits from BodyText
                leftIndent=20,
                spaceAfter=4 # Slightly more space after list items
            ))

        # Stile per testo piccolo (es. footer, date)
        style_name = 'SmallText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                fontName=FONT_FAMILY,
                fontSize=FONT_SIZE_SMALL,
                leading=FONT_SIZE_SMALL * 1.2,
                alignment=TA_CENTER,
                textColor=HexColor(COLOR_TEXT_SECONDARY)
            ))

        # Stili per i colori dei punteggi (used in _get_evaluation_text if applying styles directly)
        # For now, these are primarily for direct color reference, but could be full styles
        score_parent_style = self.styles['BodyText']
        style_name = 'ScoreExcellent'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_SUCCESS), fontName=FONT_FAMILY_BOLD))
        style_name = 'ScoreGood' # Typically primary or a specific "good" color
        if style_name not in self.styles:
             self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_PRIMARY), fontName=FONT_FAMILY_BOLD)) # Example: Using primary for "Good"
        style_name = 'ScoreWarning'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_WARNING), fontName=FONT_FAMILY_BOLD))
        style_name = 'ScoreCritical'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=score_parent_style, textColor=HexColor(COLOR_ERROR), fontName=FONT_FAMILY_BOLD))
        
    def _add_header(self):
        """Aggiunge l'intestazione del report"""
        self.story.append(Paragraph(self.analysis_results['summary']['report_title'], self.styles['CustomTitle']))
        self.story.append(Paragraph(self.domain, self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.2 * inch))
        self.story.append(Paragraph(f"Generato in data: {self.analysis_results['summary']['analysis_date']}", self.styles['SmallText']))
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_executive_summary(self):
        """Aggiunge il riassunto esecutivo con punteggio e valutazione"""
        self.story.append(Paragraph("Riassunto Esecutivo", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        overall_score = self.analysis_results['overall_score']
        evaluation = self._get_evaluation_text(overall_score)

        summary_text = f"""
        L'analisi SEO del sito <b>{self.domain}</b> ha rivelato un punteggio complessivo di <font color="{self._get_score_color_hex(overall_score)}"><b>{overall_score}/100</b></font>.
        Valutazione: <b>{evaluation}</b>.
        Sono state analizzate <b>{self.analysis_results['summary']['total_pages_analyzed']}</b> pagine,
        identificando <b>{self.analysis_results['summary']['total_issues']}</b> problemi e generando
        <b>{self.analysis_results['summary']['total_recommendations']}</b> raccomandazioni per il miglioramento.
        """
        self.story.append(Paragraph(summary_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2 * inch))

        # Punti di Forza e Aree di Miglioramento
        strengths, weaknesses = self._identify_strengths_weaknesses()

        self.story.append(Paragraph("Punti di Forza:", self.styles['BodyText']))
        if strengths:
            for s in strengths:
                self.story.append(Paragraph(f"• {s}", self.styles['ListItem']))
        else:
            self.story.append(Paragraph("Nessun punto di forza specifico identificato.", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph("Aree di Miglioramento:", self.styles['BodyText']))
        if weaknesses:
            for w in weaknesses:
                self.story.append(Paragraph(f"• {w}", self.styles['ListItem']))
        else:
            self.story.append(Paragraph("Nessuna area di miglioramento critica identificata.", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_score_overview(self):
        """Aggiunge una panoramica dei punteggi per categoria"""
        self.story.append(Paragraph("Panoramica Punteggi", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        data = [
            ['Categoria', 'Punteggio', 'Stato']
        ]
        
        categories = {
            'Title Tags': self.analysis_results['title_analysis']['score'],
            'Meta Descriptions': self.analysis_results['meta_description_analysis']['score'],
            'Headings': self.analysis_results['headings_analysis']['score'],
            'Immagini': self.analysis_results['images_analysis']['score'],
            'Contenuto': self.analysis_results['content_analysis']['score'],
            'Link Interni': self.analysis_results['links_analysis']['score'],
            'Performance': self.analysis_results['performance_analysis']['score'],
            'Aspetti Tecnici': self.analysis_results['technical_analysis']['score'],
            'SSL': self.analysis_results['ssl_analysis']['score']
        }

        for category, score in categories.items():
            status_text = self._get_status_text(score)
            data.append([
                Paragraph(category, self.styles['BodyText']),
                Paragraph(f"{score}/100", self.styles['BodyText']),
                Paragraph(status_text, self.styles['BodyText']) # Potresti voler applicare uno stile specifico qui per il colore
            ])

        table = Table(data, colWidths=[7*cm, 3*cm, 7*cm]) # Adjusted widths
        
        # New conceptual PDF_CONFIG values for styling this table
        COLOR_TABLE_HEADER_BG = '#004080' 
        COLOR_TABLE_HEADER_TEXT = '#FFFFFF'
        COLOR_TABLE_ROW_BG_ODD = '#F0F4F7' 
        COLOR_TABLE_ROW_BG_EVEN = '#FFFFFF'
        COLOR_BORDER = '#CCCCCC'
        FONT_FAMILY_TABLE_HEADER = 'Helvetica-Bold'
        FONT_FAMILY_TABLE_BODY = 'Helvetica'
        FONT_SIZE_TABLE_HEADER = 9
        FONT_SIZE_TABLE_BODY = 9
        COLOR_TEXT_PRIMARY_FOR_TABLE = '#222222'

        score_table_style = TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLOR_TABLE_HEADER_BG)),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor(COLOR_TABLE_HEADER_TEXT)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_FAMILY_TABLE_HEADER),
            ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_TABLE_HEADER),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Body style
            ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY_TABLE_BODY),
            ('FONTSIZE', (0, 1), (-1, -1), FONT_SIZE_TABLE_BODY),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor(COLOR_TEXT_PRIMARY_FOR_TABLE)),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'), # Align category and status text to left
            ('ALIGN', (1, 1), (1, -1), 'CENTER'), # Center score text
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor(COLOR_TABLE_ROW_BG_EVEN)),
        ])

        for i in range(1, len(data)): # Odd rows for body
            if i % 2 != 0:
                score_table_style.add('BACKGROUND', (0, i), (-1, i), HexColor(COLOR_TABLE_ROW_BG_ODD))
        
        score_table_style.add('GRID', (0, 0), (-1, -1), 0.5, HexColor(COLOR_BORDER))
        score_table_style.add('BOX', (0, 0), (-1, -1), 1, HexColor(COLOR_BORDER))
        
        table.setStyle(score_table_style)
        self.story.append(table)
        self.story.append(Spacer(1, 0.5 * inch))

    def _add_site_health_chart(self):
        """Aggiunge il grafico a torta del Site Health."""
        self.story.append(Paragraph("Site Health Overview", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        overall_score = self.analysis_results['overall_score']
        # Per il grafico a torta, mostriamo la percentuale di "salute" e la percentuale di "problemi".
        health_percentage = overall_score
        problem_percentage = 100 - overall_score

        # Dati per il grafico a torta
        data = [health_percentage, problem_percentage]
        labels = [f'Sano ({health_percentage:.0f}%)', f'Problemi ({problem_percentage:.0f}%)']
        
        # Using direct hex values conceptually from the new PDF_CONFIG
        COLOR_SUCCESS = '#28A745'
        COLOR_ERROR = '#DC3545'
        FONT_FAMILY = 'Helvetica'
        FONT_FAMILY_BOLD = 'Helvetica-Bold'
        FONT_SIZE_SMALL_CHART = 8 
        FONT_SIZE_BODY_CHART = 10
        FONT_SIZE_SCORE_CHART = 32 # Slightly reduced from 36
        COLOR_TEXT_PRIMARY_CHART = '#222222'
        COLOR_PRIMARY_CHART_LABEL = '#005A9C'


        colors_pie = [HexColor(COLOR_SUCCESS), HexColor(COLOR_ERROR)]

        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 50
        pie.height = 150
        pie.width = 150
        pie.data = data
        pie.labels = labels # ReportLab will use pie.slices[i].fontName etc for these if set
        pie.slices.strokeWidth = 0.5
        
        for i, color_val in enumerate(colors_pie):
            pie.slices[i].fillColor = color_val
            pie.slices[i].fontName = FONT_FAMILY
            pie.slices[i].fontSize = FONT_SIZE_SMALL_CHART 
            pie.slices[i].labelRadius = 1.2 # Posiziona le etichette fuori dalla torta
            # To change label text color (if needed, default is usually black and fine)
            # pie.slices[i].fontColor = HexColor(COLOR_TEXT_PRIMARY_CHART)


        # Aggiungi il testo centrale con la percentuale
        center_x = pie.x + pie.width / 2
        center_y = pie.y + pie.height / 2
        
        # Testo centrale "XX%"
        overall_score_text = String(center_x, center_y + 10, f"{int(overall_score)}%",
                                    fontName=FONT_FAMILY_BOLD, # Bold for score
                                    fontSize=FONT_SIZE_SCORE_CHART, 
                                    fillColor=HexColor(COLOR_PRIMARY_CHART_LABEL), # Use primary color for score
                                    textAnchor='middle')
        drawing.add(overall_score_text)

        # Testo centrale "Site Health"
        site_health_label = String(center_x, center_y - 15, "Site Health",
                                   fontName=FONT_FAMILY,
                                   fontSize=FONT_SIZE_BODY_CHART, # Use body size
                                   fillColor=HexColor(COLOR_TEXT_PRIMARY_CHART), # Standard text color
                                   textAnchor='middle')
        drawing.add(site_health_label)

        drawing.add(pie)
        self.story.append(drawing)
        self.story.append(Spacer(1, 0.5 * inch))


    def _add_detailed_analysis_section(self):
        """Aggiunge la sezione di analisi dettagliata con tabelle per i problemi"""
        self.story.append(Paragraph("Analisi Dettagliata", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        detailed_issues = self.analysis_results.get('detailed_issues', {})

        # Helper per aggiungere una sottosezione con tabella di problemi
        def add_issue_table_subsection(title: str, issues: List[Dict], 
                                       headers: List[str], data_keys: List[str], 
                                       column_widths: List = None):
            if not issues:
                return
            
            self.story.append(Paragraph(title, self.styles['BodyText'])) # Use BodyText for sub-section title
            self.story.append(Spacer(1, 0.1 * inch))

            # Data for the table, starting with headers
            table_data = [headers]
            for issue_item in issues:
                row = []
                for key in data_keys:
                    # Truncate long URLs/text to prevent table overflow
                    raw_text = str(issue_item.get(key, 'N/A'))
                    if len(raw_text) > 100 and ("http" in raw_text or "www" in raw_text): # Heuristic for URLs
                        raw_text = raw_text[:97] + "..."
                    elif len(raw_text) > 150: # General text truncation
                        raw_text = raw_text[:147] + "..."
                    row.append(Paragraph(raw_text, self.styles['BodyText']))
                table_data.append(row)
            
            # Define column widths if not provided (distribute equally)
            if column_widths is None:
                total_width = 17 * cm # A4 width minus margins approx
                num_cols = len(headers)
                column_widths = [total_width / num_cols] * num_cols
            
            table = Table(table_data, colWidths=column_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['secondary'])), # Header background
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), PDF_CONFIG['font_family']),
                ('FONTSIZE', (0, 0), (-1, 0), PDF_CONFIG['font_sizes']['small']),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor(PDF_CONFIG['colors']['light_gray'])),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(PDF_CONFIG['colors']['border'])),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(PDF_CONFIG['colors']['secondary_dark'])),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            self.story.append(table)
            self.story.append(Spacer(1, 0.3 * inch))

        # Title Tags
        self.story.append(Paragraph("Title Tags", self.styles['SectionHeading']))
        title_analysis = self.analysis_results['title_analysis']
        self.story.append(Paragraph(f"• Pagine con Title: {title_analysis['pages_with_title']}/{title_analysis['total_pages']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine senza Title: {len(detailed_issues.get('pages_without_title', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Title duplicati: {len(detailed_issues.get('duplicate_titles', []))} (istanze)", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Title troppo corti: {len(title_analysis.get('too_short_titles', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Title troppo lunghi: {len(title_analysis.get('too_long_titles', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {title_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine senza Title", detailed_issues.get('pages_without_title', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'], column_widths=[13*cm, 4*cm])
        add_issue_table_subsection("Title Duplicati", detailed_issues.get('duplicate_titles', []), headers=['Title Duplicato', 'URL Pagina Coinvolta', 'Conteggio Totale Duplicati'], data_keys=['title', 'url', 'duplicate_count'], column_widths=[6*cm, 9*cm, 2*cm])
        add_issue_table_subsection("Title Troppo Corti (< {0} caratteri)".format(SEO_CONFIG.get('title_min_length', 30)), title_analysis.get('too_short_titles', []), headers=['URL Pagina', 'Title', 'Lunghezza'], data_keys=['url', 'title', 'length'], column_widths=[10*cm, 5*cm, 2*cm])
        add_issue_table_subsection("Title Troppo Lunghi (> {0} caratteri)".format(SEO_CONFIG.get('title_max_length', 60)), title_analysis.get('too_long_titles', []), headers=['URL Pagina', 'Title', 'Lunghezza'], data_keys=['url', 'title', 'length'], column_widths=[10*cm, 5*cm, 2*cm])
        self.story.append(PageBreak())

        # Meta Descriptions
        self.story.append(Paragraph("Meta Descriptions", self.styles['SectionHeading']))
        meta_analysis = self.analysis_results['meta_description_analysis']
        self.story.append(Paragraph(f"• Pagine con Meta Description: {meta_analysis['pages_with_meta']}/{meta_analysis['total_pages']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine senza Meta Description: {len(detailed_issues.get('pages_without_meta', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Meta Description Duplicate: {len(detailed_issues.get('duplicate_meta_descriptions', []))} (istanze)", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Meta Description Troppo Corte: {len(meta_analysis.get('too_short_metas',[]))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Meta Description Troppo Lunghe: {len(meta_analysis.get('too_long_metas',[]))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {meta_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine senza Meta Description", detailed_issues.get('pages_without_meta', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'], column_widths=[13*cm, 4*cm])
        add_issue_table_subsection("Meta Description Duplicate", detailed_issues.get('duplicate_meta_descriptions', []), headers=['Meta Description Duplicata', 'URL Pagina Coinvolta', 'Conteggio Totale Duplicati'], data_keys=['meta', 'url', 'duplicate_count'], column_widths=[6*cm, 9*cm, 2*cm])
        add_issue_table_subsection("Meta Description Troppo Corte (< {0} caratteri)".format(SEO_CONFIG.get('meta_description_min_length', 50)), meta_analysis.get('too_short_metas',[]), headers=['URL Pagina', 'Meta Description', 'Lunghezza'], data_keys=['url', 'meta', 'length'], column_widths=[8*cm, 7*cm, 2*cm])
        add_issue_table_subsection("Meta Description Troppo Lunghe (> {0} caratteri)".format(SEO_CONFIG.get('meta_description_max_length',160)), meta_analysis.get('too_long_metas',[]), headers=['URL Pagina', 'Meta Description', 'Lunghezza'], data_keys=['url', 'meta', 'length'], column_widths=[8*cm, 7*cm, 2*cm])
        self.story.append(PageBreak())

        # Headings (H1, H2, H3)
        self.story.append(Paragraph("Headings (H1, H2, H3)", self.styles['SectionHeading']))
        headings_analysis = self.analysis_results.get('headings_analysis', {})
        self.story.append(Paragraph(f"• Pagine senza H1: {len(detailed_issues.get('missing_h1_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con H1 multipli: {len(detailed_issues.get('multiple_h1_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine senza H2: {len(detailed_issues.get('missing_h2_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine senza H3: {len(detailed_issues.get('missing_h3_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {headings_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine senza H1", detailed_issues.get('missing_h1_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'], column_widths=[13*cm, 4*cm])
        add_issue_table_subsection("Pagine con H1 Multipli", detailed_issues.get('multiple_h1_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'], column_widths=[13*cm, 4*cm])
        add_issue_table_subsection("Pagine senza H2", detailed_issues.get('missing_h2_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'], column_widths=[13*cm, 4*cm])
        add_issue_table_subsection("Pagine senza H3", detailed_issues.get('missing_h3_pages', []), headers=['URL Pagina', 'Problema Rilevato'], data_keys=['url', 'issue'], column_widths=[13*cm, 4*cm])
        self.story.append(PageBreak())

        # Immagini
        self.story.append(Paragraph("Immagini", self.styles['SectionHeading']))
        images_analysis = self.analysis_results['images_analysis'] # images_analysis from analyzer
        self.story.append(Paragraph(f"• Totale immagini: {images_analysis['total_images']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Con ALT text (contenuto): {images_analysis['images_with_alt']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Senza attributo ALT HTML: {images_analysis.get('images_without_alt',0)} ({len(detailed_issues.get('images_without_alt',[]))} instanze)", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Con attributo ALT vuoto: {images_analysis.get('images_with_empty_alt',0)} ({len(detailed_issues.get('images_with_empty_alt',[]))} instanze)", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Con attributo Title (contenuto): {images_analysis.get('images_with_title_attr',0)}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Senza attributo Title HTML: {images_analysis.get('images_without_title_attr',0)} ({len(detailed_issues.get('images_without_title_attr',[]))} instanze)", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Con attributo Title vuoto: {images_analysis.get('images_with_empty_title_attr',0)} ({len(detailed_issues.get('images_with_empty_title_attr',[]))} instanze)", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Immagini interrotte: {len(detailed_issues.get('broken_images', []))}", self.styles['ListItem'])) # Assuming broken_images are in detailed_issues
        self.story.append(Paragraph(f"• Punteggio: {images_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))

        img_headers = ['Pagina URL', 'URL Immagine', 'Problema']
        img_data_keys = ['url', 'image_src', 'issue']
        img_col_widths = [6*cm, 7*cm, 4*cm]

        add_issue_table_subsection("Immagini senza Attributo ALT HTML", detailed_issues.get('images_without_alt', []), headers=img_headers, data_keys=img_data_keys, column_widths=img_col_widths)
        add_issue_table_subsection("Immagini con Attributo ALT Vuoto", detailed_issues.get('images_with_empty_alt', []), headers=img_headers, data_keys=img_data_keys, column_widths=img_col_widths)
        add_issue_table_subsection("Immagini senza Attributo Title HTML", detailed_issues.get('images_without_title_attr', []), headers=img_headers, data_keys=img_data_keys, column_widths=img_col_widths)
        add_issue_table_subsection("Immagini con Attributo Title Vuoto", detailed_issues.get('images_with_empty_title_attr', []), headers=img_headers, data_keys=img_data_keys, column_widths=img_col_widths)
        # Assuming broken_images structure is {'url': page_url, 'image_src': img_src, 'issue': 'Immagine interrotta'}
        add_issue_table_subsection("Immagini Interrotte", detailed_issues.get('broken_images', []), headers=img_headers, data_keys=img_data_keys, column_widths=img_col_widths) 
        self.story.append(PageBreak())

        # Contenuto
        self.story.append(Paragraph("Contenuto", self.styles['SectionHeading']))
        content_analysis = self.analysis_results.get('content_analysis', {})
        self.story.append(Paragraph(f"• Pagine con conteggio parole basso: {len(detailed_issues.get('low_word_count_pages', []))}", self.styles['ListItem']))
        # Note: duplicate_content_pages and low_text_html_ratio_pages are not explicitly populated in detailed_issues by current analyzer.py
        # self.story.append(Paragraph(f"• Pagine con duplicati di contenuto: {len(detailed_issues.get('duplicate_content_pages', []))}", self.styles['ListItem']))
        # self.story.append(Paragraph(f"• Pagine con rapporto testo/HTML basso: {len(detailed_issues.get('low_text_html_ratio_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {content_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine con Conteggio Parole Basso (< {0} parole)".format(SEO_CONFIG.get('min_word_count',200)), detailed_issues.get('low_word_count_pages', []), headers=['URL Pagina', 'Conteggio Parole', 'Problema'], data_keys=['url', 'word_count', 'issue'], column_widths=[10*cm, 3*cm, 4*cm])
        # add_issue_table_subsection("Pagine con Duplicati di Contenuto", detailed_issues.get('duplicate_content_pages', []), headers=['URL Pagina', 'Problema'], data_keys=['url', 'issue'], column_widths=[12*cm, 5*cm])
        # add_issue_table_subsection("Pagine con Rapporto Testo/HTML Basso", detailed_issues.get('low_text_html_ratio_pages', []), headers=['URL Pagina', 'Rapporto T/H', 'Problema'], data_keys=['url', 'ratio', 'issue'], column_widths=[10*cm, 3*cm, 4*cm])
        self.story.append(PageBreak())

        # Link
        links_analysis = self.analysis_results.get('links_analysis', {})
        # Note: broken_links, redirect_chains, etc. are not explicitly populated in detailed_issues by current analyzer.py
        # self.story.append(Paragraph(f"• Link interni interrotti: {len(detailed_issues.get('broken_links', []))}", self.styles['ListItem']))
        # ... other list items for links ...
        self.story.append(Paragraph(f"• Punteggio: {links_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        # add_issue_table_subsection("Link Interni Interrotti", detailed_issues.get('broken_links', []), headers=['Pagina di Origine', 'URL Interrotto', 'Testo Anchor'], data_keys=['url', 'broken_link_url', 'anchor_text'], column_widths=[6*cm, 7*cm, 4*cm])
        # ... other table calls for links ...
        self.story.append(PageBreak())

        # Performance
        self.story.append(Paragraph("Performance", self.styles['SectionHeading']))
        perf_analysis = self.analysis_results['performance_analysis']
        self.story.append(Paragraph(f"• Pagine veloci: {perf_analysis['fast_pages']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine lente: {perf_analysis['slow_pages']} (Instanze: {len(detailed_issues.get('slow_pages',[]))})", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Tempo medio: {perf_analysis['average_response_time']:.2f}s", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Dimensione media: {perf_analysis['average_page_size']/1024:.1f} KB", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con dimensioni HTML troppo grandi: {len(detailed_issues.get('large_html_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {perf_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine con Dimensioni HTML Troppo Grandi (> {0} MB)".format(SEO_CONFIG.get('max_page_size_mb', 2)), detailed_issues.get('large_html_pages', []), headers=['URL Pagina', 'Dimensione (MB)', 'Problema'], data_keys=['url', 'size_mb', 'issue'], column_widths=[10*cm, 3*cm, 4*cm])
        add_issue_table_subsection("Pagine con Velocità di Caricamento Bassa (> {0}s)".format(PERFORMANCE_CONFIG.get('max_response_time',3)), detailed_issues.get('slow_pages', []), headers=['URL Pagina', 'Tempo (s)', 'Problema'], data_keys=['url', 'response_time', 'issue'], column_widths=[10*cm, 3*cm, 4*cm])
        self.story.append(PageBreak())

        # Tecnico
        tech_headers = ['URL Pagina', 'Problema Rilevato']
        tech_data_keys = ['url', 'issue']
        tech_col_widths = [13*cm, 4*cm]
        self.story.append(Paragraph("Aspetti Tecnici", self.styles['SectionHeading']))
        technical_analysis = self.analysis_results.get('technical_analysis', {})
        
        tech_issues_to_report = {
            'status_4xx_pages': "Pagine con Errori Client (4xx)",
            'status_5xx_pages': "Pagine con Errori Server (5xx)",
            'pages_without_canonical': "Pagine senza URL Canonico",
            'pages_without_lang': "Pagine senza Attributo Lingua",
            'pages_without_schema': "Pagine senza Schema Markup",
            # Add other technical issues here if analyzer.py populates their specific lists in detailed_issues
        }
        for key, text in tech_issues_to_report.items():
             self.story.append(Paragraph(f"• {text}: {len(detailed_issues.get(key, []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {technical_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        for key, text in tech_issues_to_report.items():
            data_to_pass = detailed_issues.get(key, [])
            if key == 'status_4xx_pages' or key == 'status_5xx_pages':
                 add_issue_table_subsection(text, data_to_pass, headers=['URL Pagina', 'Status Code', 'Problema'], data_keys=['url', 'status_code', 'issue'], column_widths=[10*cm, 3*cm, 4*cm])
            else:
                 add_issue_table_subsection(text, data_to_pass, headers=tech_headers, data_keys=tech_data_keys, column_widths=tech_col_widths)
        self.story.append(PageBreak())

        # SSL / Sicurezza
        # Note: SSL issues are typically domain-wide or not easily listed as page-specific URLs from current analyzer.py detailed_issues.
        # For now, the summary points from ssl_analysis are listed. If specific URL lists become available, tables can be added.
        self.story.append(Paragraph("SSL / Sicurezza", self.styles['SectionHeading']))
        ssl_analysis = self.analysis_results.get('ssl_analysis', {})
        self.story.append(Paragraph(f"• Certificato SSL presente: {'Sì' if ssl_analysis.get('has_ssl') else 'No'}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Certificato SSL valido: {'Sì' if ssl_analysis.get('ssl_valid') else 'No'}", self.styles['ListItem']))
        if ssl_analysis.get('ssl_expires'):
            self.story.append(Paragraph(f"• Scadenza Certificato SSL: {ssl_analysis.get('ssl_expires')}", self.styles['ListItem']))
        # Add more list items based on what ssl_analysis provides or what detailed_issues might contain for SSL.
        # For example:
        # self.story.append(Paragraph(f"• Pagine non sicure (HTTP): {len(detailed_issues.get('non_secure_pages', []))}", self.styles['ListItem']))
        # add_issue_table_subsection("Pagine Non Sicure (HTTP)", detailed_issues.get('non_secure_pages', []), headers=['URL Pagina', 'Problema'], data_keys=['url', 'issue'], column_widths=[13*cm, 4*cm])
        self.story.append(PageBreak())

    def _add_recommendations_section(self):
        """Aggiunge la sezione delle raccomandazioni con tabelle"""
        self.story.append(Paragraph("Raccomandazioni", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        recommendations = self.analysis_results['recommendations']

        if not recommendations:
            self.story.append(Paragraph("🎉 ECCELLENTE! Nessuna raccomandazione specifica identificata. Il sito presenta un'ottima ottimizzazione SEO.", self.styles['BodyText']))
            return

        # Helper per aggiungere una sottosezione con tabella di raccomandazioni
        def add_recommendation_table_subsection(title: str, recs: List[Dict]):
            if not recs:
                return
            
            self.story.append(Paragraph(title, self.styles['BodyText']))
            self.story.append(Spacer(1, 0.1 * inch))

            data = [['Categoria', 'Problema', 'Raccomandazione']]
            for rec in recs:
                data.append([
                    Paragraph(rec.get('category', 'N/A'), self.styles['BodyText']),
                    Paragraph(rec.get('issue', 'N/A'), self.styles['BodyText']),
                    Paragraph(rec.get('recommendation', 'N/A'), self.styles['BodyText'])
                ])
            
            table = Table(data, colWidths=[4*cm, 6*cm, 7*cm]) # Current widths, sum = 17cm
            
            # New conceptual PDF_CONFIG values for styling this table
            COLOR_TABLE_HEADER_BG = '#004080' 
            COLOR_TABLE_HEADER_TEXT = '#FFFFFF'
            COLOR_TABLE_ROW_BG_ODD = '#F0F4F7' 
            COLOR_TABLE_ROW_BG_EVEN = '#FFFFFF'
            COLOR_BORDER = '#CCCCCC'
            FONT_FAMILY_TABLE_HEADER = 'Helvetica-Bold'
            FONT_FAMILY_TABLE_BODY = 'Helvetica'
            FONT_SIZE_TABLE_HEADER = 9
            FONT_SIZE_TABLE_BODY = 9
            COLOR_TEXT_PRIMARY_FOR_TABLE = '#222222'

            rec_table_style = TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLOR_TABLE_HEADER_BG)),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor(COLOR_TABLE_HEADER_TEXT)),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), FONT_FAMILY_TABLE_HEADER),
                ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_TABLE_HEADER),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),

                # Body style
                ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY_TABLE_BODY),
                ('FONTSIZE', (0, 1), (-1, -1), FONT_SIZE_TABLE_BODY),
                ('TEXTCOLOR', (0, 1), (-1, -1), HexColor(COLOR_TEXT_PRIMARY_FOR_TABLE)),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 1), (-1, -1), 'TOP'), # Recommendations can be long
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor(COLOR_TABLE_ROW_BG_EVEN)),
            ])

            for i in range(1, len(data)): # Odd rows for body
                if i % 2 != 0:
                    rec_table_style.add('BACKGROUND', (0, i), (-1, i), HexColor(COLOR_TABLE_ROW_BG_ODD))
            
            rec_table_style.add('GRID', (0, 0), (-1, -1), 0.5, HexColor(COLOR_BORDER))
            rec_table_style.add('BOX', (0, 0), (-1, -1), 1, HexColor(COLOR_BORDER))
            
            table.setStyle(rec_table_style)
            self.story.append(table)
            self.story.append(Spacer(1, 0.3 * inch))

        high_priority = [r for r in recommendations if r['priority'] == 'Alto']
        medium_priority = [r for r in recommendations if r['priority'] == 'Medio']
        low_priority = [r for r in recommendations if r['priority'] == 'Basso']

        add_recommendation_table_subsection("Priorità Alta", high_priority)
        add_recommendation_table_subsection("Priorità Media", medium_priority)
        add_recommendation_table_subsection("Priorità Bassa", low_priority)
        self.story.append(PageBreak())

    def _add_appendix(self):
        """Aggiunge la sezione appendice con metodologia e glossario"""
        self.story.append(Paragraph("Appendice", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        self.story.append(Paragraph("Metodologia di Analisi", self.styles['BodyText']))
        methodology_text = """
        Questo report è stato generato utilizzando SEO Analyzer Pro, che esegue un'analisi completa del sito web
        basata sulle migliori pratiche SEO. L'analisi include:
        <ul>
            <li>Crawling automatico del sito web</li>
            <li>Verifica dei tag HTML principali (title, meta, headings)</li>
            <li>Analisi delle immagini e degli alt text</li>
            <li>Valutazione della qualità del contenuto</li>
            <li>Test delle performance di caricamento</li>
            <li>Controllo degli aspetti tecnici (SSL, canonical, etc.)</li>
        </ul>
        Il punteggio finale è calcolato come media ponderata di tutti i fattori analizzati.
        """
        self.story.append(Paragraph(methodology_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.2 * inch))

        self.story.append(Paragraph("Glossario", self.styles['BodyText']))
        glossary_data = [
            ['Termine', 'Definizione'],
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
        glossary_table = Table(glossary_data, colWidths=[4*cm, 13*cm]) # Total 17cm
        
        # New conceptual PDF_CONFIG values for styling this table
        COLOR_TABLE_HEADER_BG = '#004080' 
        COLOR_TABLE_HEADER_TEXT = '#FFFFFF'
        COLOR_TABLE_ROW_BG_ODD = '#F0F4F7' 
        COLOR_TABLE_ROW_BG_EVEN = '#FFFFFF'
        COLOR_BORDER = '#CCCCCC'
        FONT_FAMILY_TABLE_HEADER = 'Helvetica-Bold'
        FONT_FAMILY_TABLE_BODY = 'Helvetica'
        FONT_SIZE_TABLE_HEADER = 9
        FONT_SIZE_TABLE_BODY = 9
        COLOR_TEXT_PRIMARY_FOR_TABLE = '#222222'

        glossary_style = TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLOR_TABLE_HEADER_BG)),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor(COLOR_TABLE_HEADER_TEXT)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_FAMILY_TABLE_HEADER),
            ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_TABLE_HEADER),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Body style
            ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY_TABLE_BODY),
            ('FONTSIZE', (0, 1), (-1, -1), FONT_SIZE_TABLE_BODY),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor(COLOR_TEXT_PRIMARY_FOR_TABLE)),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'), # Definitions can be long
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor(COLOR_TABLE_ROW_BG_EVEN)),
        ])

        for i in range(1, len(glossary_data)): # Odd rows for body
            if i % 2 != 0:
                glossary_style.add('BACKGROUND', (0, i), (-1, i), HexColor(COLOR_TABLE_ROW_BG_ODD))
        
        glossary_style.add('GRID', (0, 0), (-1, -1), 0.5, HexColor(COLOR_BORDER))
        glossary_style.add('BOX', (0, 0), (-1, -1), 1, HexColor(COLOR_BORDER))
            
        glossary_table.setStyle(glossary_style)
        self.story.append(glossary_table)
        self.story.append(Spacer(1, 0.5 * inch))

    def _get_evaluation_text(self, score):
        """Restituisce il testo di valutazione basato sul punteggio"""
        if score >= 90:
            return "Eccellente"
        elif score >= 70:
            return "Buono"
        elif score >= 50:
            return "Da Migliorare"
        else:
            return "Critico"
    
    def _get_status_text(self, score):
        """Restituisce il testo di stato basato sul punteggio"""
        if score >= 90:
            return "✓ Eccellente"
        elif score >= 70:
            return "⚠ Buono"
        elif score >= 50:
            return "⚠ Da Migliorare"
        else:
            return "✗ Critico"
    
    def _get_score_color_hex(self, score):
        """Restituisce il codice colore esadecimale basato sul punteggio"""
        # Using direct hex values conceptually from the new PDF_CONFIG
        if score >= 90:
            return '#28A745'  # success (Green)
        elif score >= 70:
            return '#005A9C'  # primary (Dark Blue for "Good" as per new scheme)
        elif score >= 50:
            return '#FFC107'  # warning (Amber for "Da Migliorare")
        else:
            return '#DC3545'  # error (Red for "Critico")

    def _identify_strengths_weaknesses(self):
        """Identifica punti di forza e debolezze"""
        strengths = []
        weaknesses = []
        
        # Controlla ogni categoria
        categories = {
            'Title Tags': self.analysis_results['title_analysis']['score'],
            'Meta Descriptions': self.analysis_results['meta_description_analysis']['score'],
            'Immagini': self.analysis_results['images_analysis']['score'],
            'Contenuto': self.analysis_results['content_analysis']['score'],
            'Performance': self.analysis_results['performance_analysis']['score'],
            'SSL': self.analysis_results['ssl_analysis']['score'],
            'Link Interni': self.analysis_results['links_analysis']['score'],
            'Aspetti Tecnici': self.analysis_results['technical_analysis']['score']
        }
        
        for category, score in categories.items():
            if score >= 80:
                strengths.append(f"{category} ottimizzato correttamente (punteggio: {score}/100)")
            elif score < 50:
                weaknesses.append(f"{category} necessita miglioramenti urgenti (punteggio: {score}/100)")
            elif score < 70: # Aggiungiamo anche le aree "Da Migliorare" come debolezze
                 weaknesses.append(f"{category} richiede attenzione (punteggio: {score}/100)")

        # Aggiungi problemi specifici da detailed_issues come debolezze
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        
        # Iteriamo su tutte le liste in detailed_issues e aggiungiamo i problemi come debolezze
        for issue_type, issues_list in detailed_issues.items():
            if isinstance(issues_list, list): # Assicurati che sia una lista
                for issue in issues_list:
                    # Evitiamo di duplicare se già coperto dalle categorie di punteggio
                    # E cerchiamo di dare un messaggio più specifico se possibile
                    if 'url' in issue and 'type' in issue:
                        weaknesses.append(f"Problema: {issue.get('type')} su {issue.get('url')}")
                    elif isinstance(issue, str): # A volte è solo un URL o una stringa
                        weaknesses.append(f"Problema rilevato: {issue_type} - {issue}")
        
        return strengths, weaknesses
        
    def generate_pdf(self, filename: str) -> bool:
        """Genera il report PDF"""
        try:
            self.doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                leftMargin=PDF_CONFIG['margin']['left'] * cm,
                rightMargin=PDF_CONFIG['margin']['right'] * cm,
                topMargin=PDF_CONFIG['margin']['top'] * cm,
                bottomMargin=PDF_CONFIG['margin']['bottom'] * cm
            )
            self.story = []

            self._add_header()
            # self.story.append(PageBreak()) # Nuova pagina dopo l'header

            self._add_executive_summary()
            # self.story.append(PageBreak()) # Nuova pagina dopo il riassunto

            self._add_site_health_chart() # Aggiungi il grafico del Site Health
            # self.story.append(PageBreak()) # Nuova pagina dopo il grafico

            self._add_score_overview()
            # self.story.append(PageBreak()) # Nuova pagina dopo la panoramica punteggi

            self._add_detailed_analysis_section()
            # self.story.append(PageBreak()) # Nuova pagina dopo l'analisi dettagliata

            self._add_recommendations_section()
            # self.story.append(PageBreak()) # Nuova pagina dopo le raccomandazioni

            self._add_appendix()
            
            self.doc.build(self.story)
            return True
        except Exception as e:
            print(f"Errore durante la generazione del PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

