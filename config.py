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
    'restrict_to_start_path': False
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
    'max_response_time': 3.0,
    'min_speed_score': 70,
    'compression_threshold': 0.8,
}

# Soglie Core Web Vitals
CORE_WEB_VITALS_THRESHOLDS = {
    'LCP_ERROR': 4.0,
    'LCP_GOOD': 2.5,
    'INP_ERROR': 500,
    'INP_GOOD': 200,
    'CLS_ERROR': 0.25,
    'CLS_GOOD': 0.1
}

SERVER_RESPONSE_TIME_ERROR = 600
TOUCH_ELEMENT_MIN_SIZE_PX = 44

# Configurazioni GUI
GUI_CONFIG = {
    'window_title': 'SEO Analyzer Pro',
    'window_size': '1200x800',
    'theme': 'dark',
    'colors': {
        'primary': '#1f538d', 'primary_light': '#6699CC', 'primary_dark': '#14375e',
        'secondary': '#6699CC', 'secondary_dark': '#4477AA',
        'success': '#2fa827', 'success_dark': '#22881f',
        'warning': '#ff9500', 'warning_dark': '#cc7700',
        'error': '#d32f2f', 'error_dark': '#a32222',
        'text': '#ffffff', 'background': '#212121', 'dark_gray': '#666666',
        'white': '#FFFFFF', 'light_gray': '#EEEEEE', 'border': '#CCCCCC', 'disabled': '#AAAAAA'
    },
    'fonts': {
        'title': ('Helvetica', 24, 'bold'), 'heading': ('Helvetica', 16, 'bold'),
        'body': ('Helvetica', 12), 'small': ('Helvetica', 10),
    }
}

# Configurazioni per il report PDF
PDF_CONFIG = {
    'page_size': 'A4',
    'margin': {'left': 1.0, 'right': 1.0, 'top': 1.0, 'bottom': 1.0},
    'font_family': 'Helvetica', 'font_family_bold': 'Helvetica',
    'font_sizes': {'title': 18, 'heading': 14, 'body': 10, 'small': 8},
    'colors': {
        'primary': '#336699', 'secondary': '#6699CC', 'success': '#2fa827',
        'warning': '#ff9500', 'error': '#d32f2f', 'light_gray': '#f0f0f0',
        'dark_gray': '#333333', 'secondary_dark': '#556677', 'border': '#CCCCCC'
    }
}

NEW_SCORING_CLASSIFICATION = {
    'ERROR': (90, 100), 'WARNING': (60, 89), 'NOTICE': (20, 59)
}
E_E_A_T_SIGNALS_CONFIG = {}
YMYL_CONTENT_CONFIG = {}

