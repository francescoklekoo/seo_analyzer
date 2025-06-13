"""
Analizzatore SEO per i dati raccolti dal crawler
"""

import re
import ssl
import socket
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Any
import statistics
from datetime import datetime
import logging

from config import (
    SEO_CONFIG, PERFORMANCE_CONFIG,
    AUDIT_CHECKS_CONFIG, PDF_ISSUE_DESCRIPTIONS, CATEGORY_OCM, CATEGORY_SEO_AUDIT,
    CORE_WEB_VITALS_THRESHOLDS, SERVER_RESPONSE_TIME_ERROR,
    NEW_SCORING_CLASSIFICATION, TOUCH_ELEMENT_MIN_SIZE_PX
)

class SEOAnalyzer:
    """
    Classe principale per l'analisi SEO dei dati crawlati
    """
    
    def __init__(self, pages_data: List[Dict], domain: str, site_wide_data: Dict = None):
        self.pages_data = pages_data
        self.domain = domain
        self.site_wide_data = site_wide_data if site_wide_data is not None else {}
        self.analysis_results = {
            'categorized_issues': {
                CATEGORY_OCM: {'ERROR': [], 'WARNING': [], 'NOTICE': []},
                CATEGORY_SEO_AUDIT: {'ERROR': [], 'WARNING': [], 'NOTICE': []}
            }
        }
        self.logger = logging.getLogger(__name__)
        
    def analyze_all(self) -> Dict:
        """Esegue tutte le analisi SEO"""
        self.logger.info("Inizio analisi SEO completa")
        
        # Analisi individuali (legacy, for potential data points)
        self.analysis_results['title_analysis'] = self._analyze_titles()
        self.analysis_results['meta_description_analysis'] = self._analyze_meta_descriptions()
        self.analysis_results['headings_analysis'] = self._analyze_headings()
        self.analysis_results['images_analysis'] = self._analyze_images()
        self.analysis_results['content_analysis'] = self._analyze_content()
        self.analysis_results['links_analysis'] = self._analyze_links()
        self.analysis_results['technical_analysis'] = self._analyze_technical()
        self.analysis_results['performance_analysis'] = self._analyze_performance()
        self.analysis_results['mobile_analysis'] = self._analyze_mobile_friendly()
        self.analysis_results['ssl_analysis'] = self._analyze_ssl()

        self._analyze_detailed_issues()
        
        self.analysis_results['detailed_issues'] = self._populate_legacy_detailed_issues() # Kept for now

        site_health_data = self._calculate_site_health()
        self.analysis_results['site_health'] = site_health_data
        self.analysis_results['overall_score'] = site_health_data['health_percentage']

        self.analysis_results['recommendations'] = self._generate_recommendations()
        self.analysis_results['summary'] = self._create_summary()
        
        self.logger.info("Analisi SEO completata")
        return self.analysis_results
    
    # ... (Keep all other _analyze_... methods like _analyze_titles, _analyze_meta_descriptions, etc. exactly as they are in Turn 26) ...
    # For brevity, I'm omitting them here, but they MUST be part of the overwrite block.
    # I will only show the _analyze_detailed_issues method and the methods after it.
    # The actual tool call will contain the *full* file content.

    def _analyze_titles(self) -> Dict:
        """Analizza i title tag"""
        analysis = {
            'total_pages': len(self.pages_data),
            'pages_with_title': 0,
            'pages_without_title': 0,
            'duplicate_titles': [],
            'too_short_titles': [],
            'too_long_titles': [],
            'optimal_titles': [],
            'title_lengths': [],
            'score': 0,
            'issues': []
        }
        
        title_counts = {}
        
        for page in self.pages_data:
            title = page.get('title', '').strip()
            url = page.get('url', '')
            
            if title:
                analysis['pages_with_title'] += 1
                title_length = len(title)
                analysis['title_lengths'].append(title_length)
                
                if title in title_counts:
                    title_counts[title].append(url)
                else:
                    title_counts[title] = [url]
                
                if title_length < SEO_CONFIG['title_min_length']:
                    analysis['too_short_titles'].append({
                        'url': url, 'title': title, 'length': title_length,
                        'issue': f"Title troppo corto (attuale: {title_length}, min: {SEO_CONFIG.get('title_min_length', 'N/A')})"
                    })
                elif title_length > SEO_CONFIG['title_max_length']:
                    analysis['too_long_titles'].append({
                        'url': url, 'title': title, 'length': title_length,
                        'issue': f"Title troppo lungo (attuale: {title_length}, max: {SEO_CONFIG.get('title_max_length', 'N/A')})"
                    })
                else:
                    analysis['optimal_titles'].append({'url': url, 'title': title, 'length': title_length})
            else:
                analysis['pages_without_title'] += 1
                analysis['issues'].append(f"Pagina senza title: {url}")
        
        for title, urls in title_counts.items():
            if len(urls) > 1:
                analysis['duplicate_titles'].append({'title': title, 'urls': urls, 'count': len(urls)})
        
        analysis['score'] = 70 # Placeholder
        return analysis
    
    def _analyze_meta_descriptions(self) -> Dict:
        analysis = {
            'total_pages': len(self.pages_data), 'pages_with_meta': 0, 'pages_without_meta': 0,
            'duplicate_metas': [], 'too_short_metas': [], 'too_long_metas': [], 'optimal_metas': [],
            'meta_lengths': [], 'score': 0, 'issues': []
        }
        meta_counts = {}
        for page in self.pages_data:
            meta_desc = page.get('meta_description', '').strip()
            url = page.get('url', '')
            if meta_desc:
                analysis['pages_with_meta'] += 1
                meta_length = len(meta_desc)
                analysis['meta_lengths'].append(meta_length)
                if meta_desc in meta_counts: meta_counts[meta_desc].append(url)
                else: meta_counts[meta_desc] = [url]
                if meta_length < SEO_CONFIG['meta_description_min_length']:
                    analysis['too_short_metas'].append({'url': url, 'meta': meta_desc, 'length': meta_length, 'issue': 'Meta Description troppo corta'})
                elif meta_length > SEO_CONFIG['meta_description_max_length']:
                    analysis['too_long_metas'].append({'url': url, 'meta': meta_desc, 'length': meta_length, 'issue': 'Meta Description troppo lunga'})
                else:
                    analysis['optimal_metas'].append({'url': url, 'meta': meta_desc, 'length': meta_length})
            else:
                analysis['pages_without_meta'] += 1
                analysis['issues'].append(f"Pagina senza meta description: {url}")
        for meta, urls in meta_counts.items():
            if len(urls) > 1: analysis['duplicate_metas'].append({'meta': meta, 'urls': urls, 'count': len(urls)})
        analysis['score'] = 70 # Placeholder
        return analysis

    def _analyze_headings(self) -> Dict:
        analysis = {'total_pages': len(self.pages_data), 'pages_with_h1': 0, 'pages_without_h1': 0, 'pages_multiple_h1': 0, 'heading_structure': {}, 'issues': [], 'score': 0}
        for page in self.pages_data:
            headings = page.get('headings', {}); url = page.get('url', '')
            h1_count = len(headings.get('h1', []))
            if h1_count == 0: analysis['pages_without_h1'] += 1; analysis['issues'].append(f"Pagina senza H1: {url}")
            elif h1_count == 1: analysis['pages_with_h1'] += 1
            else: analysis['pages_multiple_h1'] += 1; analysis['issues'].append(f"Pagina con {h1_count} H1: {url}")
            for level in range(1, 7):
                h_key = f'h{level}'; count = len(headings.get(h_key, []))
                if h_key not in analysis['heading_structure']: analysis['heading_structure'][h_key] = []
                analysis['heading_structure'][h_key].append(count)
        analysis['score'] = 70 # Placeholder
        return analysis

    def _analyze_images(self) -> Dict:
        analysis = {'total_images': 0, 'images_with_alt': 0, 'images_without_alt': 0, 'images_with_empty_alt': 0, 'images_with_title_attr': 0, 'images_without_title_attr': 0, 'images_with_empty_title_attr': 0, 'alt_text_lengths': [], 'issues': [], 'score': 0}
        for page in self.pages_data:
            images = page.get('images', [])
            for img in images:
                analysis['total_images'] += 1
                alt_text_value = img.get('alt')
                if alt_text_value is not None:
                    if alt_text_value.strip() == '': analysis['images_with_empty_alt'] += 1
                    else: analysis['images_with_alt'] += 1; analysis['alt_text_lengths'].append(len(alt_text_value.strip()))
                else: analysis['images_without_alt'] += 1
                title_text_value = img.get('title')
                if title_text_value is not None:
                    if title_text_value.strip() == '': analysis['images_with_empty_title_attr'] += 1
                    else: analysis['images_with_title_attr'] += 1
                else: analysis['images_without_title_attr'] += 1
        analysis['score'] = 70 # Placeholder
        return analysis

    def _analyze_content(self) -> Dict:
        analysis = {'total_pages': len(self.pages_data), 'pages_low_word_count': 0, 'pages_good_word_count': 0, 'pages_low_text_ratio': 0, 'word_counts': [], 'text_html_ratios': [], 'average_word_count': 0, 'average_text_ratio': 0, 'issues': [], 'score': 0}
        for page in self.pages_data:
            content = page.get('content', {}); url = page.get('url', '')
            word_count = content.get('word_count', 0); text_ratio = content.get('text_html_ratio', 0)
            analysis['word_counts'].append(word_count); analysis['text_html_ratios'].append(text_ratio)
            if word_count < SEO_CONFIG['min_word_count']: analysis['pages_low_word_count'] += 1; analysis['issues'].append(f"Contenuto scarso ({word_count} parole): {url}")
            else: analysis['pages_good_word_count'] += 1
            if text_ratio < SEO_CONFIG['min_text_html_ratio']: analysis['pages_low_text_ratio'] += 1; analysis['issues'].append(f"Rapporto testo/HTML basso ({text_ratio:.2f}): {url}")
        if analysis['word_counts']: analysis['average_word_count'] = statistics.mean(analysis['word_counts'])
        if analysis['text_html_ratios']: analysis['average_text_ratio'] = statistics.mean(analysis['text_html_ratios'])
        analysis['score'] = 70 # Placeholder
        return analysis

    def _analyze_links(self) -> Dict:
        analysis = {'total_links': 0, 'internal_links': 0, 'external_links': 0, 'broken_links': [], 'links_without_text': 0, 'pages_with_few_internal_links': 0, 'average_internal_links_per_page': 0, 'score': 0}
        all_internal_links = []
        for page in self.pages_data:
            links = page.get('links', []); page_internal_links = 0
            for link in links:
                analysis['total_links'] += 1
                if link.get('is_external', False): analysis['external_links'] += 1
                else: analysis['internal_links'] += 1; page_internal_links += 1; all_internal_links.append(link.get('url'))
                if not link.get('text', '').strip(): analysis['links_without_text'] += 1
            if page_internal_links < 3: analysis['pages_with_few_internal_links'] += 1
        if len(self.pages_data) > 0: analysis['average_internal_links_per_page'] = analysis['internal_links'] / len(self.pages_data)
        analysis['score'] = 70 # Placeholder
        return analysis

    def _analyze_technical(self) -> Dict:
        analysis = {'pages_with_canonical': 0, 'pages_without_canonical': 0, 'pages_with_lang': 0, 'pages_without_lang': 0, 'pages_with_schema': 0, 'pages_without_schema': 0, 'duplicate_canonicals': [], 'score': 0}
        canonical_counts = {}
        for page in self.pages_data:
            canonical = page.get('canonical_url', '').strip(); lang = page.get('lang', '').strip(); schema = page.get('schema_markup', [])
            if canonical: analysis['pages_with_canonical'] += 1; canonical_counts[canonical] = canonical_counts.get(canonical, 0) + 1
            else: analysis['pages_without_canonical'] += 1
            if lang: analysis['pages_with_lang'] += 1
            else: analysis['pages_without_lang'] += 1
            if schema: analysis['pages_with_schema'] += 1
            else: analysis['pages_without_schema'] += 1
        for canonical, count in canonical_counts.items():
            if count > 1: analysis['duplicate_canonicals'].append({'canonical': canonical, 'count': count})
        analysis['score'] = 70 # Placeholder
        return analysis

    def _analyze_performance(self) -> Dict:
        analysis = {'total_pages': len(self.pages_data), 'fast_pages': 0, 'slow_pages': 0, 'large_pages': 0, 'response_times': [], 'page_sizes': [], 'average_response_time': 0, 'average_page_size': 0, 'score': 0}
        for page in self.pages_data:
            response_time = page.get('response_time', 0); html_size = page.get('html_size', 0)
            analysis['response_times'].append(response_time); analysis['page_sizes'].append(html_size)
            if response_time <= PERFORMANCE_CONFIG['max_response_time']: analysis['fast_pages'] += 1
            else: analysis['slow_pages'] += 1
            if html_size > SEO_CONFIG['max_page_size_mb'] * 1024 * 1024: analysis['large_pages'] += 1
        if analysis['response_times']: analysis['average_response_time'] = statistics.mean(analysis['response_times'])
        if analysis['page_sizes']: analysis['average_page_size'] = statistics.mean(analysis['page_sizes'])
        analysis['score'] = 70 # Placeholder
        return analysis

    def _analyze_mobile_friendly(self) -> Dict:
        analysis = {'pages_with_viewport': 0, 'pages_without_viewport': 0, 'responsive_pages': 0, 'score': 75}
        return analysis

    def _analyze_ssl(self) -> Dict:
        analysis = {'has_ssl': False, 'ssl_valid': False, 'ssl_expires': None, 'score': 0}
        try:
            parsed_url = urlparse(f"https://{self.domain}")
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                sock = socket.create_connection((self.domain, 443), timeout=10)
                ssock = context.wrap_socket(sock, server_hostname=self.domain)
                analysis['has_ssl'] = True; analysis['ssl_valid'] = True; analysis['score'] = 100
                cert = ssock.getpeercert()
                if cert: analysis['ssl_expires'] = cert.get('notAfter')
                ssock.close()
        except Exception as e:
            self.logger.warning(f"Errore verifica SSL: {e}"); analysis['score'] = 0
        return analysis

    def _populate_legacy_detailed_issues(self) -> Dict:
        detailed = {'errors': [], 'warnings': [], 'notices': [], 'missing_h1_pages': [], 'multiple_h1_pages': [], 'missing_h2_pages': [], 'missing_h3_pages': [], 'images_without_alt': [], 'images_with_empty_alt': [], 'images_without_title_attr': [], 'images_with_empty_title_attr': [], 'duplicate_titles': [], 'duplicate_meta_descriptions': [], 'pages_without_title': [], 'pages_without_meta': [], 'low_word_count_pages': [], 'large_html_pages': [], 'slow_pages': [], 'pages_without_viewport': [], 'pages_without_lang': [], 'pages_without_canonical': [], 'broken_links': [], 'status_4xx_pages': [], 'status_5xx_pages': [], 'pages_without_schema': [], 'redirect_chains': [], 'mixed_content_pages': []}
        for page in self.pages_data:
            url = page.get('url', ''); title = page.get('title', '').strip(); meta_desc = page.get('meta_description', '').strip(); headings = page.get('headings', {}); images = page.get('images', []); content = page.get('content', {}); status_code = page.get('status_code', 200); html_size = page.get('html_size', 0); response_time = page.get('response_time', 0); canonical = page.get('canonical_url', '').strip(); lang = page.get('lang', '').strip(); schema = page.get('schema_markup', [])
            if not title: detailed['pages_without_title'].append({'url': url, 'issue': 'Pagina senza title tag'}); detailed['errors'].append({'type': 'missing_title', 'url': url, 'message': 'Title tag mancante'})
            if status_code >= 500: detailed['status_5xx_pages'].append({'url': url, 'status_code': status_code, 'issue': f'Errore server {status_code}'}); detailed['errors'].append({'type': 'server_error', 'url': url, 'message': f'Errore server {status_code}'})
            if status_code >= 400 and status_code < 500: detailed['status_4xx_pages'].append({'url': url, 'status_code': status_code, 'issue': f'Errore client {status_code}'}); detailed['errors'].append({'type': 'client_error', 'url': url, 'message': f'Errore client {status_code}'})
            if not meta_desc: detailed['pages_without_meta'].append({'url': url, 'issue': 'Meta description mancante'}); detailed['warnings'].append({'type': 'missing_meta', 'url': url, 'message': 'Meta description mancante'})
            h1_count = len(headings.get('h1', [])); h2_count = len(headings.get('h2', [])); h3_count = len(headings.get('h3', []))
            if h1_count == 0: detailed['missing_h1_pages'].append({'url': url, 'issue': 'H1 mancante'}); detailed['warnings'].append({'type': 'missing_h1', 'url': url, 'message': 'Tag H1 mancante'})
            elif h1_count > 1: detailed['multiple_h1_pages'].append({'url': url, 'issue': f'Multipli H1 ({h1_count}) trovati'}); detailed['warnings'].append({'type': 'multiple_h1', 'url': url, 'message': f'Multipli H1 ({h1_count}) trovati'})
            if h2_count == 0: detailed['missing_h2_pages'].append({'url': url, 'issue': 'H2 mancante'}); detailed['notices'].append({'type': 'missing_h2', 'url': url, 'message': 'Nessun tag H2 trovato'})
            if h3_count == 0: detailed['missing_h3_pages'].append({'url': url, 'issue': 'H3 mancante'}); detailed['notices'].append({'type': 'missing_h3', 'url': url, 'message': 'Nessun tag H3 trovato'})
            for img in images:
                img_src = img.get('src', 'N/A'); alt_value = img.get('alt')
                if alt_value is None: detailed['images_without_alt'].append({'url': url, 'image_src': img_src, 'issue': 'Attributo ALT HTML mancante'}); detailed['warnings'].append({'type': 'missing_alt_attr', 'url': url, 'image': img_src, 'message': 'Attributo ALT HTML mancante per immagine.'})
                elif alt_value.strip() == '': detailed['images_with_empty_alt'].append({'url': url, 'image_src': img_src, 'issue': 'Attributo ALT vuoto'}); detailed['warnings'].append({'type': 'empty_alt_attr', 'url': url, 'image': img_src, 'message': 'Attributo ALT vuoto per immagine.'})
                title_value = img.get('title')
                if title_value is None: detailed['images_without_title_attr'].append({'url': url, 'image_src': img_src, 'issue': 'Attributo Title HTML mancante'}); detailed['notices'].append({'type': 'missing_title_attr', 'url': url, 'image': img_src, 'message': 'Attributo Title HTML mancante per immagine.'})
                elif title_value.strip() == '': detailed['images_with_empty_title_attr'].append({'url': url, 'image_src': img_src, 'issue': 'Attributo Title vuoto'}); detailed['notices'].append({'type': 'empty_title_attr', 'url': url, 'image': img_src, 'message': 'Attributo Title vuoto per immagine.'})
            word_count = content.get('word_count', 0); min_wc = SEO_CONFIG.get('min_word_count', 200)
            if word_count < min_wc: detailed['low_word_count_pages'].append({'url': url, 'word_count': str(word_count), 'issue': f"Conteggio parole basso ({word_count} parole, min: {min_wc})"}); detailed['warnings'].append({'type': 'low_content', 'url': url, 'message': f"Conteggio parole basso ({word_count}), minimo raccomandato {min_wc}."})
            text_html_ratio = content.get('text_html_ratio', 0.0); min_text_html_ratio = SEO_CONFIG.get('min_text_html_ratio', 0.1)
            if text_html_ratio < min_text_html_ratio: detailed.setdefault('low_text_html_ratio_pages', []).append({'url': url, 'ratio': f"{text_html_ratio:.2f}", 'issue': f"Rapporto Testo/HTML basso ({text_html_ratio:.2f}, min: {min_text_html_ratio})"}); detailed['warnings'].append({'type': 'low_text_html_ratio', 'url': url, 'message': f"Rapporto Testo/HTML basso ({text_html_ratio:.2f}), minimo raccomandato {min_text_html_ratio}."})
            if response_time > PERFORMANCE_CONFIG['max_response_time']: detailed['slow_pages'].append({'url': url, 'response_time': response_time, 'issue': f'Pagina lenta ({response_time:.2f}s)'}); detailed['warnings'].append({'type': 'slow_page', 'url': url, 'message': f'Tempo di caricamento elevato ({response_time:.2f}s)'})
            if html_size > SEO_CONFIG['max_page_size_mb'] * 1024 * 1024: detailed['large_html_pages'].append({'url': url, 'size_mb': html_size / (1024 * 1024), 'issue': f'HTML troppo grande ({html_size / (1024 * 1024):.1f}MB)'}); detailed['warnings'].append({'type': 'large_page', 'url': url, 'message': f'Pagina troppo pesante ({html_size / (1024 * 1024):.1f}MB)'})
            if not canonical: detailed['pages_without_canonical'].append({'url': url, 'issue': 'URL canonico mancante'}); detailed['notices'].append({'type': 'missing_canonical', 'url': url, 'message': 'URL canonico non specificato'})
            if not lang: detailed['pages_without_lang'].append({'url': url, 'issue': 'Attributo lang mancante'}); detailed['notices'].append({'type': 'missing_lang', 'url': url, 'message': 'Lingua della pagina non specificata'})
            if not schema: detailed['pages_without_schema'].append({'url': url, 'issue': 'Schema markup mancante'}); detailed['notices'].append({'type': 'missing_schema', 'url': url, 'message': 'Dati strutturati non presenti'})
        self._find_duplicates(detailed)
        return detailed

    def _analyze_detailed_issues(self):
        self.logger.info("Inizio nuova analisi dettagliata dei problemi con AUDIT_CHECKS_CONFIG...")

        for cat_key in [CATEGORY_OCM, CATEGORY_SEO_AUDIT]:
            if cat_key not in self.analysis_results['categorized_issues']:
                self.analysis_results['categorized_issues'][cat_key] = {}
            for sev_key in ['ERROR', 'WARNING', 'NOTICE']:
                if sev_key not in self.analysis_results['categorized_issues'][cat_key]:
                    self.analysis_results['categorized_issues'][cat_key][sev_key] = []

        site_wide_checks_processed = set()

        # --- Pass 1: Site-Wide Checks (OCM & SEO Audit) ---
        for check_key, check_config in AUDIT_CHECKS_CONFIG.items():
            category = check_config['category']
            severity = check_config['severity']
            is_site_wide_check = False
            details_for_issue = "" # Store details if issue found

            if category == CATEGORY_OCM:
                if check_key == 'ocm_assenza_cdn_siti_globali_error':
                    is_site_wide_check = True
                    is_global = self.site_wide_data.get('is_global_site', False)
                    uses_cdn = self.site_wide_data.get('uses_cdn', False)
                    if is_global and not uses_cdn:
                        details_for_issue = "Il sito ha una portata globale ma non sembra utilizzare una CDN."
                elif check_key == 'ocm_assenza_implementazione_https_error':
                    is_site_wide_check = True
                    ssl_info = self.analysis_results.get('ssl_analysis', {})
                    if not ssl_info.get('has_ssl', False):
                        details_for_issue = "Il sito non utilizza HTTPS."
                elif check_key == 'ocm_certificato_ssl_scaduto_malconfigurato_error':
                    is_site_wide_check = True
                    ssl_info = self.analysis_results.get('ssl_analysis', {})
                    if ssl_info.get('has_ssl', True) and not ssl_info.get('ssl_valid', True):
                        details_for_issue = f"Certificato SSL non valido o scaduto. Scadenza: {ssl_info.get('ssl_expires', 'N/A')}."
                elif check_key == 'ocm_malware_contenuto_compromesso_error':
                    is_site_wide_check = True
                    if self.site_wide_data.get('malware_detected', False): # Placeholder
                        details_for_issue = "Rilevamento malware o codice sospetto (placeholder)."
                elif check_key == 'ocm_risorse_critiche_bloccate_robots_txt_error':
                    is_site_wide_check = True
                    if self.site_wide_data.get('robots_txt_blocks_critical_resources', False): # Placeholder
                        details_for_issue = "robots.txt blocca risorse critiche (placeholder)."
                elif check_key == 'ocm_errori_critici_xml_sitemap_error':
                    is_site_wide_check = True
                    if self.site_wide_data.get('sitemap_has_critical_errors', False): # Placeholder
                        details_for_issue = "Sitemap XML con errori critici (placeholder)."
                elif check_key == 'ocm_assenza_compressione_sito_web_error':
                    is_site_wide_check = True
                    if not self.site_wide_data.get('compression_enabled', True): # Placeholder
                        details_for_issue = "Compressione Gzip/Brotli non abilitata (placeholder)."
                elif check_key == 'ocm_mancata_implementazione_http2_error':
                    is_site_wide_check = True
                    if not self.site_wide_data.get('uses_http2', True): # Placeholder
                        details_for_issue = "Il server non sembra utilizzare HTTP/2 o HTTP/3 (placeholder)."
                elif check_key == 'ocm_sistema_cache_inadeguato_error':
                    is_site_wide_check = True
                    if not self.site_wide_data.get('has_adequate_caching_policy', True): # Placeholder
                        details_for_issue = "Policy di caching per asset statici inadeguata (placeholder)."
                elif check_key == 'ocm_minificazione_css_js_mancante_error': # Could be page-specific too
                    is_site_wide_check = True # Assuming a general check for now
                    if self.site_wide_data.get('minification_missing_for_css_js', False): # Placeholder
                        details_for_issue = "File CSS/JS non minificati (placeholder)."
                elif check_key == 'ocm_sito_non_mobile_friendly_error':
                    is_site_wide_check = True
                    if self.site_wide_data.get('is_generally_not_mobile_friendly', False): # Placeholder
                        details_for_issue = "Il design complessivo del sito non risulta mobile-friendly (placeholder)."
                elif check_key == 'ocm_hsts_missing_warning':
                    is_site_wide_check = True
                    if not self.site_wide_data.get('hsts_enabled', True): # Placeholder
                        details_for_issue = "L'header HSTS non è implementato."
                elif check_key == 'ocm_csp_missing_warning':
                    is_site_wide_check = True
                    if not self.site_wide_data.get('csp_implemented', True): # Placeholder
                        details_for_issue = "Content Security Policy (CSP) non implementata o troppo permissiva (placeholder)."
                elif check_key == 'ocm_x_frame_options_missing_warning':
                    is_site_wide_check = True
                    if not self.site_wide_data.get('x_frame_options_present', True): # Placeholder
                        details_for_issue = "L'header X-Frame-Options (o equivalente CSP) non è configurato."
                elif check_key == 'ocm_redirect_chains_warning': # Data from site_wide_data
                    is_site_wide_check = True
                    redirect_chains = self.site_wide_data.get('redirect_chains_found', [])
                    if redirect_chains:
                        details_for_issue = f"Rilevate catene di redirect (>3 hop). Esempi: {'; '.join([f'{chain[0]} -> ... ({len(chain)-1} hops)' for chain in redirect_chains[:2]])}"
                elif check_key == 'ocm_website_uptime_low_warning':
                    is_site_wide_check = True
                    if self.site_wide_data.get('has_low_historical_uptime', False): # Placeholder
                        details_for_issue = "L'uptime storico del sito risulta basso (placeholder)."
                elif check_key in ['ocm_ga_gsc_not_configured_warning', 'ocm_ga_non_configurato_sito_warning', 'ocm_ga_non_collegato_progetto_warning', 'ocm_gsc_non_configurato_warning', 'ocm_gsc_non_collegato_progetto_warning']:
                    is_site_wide_check = True
                    # This is simplified; real logic would check specific flags in self.site_wide_data for each
                    if not self.site_wide_data.get(check_key.replace("ocm_", "").replace("_warning",""), True): # Placeholder flag name
                        details_for_issue = f"Problema di configurazione/collegamento per {check_config['label'].split(' - ')[0]} (placeholder)."

            elif category == CATEGORY_SEO_AUDIT: # Most SEO Audit checks are site-wide/strategic
                is_site_wide_check = True
                # Logic for specific, auto-detectable SEO audit checks can be added here.
                # For now, most are qualitative and will rely on 'always_add_placeholder_if_no_issue'
                # or manual review based on their presence in the report.
                # Example:
                # if check_key == 'seo_specific_detectable_issue_key':
                #     if some_condition_from_site_wide_data:
                #         details_for_issue = "Specific SEO audit issue detected."
                # No generic "not implemented" placeholder for all SEO checks anymore.
                pass # Allow falling through to the 'always_add_placeholder_if_no_issue' logic


            if is_site_wide_check:
                site_wide_checks_processed.add(check_key)
                if details_for_issue: # If an issue was actually detected by specific logic above
                     self.analysis_results['categorized_issues'][category][severity].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Site-wide issues point to the domain
                        'details': details_for_issue,
                        'description_key': check_config['description_key'],
                        'severity': severity
                    })
                elif check_config.get('always_add_placeholder_if_no_issue', False):
                     self.analysis_results['categorized_issues'][category][severity].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Verifica manuale richiesta per '{check_config['label']}'. Consultare la descrizione per dettagli su cosa controllare.", # Updated placeholder
                        'description_key': check_config['description_key'],
                        'severity': severity
                    })


        # --- Pass 2: Page-Specific OCM Checks ---
        for page in self.pages_data:
            page_url = page.get('url', self.domain)

            for check_key, check_config in AUDIT_CHECKS_CONFIG.items():
                if check_config['category'] != CATEGORY_OCM or check_key in site_wide_checks_processed:
                    continue

                category = check_config['category']
                severity = check_config['severity']
                details = ""

                if check_key == 'ocm_lcp_gt_4_error':
                    lcp = page.get('performance_metrics', {}).get('lcp')
                    if lcp is not None and lcp > CORE_WEB_VITALS_THRESHOLDS['LCP_ERROR']:
                        details = f"LCP: {lcp:.2f}s (soglia {CORE_WEB_VITALS_THRESHOLDS['LCP_ERROR']:.1f}s)."
                elif check_key == 'ocm_inp_gt_500ms_error':
                    inp = page.get('performance_metrics', {}).get('inp')
                    if inp is not None and inp > CORE_WEB_VITALS_THRESHOLDS['INP_ERROR']:
                        details = f"INP: {inp:.0f}ms (soglia {CORE_WEB_VITALS_THRESHOLDS['INP_ERROR']:.0f}ms)."
                elif check_key == 'ocm_cls_gt_025_error':
                    cls = page.get('performance_metrics', {}).get('cls')
                    if cls is not None and cls > CORE_WEB_VITALS_THRESHOLDS['CLS_ERROR']:
                        details = f"CLS: {cls:.2f} (soglia {CORE_WEB_VITALS_THRESHOLDS['CLS_ERROR']:.2f})."
                elif check_key == 'ocm_server_response_time_gt_600ms_error':
                    response_time_ms = page.get('response_time', 0) * 1000
                    if response_time_ms > SERVER_RESPONSE_TIME_ERROR:
                        details = f"Tempo risposta server: {response_time_ms:.0f}ms (soglia {SERVER_RESPONSE_TIME_ERROR}ms)."
                elif check_key == 'ocm_problemi_mixed_content_error':
                    if page.get('has_mixed_content', False):
                        details = "Pagina HTTPS con risorse HTTP."
                elif check_key == 'ocm_problemi_gravi_javascript_seo_error':
                    if page.get('js_seo_issues_detected', False):
                        details = "Problemi JS impattano SEO (placeholder)."
                elif check_key == 'ocm_problemi_canonical_tag_gravi_error':
                    if page.get('has_grave_canonical_error', False):
                        details = f"Errore canonical grave. Canonical: {page.get('canonical_url', 'N/A')} (placeholder)."
                elif check_key == 'ocm_pagine_http_404_500_error':
                    status = page.get('status_code', 200)
                    if status == 404 or status >= 500:
                        details = f"Pagina restituisce HTTP {status}."
                elif check_key == 'ocm_risorse_render_blocking_critiche_error':
                    if page.get('performance_metrics', {}).get('has_render_blocking_resources', False): # Placeholder
                        details = "Risorse bloccano rendering (placeholder)."
                elif check_key == 'ocm_immagini_non_ottimizzate_web_error':
                     if page.get('images_analysis', {}).get('unoptimized_images_count', 0) > 0: # Placeholder
                        details = f"{page.get('images_analysis', {}).get('unoptimized_images_count', 0)} immagini non ottimizzate (placeholder)."
                elif check_key == 'ocm_assenza_lazy_loading_immagini_error':
                    if page.get('images_analysis', {}).get('lazy_loading_missing_for_offscreen_images', False): # Placeholder
                        details = "Manca lazy loading per immagini offscreen (placeholder)."
                elif check_key == 'ocm_contenuto_non_accessibile_mobile_error':
                     if page.get('mobile_usability', {}).get('content_not_fully_accessible', False): # Placeholder
                        details = "Contenuto non accessibile su mobile (placeholder)."
                elif check_key == 'ocm_assenza_tag_viewport_error':
                    if not page.get('has_viewport_tag', True): # Placeholder
                        details = "Meta tag viewport mancante."
                elif check_key == 'ocm_touch_elements_lt_44px_error':
                    if page.get('mobile_usability',{}).get('small_touch_targets_found', False): # Placeholder
                        details = f"Elementi touch < {TOUCH_ELEMENT_MIN_SIZE_PX}px (placeholder)."
                elif check_key == 'ocm_structured_data_errors_warning':
                    if page.get('has_structured_data_errors', False):
                        details = f"Errori dati strutturati: {str(page.get('structured_data_error_details', ''))[:100]}..."
                elif check_key == 'ocm_404_errors_excessive_warning': # This is page-specific if we want to list individual 404s that are not "extensive"
                    if page.get('status_code') == 404 and not AUDIT_CHECKS_CONFIG.get('ocm_http_404_errors_extensive_error',{}).get('triggered_site_wide', False): # Avoid double reporting if extensive error already caught it
                        details = "Pagina restituisce errore 404."
                elif check_key == 'ocm_broken_internal_links_warning':
                     if page.get('broken_internal_links'): # Expect list of broken links found on this page
                        details = f"Rilevati {len(page.get('broken_internal_links'))} link interni rotti in questa pagina."
                elif check_key == 'ocm_internal_linking_insufficient_warning':
                    internal_links_count = sum(1 for link in page.get('links', []) if not link.get('is_external', True))
                    if internal_links_count < 3 : # Example threshold
                        details = f"Pagina ha solo {internal_links_count} link interni."
                elif check_key == 'ocm_meta_description_missing_notice':
                    if not page.get('meta_description', '').strip():
                        details = 'Meta description mancante.'
                elif check_key == 'ocm_css_js_non_utilizzato_notice':
                    if page.get('unused_css_js_bytes', 0) > 10240: # Example: >10KB unused
                        details = f"Rilevati {page.get('unused_css_js_bytes',0)//1024}KB di CSS/JS non utilizzato (placeholder)."
                elif check_key == 'ocm_font_loading_non_ottimizzato_notice':
                    if page.get('non_optimized_font_loading', False): # Placeholder
                        details = "Caricamento dei font non ottimizzato (placeholder)."
                elif check_key == 'ocm_third_party_scripts_non_ottimizzati_notice':
                    if page.get('non_optimized_third_party_scripts', 0) > 0: # Placeholder
                        details = f"{page.get('non_optimized_third_party_scripts')} script di terze parti non ottimizzati (placeholder)."
                elif check_key == 'ocm_dns_lookup_optimization_notice':
                    if page.get('needs_dns_prefetch_or_preconnect', False): # Placeholder
                        details = "Considerare dns-prefetch o preconnect per risorse esterne critiche (placeholder)."
                elif check_key == 'ocm_verifiche_url_parlanti_notice':
                    if not page.get('is_url_sef', True): # Placeholder, SEF = Search Engine Friendly
                        details = "L'URL di questa pagina potrebbe non essere ottimale (non 'parlante')."
                elif check_key == 'ocm_utilizzo_direttive_noindex_notice':
                    if 'noindex' in page.get('meta_robots', []) and page.get('should_be_indexed', True): # Placeholder
                        details = "La direttiva noindex è usata, verificare se corretto per questa pagina."
                elif check_key == 'ocm_utilizzo_attributo_alt_immagini_notice':
                    images_missing_alt = 0
                    for img in page.get('images', []):
                        if img.get('alt') is None or img.get('alt').strip() == "":
                            images_missing_alt +=1
                    if images_missing_alt > 0:
                        details = f"{images_missing_alt} immagini non hanno un attributo ALT descrittivo."
                elif check_key == 'ocm_dati_strutturati_implementazione_notice':
                    if not page.get('has_structured_data', False) and page.get('could_benefit_from_sd', True): # Placeholder
                        details = "Considerare l'implementazione di dati strutturati per questa pagina."


                if details: # If an issue was found and details populated
                    self.analysis_results['categorized_issues'][category][severity].append({
                        'key': check_key, 'label': check_config['label'], 'url': page_url,
                        'details': details, 'description_key': check_config['description_key'], 'severity': severity
                    })
                # No "else: if False:" here, as we only add if an actual condition is met or explicitly placeholder-ed above.

        self.logger.info("Nuova analisi dettagliata dei problemi completata (OCM).")

    def _find_duplicates(self, detailed_issues: Dict) -> None:
        """Trova title e meta description duplicati tra le pagine."""
        title_dict = {}
        meta_dict = {}
        for page in self.pages_data:
            url = page.get('url')
            title = page.get('title', '').strip()
            meta = page.get('meta_description', '').strip()

            if title:
                if title not in title_dict:
                    title_dict[title] = []
                title_dict[title].append(url)
            
            if meta:
                if meta not in meta_dict:
                    meta_dict[meta] = []
                meta_dict[meta].append(url)

        for title, urls in title_dict.items():
            if len(urls) > 1:
                detailed_issues['duplicate_titles'].append({
                    'title': title, 'urls': urls, 'count': len(urls),
                    'issue': f"Titolo duplicato trovato su {len(urls)} pagine."
                })
                # Aggiungi anche a 'errors' o 'warnings' se necessario
                # detailed_issues['warnings'].append({'type': 'duplicate_title', 'message': f"Titolo '{title}' duplicato su {len(urls)} URLs.", 'urls': urls})


        for meta, urls in meta_dict.items():
            if len(urls) > 1:
                detailed_issues['duplicate_meta_descriptions'].append({
                    'meta': meta, 'urls': urls, 'count': len(urls),
                    'issue': f"Meta description duplicata trovata su {len(urls)} pagine."
                })
                # detailed_issues['warnings'].append({'type': 'duplicate_meta', 'message': f"Meta '{meta}' duplicata su {len(urls)} URLs.", 'urls': urls})


    def _calculate_site_health(self) -> Dict:
        """
        Calcola la salute complessiva del sito basandosi sui problemi categorizzati.
        Ogni check in AUDIT_CHECKS_CONFIG contribuisce al punteggio.
        I problemi (ERROR, WARNING, NOTICE) detraggono punti da un massimo di 100 per check.
        Il punteggio finale è la media dei punteggi di tutti i check.
        """
        self.logger.info("Inizio calcolo della salute del sito...")

        total_possible_score = 0
        achieved_score = 0

        all_triggered_issue_keys_details = {} # Per tracciare i problemi per il conteggio

        # Inizializza i conteggi per categoria e severità
        issue_counts = {
            CATEGORY_OCM: {'ERROR': 0, 'WARNING': 0, 'NOTICE': 0, 'TOTAL': 0},
            CATEGORY_SEO_AUDIT: {'ERROR': 0, 'WARNING': 0, 'NOTICE': 0, 'TOTAL': 0}
        }
        total_critical_issues = 0 # Errori OCM + Errori SEO Audit
        total_warning_issues = 0  # Warning OCM + Warning SEO Audit
        total_notice_issues = 0   # Notice OCM + Notice SEO Audit

        # Popola i conteggi e all_triggered_issue_keys_details
        for category_name, severities in self.analysis_results.get('categorized_issues', {}).items():
            if category_name not in issue_counts: # Should not happen if initialized correctly
                issue_counts[category_name] = {'ERROR': 0, 'WARNING': 0, 'NOTICE': 0, 'TOTAL': 0}

            for severity_name, issues_list in severities.items():
                unique_check_keys_in_severity = set()
                for issue_detail in issues_list:
                    issue_key = issue_detail.get('key')
                    if issue_key:
                        unique_check_keys_in_severity.add(issue_key)
                        # Store details for later scoring if needed, or just use the presence
                        if issue_key not in all_triggered_issue_keys_details:
                            all_triggered_issue_keys_details[issue_key] = []
                        all_triggered_issue_keys_details[issue_key].append(issue_detail)

                count_for_severity = len(unique_check_keys_in_severity) # Conta i check unici falliti per questa severità
                issue_counts[category_name][severity_name] = count_for_severity
                issue_counts[category_name]['TOTAL'] += count_for_severity

                if severity_name == 'ERROR':
                    total_critical_issues += count_for_severity
                elif severity_name == 'WARNING':
                    total_warning_issues += count_for_severity
                elif severity_name == 'NOTICE':
                    total_notice_issues += count_for_severity

        # Calcolo del punteggio basato su AUDIT_CHECKS_CONFIG
        num_total_checks = len(AUDIT_CHECKS_CONFIG)
        if num_total_checks == 0:
            self.logger.warning("AUDIT_CHECKS_CONFIG è vuoto. Impossibile calcolare la salute del sito.")
            return {'health_percentage': 100, 'evaluation': 'N/A', 'issue_counts': issue_counts,
                    'total_critical_issues':0, 'total_warning_issues':0, 'total_notice_issues':0}

        total_score_points_possible = num_total_checks * 100 # Max 100 punti per check
        current_total_score_achieved = 0

        for check_key, check_config in AUDIT_CHECKS_CONFIG.items():
            check_severity_if_failed = check_config['severity']
            points_for_this_check = 100 # Parte da 100

            if check_key in all_triggered_issue_keys_details: # Se questo check è fallito
                # Applica la penalità in base alla severità definita nel config per quel check
                if check_severity_if_failed == 'ERROR':
                    points_for_this_check = NEW_SCORING_CLASSIFICATION['ERROR'][0] # Usa il limite inferiore della classificazione errore come malus (es. 10 punti se 0-20 è errore)
                                                                                # O un valore fisso, es. 10/100 se è un errore
                                                                                # Per ora, usiamo 10/100 per ERROR, 50/100 per WARNING, 80/100 per NOTICE
                    points_for_this_check = 10 # Penalità pesante
                elif check_severity_if_failed == 'WARNING':
                    points_for_this_check = 50
                elif check_severity_if_failed == 'NOTICE':
                    points_for_this_check = 80

            current_total_score_achieved += points_for_this_check

        health_percentage = 0
        if total_score_points_possible > 0:
            health_percentage = round((current_total_score_achieved / total_score_points_possible) * 100)
        else: # Evita divisione per zero se num_total_checks è 0
            health_percentage = 100 # Default a 100 se non ci sono check configurati

        evaluation_text = "N/A"
        if health_percentage >= 90: evaluation_text = "Eccellente"
        elif health_percentage >= 70: evaluation_text = "Buono"
        elif health_percentage >= 50: evaluation_text = "Da Migliorare"
        else: evaluation_text = "Critico"

        self.logger.info(f"Salute del sito calcolata: {health_percentage}%, Valutazione: {evaluation_text}")

        return {
            'health_percentage': health_percentage,
            'evaluation': evaluation_text,
            'issue_counts': issue_counts, # Ora contiene i conteggi per OCM e SEO_AUDIT
            'total_critical_issues': total_critical_issues,
            'total_warning_issues': total_warning_issues,
            'total_notice_issues': total_notice_issues
        }

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Genera raccomandazioni basate sui problemi identificati."""
        recommendations = []
        
        # Utilizza categorized_issues per generare raccomandazioni
        categorized_issues = self.analysis_results.get('categorized_issues', {})

        # Priorità: Errori OCM, Errori SEO Audit, Avvertimenti OCM, Avvertimenti SEO Audit, etc.
        priority_order = [
            (CATEGORY_OCM, 'ERROR'), (CATEGORY_SEO_AUDIT, 'ERROR'),
            (CATEGORY_OCM, 'WARNING'), (CATEGORY_SEO_AUDIT, 'WARNING'),
            (CATEGORY_OCM, 'NOTICE'), (CATEGORY_SEO_AUDIT, 'NOTICE')
        ]

        processed_recommendation_keys = set() # Per evitare duplicati se un check_key appare in più posti

        for category, severity in priority_order:
            issues_list = categorized_issues.get(category, {}).get(severity, [])
            for issue in issues_list:
                check_key = issue.get('key')
                if check_key and check_key not in processed_recommendation_keys:
                    description = PDF_ISSUE_DESCRIPTIONS.get(issue.get('description_key'), "Azione correttiva specifica non definita.")
                    recommendations.append({
                        'priority': severity, # ERROR, WARNING, NOTICE
                        'category': category,
                        'title': issue.get('label', 'Problema non specificato'),
                        'description': description, # Questa è la raccomandazione ora
                        'details': issue.get('details', ''),
                        'affected_urls_count': 1 if issue.get('url') != self.domain else 0, # Semplificato
                        'affected_urls_sample': [issue.get('url')] if issue.get('url') != self.domain else ["Sito Globale"]
                    })
                    processed_recommendation_keys.add(check_key)

        if not recommendations:
            recommendations.append({
                'priority': 'INFO',
                'category': 'Generale',
                'title': 'Ottimo Lavoro!',
                'description': 'Non sono stati identificati problemi critici o avvertimenti maggiori. Continua a monitorare il sito regolarmente.',
                'details': '',
                'affected_urls_count': 0,
                'affected_urls_sample': []
            })

        return recommendations

    def _create_summary(self) -> Dict[str, Any]:
        """Crea un sommario dell'analisi."""
        summary = {
            'domain': self.domain,
            'total_pages_analyzed': len(self.pages_data),
            'overall_score': self.analysis_results.get('site_health', {}).get('health_percentage', 'N/A'),
            'evaluation': self.analysis_results.get('site_health', {}).get('evaluation', 'N/A'),
            'critical_issues_count': self.analysis_results.get('site_health', {}).get('total_critical_issues', 0),
            'warning_issues_count': self.analysis_results.get('site_health', {}).get('total_warning_issues', 0),
            'notice_issues_count': self.analysis_results.get('site_health', {}).get('total_notice_issues', 0),
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Aggiungi altri dati aggregati se necessario
        return summary
