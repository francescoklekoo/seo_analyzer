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
import copy # Import aggiunto per deepcopy

from config import *
from utils.crawler import WebCrawler
from utils.analyzer import SEOAnalyzer
from utils.pdf_generator import PDFGenerator

# Configura CustomTkinter
ctk.set_appearance_mode(GUI_CONFIG['theme']) # 'System', 'Dark', 'Light'
ctk.set_default_color_theme("blue") # "blue", "dark-blue", "green"

class MainWindow:
    """
    Finestra principale dell'applicazione
    """
    
    def __init__(self):
        # Finestra principale
        self.root = ctk.CTk()
        self.root.title(GUI_CONFIG['window_title'])
        self.root.geometry(GUI_CONFIG['window_size'])
        self.root.minsize(900, 700) # Imposta una dimensione minima per la finestra
        
        # Variabili di stato
        self.crawler = None
        self.analysis_results = None
        self.crawl_data = None
        self.is_crawling = False
        self.is_analyzing = False
        self.adjusted_overall_score = 0 # Aggiunto per memorizzare il punteggio aggiustato
        
        # Setup variables prima dell'UI
        self._setup_variables()
        
        # Setup UI
        self._setup_ui()
        
        # Centra la finestra all'avvio
        self._center_window()
        
    def _setup_variables(self):
        """Configura le variabili tkinter"""
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto per iniziare l'analisi")
        self.progress_var = tk.DoubleVar()
        self.max_pages_var = tk.IntVar(value=CRAWL_CONFIG['max_pages'])
        
    def _setup_ui(self):
        """Configura l'interfaccia utente"""
        # Configura la griglia della finestra principale
        self.root.grid_rowconfigure(1, weight=1) # Permette alla riga del contenuto principale di espandersi
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header
        self._create_header()
        
        # Main content area
        self._create_main_content()
        
        # Status bar
        self._create_status_bar()
        
    def _create_header(self):
        """Crea l'header dell'applicazione con un design più moderno"""
        header_frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color=GUI_CONFIG['colors']['primary_dark'])
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
        
        # Titolo
        title_label = ctk.CTkLabel(
            header_frame, 
            text="SEO Analyzer Pro",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=GUI_CONFIG['colors']['white'] # Titolo bianco su sfondo scuro
        )
        title_label.pack(pady=(20, 5))
        
        # Sottotitolo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Analisi SEO completa e report dettagliati per il tuo sito web",
            font=ctk.CTkFont(size=15),
            text_color=GUI_CONFIG['colors']['light_gray'] # Sottotitolo grigio chiaro
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Pulsante Impostazioni nell'header
        settings_button = ctk.CTkButton(
            header_frame,
            text="Impostazioni",
            command=lambda: SettingsWindow(self), # Apre la finestra delle impostazioni
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=GUI_CONFIG['colors']['primary'],
            text_color=GUI_CONFIG['colors']['white'],
            border_width=2,
            border_color=GUI_CONFIG['colors']['white']
        )
        settings_button.place(relx=0.95, rely=0.5, anchor="e") # Posiziona il pulsante a destra
        
    def _create_main_content(self):
        """Crea l'area principale del contenuto con un layout a due colonne"""
        main_container = ctk.CTkFrame(self.root, corner_radius=10)
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Configura la griglia del main_container
        main_container.grid_columnconfigure(0, weight=1) # Colonna sinistra
        main_container.grid_columnconfigure(1, weight=2) # Colonna destra, più larga
        main_container.grid_rowconfigure(0, weight=1)
        
        # Pannello sinistro - Input e controlli
        left_panel = ctk.CTkFrame(main_container, corner_radius=10)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Pannello destro - Risultati
        right_panel = ctk.CTkFrame(main_container, corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self._create_input_panel(left_panel)
        self._create_results_panel(right_panel)
        
    def _create_input_panel(self, parent):
        """Crea il pannello di input con un design migliorato"""
        parent.grid_columnconfigure(0, weight=1) # Permette agli elementi di espandersi orizzontalmente
        
        # Titolo sezione
        input_title = ctk.CTkLabel(
            parent,
            text="Configurazione Analisi",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=GUI_CONFIG['colors']['primary']
        )
        input_title.pack(pady=(20, 15))
        
        # URL Input
        url_frame = ctk.CTkFrame(parent, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        url_label = ctk.CTkLabel(url_frame, text="URL del sito:")
        url_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="https://example.com",
            font=ctk.CTkFont(size=12),
            height=35,
            corner_radius=8,
            border_color=GUI_CONFIG['colors']['primary'],
            border_width=2
        )
        self.url_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Impostazioni crawling
        settings_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        settings_label = ctk.CTkLabel(
            settings_frame, 
            text="Impostazioni Crawling:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=GUI_CONFIG['colors']['text']
        )
        settings_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Max pagine
        max_pages_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        max_pages_frame.pack(fill="x", padx=10, pady=5)
        
        max_pages_label = ctk.CTkLabel(max_pages_frame, text="Massimo pagine:")
        max_pages_label.pack(side="left", padx=(10, 5))
        
        self.max_pages_spinbox = ctk.CTkEntry(
            max_pages_frame,
            textvariable=self.max_pages_var,
            width=80,
            height=30,
            corner_radius=8
        )
        self.max_pages_spinbox.pack(side="right", padx=(5, 10))
        
        # Opzioni analisi
        options_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.check_images = ctk.CTkCheckBox(options_frame, text="Analizza immagini", corner_radius=5)
        self.check_images.pack(anchor="w", padx=10, pady=2)
        self.check_images.select()
        
        self.check_performance = ctk.CTkCheckBox(options_frame, text="Test performance", corner_radius=5)
        self.check_performance.pack(anchor="w", padx=10, pady=2)
        self.check_performance.select()
        
        self.check_mobile = ctk.CTkCheckBox(options_frame, text="Test mobile-friendly", corner_radius=5)
        self.check_mobile.pack(anchor="w", padx=10, pady=2)
        self.check_mobile.select()
        
        # Pulsanti azione
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.start_button = ctk.CTkButton(
            buttons_frame,
            text="Avvia Analisi",
            command=self._start_analysis,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color=GUI_CONFIG['colors']['success'],
            hover_color=GUI_CONFIG['colors']['success_dark']
        )
        self.start_button.pack(fill="x", padx=10, pady=(10, 5))
        
        self.stop_button = ctk.CTkButton(
            buttons_frame,
            text="Ferma Analisi",
            command=self._stop_analysis,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=10,
            fg_color=GUI_CONFIG['colors']['error'],
            hover_color=GUI_CONFIG['colors']['error_dark'],
            state="disabled"
        )
        self.stop_button.pack(fill="x", padx=10, pady=5)
        
        # Progress bar con label
        progress_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.progress_label.pack(pady=(5, 2))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=10, corner_radius=5)
        self.progress_bar.pack(fill="x", padx=5, pady=(0, 5))
        self.progress_bar.set(0)
        
        # Export buttons
        export_frame = ctk.CTkFrame(parent, fg_color="transparent")
        export_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        export_label = ctk.CTkLabel(
            export_frame,
            text="Esporta Risultati:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=GUI_CONFIG['colors']['text']
        )
        export_label.pack(pady=(10, 5))
        
        self.preview_button = ctk.CTkButton(
            export_frame,
            text="Anteprima Report",
            command=self._preview_report,
            state="disabled",
            height=35,
            corner_radius=10,
            fg_color=GUI_CONFIG['colors']['secondary'],
            hover_color=GUI_CONFIG['colors']['secondary_dark']
        )
        self.preview_button.pack(fill="x", padx=10, pady=2)
        
        self.export_pdf_button = ctk.CTkButton(
            export_frame,
            text="Esporta PDF",
            command=self._export_pdf,
            state="disabled",
            height=35,
            corner_radius=10,
            fg_color=GUI_CONFIG['colors']['warning'],
            hover_color=GUI_CONFIG['colors']['warning_dark']
        )
        self.export_pdf_button.pack(fill="x", padx=10, pady=(2, 10))
        
    def _create_results_panel(self, parent):
        """Crea il pannello dei risultati con un design migliorato"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Titolo
        results_title = ctk.CTkLabel(
            parent,
            text="Risultati Analisi",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=GUI_CONFIG['colors']['primary']
        )
        results_title.pack(pady=(20, 15))
        
        # Notebook per organizzare i risultati (stilizzato con CustomTkinter)
        # CustomTkinter non ha un widget Notebook nativo, ma possiamo usare ttk.Notebook
        # e stilizzarlo con ttk.Style per farlo assomigliare a CTk.
        style = ttk.Style()
        style.theme_use("default") # Usa il tema di default per ttk
        
        # Configura lo stile delle tab per CustomTkinter
        # Questi colori devono corrispondere al tema di CTk
        bg_color = self.root._apply_appearance_mode(self.root.cget("fg_color"))
        # Correzione: Usa direttamente il colore del testo dalla configurazione
        text_color = GUI_CONFIG['colors']['text'] 
        selected_tab_color = GUI_CONFIG['colors']['primary']
        
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background=bg_color, 
                        foreground=text_color,
                        lightcolor=bg_color,
                        darkcolor=bg_color,
                        bordercolor=bg_color,
                        padding=[10, 5])
        style.map("TNotebook.Tab", 
                  background=[("selected", selected_tab_color)],
                  foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        # Tab Overview
        self.overview_frame = ctk.CTkFrame(self.notebook, corner_radius=8)
        self.notebook.add(self.overview_frame, text="Panoramica")
        self._create_overview_tab()
        
        # Tab Dettagli
        self.details_frame = ctk.CTkFrame(self.notebook, corner_radius=8)
        self.notebook.add(self.details_frame, text="Dettagli")
        self._create_details_tab()
        
        # Tab Raccomandazioni
        self.recommendations_frame = ctk.CTkFrame(self.notebook, corner_radius=8)
        self.notebook.add(self.recommendations_frame, text="Raccomandazioni")
        self._create_recommendations_tab()
        
    def _create_overview_tab(self):
        """Crea la tab panoramica con un layout più pulito"""
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.overview_frame, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Punteggio generale
        self.score_frame = ctk.CTkFrame(scroll_frame, corner_radius=10, fg_color=GUI_CONFIG['colors']['primary_light'])
        self.score_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        self.score_label = ctk.CTkLabel(
            self.score_frame,
            text="Punteggio SEO: --",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=GUI_CONFIG['colors']['white']
        )
        self.score_label.pack(pady=20)
        
        # Metriche principali
        self.metrics_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        self.metrics_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        metrics_title = ctk.CTkLabel(
            self.metrics_frame,
            text="Metriche Principali",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=GUI_CONFIG['colors']['primary']
        )
        metrics_title.pack(pady=(10, 5))
        
        self.metrics_text = ctk.CTkTextbox(
            self.metrics_frame,
            height=200,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            border_width=1,
            border_color=GUI_CONFIG['colors']['border']
        )
        self.metrics_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Problemi principali
        self.issues_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        self.issues_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        issues_title = ctk.CTkLabel(
            self.issues_frame,
            text="Problemi Principali",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=GUI_CONFIG['colors']['primary']
        )
        issues_title.pack(pady=(10, 5))
        
        self.issues_text = ctk.CTkTextbox(
            self.issues_frame,
            height=150,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            border_width=1,
            border_color=GUI_CONFIG['colors']['border']
        )
        self.issues_text.pack(fill="x", padx=10, pady=(0, 10))
        
    def _create_details_tab(self):
        """Crea la tab dettagli"""
        scroll_frame = ctk.CTkScrollableFrame(self.details_frame, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.details_text = ctk.CTkTextbox(
            scroll_frame,
            font=ctk.CTkFont(size=10),
            corner_radius=8,
            border_width=1,
            border_color=GUI_CONFIG['colors']['border']
        )
        self.details_text.pack(fill="both", expand=True)
        
    def _create_recommendations_tab(self):
        """Crea la tab raccomandazioni"""
        scroll_frame = ctk.CTkScrollableFrame(self.recommendations_frame, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.recommendations_text = ctk.CTkTextbox(
            scroll_frame,
            font=ctk.CTkFont(size=11),
            corner_radius=8,
            border_width=1,
            border_color=GUI_CONFIG['colors']['border']
        )
        self.recommendations_text.pack(fill="both", expand=True)
        
    def _create_status_bar(self):
        """Crea la barra di stato più sottile e discreta"""
        status_frame = ctk.CTkFrame(self.root, height=25, corner_radius=0, fg_color=GUI_CONFIG['colors']['primary_dark'])
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew") # Occupa tutta la larghezza
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=10),
            text_color=GUI_CONFIG['colors']['white']
        )
        self.status_label.pack(side="left", padx=10, pady=2)
        
        # Info app
        info_label = ctk.CTkLabel(
            status_frame,
            text="SEO Analyzer Pro v1.0",
            font=ctk.CTkFont(size=10),
            text_color=GUI_CONFIG['colors']['light_gray']
        )
        info_label.pack(side="right", padx=10, pady=2)
        
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
        self.start_button.configure(state="disabled", fg_color=GUI_CONFIG['colors']['disabled'])
        self.stop_button.configure(state="normal", fg_color=GUI_CONFIG['colors']['error'])
        self.export_pdf_button.configure(state="disabled", fg_color=GUI_CONFIG['colors']['disabled'])
        self.preview_button.configure(state="disabled", fg_color=GUI_CONFIG['colors']['disabled']) 
        
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
        self.start_button.configure(state="normal", fg_color=GUI_CONFIG['colors']['success'])
        self.stop_button.configure(state="disabled", fg_color=GUI_CONFIG['colors']['error'])
        
        if self.analysis_results:
            self.export_pdf_button.configure(state="normal", fg_color=GUI_CONFIG['colors']['warning'])
            self.preview_button.configure(state="normal", fg_color=GUI_CONFIG['colors']['secondary'])
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
            # Se analysis_results è None, imposta il punteggio a 0
            self.adjusted_overall_score = 0
            self.score_label.configure(text=f"Punteggio SEO: 0/100", text_color=GUI_CONFIG['colors']['error'])
            self.metrics_text.delete("1.0", "end")
            self.metrics_text.insert("1.0", "Nessun risultato di analisi disponibile.")
            self.issues_text.delete("1.0", "end")
            self.issues_text.insert("1.0", "Nessun problema identificato.")
            self.details_text.delete("1.0", "end")
            self.details_text.insert("1.0", "Nessun dettaglio disponibile.")
            self.recommendations_text.delete("1.0", "end")
            self.recommendations_text.insert("1.0", "Nessuna raccomandazione disponibile.")
            return
            
        # Estrai i conteggi di errori, avvertimenti e avvisi dai detailed_issues
        detailed_issues = self.analysis_results.get('detailed_issues', {})

        total_errors = sum(len(v) for k, v in detailed_issues.items() if 'error' in k.lower()) # Conta tutti gli errori
        total_warnings = sum(len(v) for k, v in detailed_issues.items() if 'warning' in k.lower()) # Conta tutti gli avvertimenti
        total_notices = sum(len(v) for k, v in detailed_issues.items() if 'notice' in k.lower()) # Conta tutti gli avvisi

        # Inizializza il punteggio aggiustato con il punteggio complessivo originale
        adjusted_overall_score = self.analysis_results.get('overall_score', 0)

        # Penalità per tipo di problema (valori arbitrari, possono essere tarati in config.py se necessario)
        PENALTY_ERROR_FACTOR = 5 
        PENALTY_WARNING_FACTOR = 2 
        PENALTY_NOTICE_FACTOR = 0.5 

        # Applica la penalità
        adjusted_overall_score -= (total_errors * PENALTY_ERROR_FACTOR)
        adjusted_overall_score -= (total_warnings * PENALTY_WARNING_FACTOR)
        adjusted_overall_score -= (total_notices * PENALTY_NOTICE_FACTOR)

        # Assicurati che il punteggio rimanga tra 0 e 100
        self.adjusted_overall_score = max(0, min(100, adjusted_overall_score)) # Store the adjusted score
            
        # Aggiorna punteggio generale
        score_color = self._get_score_color(self.adjusted_overall_score)
        
        self.score_label.configure(
            text=f"Punteggio SEO: {int(self.adjusted_overall_score)}/100",
            text_color=score_color
        )
        
        # Aggiorna metriche
        self._update_metrics(self.adjusted_overall_score) # Pass the adjusted score
        
        # Aggiorna problemi
        self._update_issues()
        
        # Aggiorna dettagli
        self._update_details()
        
        # Aggiorna raccomandazioni
        self._update_recommendations()
        
        self._update_status("Analisi completata con successo!")
        
    def _update_metrics(self, overall_score_for_display: float):
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

• Punteggio Complessivo: {int(overall_score_for_display)}/100
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
        
        # Aggiungi problemi specifici da detailed_issues
        detailed_issues = self.analysis_results.get('detailed_issues', {})

        # Funzione helper per formattare gli URL in una stringa leggibile
        def format_urls_for_display(urls: list, max_display=3):
            if not urls:
                return ""
            displayed_urls = [f"→ {url}" for url in urls[:max_display]]
            if len(urls) > max_display:
                displayed_urls.append(f"... e altre {len(urls) - max_display} pagine")
            return "\n".join(displayed_urls)

        # Errori
        if detailed_issues.get('errors'):
            issues_text += "🔴 ERRORI:\n"
            for issue in detailed_issues['errors']:
                issues_text += f"- {issue.get('type', 'Sconosciuto')}\n"
                if issue.get('urls'):
                    issues_text += f"{format_urls_for_display(issue['urls'])}\n\n"
                else:
                    issues_text += "\n" # Spazio anche se non ci sono URL

        # Avvertimenti
        if detailed_issues.get('warnings'):
            issues_text += "⚠️ AVVERTIMENTI:\n"
            for issue in detailed_issues['warnings']:
                issues_text += f"- {issue.get('type', 'Sconosciuto')}\n"
                if issue.get('urls'):
                    issues_text += f"{format_urls_for_display(issue['urls'])}\n\n"
                else:
                    issues_text += "\n"

        # Avvisi
        if detailed_issues.get('notices'):
            issues_text += "ℹ️ AVVISI:\n"
            for issue in detailed_issues['notices']:
                issues_text += f"- {issue.get('type', 'Sconosciuto')}\n"
                if issue.get('urls'):
                    issues_text += f"{format_urls_for_display(issue['urls'])}\n\n"
                else:
                    issues_text += "\n"

        if not detailed_issues.get('errors') and not detailed_issues.get('warnings') and not detailed_issues.get('notices'):
            issues_text += "🎉 Nessun problema critico, avvertimento o avviso identificato!\n\nIl sito presenta un'ottima ottimizzazione SEO."
            
        self.issues_text.delete("1.0", "end")
        self.issues_text.insert("1.0", issues_text)
        
    def _update_details(self):
        """Aggiorna i dettagli completi"""
        details_text = "📋 ANALISI DETTAGLIATA\n\n"
        
        # Funzione helper per creare tabelle di URL per i dettagli
        def create_url_table_string(title: str, issue_list: List[Dict]):
            if not issue_list:
                return ""
            
            table_content = f"\n--- {title} ({len(issue_list)}) ---\n"
            table_content += "{:<80} {:<20}\n".format("URL", "Tipo Problema")
            table_content += "-" * 100 + "\n"
            
            for issue in issue_list:
                url = issue.get('url', 'N/A')
                issue_type = issue.get('type', 'Sconosciuto')
                table_content += "{:<80} {:<20}\n".format(url[:77] + '...' if len(url) > 80 else url, issue_type)
            table_content += "\n"
            return table_content

        detailed_issues = self.analysis_results.get('detailed_issues', {})

        # Title Tags
        title_analysis = self.analysis_results['title_analysis']
        details_text += f"""
