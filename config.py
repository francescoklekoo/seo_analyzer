"""
Configurazioni per l'applicazione SEO Analyzer
"""

import os
from pathlib import Path

# Percorsi dell'applicazione
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"

# Crea le directory se non esistono
REPORTS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Configurazioni di crawling
CRAWL_CONFIG = {
    'max_pages': 50,  # Numero massimo di pagine da analizzare
    'timeout': 30,    # Timeout per le richieste HTTP
    'delay': 1,       # Delay tra le richieste (in secondi)
    'max_depth': 3,   # Profondità massima di crawling
    'follow_external': False,  # Se seguire link esterni
    'respect_robots': True,    # Se rispettare robots.txt
}

# User agents per il crawling
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# Configurazioni SEO
SEO_CONFIG = {
    'title_min_length': 30,
    'title_max_length': 60,
    'meta_description_min_length': 120,
    'meta_description_max_length': 160,
    'h1_max_count': 1,
    'min_word_count': 300,
    'max_page_size_mb': 3,
    'min_text_html_ratio': 0.15,
}

# Configurazioni per le performance
PERFORMANCE_CONFIG = {
    'max_response_time': 3.0,  # secondi
    'min_speed_score': 70,     # punteggio minimo PageSpeed
    'compression_threshold': 0.8,  # soglia di compressione
}

# Configurazioni GUI (Aggiornato con colori aggiuntivi)
GUI_CONFIG = {
    'window_title': 'SEO Analyzer Pro',
    'window_size': '1200x800',
    'theme': 'dark', # 'System', 'Dark', 'Light'
    'colors': {
        'primary': '#1f538d',
        'primary_light': '#6699CC', # Aggiunto
        'primary_dark': '#14375e',  # Modificato per essere più scuro del primary
        'secondary': '#6699CC',
        'secondary_dark': '#4477AA', # Aggiunto
        'success': '#2fa827',
        'success_dark': '#22881f',   # Aggiunto
        'warning': '#ff9500',
        'warning_dark': '#cc7700',   # Aggiunto
        'error': '#d32f2f',
        'error_dark': '#a32222',     # Aggiunto
        'text': '#ffffff',
        'background': '#212121',
        'dark_gray': '#666666',
        'white': '#FFFFFF',          # Aggiunto
        'light_gray': '#EEEEEE',     # Aggiunto
        'border': '#CCCCCC',         # Aggiunto
        'disabled': '#AAAAAA'        # Aggiunto
    },
    'fonts': {
        'title': ('Helvetica', 24, 'bold'),
        'heading': ('Helvetica', 16, 'bold'),
        'body': ('Helvetica', 12),
        'small': ('Helvetica', 10),
    }
}

# Selenium WebDriver configurazioni
SELENIUM_CONFIG = {
    'headless': True,
    'window_size': (1920, 1080),
    'page_load_timeout': 30,
    'implicit_wait': 10,
    'chrome_options': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',  # Per velocizzare il caricamento
        '--disable-javascript',  # Per alcune analisi statiche
    ]
}

# Configurazioni per il report PDF
PDF_CONFIG = {
    'page_size': 'A4',
    'margin': {
        'left': 2.5,
        'right': 2.5,
        'top': 2.5,
        'bottom': 2.5
    },
    'font_family': 'Helvetica',
    'font_sizes': {
        'title': 18,
        'heading': 14,
        'body': 10,
        'small': 8
    },
    'colors': {
        'primary': '#336699',
        'secondary': '#6699CC',
        'success': '#2fa827',
        'warning': '#ff9500',
        'error': '#d32f2f',
        'light_gray': '#f0f0f0',
        'dark_gray': '#333333',
        'secondary_dark': '#556677',
        'border': '#CCCCCC'  # Added border color
    }
}

# Messaggi e testi dell'applicazione
MESSAGES = {
    'crawling_started': 'Crawling iniziato per: {}',
    'crawling_completed': 'Crawling completato. Analizzate {} pagine',
    'analysis_started': 'Analisi SEO in corso...',
    'analysis_completed': 'Analisi SEO completata!',
    'report_generated': 'Report generato con successo: {}',
    'error_invalid_url': 'URL non valido. Inserisci un URL completo (es: https://example.com)',
    'error_crawling': 'Errore durante il crawling: {}',
    'error_analysis': 'Errore durante l\'analisi: {}',
    'error_pdf_generation': 'Errore durante la generazione del PDF: {}',
}

# Pesi per il calcolo del punteggio SEO (totale deve essere 100)
SEO_WEIGHTS = {
    'title_tags': 15,
    'meta_descriptions': 10,
    'headings': 10,
    'images_alt': 15,
    'internal_links': 5,
    'page_speed': 20,
    'mobile_friendly': 10,
    'ssl_certificate': 5,
    'content_quality': 10,
}

# Configurazioni per controlli specifici
CHECKS_CONFIG = {
    'check_images': True,
    'check_links': True,
    'check_speed': True,
    'check_mobile': True,
    'check_ssl': True,
    'check_meta_tags': True,
    'check_headings': True,
    'check_content': True,
    'check_sitemap': True,
    'check_robots': True,
}

# Headers HTTP standard
HTTP_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
}

# Estensioni file da ignorare durante il crawling
IGNORED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.rar', '.tar', '.gz', '.7z',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
    '.css', '.js', '.json', '.xml'
}

# Regex per validazione URL
URL_REGEX = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'

# Configurazioni logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'seo_analyzer.log'
}
