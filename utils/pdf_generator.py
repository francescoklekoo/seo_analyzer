"""
Generatore di report PDF per l'analisi SEO
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, red, green, orange
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.lib import colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from datetime import datetime
from typing import Dict, List
import os

from config import *

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
        """Configura gli stili personalizzati"""
        # Stile titolo principale
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor(PDF_CONFIG['colors']['primary']),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Stile sezione
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor(PDF_CONFIG['colors']['primary']),
            fontName='Helvetica-Bold'
        ))
        
        # Stile sottosezione
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=HexColor(PDF_CONFIG['colors']['dark_gray']),
            fontName='Helvetica-Bold'
        ))
        
        # Stile corpo
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Stile per highlight
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor(PDF_CONFIG['colors']['primary']),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        
        # Stile per raccomandazioni
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=8,
            fontName='Helvetica'
        ))
    
    def generate_pdf(self, output_path: str) -> bool:
        """Genera il report PDF completo"""
        try:
            print(f"Debug PDF: Inizio generazione PDF in {output_path}")
            
            # Configura il documento
            self.doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=PDF_CONFIG['margin']['right'] * cm,
                leftMargin=PDF_CONFIG['margin']['left'] * cm,
                topMargin=PDF_CONFIG['margin']['top'] * cm,
                bottomMargin=PDF_CONFIG['margin']['bottom'] * cm
            )
            
            print("Debug PDF: SimpleDocTemplate creato")
            
            # Costruisci il contenuto
            print("Debug PDF: Costruzione pagina 1 - Cover...")
            self._build_cover_page_new()
            
            print("Debug PDF: Costruzione pagina 2 - Site Health...")
            self._build_site_health_page()
            
            print("Debug PDF: Costruzione sezione errori...")
            self._build_errors_section()
            
            print("Debug PDF: Costruzione sezione avvertimenti...")
            self._build_warnings_section()
            
            print("Debug PDF: Costruzione sezione avvisi...")
            self._build_notices_section()
            
            print("Debug PDF: Costruzione detailed issues...")
            self._build_detailed_issues_pages()
            
            print("Debug PDF: Build del documento...")
            # Genera il PDF
            self.doc.build(self.story)
            
            print(f"Debug PDF: PDF generato con successo in {output_path}")
            return True
            
        except Exception as e:
            print(f"Debug PDF: Errore generazione PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _build_cover_page_new(self):
        """Costruisce la nuova pagina di copertina"""
        # Logo del sito (se disponibile)
        try:
            # Prova a recuperare il favicon/logo del sito
            favicon_url = f"https://{self.domain}/favicon.ico"
            # Per ora saltiamo il logo, potremo implementarlo in futuro
            pass
        except:
            pass
        
        # Spazio per logo (per ora vuoto)
        self.story.append(Spacer(1, 1*inch))
        
        # Titolo principale
        title = "Site Audit: Full Report"
        title_para = Paragraph(title, self.styles['CustomTitle'])
        self.story.append(title_para)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Nome del dominio
        domain_para = Paragraph(self.domain, self.styles['Highlight'])
        self.story.append(domain_para)
        
        # Spazio fino al fondo
        self.story.append(Spacer(1, 4*inch))
        
        # Data in fondo alla pagina
        date_text = f"Generato in data: {datetime.now().strftime('%d %B, %Y')}"
        date_para = Paragraph(date_text, self.styles['CustomBody'])
        date_para.style.alignment = TA_CENTER
        self.story.append(date_para)
        
        self.story.append(PageBreak())
    
    def _build_site_health_page(self):
        """Costruisce la pagina Site Health"""
        # Header della pagina
        total_pages = self.analysis_results.get("summary", {}).get("total_pages_analyzed", 0)
        header_data = [
            ['Site Audit: Full Report', ''],
            [f'Sottodominio: {self.domain}', ''],
            [f'Ultimo update: {datetime.now().strftime("%d %B %Y")}', ''],
            [f'Pagine sottoposte a crawling: {total_pages}', '']
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(header_table)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Site Health con grafico
        site_health = self.analysis_results.get('site_health', {})
        health_percentage = site_health.get('health_percentage', 0)
        
        # Grafico Site Health
        health_title = Paragraph("Site Health", self.styles['SectionHeader'])
        self.story.append(health_title)
        
        # Creiamo un layout a due colonne
        left_column = []
        right_column = []
        
        # Grafico circolare per Site Health
        health_chart = self._create_health_chart(health_percentage)
        if health_chart:
            left_column.append(health_chart)
        
        # Statistiche a destra
        pages_crawled = site_health.get('total_pages', 0)
        right_column.append(Paragraph(f"<b>Pagine Sottoposte A Crawling</b><br/>{pages_crawled}", self.styles['Highlight']))
        
        # Grafico delle categorie di pagine
        health_data = [
            ['Stato Pagina', 'Numero'],
            ['Sane', str(site_health.get('healthy_pages', 0))],
            ['Interrotte', str(site_health.get('broken_pages', 0))],
            ['Con problemi', str(site_health.get('problematic_pages', 0))],
            ['Reindirizzate', str(site_health.get('redirected_pages', 0))],
            ['Bloccate', str(site_health.get('blocked_pages', 0))]
        ]
        
        health_table = Table(health_data, colWidths=[2*inch, 1*inch])
        health_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        right_column.append(health_table)
        
        # Layout delle colonne
        columns_data = [[left_column, right_column]]
        columns_table = Table(columns_data, colWidths=[3*inch, 3*inch])
        columns_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(columns_table)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Contatori Errori, Avvertimenti, Avvisi
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        errors_count = len(detailed_issues.get('errors', []))
        warnings_count = len(detailed_issues.get('warnings', []))
        notices_count = len(detailed_issues.get('notices', []))
        
        counters_data = [
            ['Errori', 'Avvertimenti', 'Avvisi'],
            [str(errors_count), str(warnings_count), str(notices_count)]
        ]
        
        counters_table = Table(counters_data, colWidths=[2*inch, 2*inch, 2*inch])
        counters_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('BACKGROUND', (0, 1), (0, 1), HexColor(PDF_CONFIG['colors']['error'])),
            ('BACKGROUND', (1, 1), (1, 1), HexColor(PDF_CONFIG['colors']['warning'])),
            ('BACKGROUND', (2, 1), (2, 1), HexColor(PDF_CONFIG['colors']['success'])),
            ('TEXTCOLOR', (0, 1), (-1, 1), white),
        ]))
        self.story.append(counters_table)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Problemi Principali
        self.story.append(Paragraph("Problemi Principali", self.styles['SectionHeader']))
        
        # Calcola le percentuali
        total_issues = errors_count + warnings_count
        
        problems_text = []
        if len(detailed_issues.get('pages_without_title', [])) > 0:
            count = len(detailed_issues['pages_without_title'])
            percentage = round((count / total_issues * 100), 1) if total_issues > 0 else 0
            problems_text.append(f"{count} pagine non hanno title tag - errori {percentage}% tra errori & avvertimenti complessivi")
        
        if len(detailed_issues.get('low_word_count_pages', [])) > 0:
            count = len(detailed_issues['low_word_count_pages'])
            percentage = round((count / total_issues * 100), 1) if total_issues > 0 else 0
            problems_text.append(f"{count} pagine hanno un conteggio parole basso - avvertimenti {percentage}% tra errori & avvertimenti complessivi")
        
        if len(detailed_issues.get('images_without_alt', [])) > 0:
            count = len(detailed_issues['images_without_alt'])
            percentage = round((count / total_issues * 100), 1) if total_issues > 0 else 0
            problems_text.append(f"{count} immagini senza alt text - avvertimenti {percentage}% tra errori & avvertimenti complessivi")
        
        for problem in problems_text[:3]:  # Primi 3 problemi principali
            self.story.append(Paragraph(f"• {problem}", self.styles['CustomBody']))
        
        # Footer con data
        self.story.append(Spacer(1, 2*inch))
        footer_text = f"Generato in data: {datetime.now().strftime('%d %B, %Y')}"
        footer_para = Paragraph(footer_text, self.styles['CustomBody'])
        footer_para.style.alignment = TA_CENTER
        footer_para.style.fontSize = 8
        self.story.append(footer_para)
        
        self.story.append(PageBreak())
    
    def _create_health_chart(self, percentage):
        """Crea un grafico per la Site Health"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(3, 3))
            
            # Colore basato sulla percentuale
            if percentage >= 80:
                color = '#2fa827'
            elif percentage >= 60:
                color = '#ff9500'
            else:
                color = '#d32f2f'
            
            # Grafico a ciambella
            sizes = [percentage, 100-percentage]
            colors = [color, '#f0f0f0']
            
            wedges, texts = ax.pie(sizes, colors=colors, startangle=90, counterclock=False)
            
            # Testo al centro
            ax.text(0, 0, f'{percentage}%', ha='center', va='center', fontsize=24, fontweight='bold')
            ax.text(0, -0.25, 'Site Health', ha='center', va='center', fontsize=10)
            
            # Effetto ciambella
            centre_circle = plt.Circle((0,0), 0.60, fc='white')
            fig.gca().add_artist(centre_circle)
            
            ax.axis('equal')
            plt.tight_layout()
            
            # Salva in memoria
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # Immagine ReportLab
            img = RLImage(img_buffer, width=2.5*inch, height=2.5*inch)
            return img
            
        except Exception as e:
            print(f"Debug PDF: Errore creazione grafico health: {e}")
            return None
    
    def _build_errors_section(self):
        """Costruisce la sezione errori"""
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        errors = detailed_issues.get('errors', [])
        
        if not errors:
            return
        
        self.story.append(Paragraph("🔴 ERRORI", self.styles['SectionHeader']))
        
        # Raggruppa errori per tipo
        error_groups = {}
        for error in errors:
            error_type = error.get('type', 'unknown')
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        for error_type, error_list in error_groups.items():
            count = len(error_list)
            
            if error_type == 'missing_title':
                self.story.append(Paragraph(f"{count} pagine non hanno title tag", self.styles['CustomBody']))
                for error in error_list[:5]:  # Prime 5
                    self.story.append(Paragraph(f"  → {error['url']}", self.styles['Recommendation']))
                if count > 5:
                    self.story.append(Paragraph(f"  ... e altre {count-5} pagine", self.styles['Recommendation']))
            
            elif error_type == 'server_error':
                self.story.append(Paragraph(f"{count} pagine hanno riportato codici di stato 5XX", self.styles['CustomBody']))
                for error in error_list[:5]:
                    self.story.append(Paragraph(f"  → {error['url']} (Status: {error.get('status_code', 'N/A')})", self.styles['Recommendation']))
            
            elif error_type == 'client_error':
                self.story.append(Paragraph(f"{count} pagine hanno riportato codici di stato 4XX", self.styles['CustomBody']))
                for error in error_list[:5]:
                    self.story.append(Paragraph(f"  → {error['url']} (Status: {error.get('status_code', 'N/A')})", self.styles['Recommendation']))
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = f"Generato in data: {datetime.now().strftime('%d %B, %Y')}"
        footer_para = Paragraph(footer_text, self.styles['CustomBody'])
        footer_para.style.alignment = TA_CENTER
        footer_para.style.fontSize = 8
        self.story.append(footer_para)
        
        self.story.append(PageBreak())
    
    def _build_warnings_section(self):
        """Costruisce la sezione avvertimenti"""
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        warnings = detailed_issues.get('warnings', [])
        
        if not warnings:
            return
        
        self.story.append(Paragraph("⚠️ AVVERTIMENTI", self.styles['SectionHeader']))
        
        # Raggruppa warnings per tipo
        warning_groups = {}
        for warning in warnings:
            warning_type = warning.get('type', 'unknown')
            if warning_type not in warning_groups:
                warning_groups[warning_type] = []
            warning_groups[warning_type].append(warning)
        
        for warning_type, warning_list in warning_groups.items():
            count = len(warning_list)
            
            if warning_type == 'missing_meta':
                self.story.append(Paragraph(f"{count} pagine non hanno meta description", self.styles['CustomBody']))
            elif warning_type == 'missing_h1':
                self.story.append(Paragraph(f"{count} pagine non hanno tag H1", self.styles['CustomBody']))
            elif warning_type == 'multiple_h1':
                self.story.append(Paragraph(f"{count} pagine hanno multipli tag H1", self.styles['CustomBody']))
            elif warning_type == 'missing_alt':
                self.story.append(Paragraph(f"{count} immagini senza alt text", self.styles['CustomBody']))
            elif warning_type == 'low_content':
                self.story.append(Paragraph(f"{count} pagine hanno un conteggio parole basso", self.styles['CustomBody']))
            elif warning_type == 'slow_page':
                self.story.append(Paragraph(f"{count} pagine hanno una velocità di caricamento bassa", self.styles['CustomBody']))
            elif warning_type == 'large_page':
                self.story.append(Paragraph(f"{count} pagine hanno dimensioni HTML troppo grandi", self.styles['CustomBody']))
            elif warning_type == 'duplicate_title':
                self.story.append(Paragraph(f"{count} problemi con duplicato di title tag", self.styles['CustomBody']))
            elif warning_type == 'duplicate_meta':
                self.story.append(Paragraph(f"{count} pagine hanno duplicati di meta description", self.styles['CustomBody']))
            
            # Mostra alcuni esempi per ogni tipo
            for warning in warning_list[:3]:
                if 'url' in warning:
                    self.story.append(Paragraph(f"  → {warning['url']}", self.styles['Recommendation']))
            
            if count > 3:
                self.story.append(Paragraph(f"  ... e altre {count-3} pagine", self.styles['Recommendation']))
            
            self.story.append(Spacer(1, 0.1*inch))
        
        # Footer
        self.story.append(Spacer(1, 1*inch))
        footer_text = f"Generato in data: {datetime.now().strftime('%d %B, %Y')}"
        footer_para = Paragraph(footer_text, self.styles['CustomBody'])
        footer_para.style.alignment = TA_CENTER
        footer_para.style.fontSize = 8
        self.story.append(footer_para)
        
        self.story.append(PageBreak())
    
    def _build_notices_section(self):
        """Costruisce la sezione avvisi/info"""
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        notices = detailed_issues.get('notices', [])
        
        if not notices:
            return
        
        self.story.append(Paragraph("ℹ️ AVVISI", self.styles['SectionHeader']))
        
        # Raggruppa notices per tipo
        notice_groups = {}
        for notice in notices:
            notice_type = notice.get('type', 'unknown')
            if notice_type not in notice_groups:
                notice_groups[notice_type] = []
            notice_groups[notice_type].append(notice)
        
        for notice_type, notice_list in notice_groups.items():
            count = len(notice_list)
            
            if notice_type == 'missing_h2':
                self.story.append(Paragraph(f"{count} pagine non hanno tag H2", self.styles['CustomBody']))
            elif notice_type == 'missing_h3':
                self.story.append(Paragraph(f"{count} pagine non hanno tag H3", self.styles['CustomBody']))
            elif notice_type == 'missing_img_title':
                self.story.append(Paragraph(f"{count} immagini senza attributo title", self.styles['CustomBody']))
            elif notice_type == 'missing_canonical':
                self.story.append(Paragraph(f"{count} pagine senza URL canonico", self.styles['CustomBody']))
            elif notice_type == 'missing_lang':
                self.story.append(Paragraph(f"{count} pagine senza attributo lang", self.styles['CustomBody']))
            elif notice_type == 'missing_schema':
                self.story.append(Paragraph(f"{count} pagine senza schema markup", self.styles['CustomBody']))
            
            # Mostra alcuni esempi
            for notice in notice_list[:3]:
                if 'url' in notice:
                    self.story.append(Paragraph(f"  → {notice['url']}", self.styles['Recommendation']))
            
            if count > 3:
                self.story.append(Paragraph(f"  ... e altre {count-3} pagine", self.styles['Recommendation']))
            
            self.story.append(Spacer(1, 0.1*inch))
        
        # Footer
        self.story.append(Spacer(1, 1*inch))
        footer_text = f"Generato in data: {datetime.now().strftime('%d %B, %Y')}"
        footer_para = Paragraph(footer_text, self.styles['CustomBody'])
        footer_para.style.alignment = TA_CENTER
        footer_para.style.fontSize = 8
        self.story.append(footer_para)
        
        self.story.append(PageBreak())
    
    def _build_detailed_issues_pages(self):
        """Costruisce le pagine con tutti i dettagli tecnici"""
        detailed_issues = self.analysis_results.get('detailed_issues', {})
        
        self.story.append(Paragraph("📊 ANALISI DETTAGLIATA", self.styles['SectionHeader']))
        
        # Lista completa di tutti i controlli con conteggi
        checks_data = [
            ['Controllo', 'Risultato'],
            [f"pagine hanno riportato codici di stato 5XX", str(len(detailed_issues.get('status_5xx_pages', [])))],
            [f"pagine hanno riportato codici di stato 4XX", str(len(detailed_issues.get('status_4xx_pages', [])))],
            [f"pagine non hanno title tag", str(len(detailed_issues.get('pages_without_title', [])))],
            [f"problemi con duplicato di title tag", str(len(detailed_issues.get('duplicate_titles', [])))],
            [f"pagine non hanno meta description", str(len(detailed_issues.get('pages_without_meta', [])))],
            [f"pagine hanno duplicati di meta description", str(len(detailed_issues.get('duplicate_meta_descriptions', [])))],
            [f"pagine non hanno tag H1", str(len(detailed_issues.get('missing_h1_pages', [])))],
            [f"pagine non hanno tag H2", str(len(detailed_issues.get('missing_h2_pages', [])))],
            [f"pagine non hanno tag H3", str(len(detailed_issues.get('missing_h3_pages', [])))],
            [f"immagini senza alt text", str(len(detailed_issues.get('images_without_alt', [])))],
            [f"immagini senza attributo title", str(len(detailed_issues.get('images_without_title', [])))],
            [f"pagine con contenuto insufficiente", str(len(detailed_issues.get('low_word_count_pages', [])))],
            [f"pagine con caricamento lento", str(len(detailed_issues.get('slow_pages', [])))],
            [f"pagine con HTML troppo grande", str(len(detailed_issues.get('large_html_pages', [])))],
            [f"pagine senza URL canonico", str(len(detailed_issues.get('pages_without_canonical', [])))],
            [f"pagine senza attributo lang", str(len(detailed_issues.get('pages_without_lang', [])))],
            [f"pagine senza schema markup", str(len(detailed_issues.get('pages_without_schema', [])))],
            [f"pagine senza tag viewport", str(len(detailed_issues.get('pages_without_viewport', [])))],
            [f"link interni interrotti", str(len(detailed_issues.get('broken_links', [])))],
            [f"catene di reindirizzamento", str(len(detailed_issues.get('redirect_chains', [])))],
            [f"pagine con contenuti misti", str(len(detailed_issues.get('mixed_content_pages', [])))],
        ]
        
        # Dividi in più tabelle per evitare overflow
        items_per_page = 12
        for i in range(0, len(checks_data[1:]), items_per_page):
            page_data = [checks_data[0]] + checks_data[1+i:1+i+items_per_page]
            
            checks_table = Table(page_data, colWidths=[4.5*inch, 1*inch])
            checks_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(PDF_CONFIG['colors']['primary'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor(PDF_CONFIG['colors']['light_gray'])]),
            ]))
            
            self.story.append(checks_table)
            self.story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer_text = f"Generato in data: {datetime.now().strftime('%d %B, %Y')}"
            footer_para = Paragraph(footer_text, self.styles['CustomBody'])
            footer_para.style.alignment = TA_CENTER
            footer_para.style.fontSize = 8
            self.story.append(footer_para)
            
            if i + items_per_page < len(checks_data[1:]):
                self.story.append(PageBreak())
    
    def _get_score_color(self, score):
        """Restituisce il colore basato sul punteggio"""
        if score >= 90:
            return PDF_CONFIG['colors']['success']
        elif score >= 70:
            return PDF_CONFIG['colors']['warning']
        else:
            return PDF_CONFIG['colors']['error']
    
    def _get_score_evaluation(self, score):
        """Restituisce la valutazione testuale del punteggio"""
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
            'SSL': self.analysis_results['ssl_analysis']['score']
        }
        
        for category, score in categories.items():
            if score >= 80:
                strengths.append(f"{category} ottimizzato correttamente (punteggio: {score}/100)")
            elif score < 50:
                weaknesses.append(f"{category} necessita miglioramenti urgenti (punteggio: {score}/100)")
        
        return strengths, weaknesses