🏷️ TITLE TAGS
• Pagine con Title: {title_analysis['pages_with_title']}/{title_analysis['total_pages']}
• Pagine senza Title: {len(detailed_issues.get('pages_without_title', []))}
• Title duplicati: {len(detailed_issues.get('duplicate_titles', []))}
• Title troppo corti: {len(title_analysis['too_short_titles'])}
• Title troppo lunghi: {len(title_analysis['too_long_titles'])}
• Punteggio: {title_analysis['score']}/100
"""
        details_text += create_url_table_string("Pagine senza Title", detailed_issues.get('pages_without_title', []))
        details_text += create_url_table_string("Title Duplicati", detailed_issues.get('duplicate_titles', []))
        details_text += create_url_table_string("Title Troppo Corti", title_analysis['too_short_titles'])
        details_text += create_url_table_string("Title Troppo Lunghi", title_analysis['too_long_titles'])
        details_text += "\n"
        
        # Meta Descriptions
        meta_analysis = self.analysis_results['meta_description_analysis']
        details_text += f"""
📝 META DESCRIPTIONS
• Pagine con Meta Description: {meta_analysis['pages_with_meta']}/{meta_analysis['total_pages']}
• Pagine senza Meta Description: {len(detailed_issues.get('pages_without_meta', []))}
• Meta duplicate: {len(detailed_issues.get('duplicate_meta_descriptions', []))}
• Meta troppo corte: {len(meta_analysis['too_short_metas'])}
• Meta troppo lunghe: {len(meta_analysis['too_long_metas'])}
• Punteggio: {meta_analysis['score']}/100
"""
        details_text += create_url_table_string("Pagine senza Meta Description", detailed_issues.get('pages_without_meta', []))
        details_text += create_url_table_string("Meta Description Duplicate", detailed_issues.get('duplicate_meta_descriptions', []))
        details_text += create_url_table_string("Meta Description Troppo Corte", meta_analysis['too_short_metas'])
        details_text += create_url_table_string("Meta Description Troppo Lunghe", meta_analysis['too_long_metas'])
        details_text += "\n"
        
        # Headings (H1, H2, H3)
        headings_analysis = self.analysis_results.get('headings_analysis', {})
        details_text += f"""
 headingS (H1, H2, H3)
