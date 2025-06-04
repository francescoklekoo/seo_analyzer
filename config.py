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

# Configurazioni per il report PDF
PDF_CONFIG = {
    'page_size': 'A4',
    'margin': {
        'left': 2.0,
        'right': 2.0,
        'top': 2.0,
        'bottom': 2.0
    },
    'font_family': 'Helvetica',
    'font_family_bold': 'Helvetica',
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

# Etichette user-friendly per i tipi di problemi nel report PDF
PDF_ISSUE_TYPE_LABELS = {
    # User-specified / preferred labels:
    'missing_title': 'Titolo mancante',
    'duplicate_title': 'Titolo duplicato',
    'short_title': 'Titolo troppo corto',
    'long_title': 'Titolo troppo lungo',
    'missing_meta_description': 'Meta description mancante', # Covers 'missing_meta'
    'duplicate_meta': 'Meta description duplicato', # User's explicit preference
    'short_meta_description': 'Meta description troppo corta',
    'long_meta_description': 'Meta description troppo lunga',
    'missing_h1': 'H1 mancante',
    'multiple_h1_tags': 'Tag H1 multipli', # Covers 'multiple_h1'
    'missing_h2': 'H2 mancanti', # User's preference for plural
    'missing_alt_attribute': 'Attributo ALT mancante', # Covers 'missing_alt_attr'
    'empty_alt_attribute': 'Attributo ALT vuoto', # Covers 'empty_alt_attr'
    'broken_image': 'Immagine interrotta', # Keeping existing good label
    'low_word_count': 'Conteggio parole basso', # Specific key, good label
    'low_text_html_ratio': 'Basso rapporto testo/HTML',
    'slow_page_load': 'Caricamento pagina lento', # Covers 'slow_page'
    'large_html_size': 'Dimensioni HTML elevate', # Covers 'large_page'
    'http_status_4xx': 'Errore client (4xx)', # Covers 'client_error'
    'http_status_5xx': 'Errore server (5xx)', # Covers 'server_error'
    'no_canonical_tag': 'Tag Canonical mancante', # Covers 'missing_canonical'
    'missing_lang_attribute': 'Attributo Lingua mancante', # Covers 'missing_lang'
    'no_schema_markup': 'Markup Schema mancante', # Covers 'missing_schema'

    # Aliases/duplicates from existing list pointing to new preferred labels if functionality relies on old keys:
    'missing_meta': 'Meta description mancante', # Alias for 'missing_meta_description'
    'multiple_h1': 'Tag H1 multipli',          # Alias for 'multiple_h1_tags'
    # 'missing_alt_attr' already covered by user preference if key is 'missing_alt_attribute'
    # 'empty_alt_attr' already covered by user preference if key is 'empty_alt_attribute'
    'low_content': 'Conteggio parole basso', # Alias for 'low_word_count'
    'slow_page': 'Caricamento pagina lento',
    'large_page': 'Dimensioni HTML elevate',
    'missing_canonical': 'Tag Canonical mancante',
    'missing_lang': 'Attributo Lingua mancante',
    'missing_schema': 'Markup Schema mancante',
    'server_error': 'Errore server (5xx)',
    'client_error': 'Errore client (4xx)',

    # Existing labels for specific page lists (standardized where possible)
    'pages_without_title': 'Titolo mancante',
    'pages_without_meta': 'Meta description mancante',
    'missing_h1_pages': 'H1 mancante',
    'multiple_h1_pages': 'Tag H1 multipli',
    'images_without_alt': 'Attributo ALT mancante',
    'images_with_empty_alt': 'Attributo ALT vuoto',
    'images_without_title_attr': 'Attributo Title immagine mancante', # Kept specific "immagine" as it was distinct
    'images_with_empty_title_attr': 'Attributo Title immagine vuoto', # Kept specific "immagine"
    'low_word_count_pages': 'Conteggio parole basso',
    'large_html_pages': 'Dimensioni HTML elevate',
    'slow_pages': 'Caricamento pagina lento', # Note: This key 'slow_pages' is now an alias and also a page list key.
                                            # The PDF generator might use it for specific list reporting.
                                            # Value should be consistent.
    'status_4xx_pages': 'Errore client (4xx)',
    'status_5xx_pages': 'Errore server (5xx)',
    'pages_without_canonical': 'Tag Canonical mancante',
    'pages_without_lang': 'Attributo Lingua mancante',
    'pages_without_schema': 'Markup Schema mancante',

    # Fallback generici from existing (good to keep)
    'unknown_issue': 'Problema Sconosciuto',
    'unknown_type': 'Tipo Problema Non Specificato'
}

PDF_ISSUE_RECOMMENDATIONS = {
    # Errori Comuni (anche se le raccomandazioni principali potrebbero venire da analisi più specifiche)
    'missing_title': "Ogni pagina deve avere un tag title unico e descrittivo. È fondamentale per la SEO.",
    'duplicate_title': "Evita titoli duplicati. Ogni pagina necessita di un titolo unico per distinguersi nei risultati di ricerca.",
    'missing_meta_description': "Aggiungi una meta description univoca per ogni pagina. Questo testo appare nei risultati di ricerca e influenza il click-through rate.",
    'duplicate_meta': "Rendi uniche le meta description per ogni pagina. Descrizioni duplicate possono confondere i motori di ricerca.", # 'duplicate_meta_description' is often the key
    'duplicate_meta_descriptions': "Rendi uniche le meta description per ogni pagina. Descrizioni duplicate possono confondere i motori di ricerca.",
    'missing_h1': "Includi un tag H1 su ogni pagina per definirne l'argomento principale. Dovrebbe essere unico per pagina.",
    'broken_image': "Correggi i link delle immagini interrotte per migliorare l'esperienza utente e assicurare che i motori di ricerca possano indicizzarle.",
    'http_status_4xx': "Risolvi gli errori client (4xx). Assicurati che tutti i link interni puntino a risorse valide e considera di implementare redirect 301 per pagine permanentemente spostate.",
    'http_status_5xx': "Indaga e risolvi gli errori server (5xx). Questi problemi possono rendere il tuo sito inaccessibile a utenti e motori di ricerca.",
    'no_canonical_tag': "Implementa i tag canonical per specificare la versione preferita di una pagina, specialmente se hai contenuti duplicati o molto simili.",

    # Warnings (Problemi di media gravità)
    'short_title': "Allunga il titolo della pagina per includere parole chiave pertinenti e descrivere meglio il contenuto (ideale: 30-60 caratteri).",
    'long_title': "Accorcia il titolo della pagina per assicurarti che venga visualizzato correttamente nei risultati di ricerca (ideale: 30-60 caratteri).",
    'short_meta_description': "Espandi la meta description per fornire un riassunto più convincente e dettagliato del contenuto della pagina (ideale: 120-160 caratteri).",
    'long_meta_description': "Riduci la lunghezza della meta description per evitare che venga troncata nei risultati di ricerca (ideale: 120-160 caratteri).",
    'multiple_h1_tags': "Assicurati che ogni pagina abbia un solo tag H1, che dovrebbe rappresentare il titolo principale o l'argomento della pagina.",
    'low_word_count': "Aumenta la quantità di contenuto testuale sulla pagina per fornire più valore agli utenti e migliorare il ranking (minimo consigliato: 300 parole).",
    'low_text_html_ratio': "Incrementa la proporzione di testo effettivo rispetto al codice HTML sulla pagina. Rimuovi codice non necessario o aggiungi più contenuto testuale.",
    'slow_page_load': "Ottimizza la velocità di caricamento della pagina. Comprimi immagini, minimizza CSS/JS, usa la cache del browser e considera un hosting più performante.",
    'large_html_size': "Riduci le dimensioni del documento HTML. Ottimizza il codice, rimuovi commenti e spazi non necessari, e considera di spostare CSS/JS inline in file esterni.",
    'missing_lang_attribute': "Specifica la lingua principale del contenuto della pagina aggiungendo l'attributo 'lang' al tag <html> (es. <html lang=\"it\">).",
    'no_schema_markup': "Implementa lo schema markup (dati strutturati) per aiutare i motori di ricerca a comprendere meglio il contenuto della tua pagina e abilitare rich snippet.",

    # Notices (Ottimizzazioni e buone pratiche)
    'images_without_alt': "Aggiungi un testo alternativo (attributo ALT) descrittivo a tutte le immagini per migliorare l'accessibilità e la SEO.",
    'images_with_empty_alt': "Fornisci un testo alternativo significativo nell'attributo ALT delle immagini invece di lasciarlo vuoto, a meno che l'immagine sia puramente decorativa e non aggiunga contesto.",
    'images_without_title_attr': "Considera di aggiungere un attributo 'title' alle immagini se fornisce informazioni contestuali aggiuntive utili al passaggio del mouse (opzionale per SEO, più per UX).",
    'images_with_empty_title_attr': "Se usi l'attributo 'title' per le immagini, assicurati che contenga testo utile. Se non necessario, rimuovi l'attributo vuoto.",

    # Aggiunte basate su chiavi comuni da PDF_ISSUE_TYPE_LABELS
    'missing_h2': "Utilizza i tag H2 per strutturare le sezioni principali del tuo contenuto. Aiutano la leggibilità e la SEO.",
    'pages_without_title': "Assicurati che ogni pagina abbia un tag <title> univoco e descrittivo.", # Alias di missing_title
    'pages_without_meta': "Aggiungi una meta description a ogni pagina per migliorare la presentazione nei risultati di ricerca.", # Alias di missing_meta_description
    'missing_h1_pages': "Ogni pagina dovrebbe avere un tag H1 per indicare il suo argomento principale.", # Alias di missing_h1
    'multiple_h1_pages': "Utilizza un solo tag H1 per pagina. Titoli multipli H1 possono confondere i motori di ricerca.", # Alias di multiple_h1_tags
    'large_html_pages': "Riduci le dimensioni dell'HTML per le pagine indicate per migliorare i tempi di caricamento.", # Alias di large_html_size
    'slow_pages': "Ottimizza le pagine lente per migliorare l'esperienza utente e il ranking. Analizza le cause specifiche del rallentamento.", # Alias di slow_page_load
    'status_4xx_pages': "Correggi i link che portano a pagine con errori 4xx (es. Pagina Non Trovata) per migliorare l'esperienza utente.", # Alias di http_status_4xx
    'status_5xx_pages': "Risolvi gli errori server 5xx il prima possibile per garantire che le tue pagine siano accessibili.", # Alias di http_status_5xx
    'pages_without_canonical': "Aggiungi tag canonical alle pagine per indicare la versione preferita ed evitare problemi di contenuto duplicato.", # Alias di no_canonical_tag
    'pages_without_lang': "Definisci la lingua per ogni pagina usando l'attributo 'lang' nel tag <html>.", # Alias di missing_lang_attribute
    'pages_without_schema': "Considera l'aggiunta di dati strutturati (Schema.org) per migliorare come i motori di ricerca interpretano e visualizzano le tue pagine.", # Alias di no_schema_markup

    # General fallback recommendation
    'generic_seo_tip': "Consulta le linee guida per i webmaster e le best practice SEO per ottimizzare ulteriormente questo aspetto."
}

# Fattori di penalità per categoria di problemi nel calcolo del punteggio
CATEGORY_ISSUE_PENALTY_FACTORS = {
    'error': 1.0,    # Le problematiche classificate come 'error' hanno un impatto di penalità completo sul punteggio della categoria
    'warning': 0.20, # Le problematiche classificate come 'warning' hanno il 20% dell'impatto di penalità
    'notice': 0.02,  # Le problematiche classificate come 'notice' hanno il 2% dell'impatto di penalità
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

# Configurazioni Selenium
SELENIUM_CONFIG = {
    'headless': True,
    'chrome_options': ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1920x1080"],
    'window_size': [1920, 1080],
    'page_load_timeout': 30,
    'implicit_wait': 10,
}
