#!/usr/bin/env python3
"""
SEO Analyzer Pro - Applicazione principale
Analizzatore SEO completo per siti web

Autore: SEO Analyzer Team
Versione: 1.0.0
"""

import sys
import os
import logging
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Aggiungi il percorso del progetto al sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import delle configurazioni
    from config import *
    
    # Import dell'interfaccia grafica
    from gui.main_window import MainWindow
    
    # Import delle utility (per verificare che tutto sia correttamente importabile)
    from utils.crawler import WebCrawler
    from utils.analyzer import SEOAnalyzer
    from utils.pdf_generator import PDFGenerator
    
except ImportError as e:
    print(f"Errore nell'importazione dei moduli: {e}")
    print("Assicurati che tutte le dipendenze siano installate:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """
    Configura il sistema di logging per l'applicazione
    """
    try:
        # Crea la directory dei log se non esiste
        log_dir = BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Configura il logging
        log_file = log_dir / LOGGING_CONFIG['file']
        
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Logger principale
        logger = logging.getLogger(__name__)
        logger.info("=" * 50)
        logger.info("SEO Analyzer Pro - Avvio applicazione")
        logger.info(f"Versione Python: {sys.version}")
        logger.info(f"Directory di lavoro: {os.getcwd()}")
        logger.info(f"File di log: {log_file}")
        logger.info("=" * 50)
        
        return logger
        
    except Exception as e:
        print(f"Errore nella configurazione del logging: {e}")
        # Fallback su configurazione base
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

def check_dependencies():
    """
    Verifica che tutte le dipendenze necessarie siano installate
    """
    logger = logging.getLogger(__name__)
    missing_deps = []
    
    dependencies = [
        ('customtkinter', 'CustomTkinter'),
        ('requests', 'Requests'),
        ('bs4', 'Beautiful Soup'),
        ('selenium', 'Selenium'),
        ('reportlab', 'ReportLab'),
        ('jinja2', 'Jinja2'),
        ('pandas', 'Pandas'),
        ('tqdm', 'TQDM'),
        ('webdriver_manager', 'WebDriver Manager'),
        ('PIL', 'Pillow'),
        ('matplotlib', 'Matplotlib')
    ]
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            logger.debug(f"✓ {display_name} - OK")
        except ImportError:
            missing_deps.append(display_name)
            logger.error(f"✗ {display_name} - MANCANTE")
    
    if missing_deps:
        error_msg = f"""
Dipendenze mancanti:
{', '.join(missing_deps)}

Installa le dipendenze mancanti con:
pip install -r requirements.txt

Oppure installa manualmente:
pip install {' '.join([dep[0] for dep in dependencies if dep[1] in missing_deps])}
        """
        logger.error(error_msg)
        return False, error_msg
    
    logger.info("✓ Tutte le dipendenze sono installate correttamente")
    return True, None

def check_system_requirements():
    """
    Verifica i requisiti di sistema
    """
    logger = logging.getLogger(__name__)
    
    # Verifica versione Python
    if sys.version_info < (3, 7):
        error_msg = f"Python 3.7+ richiesto. Versione attuale: {sys.version}"
        logger.error(error_msg)
        return False, error_msg
    
    # Verifica spazio su disco (almeno 100MB)
    try:
        import shutil
        free_space = shutil.disk_usage('.').free
        if free_space < 100 * 1024 * 1024:  # 100MB
            logger.warning(f"Poco spazio libero su disco: {free_space / (1024*1024):.1f}MB")
    except Exception as e:
        logger.warning(f"Impossibile verificare lo spazio su disco: {e}")
    
    # Verifica che le directory necessarie esistano o possano essere create
    try:
        for directory in [REPORTS_DIR, TEMPLATES_DIR, ASSETS_DIR]:
            directory.mkdir(exist_ok=True)
            if not directory.exists():
                raise Exception(f"Impossibile creare la directory: {directory}")
        logger.info("✓ Directory del progetto create/verificate")
    except Exception as e:
        error_msg = f"Errore nella creazione delle directory: {e}"
        logger.error(error_msg)
        return False, error_msg
    
    logger.info("✓ Requisiti di sistema soddisfatti")
    return True, None

def create_default_template():
    """
    Crea il template HTML di default per i report se non esiste
    """
    template_path = TEMPLATES_DIR / "report_template.html"
    
    if not template_path.exists():
        logger = logging.getLogger(__name__)
        logger.info("Creazione template HTML di default...")
        
        template_content = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Report - {{ domain }}</title>
    <style>
        body {
            font-family: 'Helvetica', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: #1f538d;
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .score {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }
        .section {
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #1f538d;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .good { color: #2fa827; }
        .warning { color: #ff9500; }
        .error { color: #d32f2f; }
        @media print {
            body { margin: 0; }
            .section { break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>SEO Analysis Report</h1>
        <h2>{{ domain }}</h2>
        <div class="score">{{ overall_score }}/100</div>
        <p>Generated on {{ analysis_date }}</p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <div class="metric">
            <span>Pages Analyzed:</span>
            <span>{{ total_pages }}</span>
        </div>
        <div class="metric">
            <span>Total Issues:</span>
            <span>{{ total_issues }}</span>
        </div>
        <div class="metric">
            <span>Recommendations:</span>
            <span>{{ total_recommendations }}</span>
        </div>
    </div>
    
    <div class="section">
        <h2>Detailed Scores</h2>
        {% for category, score in scores.items() %}
        <div class="metric">
            <span>{{ category }}:</span>
            <span class="{% if score >= 80 %}good{% elif score >= 50 %}warning{% else %}error{% endif %}">
                {{ score }}/100
            </span>
        </div>
        {% endfor %}
    </div>
</body>
</html>
        """
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content.strip())
            logger.info(f"✓ Template creato: {template_path}")
        except Exception as e:
            logger.error(f"Errore nella creazione del template: {e}")

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Gestisce le eccezioni non catturate
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Consenti l'interruzione da tastiera
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger = logging.getLogger(__name__)
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical(f"Eccezione non gestita:\n{error_msg}")
    
    # Mostra errore all'utente se possibile
    try:
        root = tk.Tk()
        root.withdraw()  # Nascondi la finestra principale
        messagebox.showerror(
            "Errore Critico",
            f"Si è verificato un errore inaspettato:\n\n{exc_value}\n\nL'applicazione verrà chiusa.\n\nControlla il file di log per dettagli completi."
        )
        root.destroy()
    except:
        pass  # Se anche questo fallisce, non fare nulla