• Pagine senza H1: {len(detailed_issues.get('missing_h1_pages', []))}
• Pagine con H1 multipli: {len(detailed_issues.get('multiple_h1_pages', []))}
• Pagine senza H2: {len(detailed_issues.get('missing_h2_pages', []))}
• Pagine senza H3: {len(detailed_issues.get('missing_h3_pages', []))}
• Punteggio: {headings_analysis.get('score', 'N/A')}/100
"""
        details_text += create_url_table_string("Pagine senza H1", detailed_issues.get('missing_h1_pages', []))
        details_text += create_url_table_string("Pagine con H1 Multipli", detailed_issues.get('multiple_h1_pages', []))
        details_text += create_url_table_string("Pagine senza H2", detailed_issues.get('missing_h2_pages', []))
        details_text += create_url_table_string("Pagine senza H3", detailed_issues.get('missing_h3_pages', []))
        details_text += "\n"

        # Immagini
        images_analysis = self.analysis_results['images_analysis']
        details_text += f"""
🖼️ IMMAGINI
• Totale immagini: {images_analysis['total_images']}
• Con alt text: {images_analysis['images_with_alt']}
• Senza alt text: {len(detailed_issues.get('images_without_alt', []))}
• Senza attributo title: {len(detailed_issues.get('images_without_title', []))}
• Alt vuoto: {images_analysis['images_with_empty_alt']}
• Immagini interrotte: {len(detailed_issues.get('broken_images', []))}
• Punteggio: {images_analysis['score']}/100
"""
        details_text += create_url_table_string("Immagini senza Alt Text", detailed_issues.get('images_without_alt', []))
        details_text += create_url_table_string("Immagini senza Attributo Title", detailed_issues.get('images_without_title', []))
        details_text += create_url_table_string("Immagini Interrotte", detailed_issues.get('broken_images', []))
        details_text += "\n"
        
        # Contenuto
        content_analysis = self.analysis_results.get('content_analysis', {})
        details_text += f"""
