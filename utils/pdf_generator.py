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

        # Stili per i titoli delle sottosezioni di impatto (Errori, Avvertimenti, Avvisi)
        style_name = 'ImpactSectionTitleError'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['h3'], fontName=PDF_CONFIG['font_family'], fontSize=PDF_CONFIG['font_sizes']['body'] + 1, textColor=HexColor(PDF_CONFIG['colors']['error']), spaceBefore=10, spaceAfter=5))

        style_name = 'ImpactSectionTitleWarning'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['h3'], fontName=PDF_CONFIG['font_family'], fontSize=PDF_CONFIG['font_sizes']['body'] + 1, textColor=HexColor(PDF_CONFIG['colors']['warning']), spaceBefore=10, spaceAfter=5))

        style_name = 'ImpactSectionTitleNotice'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['h3'], fontName=PDF_CONFIG['font_family'], fontSize=PDF_CONFIG['font_sizes']['body'] + 1, textColor=HexColor(PDF_CONFIG['colors']['success']), spaceBefore=10, spaceAfter=5)) # Using success for notices

        # Stile per la descrizione di un check specifico
        style_name = 'CheckDescription'
        if style_name not in self.styles:
            self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['BodyText'], fontName=PDF_CONFIG['font_family'], spaceBefore=5, spaceAfter=2, keepWithNext=1))
            self.styles['CheckDescription'].fontName = PDF_CONFIG['font_family'] # Ensure bold or specific font if needed

        # Stile per i singoli risultati (URL + messaggio)
        style_name = 'FindingListItem'
        if style_name not in self.styles:
             self.styles.add(ParagraphStyle(name=style_name, parent=self.styles['ListItem'], leftIndent=30, spaceAfter=1))
        
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
            'SSL': self.analysis_results['ssl_analysis']['score'],
            # New Scores
            'Punteggio OCM': self.analysis_results.get('ocm_category_score', 0),
            'Punteggio SEO Audit': self.analysis_results.get('seo_audit_category_score', 0),
        }

        for category_name, score_value in categories.items():
            status_text = self._get_status_text(score_value)
            # Determina lo stile del testo del punteggio in base al valore
            score_style = self.styles['BodyText'] # Default
            if score_value >= 90: score_style = self.styles['ScoreExcellent']
            elif score_value >= 70: score_style = self.styles['ScoreGood']
            elif score_value >= 50: score_style = self.styles['ScoreWarning'] # Adattato, prima era 'ScoreGood' per 70-90
            else: score_style = self.styles['ScoreCritical']

            # Allinea a sinistra il nome della categoria, a destra il punteggio
            category_paragraph = Paragraph(category_name, self.styles['BodyText'])
            score_paragraph = Paragraph(f"{score_value}/100", score_style) # Usa lo stile colorato e allineato a destra
            status_paragraph = Paragraph(status_text, self.styles['BodyText']) # Allineamento centrale di default per la tabella

            data.append([category_paragraph, score_paragraph, status_paragraph])

        table = Table(data, colWidths=[7*cm, 3*cm, 7*cm]) # Adjusted colWidths for better spacing
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
            ('ALIGN', (0,1), (0,-1), 'LEFT'),      # Allinea a sinistra i nomi delle categorie
            ('ALIGN', (1,1), (1,-1), 'RIGHT'),     # Allinea a destra i punteggi
            ('ALIGN', (2,1), (2,-1), 'CENTER'),    # Allinea al centro gli stati
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


    # def _add_detailed_analysis_section(self): # Commenting out old section
    #     """Aggiunge la sezione di analisi dettagliata con tabelle per i problemi"""
    #     self.story.append(Paragraph("Analisi Dettagliata", self.styles['SectionHeading']))
    #     self.story.append(Spacer(1, 0.2 * inch))
    #     # ... (implementation of old detailed analysis) ...
    #     pass


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

            # self._add_detailed_analysis_section() # Old section commented out
            # self.story.append(PageBreak())

            self._add_ocm_report_section()
            self.story.append(PageBreak())
            self._add_seo_audit_report_section()
            self.story.append(PageBreak())

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

    # --- New methods for OCM and SEO_AUDIT sections ---

    def _add_ocm_report_section(self):
        """Aggiunge la sezione del report OCM."""
        self.story.append(Paragraph("OCM (Ottimizzazione Contenuti per Motori di Ricerca)", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        if 'classified_detailed_issues' not in self.analysis_results or \
           CATEGORY_OCM not in self.analysis_results['classified_detailed_issues']:
            self.story.append(Paragraph("Dati OCM non disponibili.", self.styles['BodyText']))
            return

        ocm_data = self.analysis_results['classified_detailed_issues'][CATEGORY_OCM]

        self._add_impact_subsection(CATEGORY_OCM, IMPACT_ERROR, "🔴 ERRORI OCM (Alto Impatto):", ocm_data.get(IMPACT_ERROR, {}), PDF_CONFIG['colors']['error'])
        self._add_impact_subsection(CATEGORY_OCM, IMPACT_WARNING, "🟡 AVVERTIMENTI OCM (Medio Impatto):", ocm_data.get(IMPACT_WARNING, {}), PDF_CONFIG['colors']['warning'])
        self._add_impact_subsection(CATEGORY_OCM, IMPACT_NOTICE, "🟢 AVVISI OCM (Basso Impatto):", ocm_data.get(IMPACT_NOTICE, {}), PDF_CONFIG['colors']['success']) # Using success for notices

    def _add_seo_audit_report_section(self):
        """Aggiunge la sezione del report SEO AUDIT."""
        self.story.append(Paragraph("📊 SEO AUDIT (Analisi Strategica e Tecnica Approfondita)", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2 * inch))

        if 'classified_detailed_issues' not in self.analysis_results or \
           CATEGORY_SEO_AUDIT not in self.analysis_results['classified_detailed_issues']:
            self.story.append(Paragraph("Dati SEO Audit non disponibili.", self.styles['BodyText']))
            return

        seo_audit_data = self.analysis_results['classified_detailed_issues'][CATEGORY_SEO_AUDIT]

        self._add_impact_subsection(CATEGORY_SEO_AUDIT, IMPACT_ERROR, "🔴 ERRORI SEO AUDIT (Alto Impatto):", seo_audit_data.get(IMPACT_ERROR, {}), PDF_CONFIG['colors']['error'])
        self._add_impact_subsection(CATEGORY_SEO_AUDIT, IMPACT_WARNING, "🟡 AVVERTIMENTI SEO AUDIT (Medio Impatto):", seo_audit_data.get(IMPACT_WARNING, {}), PDF_CONFIG['colors']['warning'])
        self._add_impact_subsection(CATEGORY_SEO_AUDIT, IMPACT_NOTICE, "🟢 AVVISI SEO AUDIT (Basso Impatto):", seo_audit_data.get(IMPACT_NOTICE, {}), PDF_CONFIG['colors']['success'])


    def _add_impact_subsection(self, category_key: str, impact_key: str, section_title_text: str, checks_in_impact_level: Dict, title_color_hex: str):
        """
        Aggiunge una sottosezione per un livello di impatto specifico (Errori, Avvertimenti, Avvisi)
        all'interno di una categoria (OCM o SEO_AUDIT).
        """
        # Determina lo stile del titolo della sottosezione in base all'impatto
        if impact_key == IMPACT_ERROR:
            title_style = self.styles['ImpactSectionTitleError']
        elif impact_key == IMPACT_WARNING:
            title_style = self.styles['ImpactSectionTitleWarning']
        elif impact_key == IMPACT_NOTICE:
            title_style = self.styles['ImpactSectionTitleNotice']
        else: # Fallback
            title_style = self.styles['h3']
            # Manually set color if not using specific styles
            # title_style.textColor = HexColor(title_color_hex)


        self.story.append(Paragraph(section_title_text, title_style))
        self.story.append(Spacer(1, 0.1 * inch))

        found_issues_in_subsection = False
        if checks_in_impact_level:
            for check_id, check_data in checks_in_impact_level.items():
                if check_data.get('count', 0) > 0:
                    found_issues_in_subsection = True

                    # Add check description as a sub-sub-heading
                    self.story.append(Paragraph(f"<b>{check_data['description']}</b> (ID: {check_id}, Peso: {check_data['weight']})", self.styles['CheckDescription']))

                    # List each finding
                    for finding in check_data.get('findings', []):
                        finding_text = f"URL: {finding.get('url', 'N/A')}"
                        if 'message' in finding and finding['message']:
                             # Escape HTML entities in message if any, to prevent ReportLab errors
                            message_clean = finding['message'].replace('<', '&lt;').replace('>', '&gt;')
                            finding_text += f" - <i>Dettaglio: {message_clean}</i>"

                        self.story.append(Paragraph(f"• {finding_text}", self.styles['FindingListItem']))
                    self.story.append(Spacer(1, 0.1 * inch)) # Spacer after each check's findings

        if not found_issues_in_subsection:
            self.story.append(Paragraph(f"Nessun problema di tipo '{impact_key.lower()}' trovato in questa categoria.", self.styles['BodyText']))

        self.story.append(Spacer(1, 0.2 * inch)) # Spacer after the whole impact subsection
