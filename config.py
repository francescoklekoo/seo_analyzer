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

# Categorie Audit
CATEGORY_OCM = "OTTIMIZZAZIONE CODICE PER I MOTORI DI RICERCA (OCM)"
CATEGORY_SEO_AUDIT = "SITE SEO AUDIT"

# Configurazioni di crawling
CRAWL_CONFIG = {
    'max_pages': 50,  # Numero massimo di pagine da analizzare
    'timeout': 30,    # Timeout per le richieste HTTP
    'delay': 1,       # Delay tra le richieste (in secondi)
    'max_depth': 3,   # Profondità massima di crawling
    'follow_external': False,  # Se seguire link esterni
    'respect_robots': True,    # Se rispettare robots.txt
        'restrict_to_start_path': False  # NEW: Restrict crawl to the initial path (e.g., /it/, /en/)
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

# Soglie Core Web Vitals
CORE_WEB_VITALS_THRESHOLDS = {
    'LCP_ERROR': 4.0,  # secondi
    'LCP_GOOD': 2.5,   # secondi
    'INP_ERROR': 500,  # millisecondi
    'INP_GOOD': 200,   # millisecondi
    'CLS_ERROR': 0.25,
    'CLS_GOOD': 0.1
}

SERVER_RESPONSE_TIME_ERROR = 600  # millisecondi

TOUCH_ELEMENT_MIN_SIZE_PX = 44 # Dimensione minima elementi touch in px

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
        'left': 1.0,
        'right': 1.0,
        'top': 1.0,
        'bottom': 1.0
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

# Nuova classificazione Punteggio
NEW_SCORING_CLASSIFICATION = {
    'ERROR': (90, 100),    # Punteggio da 90 a 100 è ERRORE (es. 95% problemi trovati)
    'WARNING': (60, 89),   # Punteggio da 60 a 89 è WARNING
    'NOTICE': (20, 59)     # Punteggio da 20 a 59 è NOTICE
    # Sotto 20 potrebbe essere considerato 'GOOD' o non classificato come problema
}

# Configurazioni per segnali E-E-A-T e contenuti YMYL (da definire)
E_E_A_T_SIGNALS_CONFIG = {}
YMYL_CONTENT_CONFIG = {}


# CONFIGURAZIONE DETTAGLIATA DEI CHECK DI AUDIT
# Sostituisce e migliora PDF_ISSUE_TYPE_LABELS
AUDIT_CHECKS_CONFIG = {
    # OCM Checks
    'ocm_lcp_gt_4_error': { # Key kept from previous step, label and desc value updated
        'label': 'Largest Contentful Paint (LCP) > 4.0 secondi - Tempo di caricamento contenuto principale troppo lento',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_lcp_gt_4_error'
    },
    'ocm_inp_gt_500ms_error': { # Key renamed, label and desc value updated
        'label': 'Interaction to Next Paint (INP) > 500ms - Tempo di risposta alle interazioni utente eccessivo',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_inp_gt_500ms_error'
    },
    'ocm_cls_gt_025_error': { # Key renamed, label and desc value updated
        'label': 'Cumulative Layout Shift (CLS) > 0.25 - Spostamenti visivi imprevisti durante il caricamento',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_cls_gt_025_error'
    },
    'ocm_server_response_time_gt_600ms_error': { # Key renamed, label and desc value updated
        'label': 'Server Response Time > 600ms - Il server deve essere adeguatamente veloce',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_server_response_time_gt_600ms_error'
    },
    'ocm_assenza_cdn_siti_globali_error': { # Key renamed, label and desc value updated
        'label': 'Assenza CDN per siti globali - È importante utilizzare una CDN per le risorse del sito',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_assenza_cdn_siti_globali_error'
    },
    'ocm_assenza_implementazione_https_error': { # Key renamed, label updated
        'label': 'Assenza implementazione HTTPS - Il sito deve avere un certificato SSL valido',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_assenza_implementazione_https_error'
    },
    'ocm_certificato_ssl_scaduto_malconfigurato_error': { # Key renamed, label updated
        'label': 'Certificato SSL scaduto/malconfigurato - Il certificato SSL deve essere valido e configurato correttamente',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_certificato_ssl_scaduto_malconfigurato_error'
    },
    'ocm_problemi_mixed_content_error': { # Key renamed from ocm_mixed_content_warning, label updated, severity changed to ERROR
        'label': 'Problemi mixed content (HTTP/HTTPS) - Il sito non deve presentare contenuti misti http/https',
        'category': CATEGORY_OCM,
        'severity': 'ERROR', # Was WARNING
        'description_key': 'desc_ocm_problemi_mixed_content_error'
    },
    'ocm_malware_contenuto_compromesso_error': { # Key renamed, label updated
        'label': 'Malware o contenuto compromesso - Presenza di codice malevolo o contenuti dannosi',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_malware_contenuto_compromesso_error'
    },
    'ocm_risorse_critiche_bloccate_robots_txt_error': { # Key renamed, label updated
        'label': 'Risorse critiche bloccate in robots.txt - Il file robots.txt deve essere configurato adeguatamente',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_risorse_critiche_bloccate_robots_txt_error'
    },
    'ocm_problemi_gravi_javascript_seo_error': { # Key renamed, label updated
        'label': 'Problemi gravi JavaScript SEO - Contenuto JavaScript non accessibile ai motori di ricerca',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_problemi_gravi_javascript_seo_error'
    },
    'ocm_errori_critici_xml_sitemap_error': { # Key renamed, label updated
        'label': 'Errori critici XML sitemap - È necessario creare e inviare una sitemap XML in Google Search Console',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_errori_critici_xml_sitemap_error'
    },
    'ocm_problemi_canonical_tag_gravi_error': { # Key renamed, label updated
        'label': 'Problemi canonical tag gravi - Il meta tag canonical deve essere configurato adeguatamente; il sito non deve essere indicizzato con www e senza www',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_problemi_canonical_tag_gravi_error'
    },
    'ocm_pagine_http_404_500_error': { # New entry
        'label': 'Pagine con codice di stato HTTP 404 o 500 - Le pagine 404 devono essere verificate e ottimizzate',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_pagine_http_404_500_error'
    },
    # Existing specific 404 and 500 error checks are kept for now.
    'ocm_http_404_errors_extensive_error': { # No changes to this, kept for its specificity
        'label': 'Errori 404 estensivi (link interni rotti)',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_http_404_errors_extensive_error'
    },
    'ocm_http_500_errors_error': { # No changes to this, kept for its specificity
        'label': 'Errori Server (5xx) frequenti o diffusi',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_http_500_errors_error'
    },
    'ocm_structured_data_errors_warning': { # Label updated
        'label': "Structured data errors - Errori nell'implementazione dei dati strutturati",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_structured_data_errors_warning'
    },
    'ocm_redirect_chains_warning': { # Label updated
        'label': "Redirect chains > 3 hop - Catene di reindirizzamento troppo lunghe",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_redirect_chains_warning'
    },
    'ocm_meta_description_missing_notice': { # Label updated
        'label': "Meta description mancanti - Verificare pagine con meta description mancanti",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_meta_description_missing_notice'
    },
    'ocm_css_js_non_utilizzato_notice': { # New entry
        'label': "CSS/JS non utilizzato - Presenza di codice CSS/JavaScript inutilizzato",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_css_js_non_utilizzato_notice'
    },
    'ocm_font_loading_non_ottimizzato_notice': { # New entry
        'label': "Font loading non ottimizzato - Caricamento dei font non ottimizzato",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_font_loading_non_ottimizzato_notice'
    },
    'ocm_third_party_scripts_non_ottimizzati_notice': { # New entry
        'label': "Third-party scripts non ottimizzati - Script di terze parti non ottimizzati",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_third_party_scripts_non_ottimizzati_notice'
    },
    'ocm_dns_lookup_optimization_notice': { # New entry
        'label': "DNS lookup optimization - Ottimizzazione delle ricerche DNS",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_dns_lookup_optimization_notice'
    },
    'ocm_verifiche_url_parlanti_notice': { # New entry
        'label': "Verifiche URL parlanti - Verificare URL parlanti",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_verifiche_url_parlanti_notice'
    },
    'ocm_utilizzo_direttive_noindex_notice': { # New entry
        'label': "Utilizzo direttive noindex - Verificare che le direttive noindex siano utilizzate adeguatamente",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_utilizzo_direttive_noindex_notice'
    },
    'ocm_utilizzo_attributo_alt_immagini_notice': { # New entry
        'label': "Utilizzo attributo ALT immagini - Verificare l'utilizzo dell'attributo ALT per descrivere le immagini",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_utilizzo_attributo_alt_immagini_notice'
    },
    'ocm_dati_strutturati_implementazione_notice': { # New entry
        'label': "Dati strutturati implementazione - Utilizzare dati strutturati per descrivere meglio i contenuti delle pagine web",
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_dati_strutturati_implementazione_notice'
    },
    # Performance Critica ERROR Checks (formerly part of Added OCM ERROR Checks)
    'ocm_risorse_render_blocking_critiche_error': { # Key renamed, label updated
        'label': 'Risorse render-blocking critiche - Elementi che bloccano il rendering della pagina',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_risorse_render_blocking_critiche_error'
    },
    'ocm_assenza_compressione_sito_web_error': { # Key renamed, label updated
        'label': 'Assenza compressione sito web - Il sito web deve utilizzare un sistema di compressione',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_assenza_compressione_sito_web_error'
    },
    'ocm_mancata_implementazione_http2_error': { # Key renamed, label updated
        'label': 'Mancata implementazione HTTP/2 - Il sito web deve utilizzare HTTP/2',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_mancata_implementazione_http2_error'
    },
    'ocm_sistema_cache_inadeguato_error': { # Key renamed, label updated
        'label': 'Sistema di cache inadeguato - Il sito web deve utilizzare un sistema di cache',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_sistema_cache_inadeguato_error'
    },
    'ocm_minificazione_css_js_mancante_error': { # Key renamed, label updated, description_key corrected
        'label': 'Minificazione CSS e JS mancante - Il sito deve utilizzare la minificazione sui file CSS e JS',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_minificazione_css_js_mancante_error' # Corrected
    },
    # Ottimizzazione Immagini ERROR Checks
    'ocm_immagini_non_ottimizzate_web_error': { # Key renamed, label updated
        'label': 'Immagini non ottimizzate per web - Le immagini caricate sul sito devono essere ottimizzate per il web',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_immagini_non_ottimizzate_web_error'
    },
    'ocm_assenza_lazy_loading_immagini_error': { # Key renamed, label updated
        'label': 'Assenza lazy loading immagini - Deve essere utilizzato il caricamento differito delle immagini fuori dallo schermo (Lazy loading)',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_assenza_lazy_loading_immagini_error'
    },
    # Mobile-First Indexing ERROR Checks
    'ocm_contenuto_non_accessibile_mobile_error': { # Key renamed, label updated
        'label': 'Contenuto non accessibile su mobile - Tutti i contenuti devono essere fruibili da mobile',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_contenuto_non_accessibile_mobile_error'
    },
    'ocm_assenza_tag_viewport_error': { # Key renamed, label updated
        'label': 'Assenza tag viewport - Meta tag viewport mancante per responsive design',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_assenza_tag_viewport_error'
    },
    'ocm_touch_elements_lt_44px_error': { # Key renamed, label updated
        'label': "Touch elements < 44px - Elementi touch troppo piccoli per l'interazione mobile",
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_touch_elements_lt_44px_error'
    },
    'ocm_sito_non_mobile_friendly_error': { # Key renamed, label updated
        'label': 'Sito non mobile-friendly - Il sito deve essere mobile friendly',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_sito_non_mobile_friendly_error'
    },
    # OCM WARNING CHECKS (Labels updated for Technical SEO warnings)
    'ocm_unnecessary_redirects_warning': { # Label updated
        'label': "Reindirizzamenti inutili - I reindirizzamenti inutili devono essere eliminati",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_unnecessary_redirects_warning'
    },
    'ocm_url_structure_suboptimal_warning': { # Label updated
        'label': "URL structure non ottimizzata - Le URL devono essere \"parlanti\"",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_url_structure_suboptimal_warning'
    },
    'ocm_hsts_missing_warning': { # Label updated
        'label': "Assenza HSTS - Header di sicurezza HSTS mancante",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_hsts_missing_warning'
    },
    'ocm_csp_missing_warning': { # Label updated
        'label': "Content Security Policy mancante - Policy di sicurezza dei contenuti non implementata",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_csp_missing_warning'
    },
    'ocm_x_frame_options_missing_warning': { # Label updated
        'label': "Assenza X-Frame-Options - Header di protezione da clickjacking mancante",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_x_frame_options_missing_warning'
    },
    'ocm_404_errors_excessive_warning': { # Label updated
        'label': "404 errors eccessivi - Le pagine 404 devono essere verificate e ottimizzate",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_404_errors_excessive_warning'
    },
    'ocm_broken_internal_links_warning': { # Label updated
        'label': "Broken links interni - I link interni rotti devono essere corretti",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_broken_internal_links_warning'
    },
    'ocm_internal_linking_insufficient_warning': { # Label updated
        'label': "Internal linking insufficiente - Collegamento interno tra pagine inadeguato",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_internal_linking_insufficient_warning'
    },
    'ocm_gestione_url_meta_inadeguata_warning': { # New entry
        'label': "Gestione URL e Meta inadeguata - La gestione URL e Meta deve essere implementata lato codice",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_gestione_url_meta_inadeguata_warning'
    },
    'ocm_sistema_controllo_uptime_mancante_warning': { # New entry
        'label': "Sistema controllo uptime mancante - Deve essere utilizzato un sistema di controllo uptime",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_sistema_controllo_uptime_mancante_warning'
    },
    # Keeping existing related checks
    'ocm_meta_tags_inconsistent_warning': {
        'label': 'Strategia meta tag (title/description) inconsistente tra pagine',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_meta_tags_inconsistent_warning'
    },
    'ocm_url_strategy_inconsistent_warning': {
        'label': 'Strategia URL (es. trailing slash, case) inconsistente',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_url_strategy_inconsistent_warning'
    },
    'ocm_hreflang_errors_warning': {
        'label': 'Errori implementazione hreflang (non critici)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_hreflang_errors_warning'
    },
    'ocm_website_uptime_low_warning': { # Keeping this as it's different from missing control system
        'label': 'Uptime del sito web storicamente basso (richiede monitoraggio esterno)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_website_uptime_low_warning'
    },
    'ocm_ga_gsc_not_configured_warning': { # General existing check
        'label': 'Google Analytics o Google Search Console non configurati/collegati',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_ga_gsc_not_configured_warning'
    },
    'ocm_ga_non_configurato_sito_warning': { # New entry
        'label': "Google Analytics non configurato sul sito - Google Analytics deve essere configurato sul sito",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_ga_non_configurato_sito_warning'
    },
    'ocm_ga_non_collegato_progetto_warning': { # New entry
        'label': "Google Analytics non collegato al progetto - Google Analytics deve essere collegato al progetto",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_ga_non_collegato_progetto_warning'
    },
    'ocm_gsc_non_configurato_warning': { # New entry
        'label': "Google Search Console non configurato - Google Search Console deve essere configurata",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_gsc_non_configurato_warning'
    },
    'ocm_gsc_non_collegato_progetto_warning': { # New entry
        'label': "Google Search Console non collegato al progetto - Google Search Console deve essere collegata al progetto",
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_gsc_non_collegato_progetto_warning'
    },
    # Note: 'ocm_structured_data_errors_warning' and 'ocm_redirect_chains_warning' should exist from previous steps.
    # 'ocm_mixed_content_warning' was moved and changed to 'ocm_problemi_mixed_content_error'

    # SITE SEO AUDIT Checks
    # Existing ones verified/modified:
    'seo_no_eeat_signals_error': { # Renamed from seo_no_eeat_error
        'label': 'Assenza o carenza segnali E-E-A-T per contenuti rilevanti',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_no_eeat_signals_error' # Updated description key
    },
    'seo_low_quality_ymyl_error': { # Verified
        'label': 'Contenuti YMYL di bassa qualità o non autorevoli',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_low_quality_ymyl_error'
    },
    'seo_extensive_duplicate_content_error': { # Verified
        'label': 'Contenuti duplicati estensivi interni/esterni',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_extensive_duplicate_content_error'
    },
    # 'seo_title_missing_error' is now part of 'seo_title_meta_missing_duplicated_error'
    'seo_keyword_stuffing_error': { # Verified
        'label': 'Keyword stuffing evidente nel contenuto',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_keyword_stuffing_error'
    },
    # New SITE SEO AUDIT ERROR Checks:
    'seo_thin_content_pages_error': {
        'label': 'Pagine con contenuto scarso (thin content)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_thin_content_pages_error'
    },
    'seo_page_titles_not_optimized_error': {
        'label': 'Titoli pagina non ottimizzati (non unici, non descrittivi)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_page_titles_not_optimized_error'
    },
    'seo_meta_descriptions_not_optimized_error': {
        'label': 'Meta descriptions non ottimizzate (non uniche, non persuasive)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_meta_descriptions_not_optimized_error'
    },
    'seo_no_clear_seo_strategy_error': {
        'label': 'Mancanza di una chiara strategia SEO (obiettivi, target, keyword)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_no_clear_seo_strategy_error'
    },
    'seo_outdated_content_error': {
        'label': 'Contenuti obsoleti o non aggiornati su temi importanti',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_outdated_content_error'
    },
    'seo_keyword_cannibalization_error': {
        'label': 'Cannibalizzazione delle keyword tra più pagine',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_keyword_cannibalization_error'
    },
    'seo_seasonal_keywords_missed_error': {
        'label': 'Mancata ottimizzazione per keyword stagionali rilevanti',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_seasonal_keywords_missed_error'
    },
    'seo_toxic_backlinks_error': {
        'label': 'Presenza significativa di backlink tossici o spam',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_toxic_backlinks_error'
    },
    'seo_poor_internal_linking_strategy_error': {
        'label': 'Strategia di internal linking carente o inefficace',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_poor_internal_linking_strategy_error'
    },
    'seo_anchor_text_not_optimized_error': {
        'label': 'Anchor text dei link interni non ottimizzati',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_anchor_text_not_optimized_error'
    },
    'seo_gsc_critical_errors_unresolved_error': {
        'label': 'Errori critici non risolti in Google Search Console',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_gsc_critical_errors_unresolved_error'
    },
    'seo_title_meta_missing_duplicated_error': {
        'label': 'Titoli o Meta Description mancanti o duplicati',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_title_meta_missing_duplicated_error'
    },
    'seo_title_too_long_error': {
        'label': f"Titolo pagina troppo lungo (> {SEO_CONFIG['title_max_length']} caratteri)",
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_title_too_long_error'
    },
    'seo_meta_desc_bad_length_error': {
        'label': f"Meta Description con lunghezza non ottimale (< {SEO_CONFIG['meta_description_min_length']} o > {SEO_CONFIG['meta_description_max_length']} caratteri)",
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'ERROR',
        'description_key': 'desc_seo_meta_desc_bad_length_error'
    },
    # Existing WARNING/NOTICE for SEO Audit
    'seo_inconsistent_header_structure_warning': {
        'label': 'Struttura degli header (H1-H6) inconsistente o non gerarchica',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'WARNING',
        'description_key': 'desc_seo_inconsistent_header_structure_warning'
    },
    'seo_author_bylines_missing_warning': {
        'label': 'Author bylines (autori) mancanti per contenuti informativi/YMYL',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'WARNING',
        'description_key': 'desc_seo_author_bylines_missing_warning'
    },
    'seo_social_sharing_notice': {
        'label': 'Contenuti non facilmente condivisibili sui social media',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_social_sharing_notice'
    },
    'seo_gmb_not_optimized_notice': { # Se applicabile (es. per business locali)
        'label': 'Profilo Google My Business non ottimizzato o incompleto',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_gmb_not_optimized_notice'
    },
    # New SITE SEO AUDIT NOTICE Checks
    'seo_faq_schema_missing_notice': {
        'label': 'FAQ Schema mancante per pagine Q&A',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_faq_schema_missing_notice'
    },
    'seo_howto_schema_missing_notice': {
        'label': 'HowTo Schema mancante per guide/tutorial',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_howto_schema_missing_notice'
    },
    'seo_video_schema_missing_notice': {
        'label': 'Video Schema mancante per contenuti video',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_video_schema_missing_notice'
    },
    'seo_event_schema_missing_notice': {
        'label': 'Event Schema mancante per eventi',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_event_schema_missing_notice'
    },
    'seo_localbusiness_schema_missing_notice': {
        'label': 'LocalBusiness Schema mancante (se attività locale)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_localbusiness_schema_missing_notice'
    },
    'seo_product_schema_missing_notice': {
        'label': 'Product Schema mancante per schede prodotto e-commerce',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_product_schema_missing_notice'
    },
    'seo_review_schema_missing_notice': {
        'label': 'Review Schema mancante per recensioni',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_review_schema_missing_notice'
    },
    'seo_internal_search_ux_poor_notice': {
        'label': 'Esperienza utente della ricerca interna sito scarsa',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_internal_search_ux_poor_notice'
    },
    'seo_blog_category_tags_suboptimal_notice': {
        'label': 'Categorie e tag del blog non ottimizzati',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_blog_category_tags_suboptimal_notice'
    },
    'seo_pagination_seo_issues_notice': {
        'label': 'Paginazione con potenziali problemi SEO (es. no rel prev/next)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_pagination_seo_issues_notice'
    },
    'seo_faceted_navigation_seo_issues_notice': {
        'label': 'Navigazione a faccette con potenziali problemi SEO',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_faceted_navigation_seo_issues_notice'
    },
    'seo_website_accessibility_basic_review_notice': {
        'label': 'Revisione base accessibilità sito (es. contrasto, navigazione tastiera)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_website_accessibility_basic_review_notice'
    },
    'seo_privacy_policy_cookie_notice_review_notice': {
        'label': 'Revisione Privacy Policy e Cookie Notice per completezza/trasparenza',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_privacy_policy_cookie_notice_review_notice'
    },
    'seo_terms_conditions_review_notice': {
        'label': 'Revisione Termini e Condizioni per chiarezza',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_terms_conditions_review_notice'
    },
    'seo_user_engagement_signals_low_notice': {
        'label': 'Segnali di user engagement bassi (alta bounce rate, basso tempo su pagina)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_user_engagement_signals_low_notice'
    },
    'seo_conversion_rate_tracking_notice': {
        'label': 'Tracciamento conversioni (goal) non impostato o incompleto',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_conversion_rate_tracking_notice'
    },
    'seo_regular_seo_audits_missing_notice': {
        'label': 'Mancanza di audit SEO regolari pianificati',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_regular_seo_audits_missing_notice'
    },
    'seo_seo_kpi_monitoring_absent_notice': {
        'label': 'Mancato monitoraggio KPI SEO fondamentali',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_seo_kpi_monitoring_absent_notice'
    },
    'seo_core_web_vitals_monitoring_notice': {
        'label': 'Monitoraggio Core Web Vitals non attivo (es. via GSC)',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_core_web_vitals_monitoring_notice'
    },
    'seo_backlink_profile_growth_slow_notice': {
        'label': 'Crescita profilo backlink lenta o stagnante',
        'category': CATEGORY_SEO_AUDIT,
        'severity': 'NOTICE',
        'description_key': 'desc_seo_backlink_profile_growth_slow_notice'
    }
}

# DESCRIZIONI E CONSIGLI PER IL PDF (basate su description_key da AUDIT_CHECKS_CONFIG)
# Sostituisce e migliora PDF_ISSUE_RECOMMENDATIONS
PDF_ISSUE_DESCRIPTIONS = {
    # OCM Descriptions
    'desc_ocm_lcp_gt_4_error': "Largest Contentful Paint (LCP) > 4.0 secondi. Indica che il tempo di caricamento del contenuto principale della pagina è troppo lento. Ottimizzare le immagini, il codice JavaScript/CSS critico e le risorse del server per migliorare questa metrica fondamentale per l'esperienza utente e il ranking.",
    'desc_ocm_inp_gt_500ms_error': "Interaction to Next Paint (INP) > 500ms. Segnala che il tempo di risposta della pagina alle interazioni dell'utente (click, tap, input da tastiera) è eccessivo. Ottimizzare il codice JavaScript, ridurre il carico del thread principale e migliorare l'efficienza degli script per garantire una reattività rapida.",
    'desc_ocm_cls_gt_025_error': "Cumulative Layout Shift (CLS) > 0.25. Indica la presenza di spostamenti visivi imprevisti degli elementi della pagina durante il caricamento, peggiorando l'esperienza utente. Specificare le dimensioni per immagini e video, gestire dinamicamente i contenuti e precaricare i font per migliorare la stabilità visuale.",
    'desc_ocm_server_response_time_gt_600ms_error': "Server Response Time > 600ms. Il tempo di risposta del server (TTFB) è troppo alto, indicando che il server non è adeguatamente veloce. Ottimizzare le query del database, implementare un sistema di caching efficace, considerare un upgrade del server o scegliere un provider hosting più performante.",
    'desc_ocm_assenza_cdn_siti_globali_error': "Assenza CDN per siti globali. Segnala che non viene utilizzata una Content Delivery Network (CDN), importante per siti con traffico globale. Implementare una CDN per distribuire le risorse del sito (immagini, CSS, JS) su server geograficamente più vicini agli utenti, riducendo la latenza e migliorando i tempi di caricamento.",
    'desc_ocm_assenza_implementazione_https_error': "Assenza implementazione HTTPS. Indica che il sito non utilizza HTTPS, esponendo i dati degli utenti a rischi. È cruciale installare un certificato SSL valido e configurare il server per forzare HTTPS su tutte le connessioni per garantire sicurezza, fiducia e migliorare il ranking.",
    'desc_ocm_certificato_ssl_scaduto_malconfigurato_error': "Certificato SSL scaduto/malconfigurato. Segnala che il certificato SSL del sito è scaduto, non valido o malconfigurato, compromettendo la sicurezza. Rinnovare immediatamente il certificato SSL e assicurarsi che sia installato e configurato correttamente per tutte le varianti del dominio.",
    'desc_ocm_problemi_mixed_content_error': "Problemi mixed content (HTTP/HTTPS). Indica che la pagina HTTPS carica risorse (immagini, script, CSS) tramite HTTP non sicuro, creando vulnerabilità. Identificare e aggiornare tutti i link a risorse interne ed esterne affinché utilizzino HTTPS.",
    'desc_ocm_malware_contenuto_compromesso_error': "Malware o contenuto compromesso. Rilevata possibile presenza di codice malevolo o contenuti dannosi sul sito. Effettuare una scansione completa del sito, rimuovere immediatamente qualsiasi malware o codice sospetto e mettere in sicurezza il sito per proteggere gli utenti e la reputazione.",
    'desc_ocm_risorse_critiche_bloccate_robots_txt_error': "Risorse critiche bloccate in robots.txt. Indica che il file robots.txt impedisce ai motori di ricerca di accedere a risorse cruciali (come CSS o JavaScript) per la corretta visualizzazione e interpretazione del sito. Rivedere le direttive in robots.txt per assicurarsi che non blocchino file necessari al rendering.",
    'desc_ocm_problemi_gravi_javascript_seo_error': "Problemi gravi JavaScript SEO. Segnala che contenuti importanti generati tramite JavaScript potrebbero non essere accessibili o indicizzabili dai motori di ricerca. Assicurarsi che il rendering lato client (CSR) sia gestito correttamente, considerare il rendering lato server (SSR) o il rendering dinamico per contenuti critici.",
    'desc_ocm_errori_critici_xml_sitemap_error': "Errori critici XML sitemap. Indica errori gravi nella sitemap XML (es. formato non valido, URL errati o non raggiungibili) che ne compromettono l'utilità. Correggere la sitemap, assicurarsi che sia aggiornata e inviarla tramite Google Search Console per facilitare la scoperta dei contenuti.",
    'desc_ocm_problemi_canonical_tag_gravi_error': "Problemi canonical tag gravi. Segnala errori significativi nell'uso dei tag canonical (es. loop di canonical, puntamento a URL non indicizzabili, o a versioni multiple del sito come www e non-www). Verificare e correggere l'implementazione dei tag canonical per consolidare i segnali di ranking e prevenire problemi di contenuto duplicato.",
    'desc_ocm_pagine_http_404_500_error': "Pagine con codice di stato HTTP 404 o 500. Rilevazione di pagine che restituiscono errori 404 (Non Trovato) o 500 (Errore Interno del Server). Verificare l'origine di questi errori, correggere i link interni rotti, ripristinare le pagine mancanti o implementare redirect 301 per quelle permanentemente spostate. Per gli errori 500, investigare i log del server.",
    'desc_ocm_http_404_errors_extensive_error': "Un numero elevato di errori 404 (Pagina Non Trovata) per link interni indica problemi di manutenzione e peggiora l'esperienza utente e il crawl budget.", # Kept specific
    'desc_ocm_http_500_errors_error': "Errori Server (5xx) frequenti o diffusi indicano problemi infrastrutturali seri che rendono il sito inaccessibile e danneggiano la SEO.", # Kept specific
    'desc_ocm_structured_data_errors_warning': "Structured data errors - Errori nell'implementazione dei dati strutturati",
    'desc_ocm_redirect_chains_warning': "Redirect chains > 3 hop - Catene di reindirizzamento troppo lunghe",
    'desc_ocm_meta_description_missing_notice': "Meta description mancanti. Alcune pagine del sito non hanno una meta description. Scrivere meta description uniche e persuasive per ogni pagina importante per migliorare il Click-Through Rate (CTR) dai risultati di ricerca.",
    'desc_ocm_css_js_non_utilizzato_notice': "CSS/JS non utilizzato. Rilevata la presenza di codice CSS o JavaScript non utilizzato che appesantisce inutilmente le pagine. Rimuovere il codice inutilizzato per ridurre le dimensioni dei file e migliorare i tempi di caricamento.",
    'desc_ocm_font_loading_non_ottimizzato_notice': "Font loading non ottimizzato. Il caricamento dei web font potrebbe non essere ottimale, causando ritardi nel rendering del testo (FOIT/FOUT). Utilizzare strategie come `font-display: swap`, preloading dei font critici o formati moderni (WOFF2) per migliorare le performance.",
    'desc_ocm_third_party_scripts_non_ottimizzati_notice': "Third-party scripts non ottimizzati. Script di terze parti (es. analytics, social media, advertising) potrebbero impattare negativamente le performance. Valutare la necessità di ogni script, caricarli in modo asincrono o differito, e ove possibile, ospitarli localmente o utilizzare versioni più leggere.",
    'desc_ocm_dns_lookup_optimization_notice': "DNS lookup optimization. Le risoluzioni DNS per domini di terze parti possono aggiungere latenza. Utilizzare tecniche come `dns-prefetch` o `preconnect` per risolvere in anticipo i DNS di risorse critiche esterne e ridurre i tempi di attesa.",
    'desc_ocm_verifiche_url_parlanti_notice': "Verifiche URL parlanti. Assicurarsi che gli URL siano 'parlanti', ovvero descrittivi, facili da leggere per gli utenti e che includano keyword rilevanti. Evitare URL con parametri eccessivi o stringhe incomprensibili.",
    'desc_ocm_utilizzo_direttive_noindex_notice': "Utilizzo direttive noindex. Verificare che le direttive `noindex` (meta tag o X-Robots-Tag) siano usate correttamente per impedire l'indicizzazione di pagine non desiderate (es. contenuti duplicati, pagine di servizio). Un uso errato può escludere pagine importanti.",
    'desc_ocm_utilizzo_attributo_alt_immagini_notice': "Utilizzo attributo ALT immagini. Assicurarsi che tutte le immagini significative abbiano un attributo ALT descrittivo. Questo migliora l'accessibilità per utenti con screen reader e fornisce contesto ai motori di ricerca.",
    'desc_ocm_dati_strutturati_implementazione_notice': "Dati strutturati implementazione. Considerare l'utilizzo di dati strutturati (Schema.org) per descrivere meglio i vari tipi di contenuto nelle pagine web (articoli, prodotti, eventi, etc.). Questo può aiutare a ottenere rich snippet nei risultati di ricerca e migliorare la comprensione da parte dei motori.",
    # Descriptions for Performance Critica ERROR Checks and others previously in this block
    'desc_ocm_risorse_render_blocking_critiche_error': "Risorse render-blocking critiche. Identifica elementi (solitamente script o fogli di stile) che bloccano il rendering iniziale della pagina, peggiorando i tempi di caricamento percepiti. Differire il caricamento di JS/CSS non critico, minificare le risorse e utilizzare il caricamento asincrono.",
    'desc_ocm_assenza_compressione_sito_web_error': "Assenza compressione sito web. Il sito non utilizza sistemi di compressione (come Gzip o Brotli) per le risorse testuali (HTML, CSS, JS). Abilitare la compressione a livello server per ridurre le dimensioni dei file trasferiti e migliorare la velocità di caricamento.",
    'desc_ocm_mancata_implementazione_http2_error': "Mancata implementazione HTTP/2. Il sito non utilizza il protocollo HTTP/2 (o HTTP/3), che offre miglioramenti prestazionali rispetto a HTTP/1.1. Verificare con il provider hosting la disponibilità di HTTP/2 e abilitarlo per beneficiare di funzionalità come multiplexing e server push.",
    'desc_ocm_sistema_cache_inadeguato_error': "Sistema di cache inadeguato. Le policy di caching del browser per le risorse statiche non sono ottimali o sono assenti. Configurare correttamente gli header HTTP di caching (es. Cache-Control, Expires) per istruire il browser a memorizzare le risorse localmente, riducendo i tempi di caricamento per visite successive.",
    'desc_ocm_minificazione_css_js_mancante_error': "Minificazione CSS e JS mancante. I file CSS e JavaScript non sono minificati, aumentando inutilmente le loro dimensioni. Implementare processi di minificazione per rimuovere caratteri non necessari (spazi, commenti) dal codice e ridurre i tempi di download.",
    # Descriptions for Ottimizzazione Immagini ERROR Checks
    'desc_ocm_immagini_non_ottimizzate_web_error': "Immagini non ottimizzate per web. Segnala che le immagini sul sito non sono adeguatamente ottimizzate (es. dimensioni eccessive, formati non moderni come WebP). Comprimere le immagini, scegliere formati appropriati e utilizzare dimensioni responsive per ridurre il peso delle pagine e migliorare la velocità di caricamento.",
    'desc_ocm_assenza_lazy_loading_immagini_error': "Assenza lazy loading immagini. Indica che non è implementato il caricamento differito (lazy loading) per le immagini 'offscreen' (non visibili senza scroll). Implementare il lazy loading per le immagini per migliorare il tempo di caricamento iniziale della pagina e risparmiare banda.",
    # Descriptions for Mobile-First Indexing ERROR Checks
    'desc_ocm_contenuto_non_accessibile_mobile_error': "Contenuto non accessibile su mobile. Indica che alcuni contenuti importanti del sito non sono facilmente accessibili o visibili su dispositivi mobili. Assicurare che tutti i contenuti siano responsive e che l'esperienza utente sia ottimale su mobile, in linea con il mobile-first indexing di Google.",
    'desc_ocm_assenza_tag_viewport_error': "Assenza tag viewport. Manca il meta tag viewport nella `<head>` delle pagine, essenziale per un responsive design corretto. Inserire `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">` per garantire che la pagina si adatti correttamente alle dimensioni dello schermo dei dispositivi mobili.",
    'desc_ocm_touch_elements_lt_44px_error': "Touch elements < 44px. Alcuni elementi interattivi (pulsanti, link) sono troppo piccoli o ravvicinati, rendendo difficile l'interazione su dispositivi touch. Aumentare le dimensioni degli elementi touch ad almeno 44x44 pixel e garantire una spaziatura adeguata.",
    'desc_ocm_sito_non_mobile_friendly_error': "Sito non mobile-friendly. Il design generale del sito non è ottimizzato per i dispositivi mobili, offrendo un'esperienza utente scadente. Adottare un design responsive o adattivo, testare la mobile-friendliness con gli strumenti di Google e migliorare la navigazione e la leggibilità su schermi piccoli.",
    # Descriptions for OCM WARNING Checks - Values updated to new labels
    'desc_ocm_unnecessary_redirects_warning': "Reindirizzamenti inutili. Identificati reindirizzamenti non strettamente necessari (es. da HTTP a HTTPS per link interni già HTTPS, o da URL con/senza trailing slash se gestiti in modo incoerente). Eliminare questi passaggi superflui per migliorare la velocità e l'efficienza del crawling.",
    'desc_ocm_url_structure_suboptimal_warning': "URL structure non ottimizzata. La struttura degli URL potrebbe non essere ottimale per la SEO e l'usabilità (es. parametri eccessivi, URL non descrittive). Creare URL chiare, concise e \"parlanti\", che includano keyword rilevanti e riflettano la gerarchia del sito.",
    'desc_ocm_hsts_missing_warning': "Assenza HSTS. Manca l'header HTTP Strict Transport Security (HSTS), che protegge da attacchi di tipo man-in-the-middle. Implementare HSTS per forzare il browser a comunicare con il server esclusivamente tramite HTTPS.",
    'desc_ocm_csp_missing_warning': "Content Security Policy mancante. Non è implementata una Content Security Policy (CSP) o quella esistente è troppo permissiva. Definire una CSP robusta per controllare le risorse che la pagina può caricare, mitigando rischi come XSS.",
    'desc_ocm_x_frame_options_missing_warning': "Assenza X-Frame-Options. Manca l'header X-Frame-Options (o una direttiva CSP equivalente), esponendo il sito a rischi di clickjacking. Implementare X-Frame-Options (es. DENY o SAMEORIGIN) per impedire che il sito venga incorporato in frame non autorizzati.",
    'desc_ocm_404_errors_excessive_warning': "404 errors eccessivi. Presenza di un numero elevato di errori 404 (Pagina Non Trovata). Verificare l'origine di questi link rotti (interni o esterni) e correggerli o implementare redirect 301 se le pagine sono state spostate permanentemente. Ottimizzare la pagina 404 personalizzata.",
    'desc_ocm_broken_internal_links_warning': "Broken links interni. Rilevati link interni che puntano a pagine non esistenti (errore 404). Correggere questi link per migliorare l'esperienza utente e la distribuzione del link equity.",
    'desc_ocm_internal_linking_insufficient_warning': "Internal linking insufficiente. Un collegamento interno tra pagine inadeguato può rendere difficile per utenti e motori di ricerca scoprire contenuti importanti. Migliorare la strategia di internal linking per distribuire meglio il 'link juice'.",
    'desc_ocm_gestione_url_meta_inadeguata_warning': "Gestione URL e Meta inadeguata. La gestione di URL e meta tag (title, description) dovrebbe essere implementata in modo programmatico e centralizzato, specialmente per siti di grandi dimensioni, per garantire coerenza e facilità di aggiornamento. Verificare se CMS o framework utilizzati permettono tale gestione.",
    'desc_ocm_sistema_controllo_uptime_mancante_warning': "Sistema controllo uptime mancante. Indica che non è in uso un sistema proattivo per monitorare l'uptime del sito. Implementare un servizio di monitoraggio uptime per ricevere notifiche immediate in caso di downtime e intervenire tempestivamente.",
    'desc_ocm_meta_tags_inconsistent_warning': "Inconsistenze nella strategia dei meta tag (es. formati title variabili, lunghezza description molto diversa) possono indicare una cura non ottimale dei contenuti.",
    'desc_ocm_url_strategy_inconsistent_warning': "Incoerenze nella strategia degli URL (es. uso misto di trailing slash, maiuscole/minuscole variabili) possono creare confusione e potenziali problemi di contenuto duplicato.",
    'desc_ocm_hreflang_errors_warning': "Errori non critici nell'implementazione di hreflang (es. codici lingua/regione non validi, return tag mancanti) possono compromettere il targeting internazionale.",
    'desc_ocm_website_uptime_low_warning': "Un uptime storicamente basso del sito (basato su dati di monitoraggio esterno, se disponibili) indica inaffidabilità e impatta negativamente SEO e UX.",
    'desc_ocm_ga_gsc_not_configured_warning': "La mancata configurazione di Google Analytics o Google Search Console (o il mancato collegamento) impedisce di monitorare le performance del sito e identificare problemi SEO.", # Existing good description
    'desc_ocm_ga_non_configurato_sito_warning': "Google Analytics non configurato sul sito. Google Analytics non risulta installato o correttamente configurato su tutte le pagine del sito. Implementare il tracciamento GA per raccogliere dati vitali sul traffico e il comportamento degli utenti.",
    'desc_ocm_ga_non_collegato_progetto_warning': "Google Analytics non collegato al progetto. La proprietà di Google Analytics non è (o non sembra essere) collegata a questo progetto di analisi o ad altri strumenti rilevanti. Assicurare il corretto collegamento per un flusso di dati completo e report integrati.",
    'desc_ocm_gsc_non_configurato_warning': "Google Search Console non configurato. Google Search Console non è configurata per il sito. Verificare la proprietà del sito in GSC per accedere a dati diagnostici cruciali, performance di ricerca, stato dell'indicizzazione e inviare sitemap.",
    'desc_ocm_gsc_non_collegato_progetto_warning': "Google Search Console non collegato al progetto. La proprietà di Google Search Console non è (o non sembra essere) collegata a questo progetto di analisi. Collegare GSC per integrare dati importanti sulla salute SEO e le performance di ricerca.",
    # 'desc_ocm_mixed_content_warning' was removed as the key was changed to desc_ocm_problemi_mixed_content_error

    # SITE SEO AUDIT Descriptions
    'desc_seo_no_eeat_signals_error': "Assenza o carenza di segnali E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) per contenuti che lo richiedono. Fondamentali per il ranking, specialmente per contenuti YMYL.", # Modified
    'desc_seo_low_quality_ymyl_error': "Contenuti YMYL (Your Money Your Life) di bassa qualità, non autorevoli, o senza adeguati disclaimer. Google è molto severo su questi temi.", # Verified
    'desc_seo_extensive_duplicate_content_error': "Presenza estensiva di contenuti duplicati (interni o copiati da altri siti). Diluisce l'autorevolezza e può portare a penalizzazioni.", # Verified
    # 'desc_seo_title_missing_error' is now part of 'desc_seo_title_meta_missing_duplicated_error'
    'desc_seo_keyword_stuffing_error': "Utilizzo eccessivo e innaturale di parole chiave (keyword stuffing) nel contenuto, nei meta tag o negli alt text. Pratica penalizzata da Google.", # Verified

    # Descriptions for New SITE SEO AUDIT ERROR Checks
    'desc_seo_thin_content_pages_error': "Pagine con contenuto scarso (thin content) offrono poco valore agli utenti e sono penalizzate dai motori di ricerca.",
    'desc_seo_page_titles_not_optimized_error': "Titoli pagina non unici, non descrittivi o non pertinenti al contenuto della pagina riducono il CTR e danneggiano il ranking.",
    'desc_seo_meta_descriptions_not_optimized_error': "Meta description non uniche, non persuasive o non pertinenti al contenuto della pagina impattano negativamente il CTR dalle SERP.",
    'desc_seo_no_clear_seo_strategy_error': "L'assenza di una chiara strategia SEO (obiettivi definiti, analisi del target, selezione keyword mirate) porta a sforzi disorganizzati e risultati scarsi.",
    'desc_seo_outdated_content_error': "Contenuti obsoleti, specialmente su temi importanti per l'utente o per il settore, riducono l'autorevolezza e la pertinenza del sito.",
    'desc_seo_keyword_cannibalization_error': "Più pagine del sito competono per le stesse keyword importanti, diluendo l'autorevolezza e confondendo i motori di ricerca su quale pagina sia la più rilevante.",
    'desc_seo_seasonal_keywords_missed_error': "Mancata capitalizzazione di keyword stagionali rilevanti per il business, con perdita di opportunità di traffico e conversioni in periodi specifici.",
    'desc_seo_toxic_backlinks_error': "Un profilo backlink con una quantità significativa di link tossici o spam può portare a penalizzazioni manuali o algoritmiche da parte di Google.",
    'desc_seo_poor_internal_linking_strategy_error': "Una strategia di internal linking carente o inefficace non distribuisce adeguatamente il 'link juice', rendendo più difficile per utenti e crawler trovare contenuti importanti.",
    'desc_seo_anchor_text_not_optimized_error': "L'uso non ottimizzato degli anchor text per i link interni (es. troppi link generici come 'clicca qui') spreca opportunità di indicare ai motori di ricerca il tema delle pagine collegate.",
    'desc_seo_gsc_critical_errors_unresolved_error': "Errori critici segnalati in Google Search Console (es. problemi di copertura, usabilità mobile gravi) non risolti indicano problemi tecnici o di contenuto che danneggiano la SEO.",
    'desc_seo_title_meta_missing_duplicated_error': "Titoli o meta description mancanti o duplicati su più pagine sono errori SEO fondamentali che impattano ranking e CTR.",
    'desc_seo_title_too_long_error': f"Titoli pagina che superano i {SEO_CONFIG['title_max_length']} caratteri vengono troncati nelle SERP, riducendo la loro efficacia.",
    'desc_seo_meta_desc_bad_length_error': f"Meta description più corte di {SEO_CONFIG['meta_description_min_length']} o più lunghe di {SEO_CONFIG['meta_description_max_length']} caratteri non sono ottimali e possono essere riscritte da Google o troncate.",

    # Existing SITE SEO AUDIT WARNING/NOTICE Descriptions
    'desc_seo_inconsistent_header_structure_warning': "La struttura dei tag di intestazione (H1-H6) non è gerarchica o semanticamente corretta. Impatta accessibilità e SEO.",
    'desc_seo_author_bylines_missing_warning': "Mancanza di informazioni sull'autore (author bylines), specialmente per contenuti che richiedono expertise (es. articoli di blog, news). Importante per E-E-A-T.",
    'desc_seo_social_sharing_notice': "Il contenuto non è facilmente condivisibile sui social media (mancanza di pulsanti di condivisione evidenti, meta tag Open Graph/Twitter Cards incompleti).",
    'desc_seo_gmb_not_optimized_notice': "Profilo Google My Business (ora Google Business Profile) non ottimizzato, incompleto o con informazioni non aggiornate. Cruciale per la SEO locale.",
    # Descriptions for New SITE SEO AUDIT NOTICE Checks
    'desc_seo_faq_schema_missing_notice': "L'assenza di FAQ Schema su pagine con domande e risposte impedisce la visualizzazione di rich snippet specifici nelle SERP.",
    'desc_seo_howto_schema_missing_notice': "Le guide e i tutorial beneficiano dello HowTo Schema per una migliore rappresentazione nei risultati di ricerca.",
    'desc_seo_video_schema_missing_notice': "I contenuti video dovrebbero utilizzare Video Schema per fornire dettagli ai motori di ricerca e abilitare funzionalità specifiche.",
    'desc_seo_event_schema_missing_notice': "Le pagine relative a eventi dovrebbero implementare Event Schema per una corretta indicizzazione e visualizzazione.",
    'desc_seo_localbusiness_schema_missing_notice': "Per le attività locali, LocalBusiness Schema è cruciale per fornire informazioni precise (indirizzo, orari) ai motori di ricerca e mappe.",
    'desc_seo_product_schema_missing_notice': "Nelle schede prodotto e-commerce, Product Schema è fondamentale per mostrare dettagli come prezzo, disponibilità e recensioni nelle SERP.",
    'desc_seo_review_schema_missing_notice': "Le recensioni (es. di prodotti, servizi) dovrebbero utilizzare Review Schema per essere idonee ai rich snippet con valutazioni a stelle.",
    'desc_seo_internal_search_ux_poor_notice': "Una ricerca interna al sito poco efficace o con risultati non pertinenti peggiora l'esperienza utente e può portare all'abbandono del sito.",
    'desc_seo_blog_category_tags_suboptimal_notice': "Categorie e tag del blog non ottimizzati (troppi, duplicati, non pertinenti) possono creare confusione e pagine di archivio di bassa qualità.",
    'desc_seo_pagination_seo_issues_notice': "Una gestione non ottimale della paginazione (es. mancanza di rel='next/prev', canonical errati) può causare problemi di indicizzazione e contenuto duplicato.",
    'desc_seo_faceted_navigation_seo_issues_notice': "La navigazione a faccette (filtri), se non gestita correttamente (es. con noindex, canonical, AJAX), può generare un numero enorme di URL duplicati o di scarso valore.",
    'desc_seo_website_accessibility_basic_review_notice': "Una revisione base dell'accessibilità (WCAG) è consigliata per garantire che il sito sia utilizzabile da persone con disabilità (es. contrasto, navigazione da tastiera).",
    'desc_seo_privacy_policy_cookie_notice_review_notice': "Privacy Policy e Cookie Notice devono essere complete, aggiornate e facilmente accessibili per conformità normativa e fiducia dell'utente.",
    'desc_seo_terms_conditions_review_notice': "Termini e Condizioni d'uso del sito dovrebbero essere chiari, completi e facilmente reperibili dagli utenti.",
    'desc_seo_user_engagement_signals_low_notice': "Bassi segnali di user engagement (es. alta frequenza di rimbalzo, basso tempo sulla pagina, poche pagine per sessione) possono indicare problemi di UX o pertinenza dei contenuti.",
    'desc_seo_conversion_rate_tracking_notice': "Il mancato o incompleto tracciamento delle conversioni (goal in Analytics) impedisce di misurare l'efficacia del sito e delle attività SEO.",
    'desc_seo_regular_seo_audits_missing_notice': "La SEO è un processo continuo. La mancanza di audit SEO regolari impedisce di identificare e correggere tempestivamente nuovi problemi o opportunità.",
    'desc_seo_seo_kpi_monitoring_absent_notice': "Il mancato monitoraggio dei KPI SEO fondamentali (traffico organico, ranking, conversioni da organico) non permette di valutare i risultati delle strategie SEO.",
    'desc_seo_core_web_vitals_monitoring_notice': "Il monitoraggio attivo dei Core Web Vitals (LCP, INP, CLS), ad esempio tramite Google Search Console, è cruciale per l'esperienza utente e il ranking.",
    'desc_seo_backlink_profile_growth_slow_notice': "Una crescita lenta o stagnante del profilo backlink, specialmente se i competitor acquisiscono link di qualità, può limitare l'autorevolezza e il potenziale di ranking del sito."
}


# Etichette user-friendly per i tipi di problemi nel report PDF
# Questa sezione è ora SOSTITUITA da AUDIT_CHECKS_CONFIG e PDF_ISSUE_DESCRIPTIONS
# Mantenuta temporaneamente per retrocompatibilità o rimossa se non più usata.
# PDF_ISSUE_TYPE_LABELS = {
    # User-specified / preferred labels:
    # 'missing_title': 'Titolo mancante',
    # 'duplicate_title': 'Titolo duplicato',
    # ... (tutti gli altri elementi di PDF_ISSUE_TYPE_LABELS commentati o rimossi)
# }

# PDF_ISSUE_RECOMMENDATIONS = {
    # ... (tutti gli elementi di PDF_ISSUE_RECOMMENDATIONS commentati o rimossi)
# }

# Fattori di penalità per categoria di problemi nel calcolo del punteggio
# Commentato perché il nuovo sistema di scoring NEW_SCORING_CLASSIFICATION potrebbe renderlo obsoleto
# CATEGORY_ISSUE_PENALTY_FACTORS = {
#     'error': 1.0,    # Le problematiche classificate come 'error' hanno un impatto di penalità completo sul punteggio della categoria
#     'warning': 0.20, # Le problematiche classificate come 'warning' hanno il 20% dell'impatto di penalità
#     'notice': 0.02,  # Le problematiche classificate come 'notice' hanno il 2% dell'impatto di penalità
# }

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
# Commentato perché il nuovo sistema di scoring NEW_SCORING_CLASSIFICATION potrebbe renderlo obsoleto
# SEO_WEIGHTS = {
#     'title_tags': 15,
#     'meta_descriptions': 10,
#     'headings': 10,
#     'images_alt': 15,
#     'internal_links': 5,
#     'page_speed': 20,
#     'mobile_friendly': 10,
#     'ssl_certificate': 5,
#     'content_quality': 10,
# }

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