📄 CONTENUTO
• Pagine con conteggio parole basso: {len(detailed_issues.get('low_word_count_pages', []))}
• Pagine con duplicati di contenuto: {len(detailed_issues.get('duplicate_content_pages', []))}
• Pagine con rapporto testo/HTML basso: {len(detailed_issues.get('low_text_html_ratio_pages', []))}
• Punteggio: {content_analysis.get('score', 'N/A')}/100
"""
        details_text += create_url_table_string("Pagine con Conteggio Parole Basso", detailed_issues.get('low_word_count_pages', []))
        details_text += create_url_table_string("Pagine con Duplicati di Contenuto", detailed_issues.get('duplicate_content_pages', []))
        details_text += create_url_table_string("Pagine con Rapporto Testo/HTML Basso", detailed_issues.get('low_text_html_ratio_pages', []))
        details_text += "\n"

        # Link
        links_analysis = self.analysis_results.get('links_analysis', {})
        details_text += f"""
🔗 LINK
• Link interni interrotti: {len(detailed_issues.get('broken_links', []))}
• Loop e catene di reindirizzamenti: {len(detailed_issues.get('redirect_chains', []))}
• Pagine con link canonico interrotto: {len(detailed_issues.get('broken_canonical_links', []))}
• Pagine con più URL canonici: {len(detailed_issues.get('multiple_canonical_urls', []))}
• Punteggio: {links_analysis.get('score', 'N/A')}/100
"""
        details_text += create_url_table_string("Link Interni Interrotti", detailed_issues.get('broken_links', []))
        details_text += create_url_table_string("Loop e Catene di Reindirizzamenti", detailed_issues.get('redirect_chains', []))
        details_text += create_url_table_string("Pagine con Link Canonico Interrotto", detailed_issues.get('broken_canonical_links', []))
        details_text += create_url_table_string("Pagine con Più URL Canonici", detailed_issues.get('multiple_canonical_urls', []))
        details_text += "\n"

        # Performance
        perf_analysis = self.analysis_results['performance_analysis']
        details_text += f"""
