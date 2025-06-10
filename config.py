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
    'ocm_lcp_error': {
        'label': 'Largest Contentful Paint (LCP) > 4.0 secondi',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_lcp_error'
    },
    'ocm_inp_error': {
        'label': 'Interaction to Next Paint (INP) > 500 millisecondi',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_inp_error'
    },
    'ocm_cls_error': {
        'label': 'Cumulative Layout Shift (CLS) > 0.25',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_cls_error'
    },
    'ocm_server_response_time_error': {
        'label': f'Server Response Time > {SERVER_RESPONSE_TIME_ERROR}ms',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_server_response_time_error'
    },
    'ocm_no_cdn_global_error': {
        'label': 'Assenza CDN per siti globali',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_no_cdn_global_error'
    },
    'ocm_no_https_error': {
        'label': 'Assenza implementazione HTTPS',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_no_https_error'
    },
    'ocm_critical_robots_block_error': {
        'label': 'Risorse critiche bloccate in robots.txt',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_critical_robots_block_error'
    },
    'ocm_structured_data_errors_warning': {
        'label': 'Errori nei dati strutturati',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_structured_data_errors_warning'
    },
    'ocm_redirect_chains_warning': {
        'label': 'Catene di redirect (> 3 hop)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_redirect_chains_warning'
    },
    'ocm_meta_description_missing_notice': { # Esempio di Notice per OCM
        'label': 'Meta description mancanti (OCM Check)',
        'category': CATEGORY_OCM,
        'severity': 'NOTICE',
        'description_key': 'desc_ocm_meta_description_missing_notice'
    },
    # Added OCM ERROR Checks
    'ocm_render_blocking_resources_error': {
        'label': 'Presenza risorse render-blocking significative',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_render_blocking_resources_error'
    },
    'ocm_image_optimization_error': {
        'label': 'Immagini non ottimizzate (formati, compressione)',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_image_optimization_error'
    },
    'ocm_lazy_loading_missing_error': {
        'label': 'Mancata implementazione lazy loading per immagini offscreen',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_lazy_loading_missing_error'
    },
    'ocm_ssl_expired_error': {
        'label': 'Certificato SSL scaduto o non valido',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_ssl_expired_error'
    },
    'ocm_malware_detected_error': {
        'label': 'Rilevamento malware o codice sospetto',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_malware_detected_error'
    },
    'ocm_no_http2_error': {
        'label': 'Mancato utilizzo di HTTP/2',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_no_http2_error'
    },
    'ocm_compression_missing_error': {
        'label': 'Mancata compressione Gzip/Brotli per risorse testuali',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_compression_missing_error'
    },
    'ocm_inadequate_caching_policy_error': {
        'label': 'Policy di caching inadeguata per asset statici',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_inadequate_caching_policy_error'
    },
    'ocm_js_seo_critical_error': {
        'label': 'Errori JS che impattano la SEO critica (rendering, navigazione)',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_js_seo_critical_error'
    },
    'ocm_xml_sitemap_errors_error': {
        'label': 'Errori gravi nella XML Sitemap (parsing, URL non validi)',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_xml_sitemap_errors_error'
    },
    'ocm_canonical_grave_error': {
        'label': 'Errori gravi di canonicalizzazione (es. loop, a 404)',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_canonical_grave_error'
    },
    'ocm_http_404_errors_extensive_error': {
        'label': 'Errori 404 estensivi (link interni rotti)',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_http_404_errors_extensive_error'
    },
    'ocm_http_500_errors_error': {
        'label': 'Errori Server (5xx) frequenti o diffusi',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_http_500_errors_error'
    },
    'ocm_minification_missing_error': {
        'label': 'Mancata minificazione CSS/JS',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_minification_missing_error'
    },
    'ocm_mobile_content_not_accessible_error': {
        'label': 'Contenuti importanti non accessibili/visibili su mobile',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_mobile_content_not_accessible_error'
    },
    'ocm_no_viewport_tag_error': {
        'label': 'Assenza meta tag viewport per responsività',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_no_viewport_tag_error'
    },
    'ocm_touch_elements_too_small_error': {
        'label': 'Elementi touch troppo piccoli o ravvicinati su mobile',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_touch_elements_too_small_error'
    },
    'ocm_not_mobile_friendly_design_error': {
        'label': 'Design complessivamente non mobile-friendly',
        'category': CATEGORY_OCM,
        'severity': 'ERROR',
        'description_key': 'desc_ocm_not_mobile_friendly_design_error'
    },
    # OCM WARNING CHECKS (Adding new ones here, some might exist already)
    'ocm_unnecessary_redirects_warning': {
        'label': 'Redirect non necessari (es. HTTP > HTTPS su link interni già HTTPS)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_unnecessary_redirects_warning'
    },
    'ocm_url_structure_suboptimal_warning': {
        'label': 'Struttura URL non ottimale (es. parametri eccessivi, profondità)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_url_structure_suboptimal_warning'
    },
    'ocm_hsts_missing_warning': {
        'label': 'Mancata implementazione HSTS (HTTP Strict Transport Security)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_hsts_missing_warning'
    },
    'ocm_csp_missing_warning': {
        'label': 'Content Security Policy (CSP) non implementata o troppo permissiva',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_csp_missing_warning'
    },
    'ocm_x_frame_options_missing_warning': {
        'label': 'Header X-Frame-Options non configurato (rischio clickjacking)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_x_frame_options_missing_warning'
    },
    'ocm_404_errors_excessive_warning': {
        'label': 'Errori 404 (non critici, ma numerosi)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_404_errors_excessive_warning'
    },
    'ocm_broken_internal_links_warning': {
        'label': 'Link interni rotti (non estensivi)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_broken_internal_links_warning'
    },
    'ocm_internal_linking_insufficient_warning': {
        'label': 'Pagine importanti con pochi link interni',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_internal_linking_insufficient_warning'
    },
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
    'ocm_website_uptime_low_warning': {
        'label': 'Uptime del sito web storicamente basso (richiede monitoraggio esterno)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_website_uptime_low_warning'
    },
    'ocm_ga_gsc_not_configured_warning': {
        'label': 'Google Analytics o Google Search Console non configurati/collegati',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_ga_gsc_not_configured_warning'
    },
    'ocm_mixed_content_warning': {
        'label': 'Presenza di mixed content (contenuti HTTP su pagine HTTPS)',
        'category': CATEGORY_OCM,
        'severity': 'WARNING',
        'description_key': 'desc_ocm_mixed_content_warning'
    },
    # Note: 'ocm_structured_data_errors_warning' and 'ocm_redirect_chains_warning' should exist from previous steps.

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
    'desc_ocm_lcp_error': "Largest Contentful Paint (LCP) superiore a 4.0 secondi. Fattore di ranking primario nel Page Experience; misura la performance di caricamento percepita dall'utente.",
    'desc_ocm_inp_error': "Interaction to Next Paint (INP) superiore a 500ms. Metrica Core Web Vital che valuta la reattività generale di una pagina alle interazioni dell'utente.",
    'desc_ocm_cls_error': "Cumulative Layout Shift (CLS) superiore a 0.25. Metrica Core Web Vital che misura la stabilità visuale e previene spostamenti inattesi del layout.",
    'desc_ocm_server_response_time_error': f"Tempo di risposta del server superiore a {SERVER_RESPONSE_TIME_ERROR}ms. Un server lento impatta negativamente l'esperienza utente e il crawling.",
    'desc_ocm_no_cdn_global_error': "Mancanza di una Content Delivery Network (CDN) per siti con traffico globale. Una CDN migliora la velocità di caricamento per utenti distanti dal server.",
    'desc_ocm_no_https_error': "Il sito non utilizza HTTPS. HTTPS è cruciale per la sicurezza, la fiducia dell'utente e un fattore di ranking.",
    'desc_ocm_critical_robots_block_error': "File robots.txt blocca risorse critiche (CSS, JS) necessarie per il rendering corretto della pagina. Ciò può impedire a Google di comprendere appieno il sito.",
    'desc_ocm_structured_data_errors_warning': "Presenza di errori (es. parsing, campi mancanti) nei dati strutturati implementati. Correggere per abilitare i rich snippet e migliorare la comprensione da parte dei motori di ricerca.",
    'desc_ocm_redirect_chains_warning': "Catene di redirect con più di 3 hop. Le catene lunghe possono sprecare crawl budget e rallentare l'esperienza utente.",
    'desc_ocm_meta_description_missing_notice': "Alcune pagine presentano meta description mancanti. Anche se non un fattore di ranking diretto, le meta description influenzano il CTR dalle SERP.",
    # Descriptions for added OCM ERROR Checks
    'desc_ocm_render_blocking_resources_error': "Risorse (JS/CSS) bloccano il rendering iniziale della pagina, peggiorando LCP e l'esperienza utente.",
    'desc_ocm_image_optimization_error': "Immagini pesanti o in formati non ottimali (es. JPEG invece di WebP) rallentano il caricamento e consumano banda.",
    'desc_ocm_lazy_loading_missing_error': "Mancata implementazione del lazy loading per immagini e iframe 'below the fold', sprecando risorse e rallentando il caricamento iniziale.",
    'desc_ocm_ssl_expired_error': "Un certificato SSL scaduto o non valido compromette la sicurezza, la fiducia dell'utente e può bloccare l'accesso al sito.",
    'desc_ocm_malware_detected_error': "La presenza di malware o codice sospetto danneggia gravemente la reputazione, la sicurezza degli utenti e porta a penalizzazioni severe da Google.",
    'desc_ocm_no_http2_error': "Il mancato utilizzo di HTTP/2 (o HTTP/3) impedisce miglioramenti prestazionali significativi come multiplexing e server push.",
    'desc_ocm_compression_missing_error': "La mancata compressione (Gzip, Brotli) per risorse testuali (HTML, CSS, JS) aumenta i tempi di download e lo spreco di banda.",
    'desc_ocm_inadequate_caching_policy_error': "Policy di caching del browser inadeguate o assenti per asset statici costringono il browser a riscaricare risorse inutilmente.",
    'desc_ocm_js_seo_critical_error': "Errori JavaScript bloccano o alterano il rendering dei contenuti, la navigazione o altre funzionalità SEO-critiche.",
    'desc_ocm_xml_sitemap_errors_error': "Errori nella XML Sitemap (URL non validi, formato errato, etc.) possono impedire a Google di scoprire e indicizzare correttamente tutte le pagine.",
    'desc_ocm_canonical_grave_error': "Errori gravi di canonicalizzazione (es. canonical loop, canonical a pagine 404 o non indicizzabili) confondono i motori di ricerca e diluiscono il ranking.",
    'desc_ocm_http_404_errors_extensive_error': "Un numero elevato di errori 404 (Pagina Non Trovata) per link interni indica problemi di manutenzione e peggiora l'esperienza utente e il crawl budget.",
    'desc_ocm_http_500_errors_error': "Errori Server (5xx) frequenti o diffusi indicano problemi infrastrutturali seri che rendono il sito inaccessibile e danneggiano la SEO.",
    'desc_ocm_minification_missing_error': "La mancata minificazione di risorse CSS e JavaScript aumenta inutilmente le dimensioni dei file e i tempi di caricamento.",
    'desc_ocm_mobile_content_not_accessible_error': "Contenuti testuali o funzionali importanti presenti su desktop ma nascosti o inaccessibili su mobile, violando il mobile-first indexing.",
    'desc_ocm_no_viewport_tag_error': "Assenza del meta tag viewport, fondamentale per indicare al browser come adattare la pagina ai dispositivi mobili, causando problemi di visualizzazione.",
    'desc_ocm_touch_elements_too_small_error': "Elementi interattivi (pulsanti, link) troppo piccoli o vicini tra loro su mobile rendono difficile la navigazione e peggiorano l'usabilità.",
    'desc_ocm_not_mobile_friendly_design_error': "Il design complessivo del sito non è responsive o adattivo, offrendo un'esperienza utente scadente su dispositivi mobili, penalizzata da Google.",
    # Descriptions for OCM WARNING Checks
    'desc_ocm_unnecessary_redirects_warning': "Redirect non necessari (es. link interni a URL HTTP che poi ridirigono a HTTPS) causano piccoli ritardi e possono consumare crawl budget.",
    'desc_ocm_url_structure_suboptimal_warning': "Una struttura URL complessa, con troppi parametri o eccessiva profondità, può essere meno user-friendly e più difficile da indicizzare per i motori di ricerca.",
    'desc_ocm_hsts_missing_warning': "L'assenza di HSTS (HTTP Strict Transport Security) rende il sito più vulnerabile ad attacchi man-in-the-middle (es. SSL stripping).",
    'desc_ocm_csp_missing_warning': "Una Content Security Policy (CSP) mancante o troppo permissiva aumenta il rischio di attacchi XSS (Cross-Site Scripting).",
    'desc_ocm_x_frame_options_missing_warning': "La mancanza dell'header X-Frame-Options o di una CSP adeguata espone il sito a rischi di clickjacking.",
    'desc_ocm_404_errors_excessive_warning': "Un numero eccessivo di errori 404, anche se non critici singolarmente, può indicare scarsa manutenzione del sito e peggiorare l'esperienza utente.",
    'desc_ocm_broken_internal_links_warning': "Link interni rotti portano a pagine di errore, frustrando l'utente e sprecando crawl budget. Anche se non estensivi, vanno corretti.",
    'desc_ocm_internal_linking_insufficient_warning': "Pagine importanti con pochi link interni potrebbero non ricevere sufficiente 'link juice' e essere più difficili da scoprire per utenti e crawler.",
    'desc_ocm_meta_tags_inconsistent_warning': "Inconsistenze nella strategia dei meta tag (es. formati title variabili, lunghezza description molto diversa) possono indicare una cura non ottimale dei contenuti.",
    'desc_ocm_url_strategy_inconsistent_warning': "Incoerenze nella strategia degli URL (es. uso misto di trailing slash, maiuscole/minuscole variabili) possono creare confusione e potenziali problemi di contenuto duplicato.",
    'desc_ocm_hreflang_errors_warning': "Errori non critici nell'implementazione di hreflang (es. codici lingua/regione non validi, return tag mancanti) possono compromettere il targeting internazionale.",
    'desc_ocm_website_uptime_low_warning': "Un uptime storicamente basso del sito (basato su dati di monitoraggio esterno, se disponibili) indica inaffidabilità e impatta negativamente SEO e UX.",
    'desc_ocm_ga_gsc_not_configured_warning': "La mancata configurazione di Google Analytics o Google Search Console (o il mancato collegamento) impedisce di monitorare le performance del sito e identificare problemi SEO.",
    'desc_ocm_mixed_content_warning': "Servire risorse HTTP (immagini, script, CSS) su pagine HTTPS (mixed content) compromette la sicurezza della pagina e può causare il blocco di tali risorse da parte del browser.",

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