AUDIT_CHECKS_CONFIG = {
    # OCM Checks from previous state
    'ocm_lcp_gt_4_error': {
        'label': 'Largest Contentful Paint (LCP) > 4.0 secondi - Tempo di caricamento contenuto principale troppo lento',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_lcp_gt_4_error'
    },
    'ocm_inp_gt_500ms_error': {
        'label': 'Interaction to Next Paint (INP) > 500ms - Tempo di risposta alle interazioni utente eccessivo',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_inp_gt_500ms_error'
    },
    'ocm_cls_gt_025_error': {
        'label': 'Cumulative Layout Shift (CLS) > 0.25 - Spostamenti visivi imprevisti durante il caricamento',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_cls_gt_025_error'
    },
    'ocm_server_response_time_gt_600ms_error': {
        'label': 'Server Response Time > 600ms - Il server deve essere adeguatamente veloce',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_server_response_time_gt_600ms_error'
    },
    'ocm_assenza_cdn_siti_globali_error': {
        'label': 'Assenza CDN per siti globali - È importante utilizzare una CDN per le risorse del sito',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_assenza_cdn_siti_globali_error'
    },
    'ocm_assenza_implementazione_https_error': {
        'label': 'Assenza implementazione HTTPS - Il sito deve avere un certificato SSL valido',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_assenza_implementazione_https_error'
    },
    'ocm_certificato_ssl_scaduto_malconfigurato_error': {
        'label': 'Certificato SSL scaduto/malconfigurato - Il certificato SSL deve essere valido e configurato correttamente',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_certificato_ssl_scaduto_malconfigurato_error'
    },
    'ocm_problemi_mixed_content_error': {
        'label': 'Problemi mixed content (HTTP/HTTPS) - Il sito non deve presentare contenuti misti http/https',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_problemi_mixed_content_error'
    },
    'ocm_malware_contenuto_compromesso_error': {
        'label': 'Malware o contenuto compromesso - Presenza di codice malevolo o contenuti dannosi',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_malware_contenuto_compromesso_error'
    },
    'ocm_risorse_critiche_bloccate_robots_txt_error': {
        'label': 'Risorse critiche bloccate in robots.txt - Il file robots.txt deve essere configurato adeguatamente',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_risorse_critiche_bloccate_robots_txt_error'
    },
    'ocm_problemi_gravi_javascript_seo_error': {
        'label': 'Problemi gravi JavaScript SEO - Contenuto JavaScript non accessibile ai motori di ricerca',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_problemi_gravi_javascript_seo_error'
    },
    'ocm_errori_critici_xml_sitemap_error': {
        'label': 'Errori critici XML sitemap - È necessario creare e inviare una sitemap XML in Google Search Console',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_errori_critici_xml_sitemap_error'
    },
    'ocm_problemi_canonical_tag_gravi_error': {
        'label': 'Problemi canonical tag gravi - Il meta tag canonical deve essere configurato adeguatamente; il sito non deve essere indicizzato con www e senza www',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_problemi_canonical_tag_gravi_error'
    },
    'ocm_pagine_http_404_500_error': {
        'label': 'Pagine con codice di stato HTTP 404 o 500 - Le pagine 404 devono essere verificate e ottimizzate',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_pagine_http_404_500_error'
    },
    'ocm_http_404_errors_extensive_error': {
        'label': 'Errori 404 estensivi (link interni rotti)',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_http_404_errors_extensive_error'
    },
    'ocm_http_500_errors_error': {
        'label': 'Errori Server (5xx) frequenti o diffusi',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_http_500_errors_error'
    },
    'ocm_structured_data_errors_warning': {
        'label': "Structured data errors - Errori nell'implementazione dei dati strutturati",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_structured_data_errors_warning'
    },
    'ocm_redirect_chains_warning': {
        'label': "Redirect chains > 3 hop - Catene di reindirizzamento troppo lunghe",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_redirect_chains_warning'
    },
    'ocm_meta_description_missing_notice': {
        'label': "Meta description mancanti - Verificare pagine con meta description mancanti",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_meta_description_missing_notice'
    },
    'ocm_css_js_non_utilizzato_notice': {
        'label': "CSS/JS non utilizzato - Presenza di codice CSS/JavaScript inutilizzato",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_css_js_non_utilizzato_notice'
    },
    'ocm_font_loading_non_ottimizzato_notice': {
        'label': "Font loading non ottimizzato - Caricamento dei font non ottimizzato",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_font_loading_non_ottimizzato_notice'
    },
    'ocm_third_party_scripts_non_ottimizzati_notice': {
        'label': "Third-party scripts non ottimizzati - Script di terze parti non ottimizzati",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_third_party_scripts_non_ottimizzati_notice'
    },
    'ocm_dns_lookup_optimization_notice': {
        'label': "DNS lookup optimization - Ottimizzazione delle ricerche DNS",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_dns_lookup_optimization_notice'
    },
    'ocm_verifiche_url_parlanti_notice': {
        'label': "Verifiche URL parlanti - Verificare URL parlanti",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_verifiche_url_parlanti_notice'
    },
    'ocm_utilizzo_direttive_noindex_notice': {
        'label': "Utilizzo direttive noindex - Verificare che le direttive noindex siano utilizzate adeguatamente",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_utilizzo_direttive_noindex_notice'
    },
    'ocm_utilizzo_attributo_alt_immagini_notice': {
        'label': "Utilizzo attributo ALT immagini - Verificare l'utilizzo dell'attributo ALT per descrivere le immagini",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_utilizzo_attributo_alt_immagini_notice'
    },
    'ocm_dati_strutturati_implementazione_notice': {
        'label': "Dati strutturati implementazione - Utilizzare dati strutturati per descrivere meglio i contenuti delle pagine web",
        'category': CATEGORY_OCM, 'severity': 'NOTICE', 'description_key': 'desc_ocm_dati_strutturati_implementazione_notice'
    },
    'ocm_risorse_render_blocking_critiche_error': {
        'label': 'Risorse render-blocking critiche - Elementi che bloccano il rendering della pagina',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_risorse_render_blocking_critiche_error'
    },
    'ocm_assenza_compressione_sito_web_error': {
        'label': 'Assenza compressione sito web - Il sito web deve utilizzare un sistema di compressione',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_assenza_compressione_sito_web_error'
    },
    'ocm_mancata_implementazione_http2_error': {
        'label': 'Mancata implementazione HTTP/2 - Il sito web deve utilizzare HTTP/2',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_mancata_implementazione_http2_error'
    },
    'ocm_sistema_cache_inadeguato_error': {
        'label': 'Sistema di cache inadeguato - Il sito web deve utilizzare un sistema di cache',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_sistema_cache_inadeguato_error'
    },
    'ocm_minificazione_css_js_mancante_error': {
        'label': 'Minificazione CSS e JS mancante - Il sito deve utilizzare la minificazione sui file CSS e JS',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_minificazione_css_js_mancante_error'
    },
    'ocm_immagini_non_ottimizzate_web_error': {
        'label': 'Immagini non ottimizzate per web - Le immagini caricate sul sito devono essere ottimizzate per il web',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_immagini_non_ottimizzate_web_error'
    },
    'ocm_assenza_lazy_loading_immagini_error': {
        'label': 'Assenza lazy loading immagini - Deve essere utilizzato il caricamento differito delle immagini fuori dallo schermo (Lazy loading)',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_assenza_lazy_loading_immagini_error'
    },
    'ocm_contenuto_non_accessibile_mobile_error': {
        'label': 'Contenuto non accessibile su mobile - Tutti i contenuti devono essere fruibili da mobile',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_contenuto_non_accessibile_mobile_error'
    },
    'ocm_assenza_tag_viewport_error': {
        'label': 'Assenza tag viewport - Meta tag viewport mancante per responsive design',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_assenza_tag_viewport_error'
    },
    'ocm_touch_elements_lt_44px_error': {
        'label': "Touch elements < 44px - Elementi touch troppo piccoli per l'interazione mobile",
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_touch_elements_lt_44px_error'
    },
    'ocm_sito_non_mobile_friendly_error': {
        'label': 'Sito non mobile-friendly - Il sito deve essere mobile friendly',
        'category': CATEGORY_OCM, 'severity': 'ERROR', 'description_key': 'desc_ocm_sito_non_mobile_friendly_error'
    },
    'ocm_unnecessary_redirects_warning': {
        'label': "Reindirizzamenti inutili - I reindirizzamenti inutili devono essere eliminati",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_unnecessary_redirects_warning'
    },
    'ocm_url_structure_suboptimal_warning': {
        'label': "URL structure non ottimizzata - Le URL devono essere \"parlanti\"",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_url_structure_suboptimal_warning'
    },
    'ocm_hsts_missing_warning': {
        'label': "Assenza HSTS - Header di sicurezza HSTS mancante",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_hsts_missing_warning'
    },
    'ocm_csp_missing_warning': {
        'label': "Content Security Policy mancante - Policy di sicurezza dei contenuti non implementata",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_csp_missing_warning'
    },
    'ocm_x_frame_options_missing_warning': {
        'label': "Assenza X-Frame-Options - Header di protezione da clickjacking mancante",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_x_frame_options_missing_warning'
    },
    'ocm_404_errors_excessive_warning': {
        'label': "404 errors eccessivi - Le pagine 404 devono essere verificate e ottimizzate",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_404_errors_excessive_warning'
    },
    'ocm_broken_internal_links_warning': {
        'label': "Broken links interni - I link interni rotti devono essere corretti",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_broken_internal_links_warning'
    },
    'ocm_internal_linking_insufficient_warning': {
        'label': "Internal linking insufficiente - Collegamento interno tra pagine inadeguato",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_internal_linking_insufficient_warning'
    },
    'ocm_gestione_url_meta_inadeguata_warning': {
        'label': "Gestione URL e Meta inadeguata - La gestione URL e Meta deve essere implementata lato codice",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_gestione_url_meta_inadeguata_warning'
    },
    'ocm_sistema_controllo_uptime_mancante_warning': {
        'label': "Sistema controllo uptime mancante - Deve essere utilizzato un sistema di controllo uptime",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_sistema_controllo_uptime_mancante_warning'
    },
    'ocm_meta_tags_inconsistent_warning': {
        'label': 'Strategia meta tag (title/description) inconsistente tra pagine',
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_meta_tags_inconsistent_warning'
    },
    'ocm_url_strategy_inconsistent_warning': {
        'label': 'Strategia URL (es. trailing slash, case) inconsistente',
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_url_strategy_inconsistent_warning'
    },
    'ocm_hreflang_errors_warning': {
        'label': 'Errori implementazione hreflang (non critici)',
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_hreflang_errors_warning'
    },
    'ocm_website_uptime_low_warning': {
        'label': 'Uptime del sito web storicamente basso (richiede monitoraggio esterno)',
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_website_uptime_low_warning'
    },
    'ocm_ga_gsc_not_configured_warning': {
        'label': 'Google Analytics o Google Search Console non configurati/collegati',
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_ga_gsc_not_configured_warning'
    },
    'ocm_ga_non_configurato_sito_warning': {
        'label': "Google Analytics non configurato sul sito - Google Analytics deve essere configurato sul sito",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_ga_non_configurato_sito_warning'
    },
    'ocm_ga_non_collegato_progetto_warning': {
        'label': "Google Analytics non collegato al progetto - Google Analytics deve essere collegato al progetto",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_ga_non_collegato_progetto_warning'
    },
    'ocm_gsc_non_configurato_warning': {
        'label': "Google Search Console non configurato - Google Search Console deve essere configurata",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_gsc_non_configurato_warning'
    },
    'ocm_gsc_non_collegato_progetto_warning': {
        'label': "Google Search Console non collegato al progetto - Google Search Console deve essere collegata al progetto",
        'category': CATEGORY_OCM, 'severity': 'WARNING', 'description_key': 'desc_ocm_gsc_non_collegato_progetto_warning'
    },

    # SEO Audit Checks (merged from previous step + new additions)
    'seo_audit_eeat_signals_error': {
        'label': "Verificare presenza segnali E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_eeat_signals_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_ymyl_quality_error': {
        'label': "Controllare qualità contenuti YMYL (Your Money Your Life)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_ymyl_quality_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_duplicate_content_extensive_error': {
        'label': "Identificare contenuti duplicati estensivi",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_duplicate_content_extensive_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_thin_content_error': {
        'label': "Rimuovere thin content pages (pagine con contenuto scarso)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_thin_content_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_title_missing_duplicate_error': {
        'label': "Verificare tag title mancanti o duplicati",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_title_missing_duplicate_error'
    },
    'seo_audit_meta_description_missing_duplicate_error': {
        'label': "Verificare meta description mancanti o duplicate",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_meta_description_missing_duplicate_error'
    },
    'seo_audit_title_too_long_error': {
        'label': "Controllare title tag oltre 60 caratteri",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_title_too_long_error'
    },
    'seo_audit_meta_description_length_error': {
        'label': "Verificare meta description troppo lunghe o corte",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_meta_description_length_error'
    },
    'seo_audit_title_generic_error': {
        'label': "Ottimizzare title delle pagine generici o poco descrittivi",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_title_generic_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_keyword_stuffing_error': {
        'label': "Identificare keyword stuffing evidente",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_keyword_stuffing_error'
    },
    'seo_audit_keyword_research_strategy_error': {
        'label': "Sviluppare keyword research strategy",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_keyword_research_strategy_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_update_evergreen_content_error': {
        'label': "Aggiornare contenuto per topic evergreen",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_update_evergreen_content_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_keyword_cannibalization_error': {
        'label': "Risolvere problemi di cannibalizzazione keyword",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_keyword_cannibalization_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_seasonal_keywords_error': {
        'label': "Analizzare keyword stagionali",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_seasonal_keywords_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_toxic_backlinks_error': {
        'label': "Analizzare profilo backlink per identificare link tossici",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_toxic_backlinks_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_internal_linking_strategy_error': {
        'label': "Implementare internal linking strategy",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_internal_linking_strategy_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_anchor_text_over_optimization_error': {
        'label': "Verificare anchor text over-optimization",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_anchor_text_over_optimization_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gsc_coverage_issues_error': {
        'label': "Risolvere problemi di copertura dell'indice (Google Search Console)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_gsc_coverage_issues_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gsc_manual_penalties_error': {
        'label': "Verificare presenza penalizzazioni manuali (Google Search Console)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_gsc_manual_penalties_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_images_missing_alt_error': { # Updated/Ensured
        'label': "Immagini senza attributo ALT",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR',
        'description_key': 'desc_seo_audit_images_missing_alt_error',
        'always_add_placeholder_if_no_issue': False
    },
    'seo_audit_images_missing_title_error': { # New
        'label': "Immagini senza attributo Title",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR',
        'description_key': 'desc_seo_audit_images_missing_title_error',
        'always_add_placeholder_if_no_issue': False
    },
    'seo_audit_images_decorative_alt_error': {
        'label': "Aggiungere ALT mancante su immagini decorative (se necessario, o specificare alt vuoto)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_images_decorative_alt_error', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_images_not_optimized_web_error': {
        'label': "Ottimizzare immagini non ottimizzate per web",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_images_not_optimized_web_error'
    },
    'seo_audit_images_lazy_loading_error': {
        'label': "Implementare lazy loading immagini",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'ERROR', 'description_key': 'desc_seo_audit_images_lazy_loading_error'
    },
    'seo_audit_header_structure_warning': {
        'label': "Verificare header structure consistente",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_header_structure_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_h1_usage_warning': {
        'label': "Controllare presenza e uso corretto tag H1",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_h1_usage_warning'
    },
    'seo_audit_content_length_warning': {
        'label': "Valutare content length adeguata",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_content_length_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_readability_scores_warning': {
        'label': "Migliorare readability scores",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_readability_scores_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_broken_internal_links_warning': {
        'label': "Riparare link interni non funzionanti",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_broken_internal_links_warning'
    },
    'seo_audit_excessive_keyword_usage_warning': {
        'label': "Ridurre uso eccessivo parole chiave (non stuffing, ma sovra-ottimizzazione)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_excessive_keyword_usage_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_fix_broken_internal_links_warning': {
        'label': "Sistemare link interni rotti",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_fix_broken_internal_links_warning'
    },
    'seo_audit_author_bylines_missing_warning': {
        'label': "Aggiungere author bylines mancanti",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_author_bylines_missing_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_business_info_complete_warning': {
        'label': "Completare business information (NAP, about us)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_business_info_complete_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_contact_info_improve_warning': {
        'label': "Migliorare contact information (accessibilità, completezza)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_contact_info_improve_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_page_modification_monitoring_warning': {
        'label': "Implementare monitoraggio rendimento modifiche pagine",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_page_modification_monitoring_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_increase_keyword_monitoring_warning': {
        'label': "Aumentare keyword monitorate",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_increase_keyword_monitoring_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_brand_references_improve_warning': {
        'label': "Migliorare riferimenti brand (citazioni, menzioni)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_brand_references_improve_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_competitor_analysis_enhance_warning': {
        'label': "Potenziare competitor analysis",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'WARNING', 'description_key': 'desc_seo_audit_competitor_analysis_enhance_warning', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_content_shareable_notice': {
        'label': "Rendere contenuti facilmente condivisibili",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_content_shareable_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_featured_snippets_opportunities_notice': {
        'label': "Sfruttare featured snippets opportunities",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_featured_snippets_opportunities_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_long_tail_keyword_opportunities_notice': {
        'label': "Identificare long-tail keyword opportunities",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_long_tail_keyword_opportunities_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_content_freshness_minor_updates_notice': {
        'label': "Pianificare content freshness minor updates",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_content_freshness_minor_updates_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_social_signals_improve_notice': {
        'label': "Migliorare social signals",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_social_signals_improve_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_identify_main_pages_notice': {
        'label': "Identificare pagine principali del sito",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_identify_main_pages_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_exploit_underutilized_pages_notice': {
        'label': "Sfruttare pagine con potenziale non utilizzate",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_exploit_underutilized_pages_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_improve_main_content_control_notice': {
        'label': "Migliorare controllo contenuti principali",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_improve_main_content_control_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_deepen_keyword_research_notice': {
        'label': "Approfondire keyword research",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_deepen_keyword_research_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_align_content_search_intent_notice': {
        'label': "Allineare contenuti al search intent",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_align_content_search_intent_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_use_editorial_assistant_notice': {
        'label': "Utilizzare assistente editoriale (es. per grammatica, stile)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_use_editorial_assistant_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_develop_content_strategy_editorial_plan_notice': {
        'label': "Sviluppare strategia contenuti con piano editoriale",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_develop_content_strategy_editorial_plan_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_implement_guest_post_strategy_notice': {
        'label': "Implementare guest post strategy (per contenuti e/o backlink)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_implement_guest_post_strategy_content_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gmb_optimize_notice': {
        'label': "Ottimizzare Google My Business",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_gmb_optimize_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gmb_upload_images_notice': {
        'label': "Caricare immagini attività GMB",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_gmb_upload_images_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gmb_update_hours_notice': {
        'label': "Aggiornare orari apertura GMB",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_gmb_update_hours_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gmb_manage_reviews_notice': {
        'label': "Migliorare gestione recensioni GMB",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_gmb_manage_reviews_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gmb_geolocalized_keywords_notice': {
        'label': "Inserire keyword geolocalizzate (in GMB e sito)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_gmb_geolocalized_keywords_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_backlink_anchor_text_optimize_notice': {
        'label': "Ottimizzare anchor text backlink (naturali e variati)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_backlink_anchor_text_optimize_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_identify_websites_link_building_notice': {
        'label': "Identificare siti web per link building",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_identify_websites_link_building_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_analyze_backlink_profile_quality_notice': {
        'label': "Analizzare qualità profilo backlink (autorevolezza, pertinenza)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_analyze_backlink_profile_quality_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_plan_guest_post_strategy_backlinks_notice': {
        'label': "Pianificare guest post strategy (per backlink)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_plan_guest_post_strategy_backlinks_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_verify_brand_mentions_citations_notice': {
        'label': "Verificare menzioni e citazioni brand (e trasformarle in link se possibile)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_verify_brand_mentions_citations_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_images_alt_description_notice': {
        'label': "Verificare utilizzo attributo ALT per descrivere immagini (non solo keyword)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_images_alt_description_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_images_optimize_performance_notice': {
        'label': "Controllare ottimizzazione immagini per performance (compressione, formati moderni)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_images_optimize_performance_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_images_lazy_loading_offscreen_notice': {
        'label': "Implementare lazy loading su immagini fuori schermo",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_images_lazy_loading_offscreen_notice'
    },
    'seo_audit_gmb_upload_activity_images_notice': {
        'label': "Caricare immagini dell'attività su Google My Business",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_gmb_upload_activity_images_notice', 'always_add_placeholder_if_no_issue': True
    },
    'seo_audit_gmb_optimize_images_local_search_notice': {
        'label': "Ottimizzare immagini per ricerche locali (geotag, nomi file descrittivi)",
        'category': CATEGORY_SEO_AUDIT, 'severity': 'NOTICE', 'description_key': 'desc_seo_audit_gmb_optimize_images_local_search_notice', 'always_add_placeholder_if_no_issue': True
    }
}

