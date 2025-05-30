"""
Finestra principale dell'applicazione SEO Analyzer
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import webbrowser
from datetime import datetime
import re
from typing import Optional, Dict, List

from config import *
from utils.crawler import WebCrawler
from utils.analyzer import SEOAnalyzer
from utils.pdf_generator import PDFGenerator

# Configura CustomTkinter
ctk.set_appearance_mode(GUI_CONFIG['theme'])
ctk.set_default_color_theme("blue")

class MainWindow:
    """
    Finestra principale dell'applicazione
    """
    
    def __init__(self):
        # Finestra principale
        self.root = ctk.CTk()
        self.root.title(GUI_CONFIG['window_title'])
        self.root.geometry(GUI_CONFIG['window_size'])
        
        # Variabili di stato
        self.crawler = None
        self.analysis_results = None
        self.crawl_data = None
        self.is_crawling = False
        self.is_analyzing = False
        
        # Setup variables prima dell'UI
        self._setup_variables()
        
        # Setup UI
        self._setup_ui()
        
        # Centra la finestra
        self._center_window()
        
    def _setup_variables(self):
        """Configura le variabili tkinter"""
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto per iniziare l'analisi")
        self.progress_var = tk.DoubleVar()
        self.max_pages_var = tk.IntVar(value=CRAWL_CONFIG['max_pages'])
        
    def _setup_ui(self):
        """Configura l'interfaccia utente"""
        # Header
        self._create_header()
        
        # Main content area
        self._create_main_content()
        
        # Status bar
        self._create_status_bar()
        
    def _create_header(self):
        """Crea l'header dell'applicazione"""
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Titolo
        title_label = ctk.CTkLabel(
            header_frame, 
            text="SEO Analyzer Pro",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=GUI_CONFIG['colors']['primary']
        )
        title_label.pack(pady=20)
        
        # Sottotitolo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Analisi SEO completa per il tuo sito web",
            font=ctk.CTkFont(size=14),
            text_color=GUI_CONFIG['colors']['text']
        )
        subtitle_label.pack(pady=(0, 10))
        
    def _create_main_content(self):
        """Crea l'area principale del contenuto"""
        # Container principale
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Pannello sinistro - Input e controlli
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        # Pannello destro - Risultati
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)
        
        self._create_input_panel(left_panel)
        self._create_results_panel(right_panel)
        
    def _create_input_panel(self, parent):
        """Crea il pannello di input"""
        # Titolo sezione
        input_title = ctk.CTkLabel(
            parent,
            text="Configurazione Analisi",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        input_title.pack(pady=(20, 15))
        
        # URL Input
        url_frame = ctk.CTkFrame(parent)
        url_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        url_label = ctk.CTkLabel(url_frame, text="URL del sito:")
        url_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="https://example.com",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.url_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Impostazioni crawling
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        settings_label = ctk.CTkLabel(
            settings_frame, 
            text="Impostazioni Crawling:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Max pagine
        max_pages_frame = ctk.CTkFrame(settings_frame)
        max_pages_frame.pack(fill="x", padx=10, pady=5)
        
        max_pages_label = ctk.CTkLabel(max_pages_frame, text="Massimo pagine:")
        max_pages_label.pack(side="left", padx=(10, 5))
        
        self.max_pages_spinbox = ctk.CTkEntry(
            max_pages_frame,
            textvariable=self.max_pages_var,
            width=80,
            height=30
        )
        self.max_pages_spinbox.pack(side="right", padx=(5, 10))
        
        # Opzioni analisi
        options_frame = ctk.CTkFrame(settings_frame)
        options_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.check_images = ctk.CTkCheckBox(options_frame, text="Analizza immagini")
        self.check_images.pack(anchor="w", padx=10, pady=2)
        self.check_images.select()
        
        self.check_performance = ctk.CTkCheckBox(options_frame, text="Test performance")
        self.check_performance.pack(anchor="w", padx=10, pady=2)
        self.check_performance.select()
        
        self.check_mobile = ctk.CTkCheckBox(options_frame, text="Test mobile-friendly")
        self.check_mobile.pack(anchor="w", padx=10, pady=2)
        self.check_mobile.select()
        
        # Pulsanti azione
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.start_button = ctk.CTkButton(
            buttons_frame,
            text="Avvia Analisi",
            command=self._start_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=GUI_CONFIG['colors']['success'],
            hover_color=GUI_CONFIG['colors']['primary']
        )
        self.start_button.pack(fill="x", padx=10, pady=(10, 5))
        
        self.stop_button = ctk.CTkButton(
            buttons_frame,
            text="Ferma Analisi",
            command=self._stop_analysis,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color=GUI_CONFIG['colors']['error'],
            state="disabled"
        )
        self.stop_button.pack(fill="x", padx=10, pady=5)
        
        # Progress bar con label
        progress_frame = ctk.CTkFrame(buttons_frame)
        progress_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.progress_label.pack(pady=(5, 2))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=(0, 5))
        self.progress_bar.set(0)
        
        # Export buttons
        export_frame = ctk.CTkFrame(parent)
        export_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        export_label = ctk.CTkLabel(
            export_frame,
            text="Esporta Risultati:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        export_label.pack(pady=(10, 5))
        
        self.preview_button = ctk.CTkButton(
            export_frame,
            text="Anteprima Report",
            command=self._preview_report,
            state="disabled",
            height=35
        )
        self.preview_button.pack(fill="x", padx=10, pady=2)
        
        self.export_pdf_button = ctk.CTkButton(
            export_frame,
            text="Esporta PDF",
            command=self._export_pdf,
            state="disabled",
            height=35,
            fg_color=GUI_CONFIG['colors']['warning']
        )
        self.export_pdf_button.pack(fill="x", padx=10, pady=(2, 10))
        
    def _create_results_panel(self, parent):
        """Crea il pannello dei risultati"""
        # Titolo
        results_title = ctk.CTkLabel(
            parent,
            text="Risultati Analisi",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(pady=(20, 15))
        
        # Notebook per organizzare i risultati
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        # Tab Overview
        self.overview_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.overview_frame, text="Panoramica")
        self._create_overview_tab()
        
        # Tab Dettagli
        self.details_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.details_frame, text="Dettagli")
        self._create_details_tab()
        
        # Tab Raccomandazioni
        self.recommendations_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.recommendations_frame, text="Raccomandazioni")
        self._create_recommendations_tab()
        
    def _create_overview_tab(self):
        """Crea la tab panoramica"""
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.overview_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Punteggio generale
        self.score_frame = ctk.CTkFrame(scroll_frame)
        self.score_frame.pack(fill="x", pady=(0, 15))
        
        self.score_label = ctk.CTkLabel(
            self.score_frame,
            text="Punteggio SEO: --",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.score_label.pack(pady=20)
        
        # Metriche principali
        self.metrics_frame = ctk.CTkFrame(scroll_frame)
        self.metrics_frame.pack(fill="x", pady=(0, 15))
        
        metrics_title = ctk.CTkLabel(
            self.metrics_frame,
            text="Metriche Principali",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        metrics_title.pack(pady=(10, 5))
        
        self.metrics_text = ctk.CTkTextbox(
            self.metrics_frame,
            height=200,
            font=ctk.CTkFont(size=11)
        )
        self.metrics_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Problemi principali
        self.issues_frame = ctk.CTkFrame(scroll_frame)
        self.issues_frame.pack(fill="x", pady=(0, 15))
        
        issues_title = ctk.CTkLabel(
            self.issues_frame,
            text="Problemi Principali",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        issues_title.pack(pady=(10, 5))
        
        self.issues_text = ctk.CTkTextbox(
            self.issues_frame,
            height=150,
            font=ctk.CTkFont(size=11)
        )
        self.issues_text.pack(fill="x", padx=10, pady=(0, 10))
        
    def _create_details_tab(self):
        """Crea la tab dettagli"""
        scroll_frame = ctk.CTkScrollableFrame(self.details_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.details_text = ctk.CTkTextbox(
            scroll_frame,
            font=ctk.CTkFont(size=10)
        )
        self.details_text.pack(fill="both", expand=True)
        
    def _create_recommendations_tab(self):
        """Crea la tab raccomandazioni"""
        scroll_frame = ctk.CTkScrollableFrame(self.recommendations_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.recommendations_text = ctk.CTkTextbox(
            scroll_frame,
            font=ctk.CTkFont(size=11)
        )
        self.recommendations_text.pack(fill="both", expand=True)
        
    def _create_status_bar(self):
        """Crea la barra di stato"""
        status_frame = ctk.CTkFrame(self.root, height=30)
        status_frame.pack(fill="x", side="bottom", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Info app
        info_label = ctk.CTkLabel(
            status_frame,
            text="SEO Analyzer Pro v1.0",
            font=ctk.CTkFont(size=10),
            text_color=GUI_CONFIG['colors']['dark_gray']
        )
        info_label.pack(side="right", padx=10, pady=5)
        
    def _center_window(self):
        """Centra la finestra sullo schermo"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def _validate_url(self, url: str) -> bool:
        """Valida l'URL inserito"""
        if not url.strip():
            messagebox.showerror("Errore", "Inserisci un URL valido")
            return False
            
        if not re.match(URL_REGEX, url):
            messagebox.showerror("Errore", MESSAGES['error_invalid_url'])
            return False
            
        return True
        
    def _start_analysis(self):
        """Avvia l'analisi SEO"""
        url = self.url_var.get().strip()
        
        if not self._validate_url(url):
            return
            
        # Aggiorna stato UI
        self.is_crawling = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.export_pdf_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        
        # Aggiorna configurazioni
        CRAWL_CONFIG['max_pages'] = self.max_pages_var.get()
        
        # Avvia thread di analisi
        thread = threading.Thread(target=self._run_analysis, args=(url,))
        thread.daemon = True
        thread.start()
        
    def _run_analysis(self, url: str):
        """Esegue l'analisi in un thread separato"""
        try:
            # Reset progress bar
            self.root.after(0, lambda: self.progress_bar.set(0))
            self.root.after(0, lambda: self.progress_label.configure(text="0%"))
            
            # Fase 1: Crawling
            self._update_status("Inizializzazione crawler...")
            self._update_progress(0.1, "Inizializzazione - 10%")
            
            self.crawler = WebCrawler(url, callback=self._update_crawling_status)
            
            self._update_status(MESSAGES['crawling_started'].format(url))
            self._update_progress(0.2, "Avvio crawling - 20%")
            
            self.crawl_data = self.crawler.crawl()
            
            if not self.crawl_data:
                raise Exception("Nessun dato raccolto durante il crawling")
                
            self._update_status(MESSAGES['crawling_completed'].format(len(self.crawl_data)))
            self._update_progress(0.7, "Crawling completato - 70%")
            
            # Fase 2: Analisi
            if self.is_crawling:  # Controlla se non è stato fermato
                self.is_analyzing = True
                self._update_status(MESSAGES['analysis_started'])
                self._update_progress(0.8, "Analisi SEO in corso - 80%")
                
                domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
                analyzer = SEOAnalyzer(self.crawl_data, domain)
                self.analysis_results = analyzer.analyze_all()
                
                self._update_status(MESSAGES['analysis_completed'])
                self._update_progress(1.0, "Analisi completata - 100%")
                
                # Aggiorna UI con i risultati
                self.root.after(0, self._update_results_ui)
                
        except Exception as e:
            error_msg = f"Errore durante l'analisi: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Errore", error_msg))
            self._update_status(f"Errore: {str(e)}")
            self._update_progress(0, "Errore - 0%")
            
        finally:
            # Reset stato
            self.is_crawling = False
            self.is_analyzing = False
            self.root.after(0, self._reset_ui_state)
    
    def _update_crawling_status(self, message: str):
        """Aggiorna lo status durante il crawling con progress"""
        self.root.after(0, lambda: self.status_var.set(message))
        
        # Estrai il numero di pagine dal messaggio se possibile
        if "Completate" in message and "pagine" in message:
            try:
                # Cerca pattern come "Completate 5 pagine su 50"
                import re
                match = re.search(r'Completate (\d+) pagine su (\d+)', message)
                if match:
                    completed = int(match.group(1))
                    max_pages = int(match.group(2))
                    
                    # Calcola progresso del crawling (20% - 70%)
                    crawl_progress = completed / max_pages
                    total_progress = 0.2 + (crawl_progress * 0.5)  # 20% base + 50% per crawling
                    
                    # Testo con dettagli
                    progress_text = f"Crawling: {completed}/{max_pages} pagine - {int(total_progress * 100)}%"
                    self._update_progress(total_progress, progress_text)
            except:
                pass
    
    def _update_progress(self, value: float, text: str = None):
        """Aggiorna la progress bar con valore e testo"""
        percentage = int(value * 100)
        
        if text:
            display_text = text
        else:
            display_text = f"{percentage}%"
            
        self.root.after(0, lambda: self.progress_bar.set(value))
        self.root.after(0, lambda: self.progress_label.configure(text=display_text))
            
    def _stop_analysis(self):
        """Ferma l'analisi in corso"""
        if self.crawler:
            self.crawler.stop_crawling()
            
        self.is_crawling = False
        self.is_analyzing = False
        self._update_status("Analisi fermata dall'utente")
        self._reset_ui_state()
        
    def _update_status(self, message: str):
        """Aggiorna la barra di stato"""
        self.root.after(0, lambda: self.status_var.set(message))
        
    def _reset_ui_state(self):
        """Resetta lo stato dell'UI"""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        if self.analysis_results:
            self.export_pdf_button.configure(state="normal")
            self.preview_button.configure(state="normal")
            # Progress bar al 100% quando l'analisi è completa
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="Analisi completata - 100%")
            
            # Reset dopo 3 secondi
            self.root.after(3000, lambda: self.progress_bar.set(0))
            self.root.after(3000, lambda: self.progress_label.configure(text="Pronto"))
        else:
            # Reset progress bar se l'analisi è stata fermata
            self.progress_bar.set(0)
            self.progress_label.configure(text="Fermato")
            
    def _update_results_ui(self):
        """Aggiorna l'interfaccia con i risultati dell'analisi"""
        if not self.analysis_results:
            return
            
        # Aggiorna punteggio generale
        overall_score = self.analysis_results['overall_score']
        score_color = self._get_score_color(overall_score)
        
        self.score_label.configure(
            text=f"Punteggio SEO: {overall_score}/100",
            text_color=score_color
        )
        
        # Aggiorna metriche
        self._update_metrics()
        
        # Aggiorna problemi
        self._update_issues()
        
        # Aggiorna dettagli
        self._update_details()
        
        # Aggiorna raccomandazioni
        self._update_recommendations()
        
        self._update_status("Analisi completata con successo!")
        
    def _update_metrics(self):
        """Aggiorna le metriche principali"""
        summary = self.analysis_results['summary']
        
        metrics_text = f"""
📊 PANORAMICA GENERALE

🌐 Dominio: {summary['domain']}
📅 Data Analisi: {summary['analysis_date']}
📄 Pagine Analizzate: {summary['total_pages_analyzed']}
⚠️ Problemi Totali: {summary['total_issues']}
💡 Raccomandazioni: {summary['total_recommendations']}

📈 PUNTEGGI PER CATEGORIA

• Title Tags: {self.analysis_results['title_analysis']['score']}/100
• Meta Descriptions: {self.analysis_results['meta_description_analysis']['score']}/100
• Headings: {self.analysis_results['headings_analysis']['score']}/100
• Immagini: {self.analysis_results['images_analysis']['score']}/100
• Contenuto: {self.analysis_results['content_analysis']['score']}/100
• Performance: {self.analysis_results['performance_analysis']['score']}/100
• SSL: {self.analysis_results['ssl_analysis']['score']}/100
        """
        
        self.metrics_text.delete("1.0", "end")
        self.metrics_text.insert("1.0", metrics_text.strip())
        
    def _update_issues(self):
        """Aggiorna i problemi principali"""
        issues_text = "🚨 PROBLEMI PRINCIPALI\n\n"
        
        # Raccogli i primi problemi da ogni categoria
        all_issues = []
        
        for analysis_key in ['title_analysis', 'meta_description_analysis', 'images_analysis', 'content_analysis']:
            analysis = self.analysis_results.get(analysis_key, {})
            issues = analysis.get('issues', [])
            all_issues.extend(issues[:3])  # Primi 3 per categoria
            
        if all_issues:
            for i, issue in enumerate(all_issues[:10], 1):  # Massimo 10 problemi
                issues_text += f"{i}. {issue}\n\n"
        else:
            issues_text += "🎉 Nessun problema critico identificato!\n\nIl sito presenta un'ottima ottimizzazione SEO."
            
        self.issues_text.delete("1.0", "end")
        self.issues_text.insert("1.0", issues_text)
        
    def _update_details(self):
        """Aggiorna i dettagli completi"""
        details_text = "📋 ANALISI DETTAGLIATA\n\n"
        
        # Title Tags
        title_analysis = self.analysis_results['title_analysis']
        details_text += f"""
🏷️ TITLE TAGS
• Pagine con title: {title_analysis['pages_with_title']}/{title_analysis['total_pages']}
• Pagine senza title: {title_analysis['pages_without_title']}
• Title duplicati: {len(title_analysis['duplicate_titles'])}
• Title troppo corti: {len(title_analysis['too_short_titles'])}
• Title troppo lunghi: {len(title_analysis['too_long_titles'])}
• Punteggio: {title_analysis['score']}/100

"""
        
        # Meta Descriptions
        meta_analysis = self.analysis_results['meta_description_analysis']
        details_text += f"""
📝 META DESCRIPTIONS
• Pagine con meta: {meta_analysis['pages_with_meta']}/{meta_analysis['total_pages']}
• Pagine senza meta: {meta_analysis['pages_without_meta']}
• Meta duplicate: {len(meta_analysis['duplicate_metas'])}
• Meta troppo corte: {len(meta_analysis['too_short_metas'])}
• Meta troppo lunghe: {len(meta_analysis['too_long_metas'])}
• Punteggio: {meta_analysis['score']}/100

"""
        
        # Immagini
        images_analysis = self.analysis_results['images_analysis']
        details_text += f"""
🖼️ IMMAGINI
• Totale immagini: {images_analysis['total_images']}
• Con alt text: {images_analysis['images_with_alt']}
• Senza alt text: {images_analysis['images_without_alt']}
• Alt vuoto: {images_analysis['images_with_empty_alt']}
• Punteggio: {images_analysis['score']}/100

"""
        
        # Performance
        perf_analysis = self.analysis_results['performance_analysis']
        details_text += f"""
⚡ PERFORMANCE
• Pagine veloci: {perf_analysis['fast_pages']}
• Pagine lente: {perf_analysis['slow_pages']}
• Tempo medio: {perf_analysis['average_response_time']:.2f}s
• Dimensione media: {perf_analysis['average_page_size']/1024:.1f} KB
• Punteggio: {perf_analysis['score']}/100
        """
        
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", details_text)
        
    def _update_recommendations(self):
        """Aggiorna le raccomandazioni"""
        recommendations = self.analysis_results['recommendations']
        
        if not recommendations:
            rec_text = "🎉 ECCELLENTE!\n\nNon sono state identificate raccomandazioni specifiche.\nIl sito presenta un'ottima ottimizzazione SEO!"
        else:
            rec_text = "💡 RACCOMANDAZIONI PER IL MIGLIORAMENTO\n\n"
            
            # Raggruppa per priorità
            high_priority = [r for r in recommendations if r['priority'] == 'Alto']
            medium_priority = [r for r in recommendations if r['priority'] == 'Medio']
            low_priority = [r for r in recommendations if r['priority'] == 'Basso']
            
            for priority_group, title, emoji in [
                (high_priority, 'PRIORITÀ ALTA', '🔴'),
                (medium_priority, 'PRIORITÀ MEDIA', '🟡'),
                (low_priority, 'PRIORITÀ BASSA', '🟢')
            ]:
                if priority_group:
                    rec_text += f"{emoji} {title}\n\n"
                    
                    for i, rec in enumerate(priority_group, 1):
                        rec_text += f"{i}. {rec['category']}: {rec['issue']}\n"
                        rec_text += f"   💡 {rec['recommendation']}\n\n"
        
        self.recommendations_text.delete("1.0", "end")
        self.recommendations_text.insert("1.0", rec_text)
        
    def _get_score_color(self, score: int) -> str:
        """Restituisce il colore basato sul punteggio"""
        if score >= 90:
            return GUI_CONFIG['colors']['success']
        elif score >= 70:
            return GUI_CONFIG['colors']['warning']
        else:
            return GUI_CONFIG['colors']['error']
            
    def _preview_report(self):
        """Mostra anteprima del report"""
        if not self.analysis_results:
            messagebox.showwarning("Avviso", "Nessun dato da visualizzare. Esegui prima un'analisi.")
            return
            
        # Crea finestra di anteprima
        preview_window = ctk.CTkToplevel(self.root)
        preview_window.title("Anteprima Report")
        preview_window.geometry("800x600")
        
        # Text widget con scrollbar
        text_frame = ctk.CTkFrame(preview_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        preview_text = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(size=10)
        )
        preview_text.pack(fill="both", expand=True)
        
        # Genera anteprima testuale
        summary = self.analysis_results['summary']
        preview_content = f"""
SEO ANALYZER REPORT
===================

Dominio: {summary['domain']}
Data Analisi: {summary['analysis_date']}
Punteggio Generale: {self.analysis_results['overall_score']}/100

SOMMARIO
--------
• Pagine Analizzate: {summary['total_pages_analyzed']}
• Problemi Totali: {summary['total_issues']}
• Raccomandazioni: {summary['total_recommendations']}

PUNTEGGI DETTAGLIATI
-------------------
• Title Tags: {self.analysis_results['title_analysis']['score']}/100
• Meta Descriptions: {self.analysis_results['meta_description_analysis']['score']}/100
• Headings: {self.analysis_results['headings_analysis']['score']}/100
• Immagini: {self.analysis_results['images_analysis']['score']}/100
• Contenuto: {self.analysis_results['content_analysis']['score']}/100
• Link: {self.analysis_results['links_analysis']['score']}/100
• Performance: {self.analysis_results['performance_analysis']['score']}/100
• Tecnico: {self.analysis_results['technical_analysis']['score']}/100
• SSL: {self.analysis_results['ssl_analysis']['score']}/100

RACCOMANDAZIONI PRINCIPALI
--------------------------
"""
        
        for rec in self.analysis_results['recommendations'][:5]:
            preview_content += f"\n• {rec['category']}: {rec['issue']}\n  Soluzione: {rec['recommendation']}\n"
            
        preview_text.insert("1.0", preview_content)
        
    def _export_pdf(self):
        """Esporta il report in PDF"""
        if not self.analysis_results:
            messagebox.showwarning("Avviso", "Nessun dato da esportare. Esegui prima un'analisi.")
            return
            
        # Scegli dove salvare
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Salva Report PDF",
            initialfile=f"seo_report_{self.analysis_results['summary']['domain']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if not filename:
            return
            
        try:
            self._update_status("Generazione PDF in corso...")
            print(f"Debug: Generazione PDF per {filename}")
            
            # Genera PDF in un thread separato per non bloccare l'UI
            thread = threading.Thread(target=self._generate_pdf_thread, args=(filename,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            error_msg = MESSAGES['error_pdf_generation'].format(str(e))
            print(f"Debug: Errore PDF: {e}")
            messagebox.showerror("Errore", error_msg)
            self._update_status(f"Errore: {str(e)}")
    
    def _generate_pdf_thread(self, filename):
        """Genera il PDF in un thread separato"""
        try:
            print(f"Debug: Avvio generazione PDF in thread...")
            
            # Progress per PDF
            self.root.after(0, lambda: self.progress_bar.set(0.1))
            self.root.after(0, lambda: self.progress_label.configure(text="Generazione PDF - 10%"))
            
            # Genera PDF
            domain = self.analysis_results['summary']['domain']
            pdf_generator = PDFGenerator(self.analysis_results, domain)
            
            self.root.after(0, lambda: self.progress_bar.set(0.5))
            self.root.after(0, lambda: self.progress_label.configure(text="Creazione contenuto - 50%"))
            print(f"Debug: PDFGenerator creato, generazione in corso...")
            
            success = pdf_generator.generate_pdf(filename)
            
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self.root.after(0, lambda: self.progress_label.configure(text="PDF completato - 100%"))
            print(f"Debug: Generazione completata, successo: {success}")
            
            if success:
                self.root.after(0, lambda: self._update_status(MESSAGES['report_generated'].format(filename)))
                
                # Chiedi se aprire il file
                self.root.after(0, lambda: self._ask_open_file(filename))
            else:
                self.root.after(0, lambda: messagebox.showerror("Errore", "Errore durante la generazione del PDF"))
                
        except Exception as e:
            print(f"Debug: Eccezione nel thread PDF: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Errore", f"Errore nella generazione PDF: {str(e)}"))
            self.root.after(0, lambda: self._update_status(f"Errore: {str(e)}"))
        finally:
            # Reset progress dopo qualche secondo
            self.root.after(3000, lambda: self.progress_bar.set(0))
            self.root.after(3000, lambda: self.progress_label.configure(text="Pronto"))
    
    def _ask_open_file(self, filename):
        """Chiede se aprire il file PDF generato"""
        if messagebox.askyesno("Successo", f"Report PDF salvato con successo!\n\n{filename}\n\nVuoi aprire il file?"):
            self._open_file(filename)
            
    def _open_file(self, filepath: str):
        """Apre un file con l'applicazione predefinita"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            elif os.name == 'posix':  # macOS e Linux
                if os.uname().sysname == 'Darwin':  # macOS
                    os.system(f'open "{filepath}"')
                else:  # Linux
                    os.system(f'xdg-open "{filepath}"')
        except Exception as e:
            messagebox.showwarning("Avviso", f"Impossibile aprire il file: {str(e)}")
            
    def run(self):
        """Avvia l'applicazione"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
        
    def _on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        if self.is_crawling or self.is_analyzing:
            if messagebox.askokcancel("Chiudi", "Un'analisi è in corso. Vuoi davvero uscire?"):
                if self.crawler:
                    self.crawler.stop_crawling()
                self.root.destroy()
        else:
            self.root.destroy()


class SettingsWindow:
    """
    Finestra delle impostazioni avanzate
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.window = ctk.CTkToplevel(parent.root)
        self.window.title("Impostazioni Avanzate")
        self.window.geometry("600x500")
        self.window.transient(parent.root)
        self.window.grab_set()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura l'interfaccia delle impostazioni"""
        # Titolo
        title = ctk.CTkLabel(
            self.window,
            text="Impostazioni Avanzate",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Notebook per le categorie
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tab Crawling
        crawling_frame = ctk.CTkFrame(notebook)
        notebook.add(crawling_frame, text="Crawling")
        self._create_crawling_settings(crawling_frame)
        
        # Tab SEO
        seo_frame = ctk.CTkFrame(notebook)
        notebook.add(seo_frame, text="SEO")
        self._create_seo_settings(seo_frame)
        
        # Tab PDF
        pdf_frame = ctk.CTkFrame(notebook)
        notebook.add(pdf_frame, text="PDF")
        self._create_pdf_settings(pdf_frame)
        
        # Pulsanti
        buttons_frame = ctk.CTkFrame(self.window)
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Salva",
            command=self._save_settings,
            fg_color=GUI_CONFIG['colors']['success']
        )
        save_button.pack(side="right", padx=(10, 0))
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Annulla",
            command=self.window.destroy,
            fg_color=GUI_CONFIG['colors']['error']
        )
        cancel_button.pack(side="right")
        
    def _create_crawling_settings(self, parent):
        """Crea le impostazioni di crawling"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Max pagine
        max_pages_frame = ctk.CTkFrame(scroll_frame)
        max_pages_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(max_pages_frame, text="Massimo pagine:").pack(side="left", padx=10)
        self.max_pages_var = tk.IntVar(value=CRAWL_CONFIG['max_pages'])
        ctk.CTkEntry(max_pages_frame, textvariable=self.max_pages_var, width=100).pack(side="right", padx=10)
        
        # Timeout
        timeout_frame = ctk.CTkFrame(scroll_frame)
        timeout_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(timeout_frame, text="Timeout (secondi):").pack(side="left", padx=10)
        self.timeout_var = tk.IntVar(value=CRAWL_CONFIG['timeout'])
        ctk.CTkEntry(timeout_frame, textvariable=self.timeout_var, width=100).pack(side="right", padx=10)
        
        # Delay
        delay_frame = ctk.CTkFrame(scroll_frame)
        delay_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(delay_frame, text="Delay tra richieste (secondi):").pack(side="left", padx=10)
        self.delay_var = tk.DoubleVar(value=CRAWL_CONFIG['delay'])
        ctk.CTkEntry(delay_frame, textvariable=self.delay_var, width=100).pack(side="right", padx=10)
        
        # Opzioni
        self.follow_external_var = tk.BooleanVar(value=CRAWL_CONFIG['follow_external'])
        ctk.CTkCheckBox(scroll_frame, text="Segui link esterni", variable=self.follow_external_var).pack(anchor="w", padx=10, pady=5)
        
        self.respect_robots_var = tk.BooleanVar(value=CRAWL_CONFIG['respect_robots'])
        ctk.CTkCheckBox(scroll_frame, text="Rispetta robots.txt", variable=self.respect_robots_var).pack(anchor="w", padx=10, pady=5)
        
    def _create_seo_settings(self, parent):
        """Crea le impostazioni SEO"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title length
        title_frame = ctk.CTkFrame(scroll_frame)
        title_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(title_frame, text="Lunghezza title min:").pack(side="left", padx=5)
        self.title_min_var = tk.IntVar(value=SEO_CONFIG['title_min_length'])
        ctk.CTkEntry(title_frame, textvariable=self.title_min_var, width=60).pack(side="left", padx=5)
        
        ctk.CTkLabel(title_frame, text="max:").pack(side="left", padx=5)
        self.title_max_var = tk.IntVar(value=SEO_CONFIG['title_max_length'])
        ctk.CTkEntry(title_frame, textvariable=self.title_max_var, width=60).pack(side="left", padx=5)
        
        # Meta description length
        meta_frame = ctk.CTkFrame(scroll_frame)
        meta_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(meta_frame, text="Lunghezza meta min:").pack(side="left", padx=5)
        self.meta_min_var = tk.IntVar(value=SEO_CONFIG['meta_description_min_length'])
        ctk.CTkEntry(meta_frame, textvariable=self.meta_min_var, width=60).pack(side="left", padx=5)
        
        ctk.CTkLabel(meta_frame, text="max:").pack(side="left", padx=5)
        self.meta_max_var = tk.IntVar(value=SEO_CONFIG['meta_description_max_length'])
        ctk.CTkEntry(meta_frame, textvariable=self.meta_max_var, width=60).pack(side="left", padx=5)
        
        # Min word count
        words_frame = ctk.CTkFrame(scroll_frame)
        words_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(words_frame, text="Minimo parole per pagina:").pack(side="left", padx=10)
        self.min_words_var = tk.IntVar(value=SEO_CONFIG['min_word_count'])
        ctk.CTkEntry(words_frame, textvariable=self.min_words_var, width=100).pack(side="right", padx=10)
        
    def _create_pdf_settings(self, parent):
        """Crea le impostazioni PDF"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Font size
        font_frame = ctk.CTkFrame(scroll_frame)
        font_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(font_frame, text="Dimensione font titolo:").pack(side="left", padx=10)
        self.font_title_var = tk.IntVar(value=PDF_CONFIG['font_sizes']['title'])
        ctk.CTkEntry(font_frame, textvariable=self.font_title_var, width=60).pack(side="right", padx=10)
        
        # Page margins
        margin_frame = ctk.CTkFrame(scroll_frame)
        margin_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(margin_frame, text="Margini pagina (cm):").pack(side="left", padx=10)
        self.margin_var = tk.DoubleVar(value=PDF_CONFIG['margin']['top'])
        ctk.CTkEntry(margin_frame, textvariable=self.margin_var, width=60).pack(side="right", padx=10)
        
    def _save_settings(self):
        """Salva le impostazioni"""
        try:
            # Aggiorna configurazioni globali
            CRAWL_CONFIG['max_pages'] = self.max_pages_var.get()
            CRAWL_CONFIG['timeout'] = self.timeout_var.get()
            CRAWL_CONFIG['delay'] = self.delay_var.get()
            CRAWL_CONFIG['follow_external'] = self.follow_external_var.get()
            CRAWL_CONFIG['respect_robots'] = self.respect_robots_var.get()
            
            SEO_CONFIG['title_min_length'] = self.title_min_var.get()
            SEO_CONFIG['title_max_length'] = self.title_max_var.get()
            SEO_CONFIG['meta_description_min_length'] = self.meta_min_var.get()
            SEO_CONFIG['meta_description_max_length'] = self.meta_max_var.get()
            SEO_CONFIG['min_word_count'] = self.min_words_var.get()
            
            PDF_CONFIG['font_sizes']['title'] = self.font_title_var.get()
            PDF_CONFIG['margin']['top'] = self.margin_var.get()
            PDF_CONFIG['margin']['bottom'] = self.margin_var.get()
            PDF_CONFIG['margin']['left'] = self.margin_var.get()
            PDF_CONFIG['margin']['right'] = self.margin_var.get()
            
            messagebox.showinfo("Successo", "Impostazioni salvate con successo!")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvare le impostazioni: {str(e)}")


def main():
    """Funzione principale per avviare l'applicazione"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Errore nell'avvio dell'applicazione: {e}")
        messagebox.showerror("Errore Critico", f"Impossibile avviare l'applicazione:\n{str(e)}")


if __name__ == "__main__":
    main()