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
        'dark_gray': '#333333'
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
# Adjusted to include ocm_score and seo_audit_score
SEO_WEIGHTS = {
    'title_tags': 7,        # Previously 15
    'meta_descriptions': 5, # Previously 10
    'headings': 5,          # Previously 10
    'images_alt': 7,        # Previously 15
    'internal_links': 3,    # Previously 5
    'page_speed': 6,        # Previously 20
    'mobile_friendly': 2,   # Previously 10 (assuming some general check remains, or covered by detailed)
    'ssl_certificate': 1,   # Previously 5 (assuming some general check remains, or covered by detailed)
    'content_quality': 4,   # Previously 10 (partially covered by detailed checks like thin_content)
    'ocm_score': 30,        # New score from On-Page Content Model checks
    'seo_audit_score': 30,  # New score from SEO Audit checks
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

# Categorie dei controlli
CATEGORY_OCM = "OCM"
CATEGORY_SEO_AUDIT = "SEO_AUDIT"

# Livelli di impatto
IMPACT_ERROR = "ERRORI"
IMPACT_WARNING = "AVVERTIMENTI"
IMPACT_NOTICE = "AVVISI"

# Pesi preliminari per impatto
WEIGHT_HIGH = 10
WEIGHT_MEDIUM = 5
WEIGHT_LOW = 2

# Struttura dettagliata dei controlli SEO
DETAILED_SEO_CHECKS = {
    CATEGORY_OCM: {
        IMPACT_ERROR: [
            {"id": "ocm_missing_title", "description": "Tag title mancanti - Verifica presenza <title> in tutte le pagine", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_duplicate_title", "description": "Tag title duplicati - Identifica title identici tra pagine diverse", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_missing_meta_description", "description": "Meta description mancanti - Verifica presenza meta description in tutte le pagine", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_duplicate_meta_description", "description": "Meta description duplicate - Identifica meta description identiche tra pagine diverse", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_missing_h1", "description": "Tag H1 mancanti - Assicurati che ogni pagina abbia un H1", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_duplicate_h1", "description": "Tag H1 duplicati - Evita H1 identici su pagine diverse, se non giustificato", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_multiple_h1", "description": "Tag H1 multipli - Ogni pagina dovrebbe avere un solo H1", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_missing_alt_text", "description": "Attributi ALT mancanti nelle immagini - Verifica che tutte le immagini abbiano un ALT text descrittivo", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_broken_internal_links", "description": "Link interni rotti - Identifica e correggi link interni che portano a errori 404", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_broken_external_links", "description": "Link esterni rotti - Identifica e correggi link esterni che portano a errori 404", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_http_links_on_https", "description": "Link HTTP su pagine HTTPS (mixed content) - Assicurati che tutti i link siano HTTPS su pagine sicure", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_slow_page_load_speed", "description": "Velocità di caricamento pagina lenta - Ottimizza le pagine per migliorare i tempi di caricamento (es. >3s)", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_sitemap_not_found", "description": "File sitemap.xml non trovato - Verifica la presenza e accessibilità del file sitemap.xml", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_robots_txt_not_found", "description": "File robots.txt non trovato - Verifica la presenza e accessibilità del file robots.txt", "impact": "Medio", "weight": WEIGHT_MEDIUM},
        ],
        IMPACT_WARNING: [
            {"id": "ocm_title_too_short", "description": "Tag title troppo corti - Assicurati che i title siano sufficientemente descrittivi (es. <30 caratteri)", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_title_too_long", "description": "Tag title troppo lunghi - Evita title eccessivamente lunghi (es. >60 caratteri)", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_meta_description_too_short", "description": "Meta description troppo corte - Scrivi meta description più lunghe e informative (es. <120 caratteri)", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_meta_description_too_long", "description": "Meta description troppo lunghe - Riduci la lunghezza delle meta description (es. >160 caratteri)", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_h1_too_short", "description": "Tag H1 troppo corti o poco descrittivi - Rendi gli H1 più significativi", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "ocm_h1_too_long", "description": "Tag H1 troppo lunghi - Rendi gli H1 più concisi", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "ocm_low_text_to_html_ratio", "description": "Basso rapporto testo/HTML - Aumenta il contenuto testuale rispetto al codice HTML", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_images_too_large", "description": "Immagini troppo pesanti - Ottimizza le immagini per ridurre le dimensioni dei file (es. >100KB)", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_missing_hreflang_on_multilingual", "description": "Attributi hreflang mancanti (siti multilingua) - Implementa hreflang se il sito ha versioni in più lingue", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_incorrect_hreflang", "description": "Implementazione hreflang non corretta - Verifica la correttezza dei valori hreflang", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_no_image_compression", "description": "Immagini non compresse - Utilizza formati compressi (es. WebP) e tecniche di compressione", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_no_browser_caching", "description": "Caching del browser non specificato o inefficiente - Configura header di caching per risorse statiche", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_sitemap_not_updated", "description": "File sitemap.xml non aggiornato di recente - Assicurati che la sitemap sia aggiornata regolarmente", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "ocm_robots_txt_disallow_all", "description": "File robots.txt blocca l'intero sito (Disallow: /) - Verifica che non ci siano direttive che impediscono la scansione", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "ocm_robots_txt_too_restrictive", "description": "File robots.txt troppo restrittivo - Controlla che non blocchi risorse importanti per la scansione e l'indicizzazione", "impact": "Medio", "weight": WEIGHT_MEDIUM},
        ],
        IMPACT_NOTICE: [
            {"id": "ocm_h_tags_order_incorrect", "description": "Ordine gerarchico dei tag H (H1-H6) non rispettato - Segui una struttura logica per i titoli", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "ocm_internal_links_nofollow", "description": "Uso eccessivo di 'nofollow' su link interni - Rimuovi 'nofollow' se non strettamente necessario", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "ocm_no_favicon", "description": "Favicon mancante - Aggiungi una favicon per migliorare il branding", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "ocm_meta_keywords_used", "description": "Utilizzo del meta tag keywords (obsoleto) - Rimuovi il meta tag keywords, non più usato dai motori di ricerca", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "ocm_canonical_tag_missing", "description": "Canonical tag non specificato per pagine con contenuti simili/duplicati - Usa rel='canonical' per indicare la versione preferita", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "ocm_no_structured_data", "description": "Nessun dato strutturato (Schema.org) rilevato - Implementa dati strutturati per migliorare la comprensione del contenuto da parte dei motori di ricerca", "impact": "Basso", "weight": WEIGHT_LOW},
        ]
    },
    CATEGORY_SEO_AUDIT: {
        IMPACT_ERROR: [
            {"id": "seo_audit_google_index_issue", "description": "Problemi di indicizzazione su Google - Verifica 'site:tuodominio.com' e Google Search Console per pagine non indicizzate o errori", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_manual_actions_gsc", "description": "Azioni manuali in Google Search Console - Controlla GSC per eventuali penalizzazioni manuali", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_security_issues_gsc", "description": "Problemi di sicurezza in Google Search Console - Controlla GSC per avvisi di sicurezza (malware, phishing)", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_core_web_vitals_poor", "description": "Core Web Vitals con punteggio 'Scarso' (LCP, FID, CLS) - Ottimizza per migliorare i segnali vitali del web", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_mobile_usability_errors", "description": "Errori di usabilità mobile significativi in GSC - Correggi problemi che impattano l'esperienza mobile", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_main_keyword_not_in_title", "description": "Keyword principale non presente nel tag title - Includi la keyword target nel title", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_main_keyword_not_in_h1", "description": "Keyword principale non presente nel tag H1 - Includi la keyword target nell'H1", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_main_keyword_not_in_meta_description", "description": "Keyword principale non presente nella meta description - Includi la keyword target nella meta description", "impact": "Medio", "weight": WEIGHT_MEDIUM},
        ],
        IMPACT_WARNING: [
            {"id": "seo_audit_thin_content", "description": "Pagine con contenuto di bassa qualità o scarso (thin content) - Arricchisci il contenuto rendendolo utile e informativo", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_keyword_cannibalization", "description": "Cannibalizzazione delle keyword - Più pagine competono per la stessa keyword; consolida o differenzia", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "seo_audit_duplicate_content_across_domains", "description": "Contenuto duplicato su altri domini - Verifica se il tuo contenuto è copiato altrove senza permesso", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_poor_internal_linking_structure", "description": "Struttura di linking interno debole o poco ottimizzata - Migliora la distribuzione del link juice e la navigabilità", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "seo_audit_unnatural_backlink_profile", "description": "Profilo backlink innaturale o di bassa qualità (spammy links) - Analizza e rimuovi/disavow link tossici", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_http_active", "description": "Sito accessibile sia in HTTP che HTTPS senza redirect automatico a HTTPS - Imposta un redirect 301 da HTTP a HTTPS", "impact": "Alto", "weight": WEIGHT_HIGH},
            {"id": "seo_audit_www_non_www_inconsistent", "description": "Sito accessibile sia con WWW che senza WWW senza redirect sulla versione preferita - Scegli una versione e reindirizza l'altra", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "seo_audit_core_web_vitals_needs_improvement", "description": "Core Web Vitals con punteggio 'Da Migliorare' - Intervieni per ottimizzare LCP, FID, CLS", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "seo_audit_main_keyword_not_prominent_in_content", "description": "Keyword principale non sufficientemente prominente nel contenuto (es. non nelle prime 100 parole)", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "seo_audit_low_keyword_density", "description": "Densità della keyword principale troppo bassa - Assicurati che la keyword sia presente naturalmente nel testo", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "seo_audit_high_keyword_density", "description": "Densità della keyword principale troppo alta (keyword stuffing) - Evita un uso eccessivo e innaturale della keyword", "impact": "Medio", "weight": WEIGHT_MEDIUM},
        ],
        IMPACT_NOTICE: [
            {"id": "seo_audit_missing_xml_sitemap_in_gsc", "description": "Sitemap XML non inviata a Google Search Console - Invia la sitemap tramite GSC", "impact": "Medio", "weight": WEIGHT_MEDIUM},
            {"id": "seo_audit_robots_txt_not_in_gsc", "description": "File robots.txt non testato o inviato tramite GSC - Utilizza il tester di robots.txt in GSC", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "seo_audit_few_backlinks", "description": "Numero di backlink relativamente basso rispetto ai competitor - Sviluppa una strategia di link building", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "seo_audit_social_sharing_buttons_missing", "description": "Pulsanti di condivisione social mancanti o poco visibili - Facilita la condivisione dei contenuti", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "seo_audit_blog_not_active", "description": "Blog non presente o non aggiornato regolarmente - Considera un blog per content marketing e engagement", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "seo_audit_no_clear_cta", "description": "Call to Action (CTA) non chiare o mancanti nelle pagine chiave - Guida l'utente verso le conversioni", "impact": "Basso", "weight": WEIGHT_LOW},
            {"id": "seo_audit_local_seo_not_optimized", "description": "Scheda Google My Business non ottimizzata (se applicabile) - Cura la presenza su GMB per ricerche locali", "impact": "Medio", "weight": WEIGHT_MEDIUM},
        ]
    }
}