⚡ PERFORMANCE
• Pagine veloci: {perf_analysis['fast_pages']}
• Pagine lente: {perf_analysis['slow_pages']}
• Tempo medio: {perf_analysis['average_response_time']:.2f}s
• Dimensione media: {perf_analysis['average_page_size']/1024:.1f} KB
• Pagine con dimensioni HTML troppo grandi: {len(detailed_issues.get('large_html_pages', []))}
• Pagine con velocità di caricamento bassa: {len(detailed_issues.get('slow_pages', []))}
• Punteggio: {perf_analysis['score']}/100
"""
        details_text += create_url_table_string("Pagine con Dimensioni HTML Troppo Grandi", detailed_issues.get('large_html_pages', []))
        details_text += create_url_table_string("Pagine con Velocità di Caricamento Bassa", detailed_issues.get('slow_pages', []))
        details_text += "\n"

        # Tecnico (nuove aggiunte)
        technical_analysis = self.analysis_results.get('technical_analysis', {})
        details_text += f"""
⚙️ TECNICO
• Pagine non raggiungibili dal crawler: {len(detailed_issues.get('unreachable_pages', []))}
• Problemi risoluzione DNS: {len(detailed_issues.get('dns_resolution_issues', []))}
• Formati URL non corretti: {len(detailed_issues.get('invalid_url_format_pages', []))}
• Robots.txt con errori: {len(detailed_issues.get('robots_txt_errors', []))}
• Sitemap.xml con errori: {len(detailed_issues.get('sitemap_xml_errors', []))}
• Pagine sbagliate in sitemap.xml: {len(detailed_issues.get('sitemap_wrong_pages', []))}
• Problemi risoluzione WWW: {len(detailed_issues.get('www_resolution_issues', []))}
• Pagine senza tag viewport: {len(detailed_issues.get('pages_without_viewport', []))}
• Pagine AMP senza tag canonici: {len(detailed_issues.get('amp_no_canonical_pages', []))}
• Problemi hreflang: {len(detailed_issues.get('hreflang_issues', []))}
• Conflitti hreflang: {len(detailed_issues.get('hreflang_conflicts', []))}
• Link hreflang sbagliati: {len(detailed_issues.get('hreflang_broken_links', []))}
• Pagine con meta refresh tag: {len(detailed_issues.get('meta_refresh_tags', []))}
• CSS/JS interni inaccessibili: {len(detailed_issues.get('inaccessible_css_js', []))}
• Sitemap.xml troppo pesanti: {len(detailed_issues.get('large_sitemap_files', []))}
• Elementi dati strutturati non validi: {len(detailed_issues.get('invalid_structured_data', []))}
• Pagine senza valore larghezza viewport: {len(detailed_issues.get('pages_without_viewport_width', []))}
• Punteggio: {technical_analysis.get('score', 'N/A')}/100
"""
        details_text += create_url_table_string("Pagine Non Raggiungibili dal Crawler", detailed_issues.get('unreachable_pages', []))
        details_text += create_url_table_string("Problemi Risoluzione DNS", detailed_issues.get('dns_resolution_issues', []))
        details_text += create_url_table_string("Formati URL Non Corretti", detailed_issues.get('invalid_url_format_pages', []))
        details_text += create_url_table_string("Robots.txt con Errori", detailed_issues.get('robots_txt_errors', []))
        details_text += create_url_table_string("Sitemap.xml con Errori", detailed_issues.get('sitemap_xml_errors', []))
        details_text += create_url_table_string("Pagine Sbagliate in Sitemap.xml", detailed_issues.get('sitemap_wrong_pages', []))
        details_text += create_url_table_string("Problemi Risoluzione WWW", detailed_issues.get('www_resolution_issues', []))
        details_text += create_url_table_string("Pagine senza Tag Viewport", detailed_issues.get('pages_without_viewport', []))
        details_text += create_url_table_string("Pagine AMP senza Tag Canonici", detailed_issues.get('amp_no_canonical_pages', []))
        details_text += create_url_table_string("Problemi Hreflang", detailed_issues.get('hreflang_issues', []))
        details_text += create_url_table_string("Conflitti Hreflang", detailed_issues.get('hreflang_conflicts', []))
        details_text += create_url_table_string("Link Hreflang Sbagliati", detailed_issues.get('hreflang_broken_links', []))
        details_text += create_url_table_string("Pagine con Meta Refresh Tag", detailed_issues.get('meta_refresh_tags', []))
        details_text += create_url_table_string("CSS/JS Interni Inaccessibili", detailed_issues.get('inaccessible_css_js', []))
        details_text += create_url_table_string("Sitemap.xml Troppo Pesanti", detailed_issues.get('large_sitemap_files', []))
        details_text += create_url_table_string("Elementi Dati Strutturati Non Validi", detailed_issues.get('invalid_structured_data', []))
        details_text += create_url_table_string("Pagine senza Valore Larghezza Viewport", detailed_issues.get('pages_without_viewport_width', []))
        details_text += "\n"

        # SSL (nuove aggiunte)
        ssl_analysis = self.analysis_results.get('ssl_analysis', {})
        details_text += f"""
