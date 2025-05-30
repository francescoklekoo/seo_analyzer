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
        # Stile titolo principale
        style_name = 'CustomTitle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                parent=self.styles['h1'],
                fontName=PDF_CONFIG['font_family'],
                fontSize=PDF_CONFIG['font_sizes']['title'],
                leading=36,
                alignment=TA_CENTER,
                textColor=HexColor(PDF_CONFIG['colors']['primary'])
            ))
        
        # Stile sottotitolo
        style_name = 'CustomSubtitle'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                parent=self.styles['h2'],
                fontName=PDF_CONFIG['font_family'],
                fontSize=PDF_CONFIG['font_sizes']['heading'],
                leading=20,
                alignment=TA_CENTER,
                textColor=HexColor(PDF_CONFIG['colors']['dark_gray'])
            ))

        # Stile per le sezioni
        style_name = 'SectionHeading'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                parent=self.styles['h2'],
                fontName=PDF_CONFIG['font_family'],
                fontSize=PDF_CONFIG['font_sizes']['heading'],
                leading=18,
                spaceAfter=10,
                textColor=HexColor(PDF_CONFIG['colors']['primary'])
            ))

        # Stile per il testo normale
        style_name = 'BodyText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                parent=self.styles['Normal'],
                fontName=PDF_CONFIG['font_family'],
                fontSize=PDF_CONFIG['font_sizes']['body'],
                leading=14,
                spaceAfter=6,
                textColor=HexColor(PDF_CONFIG['colors']['dark_gray'])
            ))

        # Stile per i punti elenco
        style_name = 'ListItem'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                parent=self.styles['Normal'],
                fontName=PDF_CONFIG['font_family'],
                fontSize=PDF_CONFIG['font_sizes']['body'],
                leading=14,
                leftIndent=20,
                spaceAfter=3,
                textColor=HexColor(PDF_CONFIG['colors']['dark_gray'])
            ))

        # Stile per testo piccolo (es. footer)
        style_name = 'SmallText'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(
                name=style_name,
                parent=self.styles['Normal'],
                fontName=PDF_CONFIG['font_family'],
                fontSize=PDF_CONFIG['font_sizes']['small'],
                leading=10,
                alignment=TA_CENTER,
                textColor=HexColor(PDF_CONFIG['colors']['dark_gray'])
            ))

        # Stili per i colori dei punteggi
        style_name = 'ScoreExcellent'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], textColor=HexColor(PDF_CONFIG['colors']['success']), fontName=PDF_CONFIG['font_family'], fontSize=PDF_CONFIG['font_sizes']['body'], alignment=TA_RIGHT))
        style_name = 'ScoreGood'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], textColor=HexColor(PDF_CONFIG['colors']['primary']), fontName=PDF_CONFIG['font_family'], fontSize=PDF_CONFIG['font_sizes']['body'], alignment=TA_RIGHT))
        style_name = 'ScoreWarning'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], textColor=HexColor(PDF_CONFIG['colors']['warning']), fontName=PDF_CONFIG['font_family'], fontSize=PDF_CONFIG['font_sizes']['body'], alignment=TA_RIGHT))
        style_name = 'ScoreCritical'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], textColor=HexColor(PDF_CONFIG['colors']['error']), fontName=PDF_CONFIG['font_family'], fontSize=PDF_CONFIG['font_sizes']['body'], alignment=TA_RIGHT))
        
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

        table = Table(data, colWidths=[4*cm, 2.5*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['primary_light'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), PDF_CONFIG['font_family']),
            ('FONTSIZE', (0, 0), (-1, 0), PDF_CONFIG['font_sizes']['body']),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor(PDF_CONFIG['colors']['light_gray'])),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(PDF_CONFIG['colors']['border'])),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(PDF_CONFIG['colors']['primary_dark'])),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
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
        colors_pie = [HexColor(PDF_CONFIG['colors']['success']), HexColor(PDF_CONFIG['colors']['error'])]

        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 50
        pie.height = 150
        pie.width = 150
        pie.data = data
        pie.labels = labels
        pie.slices.strokeWidth = 0.5
        
        for i, color in enumerate(colors_pie):
            pie.slices[i].fillColor = color
            pie.slices[i].fontName = PDF_CONFIG['font_family']
            pie.slices[i].fontSize = PDF_CONFIG['font_sizes']['small']
            pie.slices[i].labelRadius = 1.1 # Posiziona le etichette fuori dalla torta

        # Aggiungi il testo centrale con la percentuale
        center_x = pie.x + pie.width / 2
        center_y = pie.y + pie.height / 2
        
        # Testo centrale "XX%"
        overall_score_text = String(center_x, center_y + 10, f"{int(overall_score)}%",
                                    fontName=PDF_CONFIG['font_family'],
                                    fontSize=36, # Grande per la percentuale
                                    fillColor=HexColor(PDF_CONFIG['colors']['dark_gray']),
                                    textAnchor='middle')
        drawing.add(overall_score_text)

        # Testo centrale "Site Health"
        site_health_label = String(center_x, center_y - 15, "Site Health",
                                   fontName=PDF_CONFIG['font_family'],
                                   fontSize=PDF_CONFIG['font_sizes']['body'],
                                   fillColor=HexColor(PDF_CONFIG['colors']['dark_gray']),
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
        def add_issue_table_subsection(title: str, issues: List[Dict], issue_type_key: str = 'type'):
            if not issues:
                return
            
            self.story.append(Paragraph(title, self.styles['BodyText']))
            self.story.append(Spacer(1, 0.1 * inch))

            data = [['URL', 'Tipo Problema']]
            for issue in issues:
                url = issue.get('url', 'N/A')
                # Per i problemi di immagini, l'URL è direttamente l'URL dell'immagine, non un dizionario con 'type'
                if issue_type_key == 'url':
                    issue_type = "Immagine" # O un altro valore predefinito
                else:
                    issue_type = issue.get(issue_type_key, 'Sconosciuto')
                data.append([
                    Paragraph(url, self.styles['BodyText']),
                    Paragraph(issue_type, self.styles['BodyText'])
                ])
            
            table = Table(data, colWidths=[12*cm, 5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['secondary'])),
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
        self.story.append(Paragraph(f"• Title duplicati: {len(detailed_issues.get('duplicate_titles', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Title troppo corti: {len(title_analysis['too_short_titles'])}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Title troppo lunghi: {len(title_analysis['too_long_titles'])}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {title_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine senza Title", detailed_issues.get('pages_without_title', []))
        add_issue_table_subsection("Title Duplicati", detailed_issues.get('duplicate_titles', []))
        add_issue_table_subsection("Title Troppo Corti", title_analysis['too_short_titles'])
        add_issue_table_subsection("Title Troppo Lunghi", title_analysis['too_long_titles'])
        self.story.append(PageBreak())

        # Meta Descriptions
        self.story.append(Paragraph("Meta Descriptions", self.styles['SectionHeading']))
        meta_analysis = self.analysis_results['meta_description_analysis']
        self.story.append(Paragraph(f"• Pagine con Meta Description: {meta_analysis['pages_with_meta']}/{meta_analysis['total_pages']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine senza Meta Description: {len(detailed_issues.get('pages_without_meta', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Meta Description Duplicate: {len(detailed_issues.get('duplicate_meta_descriptions', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Meta Description Troppo Corte: {len(meta_analysis['too_short_metas'])}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Meta Description Troppo Lunghe: {len(meta_analysis['too_long_metas'])}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {meta_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine senza Meta Description", detailed_issues.get('pages_without_meta', []))
        add_issue_table_subsection("Meta Description Duplicate", detailed_issues.get('duplicate_meta_descriptions', []))
        add_issue_table_subsection("Meta Description Troppo Corte", meta_analysis['too_short_metas'])
        add_issue_table_subsection("Meta Description Troppo Lunghe", meta_analysis['too_long_metas'])
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
        add_issue_table_subsection("Pagine senza H1", detailed_issues.get('missing_h1_pages', []))
        add_issue_table_subsection("Pagine con H1 Multipli", detailed_issues.get('multiple_h1_pages', []))
        add_issue_table_subsection("Pagine senza H2", detailed_issues.get('missing_h2_pages', []))
        add_issue_table_subsection("Pagine senza H3", detailed_issues.get('missing_h3_pages', []))
        self.story.append(PageBreak())

        # Immagini
        self.story.append(Paragraph("Immagini", self.styles['SectionHeading']))
        images_analysis = self.analysis_results['images_analysis']
        self.story.append(Paragraph(f"• Totale immagini: {images_analysis['total_images']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Con alt text: {images_analysis['images_with_alt']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Senza alt text: {len(detailed_issues.get('images_without_alt', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Senza attributo title: {len(detailed_issues.get('images_without_title', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Alt vuoto: {images_analysis['images_with_empty_alt']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Immagini interrotte: {len(detailed_issues.get('broken_images', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {images_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        # Per i problemi di immagini, l'URL è direttamente l'URL dell'immagine, non un dizionario con 'type'
        add_issue_table_subsection("Immagini senza Alt Text", detailed_issues.get('images_without_alt', []), issue_type_key='url') 
        add_issue_table_subsection("Immagini senza Attributo Title", detailed_issues.get('images_without_title', []), issue_type_key='url') 
        add_issue_table_subsection("Immagini Interrotte", detailed_issues.get('broken_images', []), issue_type_key='url') 
        self.story.append(PageBreak())

        # Contenuto
        self.story.append(Paragraph("Contenuto", self.styles['SectionHeading']))
        content_analysis = self.analysis_results.get('content_analysis', {})
        self.story.append(Paragraph(f"• Pagine con conteggio parole basso: {len(detailed_issues.get('low_word_count_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con duplicati di contenuto: {len(detailed_issues.get('duplicate_content_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con rapporto testo/HTML basso: {len(detailed_issues.get('low_text_html_ratio_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {content_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine con Conteggio Parole Basso", detailed_issues.get('low_word_count_pages', []))
        add_issue_table_subsection("Pagine con Duplicati di Contenuto", detailed_issues.get('duplicate_content_pages', []))
        add_issue_table_subsection("Pagine con Rapporto Testo/HTML Basso", detailed_issues.get('low_text_html_ratio_pages', []))
        self.story.append(PageBreak())

        # Link
        self.story.append(Paragraph("Link", self.styles['SectionHeading']))
        links_analysis = self.analysis_results.get('links_analysis', {})
        self.story.append(Paragraph(f"• Link interni interrotti: {len(detailed_issues.get('broken_links', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Loop e catene di reindirizzamenti: {len(detailed_issues.get('redirect_chains', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con link canonico interrotto: {len(detailed_issues.get('broken_canonical_links', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con più URL canonici: {len(detailed_issues.get('multiple_canonical_urls', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {links_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Link Interni Interrotti", detailed_issues.get('broken_links', []))
        add_issue_table_subsection("Loop e Catene di Reindirizzamenti", detailed_issues.get('redirect_chains', []))
        add_issue_table_subsection("Pagine con Link Canonico Interrotto", detailed_issues.get('broken_canonical_links', []))
        add_issue_table_subsection("Pagine con Più URL Canonici", detailed_issues.get('multiple_canonical_urls', []))
        self.story.append(PageBreak())

        # Performance
        self.story.append(Paragraph("Performance", self.styles['SectionHeading']))
        perf_analysis = self.analysis_results['performance_analysis']
        self.story.append(Paragraph(f"• Pagine veloci: {perf_analysis['fast_pages']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine lente: {perf_analysis['slow_pages']}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Tempo medio: {perf_analysis['average_response_time']:.2f}s", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Dimensione media: {perf_analysis['average_page_size']/1024:.1f} KB", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con dimensioni HTML troppo grandi: {len(detailed_issues.get('large_html_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con velocità di caricamento bassa: {len(detailed_issues.get('slow_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {perf_analysis['score']}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine con Dimensioni HTML Troppo Grandi", detailed_issues.get('large_html_pages', []))
        add_issue_table_subsection("Pagine con Velocità di Caricamento Bassa", detailed_issues.get('slow_pages', []))
        self.story.append(PageBreak())

        # Tecnico
        self.story.append(Paragraph("Aspetti Tecnici", self.styles['SectionHeading']))
        technical_analysis = self.analysis_results.get('technical_analysis', {})
        self.story.append(Paragraph(f"• Pagine non raggiungibili dal crawler: {len(detailed_issues.get('unreachable_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Problemi risoluzione DNS: {len(detailed_issues.get('dns_resolution_issues', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Formati URL non corretti: {len(detailed_issues.get('invalid_url_format_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Robots.txt con errori: {len(detailed_issues.get('robots_txt_errors', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Sitemap.xml con errori: {len(detailed_issues.get('sitemap_xml_errors', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine sbagliate in sitemap.xml: {len(detailed_issues.get('sitemap_wrong_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Problemi risoluzione WWW: {len(detailed_issues.get('www_resolution_issues', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine senza tag viewport: {len(detailed_issues.get('pages_without_viewport', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine AMP senza tag canonici: {len(detailed_issues.get('amp_no_canonical_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Problemi hreflang: {len(detailed_issues.get('hreflang_issues', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Conflitti hreflang: {len(detailed_issues.get('hreflang_conflicts', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Link hreflang sbagliati: {len(detailed_issues.get('hreflang_broken_links', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine con meta refresh tag: {len(detailed_issues.get('meta_refresh_tags', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• CSS/JS interni inaccessibili: {len(detailed_issues.get('inaccessible_css_js', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Sitemap.xml troppo pesanti: {len(detailed_issues.get('large_sitemap_files', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Elementi dati strutturati non validi: {len(detailed_issues.get('invalid_structured_data', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Pagine senza valore larghezza viewport: {len(detailed_issues.get('pages_without_viewport_width', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {technical_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine Non Raggiungibili dal Crawler", detailed_issues.get('unreachable_pages', []))
        add_issue_table_subsection("Problemi Risoluzione DNS", detailed_issues.get('dns_resolution_issues', []))
        add_issue_table_subsection("Formati URL Non Corretti", detailed_issues.get('invalid_url_format_pages', []))
        add_issue_table_subsection("Robots.txt con Errori", detailed_issues.get('robots_txt_errors', []))
        add_issue_table_subsection("Sitemap.xml con Errori", detailed_issues.get('sitemap_xml_errors', []))
        add_issue_table_subsection("Pagine Sbagliate in Sitemap.xml", detailed_issues.get('sitemap_wrong_pages', []))
        add_issue_table_subsection("Problemi Risoluzione WWW", detailed_issues.get('www_resolution_issues', []))
        add_issue_table_subsection("Pagine senza Tag Viewport", detailed_issues.get('pages_without_viewport', []))
        add_issue_table_subsection("Pagine AMP senza Tag Canonici", detailed_issues.get('amp_no_canonical_pages', []))
        add_issue_table_subsection("Problemi Hreflang", detailed_issues.get('hreflang_issues', []))
        add_issue_table_subsection("Conflitti Hreflang", detailed_issues.get('hreflang_conflicts', []))
        add_issue_table_subsection("Link Hreflang Sbagliati", detailed_issues.get('hreflang_broken_links', []))
        add_issue_table_subsection("Pagine con Meta Refresh Tag", detailed_issues.get('meta_refresh_tags', []))
        add_issue_table_subsection("CSS/JS Interni Inaccessibili", detailed_issues.get('inaccessible_css_js', []))
        add_issue_table_subsection("Sitemap.xml Troppo Pesanti", detailed_issues.get('large_sitemap_files', []))
        add_issue_table_subsection("Elementi Dati Strutturati Non Validi", detailed_issues.get('invalid_structured_data', []))
        add_issue_table_subsection("Pagine senza Valore Larghezza Viewport", detailed_issues.get('pages_without_viewport_width', []))
        self.story.append(PageBreak())

        # SSL / Sicurezza
        self.story.append(Paragraph("SSL / Sicurezza", self.styles['SectionHeading']))
        ssl_analysis = self.analysis_results.get('ssl_analysis', {})
        self.story.append(Paragraph(f"• Pagine non sicure (HTTP): {len(detailed_issues.get('non_secure_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Certificato in scadenza/scaduto: {len(detailed_issues.get('ssl_expired_or_expiring_issues', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Vecchio protocollo sicurezza: {len(detailed_issues.get('old_security_protocol_issues', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Certificato nome errato: {len(detailed_issues.get('ssl_wrong_name_issues', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Problemi contenuti misti: {len(detailed_issues.get('mixed_content_pages', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Nessun reindirizzamento HTTP->HTTPS homepage: {len(detailed_issues.get('http_to_https_no_redirect_issues', []))}", self.styles['ListItem']))
        self.story.append(Paragraph(f"• Punteggio: {ssl_analysis.get('score', 'N/A')}/100", self.styles['ListItem']))
        self.story.append(Spacer(1, 0.1 * inch))
        add_issue_table_subsection("Pagine Non Sicure (HTTP)", detailed_issues.get('non_secure_pages', []))
        add_issue_table_subsection("Certificato in Scadenza/Scaduto", detailed_issues.get('ssl_expired_or_expiring_issues', []))
        add_issue_table_subsection("Vecchio Protocollo Sicurezza", detailed_issues.get('old_security_protocol_issues', []))
        add_issue_table_subsection("Certificato Nome Errato", detailed_issues.get('ssl_wrong_name_issues', []))
        add_issue_table_subsection("Problemi Contenuti Misti", detailed_issues.get('mixed_content_pages', []))
        add_issue_table_subsection("Nessun Reindirizzamento HTTP->HTTPS Homepage", detailed_issues.get('http_to_https_no_redirect_issues', []))
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
            
            table = Table(data, colWidths=[4*cm, 6*cm, 7*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['secondary'])),
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
        glossary_table = Table(glossary_data, colWidths=[4*cm, 13*cm])
        glossary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['secondary'])),
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
        if score >= 90:
            return PDF_CONFIG['colors']['success']
        elif score >= 70:
            return PDF_CONFIG['colors']['warning']
        elif score >= 50:
            return PDF_CONFIG['colors']['primary'] # Usiamo primary per "Da Migliorare"
        else:
            return PDF_CONFIG['colors']['error']

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
            self.story.append(PageBreak()) # Nuova pagina dopo l'header

            self._add_executive_summary()
            self.story.append(PageBreak()) # Nuova pagina dopo il riassunto

            self._add_site_health_chart() # Aggiungi il grafico del Site Health
            self.story.append(PageBreak()) # Nuova pagina dopo il grafico

            self._add_score_overview()
            self.story.append(PageBreak()) # Nuova pagina dopo la panoramica punteggi

            self._add_detailed_analysis_section()
            self.story.append(PageBreak()) # Nuova pagina dopo l'analisi dettagliata

            self._add_recommendations_section()
            self.story.append(PageBreak()) # Nuova pagina dopo le raccomandazioni

            self._add_appendix()
            
            self.doc.build(self.story)
            return True
        except Exception as e:
            print(f"Errore durante la generazione del PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