def show_startup_info():
    """
    Mostra informazioni di avvio dell'applicazione
    """
    logger = logging.getLogger(__name__)
    
    startup_info = f"""
╔══════════════════════════════════════════════════════════════╗
║                      SEO ANALYZER PRO                       ║
║                         Versione 1.0                        ║
╠══════════════════════════════════════════════════════════════╣
║ Analizzatore SEO completo per siti web                      ║
║                                                              ║
║ Caratteristiche:                                             ║
║ • Crawling automatico del sito                              ║
║ • Analisi SEO completa (Title, Meta, Images, Performance)   ║
║ • Generazione report PDF professionali                      ║
║ • Interfaccia grafica moderna                               ║
║ • Raccomandazioni personalizzate                            ║
╚══════════════════════════════════════════════════════════════╝

Configurazione attuale:
• Tema GUI: {GUI_CONFIG['theme']}
• Max pagine per crawling: {CRAWL_CONFIG['max_pages']}
• Timeout richieste: {CRAWL_CONFIG['timeout']}s
• Directory report: {REPORTS_DIR}
    """
    
    logger.info(startup_info)
    print(startup_info)

def main():
    """
    Funzione principale dell'applicazione
    """
    try:
        # Setup logging
        logger = setup_logging()
        
        # Mostra info di avvio
        show_startup_info()
        
        # Installa gestore eccezioni globale
        sys.excepthook = handle_exception
        
        # Verifica requisiti di sistema
        logger.info("Verifica requisiti di sistema...")
        system_ok, system_error = check_system_requirements()
        if not system_ok:
            messagebox.showerror("Errore Sistema", system_error)
            sys.exit(1)
        
        # Verifica dipendenze
        logger.info("Verifica dipendenze...")
        deps_ok, deps_error = check_dependencies()
        if not deps_ok:
            messagebox.showerror("Dipendenze Mancanti", deps_error)
            sys.exit(1)
        
        # Crea template di default
        create_default_template()
        
        logger.info("Avvio interfaccia grafica...")
        
        # Avvia l'applicazione GUI
        app = MainWindow()
        
        logger.info("✓ Applicazione avviata con successo")
        logger.info("Interfaccia grafica caricata, in attesa dell'utente...")
        
        # Esegui l'applicazione
        app.run()
        
        logger.info("Applicazione chiusa dall'utente")
        
    except KeyboardInterrupt:
        logger.info("Applicazione interrotta dall'utente (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        logger.critical(f"Errore critico nell'avvio: {e}")
        logger.critical(traceback.format_exc())
        
        try:
            messagebox.showerror(
                "Errore Critico",
                f"Impossibile avviare l'applicazione:\n\n{str(e)}\n\nControlla il file di log per dettagli completi."
            )
        except:
            print(f"ERRORE CRITICO: {e}")
        
        sys.exit(1)

def show_help():
    """
    Mostra informazioni di aiuto
    """
    help_text = """
SEO Analyzer Pro - Aiuto

UTILIZZO:
    python main.py              Avvia l'applicazione con interfaccia grafica
    python main.py --help       Mostra questo aiuto

REQUISITI:
    • Python 3.7+
    • Tutte le dipendenze in requirements.txt
    • Connessione internet per il crawling
    • Chrome/Chromium per analisi avanzate (opzionale)

CONFIGURAZIONE:
    Modifica il file config.py per personalizzare:
    • Limiti di crawling
    • Soglie SEO
    • Stili PDF
    • Impostazioni GUI

DIRECTORY:
    • reports/     Report PDF generati
    • templates/   Template HTML
    • logs/        File di log
    • assets/      Risorse dell'applicazione

SUPPORTO:
    Per problemi o domande, controlla i log in logs/seo_analyzer.log
    
ESEMPI D'USO:
    1. Inserisci l'URL del sito (es: https://example.com)
    2. Configura il numero massimo di pagine da analizzare
    3. Clicca "Avvia Analisi"
    4. Attendi il completamento del crawling e dell'analisi
    5. Visualizza i risultati nelle tab
    6. Esporta il report in PDF
    """
    print(help_text)

if __name__ == "__main__":
    # Gestisci argomenti da riga di comando
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
            sys.exit(0)
        elif sys.argv[1] in ['--version', '-v']:
            print("SEO Analyzer Pro v1.0.0")
            sys.exit(0)
        else:
            print(f"Argomento sconosciuto: {sys.argv[1]}")
            print("Usa --help per vedere le opzioni disponibili")
            sys.exit(1)
    
    # Avvia l'applicazione principale
    main()