🔒 SSL / SICUREZZA
• Pagine non sicure (HTTP): {len(detailed_issues.get('non_secure_pages', []))}
• Certificato in scadenza/scaduto: {len(detailed_issues.get('ssl_expired_or_expiring_issues', []))}
• Vecchio protocollo sicurezza: {len(detailed_issues.get('old_security_protocol_issues', []))}
• Certificato nome errato: {len(detailed_issues.get('ssl_wrong_name_issues', []))}
• Problemi contenuti misti: {len(detailed_issues.get('mixed_content_pages', []))}
• Nessun reindirizzamento HTTP->HTTPS homepage: {len(detailed_issues.get('http_to_https_no_redirect_issues', []))}
• Punteggio: {ssl_analysis.get('score', 'N/A')}/100
"""
        details_text += create_url_table_string("Pagine Non Sicure (HTTP)", detailed_issues.get('non_secure_pages', []))
        details_text += create_url_table_string("Certificato in Scadenza/Scaduto", detailed_issues.get('ssl_expired_or_expiring_issues', []))
        details_text += create_url_table_string("Vecchio Protocollo Sicurezza", detailed_issues.get('old_security_protocol_issues', []))
        details_text += create_url_table_string("Certificato Nome Errato", detailed_issues.get('ssl_wrong_name_issues', []))
        details_text += create_url_table_string("Problemi Contenuti Misti", detailed_issues.get('mixed_content_pages', []))
        details_text += create_url_table_string("Nessun Reindirizzamento HTTP->HTTPS Homepage", detailed_issues.get('http_to_https_no_redirect_issues', []))
        details_text += "\n"
        
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
            
            # Funzione helper per creare tabelle di raccomandazioni per i dettagli
            def create_recommendation_table_string(title: str, rec_list: List[Dict]):
                if not rec_list:
                    return ""
                
                table_content = f"\n--- {title} ({len(rec_list)}) ---\n"
                table_content += "{:<30} {:<50} {:<80}\n".format("Categoria", "Problema", "Raccomandazione")
                table_content += "-" * 160 + "\n"
                
                for rec in rec_list:
                    category = rec.get('category', 'N/A')
                    issue = rec.get('issue', 'N/A')
                    recommendation = rec.get('recommendation', 'N/A')
                    table_content += "{:<30} {:<50} {:<80}\n".format(
                        category[:27] + '...' if len(category) > 30 else category,
                        issue[:47] + '...' if len(issue) > 50 else issue,
                        recommendation[:77] + '...' if len(recommendation) > 80 else recommendation
                    )
                table_content += "\n"
                return table_content

            rec_text += create_recommendation_table_string('PRIORITÀ ALTA', high_priority)
            rec_text += create_recommendation_table_string('PRIORITÀ MEDIA', medium_priority)
            rec_text += create_recommendation_table_string('PRIORITÀ BASSA', low_priority)
        
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
        preview_window.grab_set() # Rende la finestra modale
        
        # Text widget con scrollbar
        text_frame = ctk.CTkFrame(preview_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        preview_text = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(size=10),
            corner_radius=8,
            border_width=1,
            border_color=GUI_CONFIG['colors']['border']
        )
        preview_text.pack(fill="both", expand=True)
        
        # Genera anteprima testuale
        summary = self.analysis_results['summary']
        
        # Use the adjusted score for preview
        preview_content = f"""