PDF_ISSUE_DESCRIPTIONS = {
    # OCM Descriptions from previous state
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
    'desc_ocm_http_404_errors_extensive_error': "Un numero elevato di errori 404 (Pagina Non Trovata) per link interni indica problemi di manutenzione e peggiora l'esperienza utente e il crawl budget.",
    'desc_ocm_http_500_errors_error': "Errori Server (5xx) frequenti o diffusi indicano problemi infrastrutturali seri che rendono il sito inaccessibile e danneggiano la SEO.",
    'desc_ocm_structured_data_errors_warning': "Structured data errors - Errori nell'implementazione dei dati strutturati. Verificare la validità dei dati strutturati usando lo strumento di test di Google e correggere gli errori segnalati.",
    'desc_ocm_redirect_chains_warning': "Redirect chains > 3 hop - Catene di reindirizzamento troppo lunghe. Identificare e rimuovere i passaggi di redirect intermedi per migliorare la velocità e l'efficienza del crawling.",
    'desc_ocm_meta_description_missing_notice': "Meta description mancanti. Alcune pagine del sito non hanno una meta description. Scrivere meta description uniche e persuasive per ogni pagina importante per migliorare il Click-Through Rate (CTR) dai risultati di ricerca.",
    'desc_ocm_css_js_non_utilizzato_notice': "CSS/JS non utilizzato. Rilevata la presenza di codice CSS o JavaScript non utilizzato che appesantisce inutilmente le pagine. Rimuovere il codice inutilizzato per ridurre le dimensioni dei file e migliorare i tempi di caricamento.",
    'desc_ocm_font_loading_non_ottimizzato_notice': "Font loading non ottimizzato. Il caricamento dei web font potrebbe non essere ottimale, causando ritardi nel rendering del testo (FOIT/FOUT). Utilizzare strategie come `font-display: swap`, preloading dei font critici o formati moderni (WOFF2) per migliorare le performance.",
    'desc_ocm_third_party_scripts_non_ottimizzati_notice': "Third-party scripts non ottimizzati. Script di terze parti (es. analytics, social media, advertising) potrebbero impattare negativamente le performance. Valutare la necessità di ogni script, caricarli in modo asincrono o differito, e ove possibile, ospitarli localmente o utilizzare versioni più leggere.",
    'desc_ocm_dns_lookup_optimization_notice': "DNS lookup optimization. Le risoluzioni DNS per domini di terze parti possono aggiungere latenza. Utilizzare tecniche come `dns-prefetch` o `preconnect` per risolvere in anticipo i DNS di risorse critiche esterne e ridurre i tempi di attesa.",
    'desc_ocm_verifiche_url_parlanti_notice': "Verifiche URL parlanti. Assicurarsi che gli URL siano 'parlanti', ovvero descrittivi, facili da leggere per gli utenti e che includano keyword rilevanti. Evitare URL con parametri eccessivi o stringhe incomprensibili.",
    'desc_ocm_utilizzo_direttive_noindex_notice': "Utilizzo direttive noindex. Verificare che le direttive `noindex` (meta tag o X-Robots-Tag) siano usate correttamente per impedire l'indicizzazione di pagine non desiderate. Un uso errato può escludere pagine importanti.",
    'desc_ocm_utilizzo_attributo_alt_immagini_notice': "Utilizzo attributo ALT immagini. Assicurarsi che tutte le immagini significative abbiano un attributo ALT descrittivo. Questo migliora l'accessibilità e fornisce contesto ai motori di ricerca.",
    'desc_ocm_dati_strutturati_implementazione_notice': "Dati strutturati implementazione. Considerare l'utilizzo di dati strutturati (Schema.org) per descrivere meglio i contenuti. Questo può aiutare a ottenere rich snippet.",
    'desc_ocm_risorse_render_blocking_critiche_error': "Risorse render-blocking critiche. Differire il caricamento di JS/CSS non critico, minificare le risorse e utilizzare il caricamento asincrono.",
    'desc_ocm_assenza_compressione_sito_web_error': "Assenza compressione sito web. Abilitare la compressione Gzip/Brotli a livello server per ridurre le dimensioni dei file.",
    'desc_ocm_mancata_implementazione_http2_error': "Mancata implementazione HTTP/2. Verificare con il provider hosting la disponibilità di HTTP/2 e abilitarlo.",
    'desc_ocm_sistema_cache_inadeguato_error': "Sistema di cache inadeguato. Configurare correttamente gli header HTTP di caching (Cache-Control, Expires).",
    'desc_ocm_minificazione_css_js_mancante_error': "Minificazione CSS e JS mancante. Implementare processi di minificazione per rimuovere caratteri non necessari.",
    'desc_ocm_immagini_non_ottimizzate_web_error': "Immagini non ottimizzate per web. Comprimere le immagini, scegliere formati appropriati e usare dimensioni responsive.",
    'desc_ocm_assenza_lazy_loading_immagini_error': "Assenza lazy loading immagini. Implementare il lazy loading per le immagini 'offscreen'.",
    'desc_ocm_contenuto_non_accessibile_mobile_error': "Contenuto non accessibile su mobile. Assicurare che tutti i contenuti siano responsive e l'esperienza utente ottimale su mobile.",
    'desc_ocm_assenza_tag_viewport_error': "Assenza tag viewport. Inserire `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">`.",
    'desc_ocm_touch_elements_lt_44px_error': "Touch elements < 44px. Aumentare le dimensioni degli elementi touch ad almeno 44x44 pixel.",
    'desc_ocm_sito_non_mobile_friendly_error': "Sito non mobile-friendly. Adottare un design responsive o adattivo.",
    'desc_ocm_unnecessary_redirects_warning': "Reindirizzamenti inutili. Eliminare passaggi superflui per migliorare velocità e crawl budget.",
    'desc_ocm_url_structure_suboptimal_warning': "URL structure non ottimizzata. Creare URL chiare, concise e 'parlanti'.",
    'desc_ocm_hsts_missing_warning': "Assenza HSTS. Implementare HSTS per forzare comunicazioni HTTPS.",
    'desc_ocm_csp_missing_warning': "Content Security Policy mancante. Definire una CSP robusta per mitigare rischi come XSS.",
    'desc_ocm_x_frame_options_missing_warning': "Assenza X-Frame-Options. Implementare per impedire clickjacking.",
    'desc_ocm_404_errors_excessive_warning': "404 errors eccessivi. Correggere link rotti o implementare redirect 301. Ottimizzare pagina 404.",
    'desc_ocm_broken_internal_links_warning': "Broken links interni. Correggere per migliorare UX e distribuzione link equity.",
    'desc_ocm_internal_linking_insufficient_warning': "Internal linking insufficiente. Migliorare strategia per distribuire 'link juice'.",
    'desc_ocm_gestione_url_meta_inadeguata_warning': "Gestione URL e Meta inadeguata. Implementare gestione programmatica e centralizzata.",
    'desc_ocm_sistema_controllo_uptime_mancante_warning': "Sistema controllo uptime mancante. Implementare servizio di monitoraggio.",
    'desc_ocm_meta_tags_inconsistent_warning': "Strategia meta tag inconsistente. Standardizzare formati e lunghezze.",
    'desc_ocm_url_strategy_inconsistent_warning': "Strategia URL inconsistente. Uniformare uso di trailing slash, maiuscole/minuscole.",
    'desc_ocm_hreflang_errors_warning': "Errori implementazione hreflang (non critici). Correggere codici lingua/regione e return tag.",
    'desc_ocm_website_uptime_low_warning': "Uptime del sito web storicamente basso. Indagare cause e migliorare affidabilità.",
    'desc_ocm_ga_gsc_not_configured_warning': "Google Analytics o GSC non configurati/collegati. Configurare e collegare.",
    'desc_ocm_ga_non_configurato_sito_warning': "Google Analytics non configurato sul sito. Implementare tracciamento GA.",
    'desc_ocm_ga_non_collegato_progetto_warning': "Google Analytics non collegato al progetto. Assicurare corretto collegamento.",
    'desc_ocm_gsc_non_configurato_warning': "Google Search Console non configurato. Verificare proprietà sito in GSC.",
    'desc_ocm_gsc_non_collegato_progetto_warning': "Google Search Console non collegato al progetto. Collegare GSC.",

    # SEO Audit Descriptions (merged from previous step + new additions)
    'desc_seo_audit_eeat_signals_error': "Mancanza o carenza di segnali E-E-A-T. Implementare: biografie autori dettagliate, fonti autorevoli, testimonianze, certificazioni, informazioni 'About Us' complete. Cruciale per YMYL.",
    'desc_seo_audit_ymyl_quality_error': "Contenuti YMYL di bassa qualità. Revisionare e migliorare i contenuti YMYL con informazioni accurate, aggiornate, supportate da esperti e fonti affidabili. Assicurare trasparenza e disclaimer.",
    'desc_seo_audit_duplicate_content_extensive_error': "Contenuti duplicati estensivi. Identificare e risolvere problemi di contenuto duplicato interno (usando canonical, noindex, o riscrivendo) ed esterno (richiedendo rimozione o canonicalizzazione).",
    'desc_seo_audit_thin_content_error': "Pagine con contenuto scarso (thin content). Arricchire o consolidare le pagine con poco contenuto. Se non utili, effettuare redirect 301 o rimuoverle (404/410).",
    'desc_seo_audit_title_missing_duplicate_error': "Tag title mancanti o duplicati. Assicurare che ogni pagina indicizzabile abbia un tag title unico e descrittivo.",
    'desc_seo_audit_meta_description_missing_duplicate_error': "Meta description mancanti o duplicate. Scrivere meta description uniche e persuasive per ogni pagina indicizzabile per migliorare il CTR.",
    'desc_seo_audit_title_too_long_error': "Title tag oltre 60 caratteri. Accorciare i title tag per evitare che vengano troncati nelle SERP, mantenendoli informativi e contenenti le keyword principali.",
    'desc_seo_audit_meta_description_length_error': "Meta description troppo lunghe o corte. Ottimizzare la lunghezza delle meta description (circa 120-155 caratteri) per massimizzare la visibilità e l'impatto nelle SERP.",
    'desc_seo_audit_title_generic_error': "Title generici o poco descrittivi. Riscrivere i title per renderli specifici per il contenuto della pagina, includendo keyword rilevanti e un chiaro beneficio per l'utente.",
    'desc_seo_audit_keyword_stuffing_error': "Keyword stuffing evidente. Rimuovere l'eccesso di keyword e riscrivere il contenuto in modo naturale, focalizzandosi sulla leggibilità e l'esperienza utente.",
    'desc_seo_audit_keyword_research_strategy_error': "Mancanza di una keyword research strategy. Sviluppare una strategia di ricerca keyword basata su analisi di mercato, competitor e search intent per guidare la creazione di contenuti.",
    'desc_seo_audit_update_evergreen_content_error': "Contenuto evergreen non aggiornato. Pianificare aggiornamenti regolari per i contenuti evergreen per mantenerli freschi, accurati e pertinenti.",
    'desc_seo_audit_keyword_cannibalization_error': "Cannibalizzazione keyword. Identificare le pagine in competizione per le stesse keyword. Consolidare i contenuti, differenziare il focus keyword o usare canonical/noindex.",
    'desc_seo_audit_seasonal_keywords_error': "Mancata analisi keyword stagionali. Identificare e pianificare contenuti e ottimizzazioni per le keyword stagionali rilevanti per il proprio business.",
    'desc_seo_audit_toxic_backlinks_error': "Profilo backlink con link tossici. Analizzare i backlink, identificare quelli tossici/spam e inviare un file di disavow tramite Google Search Console.",
    'desc_seo_audit_internal_linking_strategy_error': "Mancanza di una internal linking strategy. Sviluppare e implementare una strategia di internal linking per distribuire PageRank, migliorare la navigazione e aiutare i crawler.",
    'desc_seo_audit_anchor_text_over_optimization_error': "Anchor text over-optimization. Diversificare gli anchor text dei link interni ed esterni, utilizzando un mix di keyword esatte, parziali, brand e generiche.",
    'desc_seo_audit_gsc_coverage_issues_error': "Problemi di copertura dell'indice in GSC. Analizzare e risolvere gli errori di copertura segnalati in Google Search Console (es. errori server, URL bloccati, noindex errati).",
    'desc_seo_audit_gsc_manual_penalties_error': "Penalizzazioni manuali in GSC. Controllare la sezione 'Azioni manuali' in Google Search Console. Se presenti, seguire le indicazioni per risolvere il problema e inviare una richiesta di riconsiderazione.",
    'desc_seo_audit_images_missing_alt_error': "ERRORE: Rilevate immagini senza attributo ALT. Ogni immagine significativa deve avere un ALT text descrittivo per l'accessibilità e per fornire contesto ai motori di ricerca. Correggere aggiungendo ALT appropriati.", # Updated
    'desc_seo_audit_images_missing_title_error': "ERRORE: Rilevate immagini senza attributo Title. Sebbene meno critico dell'ALT, l'attributo Title può fornire informazioni aggiuntive all'utente al passaggio del mouse e in alcuni contesti. Valutare l'aggiunta di Title descrittivi dove opportuno.", # New
    'desc_seo_audit_images_decorative_alt_error': "ALT mancante su immagini decorative. Per immagini puramente decorative, usare un attributo ALT vuoto (alt=\"\") per indicare agli screen reader di ignorarle.",
    'desc_seo_audit_images_not_optimized_web_error': "Immagini non ottimizzate per web. Comprimere le immagini, usare formati moderni (WebP), e specificare dimensioni per ridurre il peso delle pagine e migliorare i tempi di caricamento.",
    'desc_seo_audit_images_lazy_loading_error': "Mancanza di lazy loading per immagini. Implementare il lazy loading per le immagini sotto la piega (below the fold) per velocizzare il caricamento iniziale della pagina.",
    'desc_seo_audit_header_structure_warning': "Header structure non consistente. Assicurare una struttura gerarchica e logica dei tag H (un solo H1 per pagina, seguito da H2, H3, ecc. in ordine).",
    'desc_seo_audit_h1_usage_warning': "Uso non corretto del tag H1. Ogni pagina dovrebbe avere un unico tag H1 che descriva accuratamente il contenuto principale.",
    'desc_seo_audit_content_length_warning': "Content length non adeguata. Valutare se la lunghezza del contenuto è appropriata per il tipo di pagina e l'intento di ricerca. Contenuti troppo scarni potrebbero non posizionarsi.",
    'desc_seo_audit_readability_scores_warning': "Readability scores bassi. Migliorare la leggibilità del testo usando frasi brevi, paragrafi concisi, elenchi puntati e un linguaggio chiaro.",
    'desc_seo_audit_broken_internal_links_warning': "Link interni non funzionanti. Identificare e correggere i link interni rotti per migliorare UX e crawlability.",
    'desc_seo_audit_excessive_keyword_usage_warning': "Uso eccessivo di parole chiave. Evitare la sovra-ottimizzazione. Il contenuto deve suonare naturale e focalizzato sull'utente, non solo sulle keyword.",
    'desc_seo_audit_fix_broken_internal_links_warning': "Sistemare link interni rotti. Simile a 'Riparare link interni non funzionanti', assicurarsi che tutti i link interni puntino a risorse valide.",
    'desc_seo_audit_author_bylines_missing_warning': "Author bylines mancanti. Aggiungere informazioni sull'autore (nome, bio, link social/expertise) per contenuti che richiedono credibilità, specialmente YMYL.",
    'desc_seo_audit_business_info_complete_warning': "Business information incompleta. Assicurarsi che le informazioni aziendali (Nome, Indirizzo, Telefono - NAP; pagina 'Chi Siamo') siano complete, accurate e consistenti ovunque.",
    'desc_seo_audit_contact_info_improve_warning': "Contact information da migliorare. Rendere le informazioni di contatto facilmente accessibili, complete e multiple (telefono, email, form, mappa se applicabile).",
    'desc_seo_audit_page_modification_monitoring_warning': "Mancato monitoraggio rendimento modifiche. Implementare un sistema per tracciare l'impatto delle modifiche SEO/contenuti sul ranking e traffico.",
    'desc_seo_audit_increase_keyword_monitoring_warning': "Keyword monitorate insufficienti. Espandere il set di keyword monitorate per avere una visione più completa delle performance organiche.",
    'desc_seo_audit_brand_references_improve_warning': "Riferimenti brand da migliorare. Lavorare per aumentare le menzioni e citazioni positive del brand online, anche non linkate.",
    'desc_seo_audit_competitor_analysis_enhance_warning': "Competitor analysis superficiale. Approfondire l'analisi dei competitor (contenuti, keyword, backlink, strategie) per identificare opportunità e minacce.",
    'desc_seo_audit_content_shareable_notice': "Contenuti poco condivisibili. Facilitare la condivisione dei contenuti sui social media con pulsanti ben visibili e meta tag Open Graph/Twitter Cards ottimizzati.",
    'desc_seo_audit_featured_snippets_opportunities_notice': "Mancato sfruttamento featured snippets. Identificare opportunità per ottimizzare i contenuti (risposte concise, elenchi, tabelle) per apparire nei featured snippet.",
    'desc_seo_audit_long_tail_keyword_opportunities_notice': "Poche opportunità long-tail keyword. Ricercare e targettizzare keyword long-tail specifiche per attrarre traffico qualificato e con intento di ricerca chiaro.",
    'desc_seo_audit_content_freshness_minor_updates_notice': "Mancanza di aggiornamenti minori per la freschezza. Pianificare piccoli aggiornamenti periodici ai contenuti (es. statistiche, date, link) per segnalare freschezza.",
    'desc_seo_audit_social_signals_improve_notice': "Social signals deboli. Incrementare l'engagement e la condivisione sui social media per migliorare indirettamente la visibilità e l'autorevolezza.",
    'desc_seo_audit_identify_main_pages_notice': "Pagine principali non chiaramente identificate. Definire e dare priorità alle pagine core del sito (es. pillar pages, pagine di servizio/prodotto principali).",
    'desc_seo_audit_exploit_underutilized_pages_notice': "Pagine con potenziale non sfruttato. Identificare pagine con buon contenuto ma scarso traffico/ranking e pianificare ottimizzazioni.",
    'desc_seo_audit_improve_main_content_control_notice': "Controllo contenuti principali da migliorare. Assicurarsi che i contenuti più importanti siano facilmente accessibili, ben linkati e ottimizzati al meglio.",
    'desc_seo_audit_deepen_keyword_research_notice': "Keyword research superficiale. Andare oltre le keyword ovvie, esplorando variazioni semantiche, domande degli utenti e keyword dei competitor.",
    'desc_seo_audit_align_content_search_intent_notice': "Contenuti non allineati al search intent. Assicurarsi che ogni pagina soddisfi l'intento di ricerca primario (informativo, navigazionale, transazionale, commerciale) per quella keyword.",
    'desc_seo_audit_use_editorial_assistant_notice': "Mancato uso di assistente editoriale. Utilizzare strumenti per migliorare grammatica, stile, leggibilità e originalità dei testi.",
    'desc_seo_audit_develop_content_strategy_editorial_plan_notice': "Strategia contenuti e piano editoriale assenti. Sviluppare una strategia di content marketing documentata e un piano editoriale per guidare la produzione di contenuti.",
    'desc_seo_audit_implement_guest_post_strategy_content_notice': "Guest post strategy (contenuti) non implementata. Considerare il guest posting su siti autorevoli per aumentare visibilità e autorevolezza (attenzione alla qualità).",
    'desc_seo_audit_gmb_optimize_notice': "Google My Business non ottimizzato. Completare e ottimizzare ogni sezione del profilo GMB (informazioni, categorie, servizi, post, Q&A, foto).",
    'desc_seo_audit_gmb_upload_images_notice': "Poche immagini su GMB. Caricare regolarmente foto di alta qualità dell'attività, prodotti, team su Google My Business.",
    'desc_seo_audit_gmb_update_hours_notice': "Orari GMB non aggiornati. Mantenere sempre aggiornati gli orari di apertura su GMB, inclusi festività ed eventi speciali.",
    'desc_seo_audit_gmb_manage_reviews_notice': "Gestione recensioni GMB carente. Rispondere a tutte le recensioni (positive e negative) in modo professionale e tempestivo. Incoraggiare recensioni autentiche.",
    'desc_seo_audit_gmb_geolocalized_keywords_notice': "Keyword geolocalizzate non inserite. Integrare keyword specifiche per la località nel profilo GMB e nei contenuti del sito, se rilevante.",
    'desc_seo_audit_backlink_anchor_text_optimize_notice': "Anchor text backlink poco ottimizzati. Per i backlink in ingresso (ove possibile influenzarli), puntare a una varietà di anchor text naturali e pertinenti.",
    'desc_seo_audit_identify_websites_link_building_notice': "Mancata identificazione siti per link building. Ricercare attivamente siti web autorevoli e pertinenti per opportunità di link building.",
    'desc_seo_audit_analyze_backlink_profile_quality_notice': "Analisi qualità profilo backlink superficiale. Valutare regolarmente l'autorevolezza, la pertinenza e la naturalezza dei siti che linkano al proprio.",
    'desc_seo_audit_plan_guest_post_strategy_backlinks_notice': "Piano guest post (backlink) assente. Sviluppare una strategia mirata per ottenere backlink di qualità tramite guest posting.",
    'desc_seo_audit_verify_brand_mentions_citations_notice': "Mancata verifica menzioni e citazioni brand. Monitorare le menzioni del brand online e, ove possibile e appropriato, richiedere che diventino link.",
    'desc_seo_audit_images_alt_description_notice': "Attributo ALT non sufficientemente descrittivo. L'ALT text deve descrivere l'immagine per chi non può vederla, non essere solo un elenco di keyword.",
    'desc_seo_audit_images_optimize_performance_notice': "Ottimizzazione immagini per performance migliorabile. Oltre alla compressione, considerare formati come WebP, SVG per icone, e responsive images.",
    'desc_seo_audit_images_lazy_loading_offscreen_notice': "Lazy loading non implementato per tutte le immagini offscreen. Assicurarsi che tutte le immagini non immediatamente visibili siano caricate in modo differito.",
    'desc_seo_audit_gmb_upload_activity_images_notice': "Caricare immagini dell'attività su GMB. Simile a 'Poche immagini su GMB', focus specifico sulle immagini che mostrano l'attività in corso.",
    'desc_seo_audit_gmb_optimize_images_local_search_notice': "Immagini GMB non ottimizzate per ricerca locale. Nominare i file immagine in modo descrittivo, aggiungere geotag se appropriato, e scrivere descrizioni utili."
}

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

CHECKS_CONFIG = {
    'check_images': True, 'check_links': True, 'check_speed': True, 'check_mobile': True,
    'check_ssl': True, 'check_meta_tags': True, 'check_headings': True, 'check_content': True,
    'check_sitemap': True, 'check_robots': True,
}

HTTP_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
}

IGNORED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.rar', '.tar', '.gz', '.7z',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
    '.css', '.js', '.json', '.xml'
}

URL_REGEX = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'seo_analyzer.log'
}

SELENIUM_CONFIG = {
    'headless': True,
    'chrome_options': ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1920x1080"],
    'window_size': [1920, 1080],
    'page_load_timeout': 30,
    'implicit_wait': 10,
}