SEO ANALYZER REPORT
===================

Dominio: {summary['domain']}
Data Analisi: {summary['analysis_date']}
Punteggio Generale (Aggiustato): {int(self.adjusted_overall_score)}/100

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
            
            # Create a deep copy of analysis_results and update the overall_score
            analysis_results_for_pdf = copy.deepcopy(self.analysis_results)
            # Assicurati che overall_score esista prima di tentare di modificarlo
            if 'overall_score' in analysis_results_for_pdf:
                analysis_results_for_pdf['overall_score'] = int(self.adjusted_overall_score) # Use the adjusted score
            else:
                # Se overall_score non esiste, lo aggiungiamo
                analysis_results_for_pdf['overall_score'] = int(self.adjusted_overall_score)
            
            # Genera PDF
            domain = analysis_results_for_pdf['summary']['domain']
            pdf_generator = PDFGenerator(analysis_results_for_pdf, domain) # Pass the modified results
            
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
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=GUI_CONFIG['colors']['primary']
        )
        title.pack(pady=20)
        
        # Notebook per le categorie
        # Anche qui, stilizziamo ttk.Notebook
        style = ttk.Style()
        style.theme_use("default")
        
        bg_color = self.window._apply_appearance_mode(self.window.cget("fg_color"))
        # Correzione: Usa direttamente il colore del testo dalla configurazione
        text_color = GUI_CONFIG['colors']['text']
        selected_tab_color = GUI_CONFIG['colors']['primary']
        
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background=bg_color, 
                        foreground=text_color,
                        lightcolor=bg_color,
                        darkcolor=bg_color,
                        bordercolor=bg_color,
                        padding=[10, 5])
        style.map("TNotebook.Tab", 
                  background=[("selected", selected_tab_color)],
                  foreground=[("selected", "white")])

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tab Crawling
        crawling_frame = ctk.CTkFrame(notebook, corner_radius=8)
        notebook.add(crawling_frame, text="Crawling")
        self._create_crawling_settings(crawling_frame)
        
        # Tab SEO
        seo_frame = ctk.CTkFrame(notebook, corner_radius=8)
        notebook.add(seo_frame, text="SEO")
        self._create_seo_settings(seo_frame)
        
        # Tab PDF
        pdf_frame = ctk.CTkFrame(notebook, corner_radius=8)
        notebook.add(pdf_frame, text="PDF")
        self._create_pdf_settings(pdf_frame)
        
        # Pulsanti
        buttons_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Salva",
            command=self._save_settings,
            fg_color=GUI_CONFIG['colors']['success'],
            hover_color=GUI_CONFIG['colors']['success_dark'],
            corner_radius=10
        )
        save_button.pack(side="right", padx=(10, 0))
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Annulla",
            command=self.window.destroy,
            fg_color=GUI_CONFIG['colors']['error'],
            hover_color=GUI_CONFIG['colors']['error_dark'],
            corner_radius=10
        )
        cancel_button.pack(side="right")
        
    def _create_crawling_settings(self, parent):
        """Crea le impostazioni di crawling"""
        scroll_frame = ctk.CTkScrollableFrame(parent, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Max pagine
        max_pages_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        max_pages_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(max_pages_frame, text="Massimo pagine:").pack(side="left", padx=10)
        self.max_pages_var = tk.IntVar(value=CRAWL_CONFIG['max_pages'])
        ctk.CTkEntry(max_pages_frame, textvariable=self.max_pages_var, width=100, corner_radius=8).pack(side="right", padx=10)
        
        # Timeout
        timeout_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        timeout_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(timeout_frame, text="Timeout (secondi):").pack(side="left", padx=10)
        self.timeout_var = tk.IntVar(value=CRAWL_CONFIG['timeout'])
        ctk.CTkEntry(timeout_frame, textvariable=self.timeout_var, width=100, corner_radius=8).pack(side="right", padx=10)
        
        # Delay
        delay_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        delay_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(delay_frame, text="Delay tra richieste (secondi):").pack(side="left", padx=10)
        self.delay_var = tk.DoubleVar(value=CRAWL_CONFIG['delay'])
        ctk.CTkEntry(delay_frame, textvariable=self.delay_var, width=100, corner_radius=8).pack(side="right", padx=10)
        
        # Opzioni
        self.follow_external_var = tk.BooleanVar(value=CRAWL_CONFIG['follow_external'])
        ctk.CTkCheckBox(scroll_frame, text="Segui link esterni", variable=self.follow_external_var, corner_radius=5).pack(anchor="w", padx=10, pady=5)
        
        self.respect_robots_var = tk.BooleanVar(value=CRAWL_CONFIG['respect_robots'])
        ctk.CTkCheckBox(scroll_frame, text="Rispetta robots.txt", variable=self.respect_robots_var, corner_radius=5).pack(anchor="w", padx=10, pady=5)
        
    def _create_seo_settings(self, parent):
        """Crea le impostazioni SEO"""
        scroll_frame = ctk.CTkScrollableFrame(parent, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title length
        title_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(title_frame, text="Lunghezza title min:").pack(side="left", padx=5)
        self.title_min_var = tk.IntVar(value=SEO_CONFIG['title_min_length'])
        ctk.CTkEntry(title_frame, textvariable=self.title_min_var, width=60, corner_radius=8).pack(side="left", padx=5)
        
        ctk.CTkLabel(title_frame, text="max:").pack(side="left", padx=5)
        self.title_max_var = tk.IntVar(value=SEO_CONFIG['title_max_length'])
        ctk.CTkEntry(title_frame, textvariable=self.title_max_var, width=60, corner_radius=8).pack(side="left", padx=5)
        
        # Meta description length
        meta_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        meta_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(meta_frame, text="Lunghezza meta min:").pack(side="left", padx=5)
        self.meta_min_var = tk.IntVar(value=SEO_CONFIG['meta_description_min_length'])
        ctk.CTkEntry(meta_frame, textvariable=self.meta_min_var, width=60, corner_radius=8).pack(side="left", padx=5)
        
        ctk.CTkLabel(meta_frame, text="max:").pack(side="left", padx=5)
        self.meta_max_var = tk.IntVar(value=SEO_CONFIG['meta_description_max_length'])
        ctk.CTkEntry(meta_frame, textvariable=self.meta_max_var, width=60, corner_radius=8).pack(side="left", padx=5)
        
        # Min word count
        words_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        words_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(words_frame, text="Minimo parole per pagina:").pack(side="left", padx=10)
        self.min_words_var = tk.IntVar(value=SEO_CONFIG['min_word_count'])
        ctk.CTkEntry(words_frame, textvariable=self.min_words_var, width=100, corner_radius=8).pack(side="right", padx=10)
        
    def _create_pdf_settings(self, parent):
        """Crea le impostazioni PDF"""
        scroll_frame = ctk.CTkScrollableFrame(parent, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Font size
        font_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        font_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(font_frame, text="Dimensione font titolo:").pack(side="left", padx=10)
        self.font_title_var = tk.IntVar(value=PDF_CONFIG['font_sizes']['title'])
        ctk.CTkEntry(font_frame, textvariable=self.font_title_var, width=60, corner_radius=8).pack(side="right", padx=10)
        
        # Page margins
        margin_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        margin_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(margin_frame, text="Margini pagina (cm):").pack(side="left", padx=10)
        self.margin_var = tk.DoubleVar(value=PDF_CONFIG['margin']['top'])
        ctk.CTkEntry(margin_frame, textvariable=self.margin_var, width=60, corner_radius=8).pack(side="right", padx=10)
        
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
            # Assicurati che tutti i margini siano aggiornati
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
    # Esempio di configurazione GUI_CONFIG (dovrebbe essere in config.py)
    # Assicurati che il tuo file config.py contenga una struttura simile
    try:
        from config import GUI_CONFIG, CRAWL_CONFIG, SEO_CONFIG, PDF_CONFIG, URL_REGEX, MESSAGES
    except ImportError:
        print("Errore: Il file config.py non è stato trovato o non è configurato correttamente.")
        print("Assicurati che config.py contenga le variabili GUI_CONFIG, CRAWL_CONFIG, SEO_CONFIG, PDF_CONFIG, URL_REGEX, MESSAGES.")
        # Definizione di default per evitare errori se config.py non esiste
        GUI_CONFIG = {
            'theme': 'System',
            'window_title': 'SEO Analyzer Pro',
            'window_size': '1200x800',
            'colors': {
                'primary': '#336699',
                'primary_light': '#6699CC',
                'primary_dark': '#224466',
                'secondary': '#6699CC',
                'secondary_dark': '#4477AA',
                'success': '#2fa827',
                'success_dark': '#22881f',
                'warning': '#ff9500',
                'warning_dark': '#cc7700',
                'error': '#d32f2f',
                'error_dark': '#a32222',
                'text': '#333333',
                'white': '#FFFFFF',
                'light_gray': '#EEEEEE',
                'dark_gray': '#555555',
                'border': '#CCCCCC',
                'disabled': '#AAAAAA'
            }
        }
        CRAWL_CONFIG = {
            'max_pages': 100,
            'timeout': 10,
            'delay': 0.5,
            'follow_external': False,
            'respect_robots': True
        }
        SEO_CONFIG = {
            'title_min_length': 30,
            'title_max_length': 60,
            'meta_description_min_length': 50,
            'meta_description_max_length': 160,
            'min_word_count': 200
        }
        PDF_CONFIG = {
            'font_sizes': {'title': 24},
            'margin': {'top': 2.5, 'bottom': 2.5, 'left': 2.5, 'right': 2.5},
            'colors': {
                'primary': '#336699',
                'secondary': '#6699CC',
                'success': '#2fa827',
                'warning': '#ff9500',
                'error': '#d32f2f',
                'light_gray': '#f0f0f0',
                'dark_gray': '#333333'
            }
        }
        URL_REGEX = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        MESSAGES = {
            'error_invalid_url': "L'URL inserito non è valido. Assicurati che inizi con http:// o https://",
            'crawling_started': "Avvio crawling di: {}",
            'crawling_completed': "Crawling completato. Trovate {} pagine.",
            'analysis_started': "Avvio analisi SEO...",
            'analysis_completed': "Analisi SEO completata!",
            'report_generated': "Report PDF generato con successo in: {}",
            'error_pdf_generation': "Errore durante la generazione del PDF: {}"
        }

    main()
