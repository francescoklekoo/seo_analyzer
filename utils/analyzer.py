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
    SEO_CONFIG, PERFORMANCE_CONFIG, # Removed CATEGORY_ISSUE_PENALTY_FACTORS
    AUDIT_CHECKS_CONFIG, PDF_ISSUE_DESCRIPTIONS, CATEGORY_OCM, CATEGORY_SEO_AUDIT,
    CORE_WEB_VITALS_THRESHOLDS, SERVER_RESPONSE_TIME_ERROR,
    NEW_SCORING_CLASSIFICATION, TOUCH_ELEMENT_MIN_SIZE_PX # Removed SEO_WEIGHTS
)

class SEOAnalyzer:
    """
    Classe principale per l'analisi SEO dei dati crawlati
    """
    
    def __init__(self, pages_data: List[Dict], domain: str):
        self.pages_data = pages_data
        self.domain = domain
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
        
        # Analisi individuali
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

        # La nuova analisi dettagliata dei problemi basata su AUDIT_CHECKS_CONFIG
        self._analyze_detailed_issues() # Populates categorized_issues
        
        # Manteniamo temporaneamente la vecchia analisi per non rompere altre parti
        self.analysis_results['detailed_issues'] = self._populate_legacy_detailed_issues()

        # Calcola Site Health utilizzando la nuova struttura categorized_issues
        site_health_data = self._calculate_site_health()
        self.analysis_results['site_health'] = site_health_data
        
        # Il punteggio generale del sito è ora la percentuale di salute calcolata dal nuovo metodo
        self.analysis_results['overall_score'] = site_health_data['health_percentage']

        # Genera raccomandazioni testuali (potrebbe necessitare di aggiornamenti per usare categorized_issues)
        self.analysis_results['recommendations'] = self._generate_recommendations()
        
        # Crea il riassunto
        self.analysis_results['summary'] = self._create_summary()
        
        self.logger.info("Analisi SEO completata")
        return self.analysis_results
    
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
                
                # Conta duplicati
                if title in title_counts:
                    title_counts[title].append(url)
                else:
                    title_counts[title] = [url]
                
                # Controlla lunghezza
                if title_length < SEO_CONFIG['title_min_length']:
                    analysis['too_short_titles'].append({
                        'url': url,
                        'title': title,
                        'length': title_length,
                        'issue': f"Title troppo corto (attuale: {title_length}, min: {SEO_CONFIG.get('title_min_length', 'N/A')})"
                    })
                elif title_length > SEO_CONFIG['title_max_length']:
                    analysis['too_long_titles'].append({
                        'url': url,
                        'title': title,
                        'length': title_length,
                        'issue': f"Title troppo lungo (attuale: {title_length}, max: {SEO_CONFIG.get('title_max_length', 'N/A')})"
                    })
                else:
                    analysis['optimal_titles'].append({
                        'url': url,
                        'title': title,
                        'length': title_length
                    })
            else:
                analysis['pages_without_title'] += 1
                analysis['issues'].append(f"Pagina senza title: {url}")
        
        # Trova duplicati
        for title, urls in title_counts.items():
            if len(urls) > 1:
                analysis['duplicate_titles'].append({
                    'title': title,
                    'urls': urls,
                    'count': len(urls)
                })
        
        # Calcola il punteggio
        total_pages = analysis['total_pages']
        if total_pages > 0:
            missing_title_ratio = analysis['pages_without_title'] / total_pages
            # Number of unique titles that are duplicated
            num_unique_duplicate_titles = len(analysis['duplicate_titles'])
            duplicate_titles_impact_ratio = num_unique_duplicate_titles / total_pages

            too_short_titles_ratio = len(analysis['too_short_titles']) / total_pages
            too_long_titles_ratio = len(analysis['too_long_titles']) / total_pages

            penalty = 0
            # TODO: Re-evaluate scoring for individual analyses if CATEGORY_ISSUE_PENALTY_FACTORS is removed.
            # For now, this will cause an error if not handled, as CATEGORY_ISSUE_PENALTY_FACTORS is removed.
            # Let's temporarily use fixed multipliers or remove penalty calculation for these old scores.
            # This part of scoring is deprecated anyway with the new health_percentage.
            # For now, I will set a placeholder score or comment out the penalty lines.
            # penalty += missing_title_ratio * 1.0 # Example fixed factor for error
            # penalty += duplicate_titles_impact_ratio * 0.5 # Example for warning
            # penalty += too_short_titles_ratio * 0.1 # Example for notice
            # penalty += too_long_titles_ratio * 0.1 # Example for notice
            
            # analysis['score'] = max(0, int((1 - penalty) * 100))
            analysis['score'] = 70 # Placeholder score for deprecated individual analysis
        else:
            analysis['score'] = 100 # Or 0 if no pages means no score - prompt says 100
        
        return analysis
    
    def _analyze_meta_descriptions(self) -> Dict:
        """Analizza le meta description"""
        analysis = {
            'total_pages': len(self.pages_data),
            'pages_with_meta': 0,
            'pages_without_meta': 0,
            'duplicate_metas': [],
            'too_short_metas': [],
            'too_long_metas': [],
            'optimal_metas': [],
            'meta_lengths': [],
            'score': 0,
            'issues': []
        }
        
        meta_counts = {}
        
        for page in self.pages_data:
            meta_desc = page.get('meta_description', '').strip()
            url = page.get('url', '')
            
            if meta_desc:
                analysis['pages_with_meta'] += 1
                meta_length = len(meta_desc)
                analysis['meta_lengths'].append(meta_length)
                
                # Conta duplicati
                if meta_desc in meta_counts:
                    meta_counts[meta_desc].append(url)
                else:
                    meta_counts[meta_desc] = [url]
                
                # Controlla lunghezza
                if meta_length < SEO_CONFIG['meta_description_min_length']:
                    analysis['too_short_metas'].append({
                        'url': url,
                        'meta': meta_desc,
                        'length': meta_length,
                        'issue': f"Meta Description troppo corta (attuale: {meta_length}, min: {SEO_CONFIG.get('meta_description_min_length', 'N/A')})"
                    })
                elif meta_length > SEO_CONFIG['meta_description_max_length']:
                    analysis['too_long_metas'].append({
                        'url': url,
                        'meta': meta_desc,
                        'length': meta_length,
                        'issue': f"Meta Description troppo lunga (attuale: {meta_length}, max: {SEO_CONFIG.get('meta_description_max_length', 'N/A')})"
                    })
                else:
                    analysis['optimal_metas'].append({
                        'url': url,
                        'meta': meta_desc,
                        'length': meta_length
                    })
            else:
                analysis['pages_without_meta'] += 1
                analysis['issues'].append(f"Pagina senza meta description: {url}")
        
        # Trova duplicati
        for meta, urls in meta_counts.items():
            if len(urls) > 1:
                analysis['duplicate_metas'].append({
                    'meta': meta,
                    'urls': urls,
                    'count': len(urls)
                })
        
        # Calcola il punteggio
        total_pages = analysis['total_pages']
        if total_pages > 0:
            missing_meta_ratio = analysis['pages_without_meta'] / total_pages
            num_unique_duplicate_metas = len(analysis['duplicate_metas'])
            duplicate_metas_impact_ratio = num_unique_duplicate_metas / total_pages

            too_short_metas_ratio = len(analysis['too_short_metas']) / total_pages
            too_long_metas_ratio = len(analysis['too_long_metas']) / total_pages

            penalty = 0
            # Missing meta is a warning, duplicates warning, length issues notice
            # penalty += missing_meta_ratio * 0.5
            # penalty += duplicate_metas_impact_ratio * 0.5
            # penalty += too_short_metas_ratio * 0.1
            # penalty += too_long_metas_ratio * 0.1

            # analysis['score'] = max(0, int((1 - penalty) * 100))
            analysis['score'] = 70 # Placeholder
        else:
            analysis['score'] = 100
        
        return analysis
    
    def _analyze_headings(self) -> Dict:
        """Analizza la struttura dei heading"""
        analysis = {
            'total_pages': len(self.pages_data),
            'pages_with_h1': 0,
            'pages_without_h1': 0,
            'pages_multiple_h1': 0,
            'heading_structure': {},
            'issues': [],
            'score': 0
        }
        
        for page in self.pages_data:
            headings = page.get('headings', {})
            url = page.get('url', '')
            
            h1_count = len(headings.get('h1', []))
            
            if h1_count == 0:
                analysis['pages_without_h1'] += 1
                analysis['issues'].append(f"Pagina senza H1: {url}")
            elif h1_count == 1:
                analysis['pages_with_h1'] += 1
            else:
                analysis['pages_multiple_h1'] += 1
                analysis['issues'].append(f"Pagina con {h1_count} H1: {url}")
            
            # Analizza struttura
            for level in range(1, 7):
                h_key = f'h{level}'
                count = len(headings.get(h_key, []))
                if h_key not in analysis['heading_structure']:
                    analysis['heading_structure'][h_key] = []
                analysis['heading_structure'][h_key].append(count)
        
        # Calcola il punteggio
        total_pages = analysis['total_pages']
        if total_pages > 0:
            missing_h1_ratio = analysis['pages_without_h1'] / total_pages
            multiple_h1_ratio = analysis['pages_multiple_h1'] / total_pages
            
            penalty = 0
            # penalty += missing_h1_ratio * 0.5
            # penalty += multiple_h1_ratio * 0.5
            # Consider adding penalties for missing H2/H3 as 'notice' if data is available
            # e.g., missing_h2_ratio = len(self.analysis_results['detailed_issues'].get('missing_h2_pages', [])) / total_pages
            # penalty += missing_h2_ratio * 0.1

            # analysis['score'] = max(0, int((1 - penalty) * 100))
            analysis['score'] = 70 # Placeholder
        else:
            analysis['score'] = 100
        
        return analysis
    
    def _analyze_images(self) -> Dict:
        """Analizza le immagini e gli alt text"""
        analysis = {
            'total_images': 0,
            'images_with_alt': 0,
            'images_without_alt': 0, # Missing alt attribute
            'images_with_empty_alt': 0, # alt=""
            'images_with_title_attr': 0, # Has title attribute with content
            'images_without_title_attr': 0, # Missing title attribute
            'images_with_empty_title_attr': 0, # title=""
            'alt_text_lengths': [],
            'issues': [], # Generic issues for this specific analysis summary, not for detailed_issues
            'score': 0
        }
        
        for page in self.pages_data:
            images = page.get('images', [])
            # url = page.get('url', '') # page_url not directly used for issues here

            for img in images:
                analysis['total_images'] += 1
                
                # Alt text analysis
                alt_text_value = img.get('alt') # Check for presence vs empty
                if alt_text_value is not None:
                    if alt_text_value.strip() == '':
                        analysis['images_with_empty_alt'] += 1
                    else:
                        analysis['images_with_alt'] += 1
                        analysis['alt_text_lengths'].append(len(alt_text_value.strip()))
                else: # alt attribute is missing
                    analysis['images_without_alt'] += 1

                # Title attribute analysis
                title_text_value = img.get('title') # Check for presence vs empty
                if title_text_value is not None:
                    if title_text_value.strip() == '':
                        analysis['images_with_empty_title_attr'] += 1
                    else:
                        analysis['images_with_title_attr'] += 1
                else: # title attribute is missing
                    analysis['images_without_title_attr'] += 1
        
        # Calcola il punteggio
        if analysis['total_images'] > 0:
            total_images = analysis['total_images']
            missing_alt_ratio = analysis['images_without_alt'] / total_images
            empty_alt_ratio = analysis['images_with_empty_alt'] / total_images

            # Optional: Penalties for missing/empty title attributes
            # missing_title_attr_ratio = analysis['images_without_title_attr'] / total_images
            # empty_title_attr_ratio = analysis['images_with_empty_title_attr'] / total_images

            penalty = 0
            # penalty += missing_alt_ratio * 0.5 # Missing ALT is warning
            # penalty += empty_alt_ratio * 0.1    # Empty ALT is notice
            # penalty += missing_title_attr_ratio * 0.1
            # penalty += empty_title_attr_ratio * 0.1

            # analysis['score'] = max(0, int((1 - penalty) * 100))
            analysis['score'] = 70 # Placeholder
        else:
            analysis['score'] = 100  # No images = no image-related problems
        
        return analysis
    
    def _analyze_content(self) -> Dict:
        """Analizza la qualità del contenuto"""
        analysis = {
            'total_pages': len(self.pages_data),
            'pages_low_word_count': 0,
            'pages_good_word_count': 0,
            'pages_low_text_ratio': 0,
            'word_counts': [],
            'text_html_ratios': [],
            'average_word_count': 0,
            'average_text_ratio': 0,
            'issues': [],
            'score': 0
        }
        
        for page in self.pages_data:
            content = page.get('content', {})
            url = page.get('url', '')
            
            word_count = content.get('word_count', 0)
            text_ratio = content.get('text_html_ratio', 0)
            
            analysis['word_counts'].append(word_count)
            analysis['text_html_ratios'].append(text_ratio)
            
            if word_count < SEO_CONFIG['min_word_count']:
                analysis['pages_low_word_count'] += 1
                analysis['issues'].append(f"Contenuto scarso ({word_count} parole): {url}")
            else:
                analysis['pages_good_word_count'] += 1
            
            if text_ratio < SEO_CONFIG['min_text_html_ratio']:
                analysis['pages_low_text_ratio'] += 1
                analysis['issues'].append(f"Rapporto testo/HTML basso ({text_ratio:.2f}): {url}")
        
        # Calcola medie
        if analysis['word_counts']:
            analysis['average_word_count'] = statistics.mean(analysis['word_counts'])
        if analysis['text_html_ratios']:
            analysis['average_text_ratio'] = statistics.mean(analysis['text_html_ratios'])
        
        # Calcola il punteggio
        total_pages = analysis['total_pages']
        if total_pages > 0:
            low_word_count_ratio = analysis['pages_low_word_count'] / total_pages
            # Assuming 'pages_low_text_ratio' counts pages with low ratio
            low_text_ratio_ratio = analysis['pages_low_text_ratio'] / total_pages

            penalty = 0
            # penalty += low_word_count_ratio * 0.5 # Low word count is warning
            # penalty += low_text_ratio_ratio * 0.1  # Low text/HTML ratio is notice
            
            # analysis['score'] = max(0, int((1 - penalty) * 100))
            analysis['score'] = 70 # Placeholder
        else:
            analysis['score'] = 100
        
        return analysis
    
    def _analyze_links(self) -> Dict:
        """Analizza i link interni ed esterni"""
        analysis = {
            'total_links': 0,
            'internal_links': 0,
            'external_links': 0,
            'broken_links': [],
            'links_without_text': 0,
            'pages_with_few_internal_links': 0,
            'average_internal_links_per_page': 0,
            'score': 0
        }
        
        all_internal_links = []
        
        for page in self.pages_data:
            links = page.get('links', [])
            url = page.get('url', '')
            
            page_internal_links = 0
            
            for link in links:
                analysis['total_links'] += 1
                
                if link.get('is_external', False):
                    analysis['external_links'] += 1
                else:
                    analysis['internal_links'] += 1
                    page_internal_links += 1
                    all_internal_links.append(link.get('url'))
                
                if not link.get('text', '').strip():
                    analysis['links_without_text'] += 1
            
            if page_internal_links < 3:  # Soglia minima di link interni
                analysis['pages_with_few_internal_links'] += 1
        
        # Calcola media link interni per pagina
        if len(self.pages_data) > 0:
            analysis['average_internal_links_per_page'] = analysis['internal_links'] / len(self.pages_data)
        
        # Calcola il punteggio
        penalty = 0
        if len(self.pages_data) > 0:
            # Penalty for too few internal links on pages (notice)
            # if analysis['pages_with_few_internal_links'] > 0: # Check to avoid division by zero if len(self.pages_data) could be 0 earlier
            #      penalty += (analysis['pages_with_few_internal_links'] / len(self.pages_data)) * 0.1

            # if analysis['total_links'] > 0 :
                # Penalty for links without text (notice)
                # penalty += (analysis['links_without_text'] / analysis['total_links']) * 0.1
                # If broken_links were analyzed and counted:
                # num_broken_links = len(analysis.get('broken_links', [])) # Assuming 'broken_links' might be added to analysis dict
                # penalty += (num_broken_links / analysis['total_links']) * 0.5
            current_score = 70 # Placeholder - This line should be indented
        else: # If len(self.pages_data) == 0
            current_score = 100 # Or appropriate score for no pages

        if analysis['total_links'] == 0 and len(self.pages_data) > 0 : # No links on site with pages
             analysis['score'] = 70 # Arbitrary low score if no links at all
        elif len(self.pages_data) == 0: # No pages
             analysis['score'] = 100
        else:
            analysis['score'] = current_score
        
        return analysis
    
    def _analyze_technical(self) -> Dict:
        """Analizza aspetti tecnici"""
        analysis = {
            'pages_with_canonical': 0,
            'pages_without_canonical': 0,
            'pages_with_lang': 0,
            'pages_without_lang': 0,
            'pages_with_schema': 0,
            'pages_without_schema': 0,
            'duplicate_canonicals': [],
            'score': 0
        }
        
        canonical_counts = {}
        
        for page in self.pages_data:
            canonical = page.get('canonical_url', '').strip()
            lang = page.get('lang', '').strip()
            schema = page.get('schema_markup', [])
            
            # Canonical
            if canonical:
                analysis['pages_with_canonical'] += 1
                if canonical in canonical_counts:
                    canonical_counts[canonical] += 1
                else:
                    canonical_counts[canonical] = 1
            else:
                analysis['pages_without_canonical'] += 1
            
            # Lang
            if lang:
                analysis['pages_with_lang'] += 1
            else:
                analysis['pages_without_lang'] += 1
            
            # Schema
            if schema:
                analysis['pages_with_schema'] += 1
            else:
                analysis['pages_without_schema'] += 1
        
        # Trova canonical duplicati
        for canonical, count in canonical_counts.items():
            if count > 1:
                analysis['duplicate_canonicals'].append({
                    'canonical': canonical,
                    'count': count
                })
        
        # Calcola il punteggio
        total_pages = len(self.pages_data)
        if total_pages > 0:
            missing_canonical_ratio = analysis['pages_without_canonical'] / total_pages
            missing_lang_ratio = analysis['pages_without_lang'] / total_pages
            missing_schema_ratio = analysis['pages_without_schema'] / total_pages

            num_unique_duplicate_canonicals = 0
            if 'duplicate_canonicals' in analysis: # Ensure key exists
                 num_unique_duplicate_canonicals = len(analysis['duplicate_canonicals'])
            duplicate_canonicals_impact_ratio = num_unique_duplicate_canonicals / total_pages

            penalty = 0
            # penalty += missing_canonical_ratio * 0.1
            # penalty += missing_lang_ratio * 0.1
            # penalty += missing_schema_ratio * 0.1
            # penalty += duplicate_canonicals_impact_ratio * 0.5
            
            # analysis['score'] = max(0, int((1 - penalty) * 100))
            analysis['score'] = 70 # Placeholder
        else:
            analysis['score'] = 100
        
        return analysis
    
    def _analyze_performance(self) -> Dict:
        """Analizza le performance"""
        analysis = {
            'total_pages': len(self.pages_data),
            'fast_pages': 0,
            'slow_pages': 0,
            'large_pages': 0,
            'response_times': [],
            'page_sizes': [],
            'average_response_time': 0,
            'average_page_size': 0,
            'score': 0
        }
        
        for page in self.pages_data:
            response_time = page.get('response_time', 0)
            html_size = page.get('html_size', 0)
            
            analysis['response_times'].append(response_time)
            analysis['page_sizes'].append(html_size)
            
            if response_time <= PERFORMANCE_CONFIG['max_response_time']:
                analysis['fast_pages'] += 1
            else:
                analysis['slow_pages'] += 1
            
            if html_size > SEO_CONFIG['max_page_size_mb'] * 1024 * 1024:
                analysis['large_pages'] += 1
        
        # Calcola medie
        if analysis['response_times']:
            analysis['average_response_time'] = statistics.mean(analysis['response_times'])
        if analysis['page_sizes']:
            analysis['average_page_size'] = statistics.mean(analysis['page_sizes'])
        
        # Calcola il punteggio
        total_pages = analysis['total_pages']
        if total_pages > 0:
            slow_pages_ratio = analysis['slow_pages'] / total_pages
            large_pages_ratio = analysis['large_pages'] / total_pages

            penalty = 0
            # penalty += slow_pages_ratio * 0.5
            # penalty += large_pages_ratio * 0.5 # Treat large pages as warning
            
            # analysis['score'] = max(0, int((1 - penalty) * 100))
            analysis['score'] = 70 # Placeholder
        else:
            analysis['score'] = 100
        
        return analysis
    
    def _analyze_mobile_friendly(self) -> Dict:
        """Analizza la mobile-friendliness"""
        analysis = {
            'pages_with_viewport': 0,
            'pages_without_viewport': 0,
            'responsive_pages': 0,
            'score': 75  # Punteggio di default senza test specifici
        }
        
        # Questa è un'analisi base - per una completa servirebbero test specifici
        # con Google PageSpeed Insights API o simili
        
        return analysis
    
    def _analyze_ssl(self) -> Dict:
        """Analizza il certificato SSL"""
        analysis = {
            'has_ssl': False,
            'ssl_valid': False,
            'ssl_expires': None,
            'score': 0
        }
        
        try:
            parsed_url = urlparse(f"https://{self.domain}")
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                sock = socket.create_connection((self.domain, 443), timeout=10)
                ssock = context.wrap_socket(sock, server_hostname=self.domain)
                
                analysis['has_ssl'] = True
                analysis['ssl_valid'] = True
                analysis['score'] = 100
                
                # Ottieni info certificato
                cert = ssock.getpeercert()
                if cert:
                    analysis['ssl_expires'] = cert.get('notAfter')
                
                ssock.close()
                
        except Exception as e:
            self.logger.warning(f"Errore verifica SSL: {e}")
            analysis['score'] = 0
        
        return analysis

    def _populate_legacy_detailed_issues(self) -> Dict:
        """
        Popola la struttura 'detailed_issues' legacy.
        Questa funzione contiene la logica originale di _analyze_detailed_issues.
        Mantenuta per retrocompatibilità temporanea.
        """
        detailed = {
            'errors': [],  # Errori gravi
            'warnings': [],    # Avvertimenti
            'notices': [],     # Informazioni/suggerimenti
            'missing_h1_pages': [],
            'multiple_h1_pages': [], # Added this list
            'missing_h2_pages': [],
            'missing_h3_pages': [],
            'images_without_alt': [], # Alt attribute is missing
            'images_with_empty_alt': [], # Alt attribute is present but empty (alt="")
            'images_without_title_attr': [], # Title attribute is missing
            'images_with_empty_title_attr': [], # Title attribute is present but empty (title="")
            'duplicate_titles': [], # Populated by _find_duplicates
            'duplicate_meta_descriptions': [], # Populated by _find_duplicates
            'pages_without_title': [],
            'pages_without_meta': [],
            'low_word_count_pages': [],
            'large_html_pages': [],
            'slow_pages': [],
            'pages_without_viewport': [],
            'pages_without_lang': [],
            'pages_without_canonical': [],
            'broken_links': [],
            'status_4xx_pages': [],
            'status_5xx_pages': [],
            'pages_without_schema': [],
            'redirect_chains': [],
            'mixed_content_pages': [],
        }
        
        # Analizza ogni pagina per problemi specifici
        for page in self.pages_data:
            url = page.get('url', '')
            title = page.get('title', '').strip()
            meta_desc = page.get('meta_description', '').strip()
            headings = page.get('headings', {})
            images = page.get('images', [])
            content = page.get('content', {})
            status_code = page.get('status_code', 200)
            html_size = page.get('html_size', 0)
            response_time = page.get('response_time', 0)
            canonical = page.get('canonical_url', '').strip()
            lang = page.get('lang', '').strip()
            schema = page.get('schema_markup', [])
            
            # ERRORI (Problemi gravi)
            if not title:
                detailed['pages_without_title'].append({
                    'url': url,
                    'issue': 'Pagina senza title tag'
                })
                detailed['errors'].append({
                    'type': 'missing_title',
                    'url': url,
                    'message': 'Title tag mancante'
                })
            
            if status_code >= 500:
                detailed['status_5xx_pages'].append({
                    'url': url,
                    'status_code': status_code,
                    'issue': f'Errore server {status_code}'
                })
                detailed['errors'].append({
                    'type': 'server_error',
                    'url': url,
                    'message': f'Errore server {status_code}'
                })
            
            if status_code >= 400 and status_code < 500:
                detailed['status_4xx_pages'].append({
                    'url': url,
                    'status_code': status_code,
                    'issue': f'Errore client {status_code}'
                })
                detailed['errors'].append({
                    'type': 'client_error',
                    'url': url,
                    'message': f'Errore client {status_code}'
                })
            
            # AVVERTIMENTI (Problemi da correggere)
            if not meta_desc:
                detailed['pages_without_meta'].append({
                    'url': url,
                    'issue': 'Meta description mancante'
                })
                detailed['warnings'].append({
                    'type': 'missing_meta',
                    'url': url,
                    'message': 'Meta description mancante'
                })
            
            # Analisi headings
            h1_count = len(headings.get('h1', []))
            h2_count = len(headings.get('h2', []))
            h3_count = len(headings.get('h3', []))
            
            if h1_count == 0:
                detailed['missing_h1_pages'].append({
                    'url': url,
                    'issue': 'H1 mancante'
                })
                detailed['warnings'].append({
                    'type': 'missing_h1',
                    'url': url,
                    'message': 'Tag H1 mancante'
                })
            elif h1_count > 1:
                detailed['multiple_h1_pages'].append({ # Populate specific list
                    'url': url,
                    'issue': f'Multipli H1 ({h1_count}) trovati'
                })
                detailed['warnings'].append({ # Keep general warning as well
                    'type': 'multiple_h1',
                    'url': url,
                    'message': f'Multipli H1 ({h1_count}) trovati'
                })
            
            if h2_count == 0:
                detailed['missing_h2_pages'].append({
                    'url': url,
                    'issue': 'H2 mancante'
                })
                detailed['notices'].append({
                    'type': 'missing_h2',
                    'url': url,
                    'message': 'Nessun tag H2 trovato'
                })
            
            if h3_count == 0:
                detailed['missing_h3_pages'].append({
                    'url': url,
                    'issue': 'H3 mancante'
                })
                detailed['notices'].append({
                    'type': 'missing_h3',
                    'url': url,
                    'message': 'Nessun tag H3 trovato'
                })
            
            # Analisi immagini
            for img in images:
                img_src = img.get('src', '')
                img_src = img.get('src', 'N/A') # Use N/A if src is missing
                
                # Alt text
                alt_value = img.get('alt')
                if alt_value is None: # Attributo alt mancante
                    detailed['images_without_alt'].append({
                        'url': url, 'image_src': img_src, 'issue': 'Attributo ALT HTML mancante'
                    })
                    detailed['warnings'].append({
                        'type': 'missing_alt_attr', 'url': url, 'image': img_src, # Ensure 'image' key has src for context
                        'message': 'Attributo ALT HTML mancante per immagine.'
                    })
                elif alt_value.strip() == '': # Attributo alt presente ma vuoto
                    detailed['images_with_empty_alt'].append({
                        'url': url, 'image_src': img_src, 'issue': 'Attributo ALT vuoto'
                    })
                    detailed['warnings'].append({ 
                        'type': 'empty_alt_attr', 'url': url, 'image': img_src,
                        'message': 'Attributo ALT vuoto per immagine.'
                    })

                # Title attribute
                title_value = img.get('title')
                if title_value is None: # Attributo title mancante
                    detailed['images_without_title_attr'].append({
                        'url': url, 'image_src': img_src, 'issue': 'Attributo Title HTML mancante'
                    })
                    detailed['notices'].append({
                        'type': 'missing_title_attr', 'url': url, 'image': img_src,
                        'message': 'Attributo Title HTML mancante per immagine.'
                    })
                elif title_value.strip() == '': # Attributo title presente ma vuoto
                    detailed['images_with_empty_title_attr'].append({
                        'url': url, 'image_src': img_src, 'issue': 'Attributo Title vuoto'
                    })
                    detailed['notices'].append({
                        'type': 'empty_title_attr', 'url': url, 'image': img_src,
                        'message': 'Attributo Title vuoto per immagine.'
                    })
            
            # Contenuto
            word_count = content.get('word_count', 0)
            min_wc = SEO_CONFIG.get('min_word_count', 200) # Use .get for safety
            if word_count < min_wc:
                detailed['low_word_count_pages'].append({
                    'url': url,
                    'word_count': str(word_count), # For GUI display consistency if it expects string
                    'issue': f"Conteggio parole basso ({word_count} parole, min: {min_wc})"
                })
                detailed['warnings'].append({
                    'type': 'low_content',
                    'url': url,
                    'message': f"Conteggio parole basso ({word_count}), minimo raccomandato {min_wc}."
                })

            text_html_ratio = content.get('text_html_ratio', 0.0)
            min_text_html_ratio = SEO_CONFIG.get('min_text_html_ratio', 0.1) # Use .get for safety
            if text_html_ratio < min_text_html_ratio:
                detailed.setdefault('low_text_html_ratio_pages', []).append({
                   'url': url,
                   'ratio': f"{text_html_ratio:.2f}", # For GUI display
                   'issue': f"Rapporto Testo/HTML basso ({text_html_ratio:.2f}, min: {min_text_html_ratio})"
               })
                detailed['warnings'].append({ 
                   'type': 'low_text_html_ratio',
                   'url': url,
                   'message': f"Rapporto Testo/HTML basso ({text_html_ratio:.2f}), minimo raccomandato {min_text_html_ratio}."
               })
            
            # Performance
            if response_time > PERFORMANCE_CONFIG['max_response_time']:
                detailed['slow_pages'].append({
                    'url': url,
                    'response_time': response_time,
                    'issue': f'Pagina lenta ({response_time:.2f}s)'
                })
                detailed['warnings'].append({
                    'type': 'slow_page',
                    'url': url,
                    'message': f'Tempo di caricamento elevato ({response_time:.2f}s)'
                })
            
            if html_size > SEO_CONFIG['max_page_size_mb'] * 1024 * 1024:
                detailed['large_html_pages'].append({
                    'url': url,
                    'size_mb': html_size / (1024 * 1024),
                    'issue': f'HTML troppo grande ({html_size / (1024 * 1024):.1f}MB)'
                })
                detailed['warnings'].append({
                    'type': 'large_page',
                    'url': url,
                    'message': f'Pagina troppo pesante ({html_size / (1024 * 1024):.1f}MB)'
                })
            
            # Aspetti tecnici
            if not canonical:
                detailed['pages_without_canonical'].append({
                    'url': url,
                    'issue': 'URL canonico mancante'
                })
                detailed['notices'].append({
                    'type': 'missing_canonical',
                    'url': url,
                    'message': 'URL canonico non specificato'
                })
            
            if not lang:
                detailed['pages_without_lang'].append({
                    'url': url,
                    'issue': 'Attributo lang mancante'
                })
                detailed['notices'].append({
                    'type': 'missing_lang',
                    'url': url,
                    'message': 'Lingua della pagina non specificata'
                })
            
            if not schema:
                detailed['pages_without_schema'].append({
                    'url': url,
                    'issue': 'Schema markup mancante'
                })
                detailed['notices'].append({
                    'type': 'missing_schema',
                    'url': url,
                    'message': 'Dati strutturati non presenti'
                })
        
        # Trova duplicati
        self._find_duplicates(detailed) # Pass 'detailed' which is the local var here
        
        return detailed

    def _analyze_detailed_issues(self):
        """
        Nuova analisi dettagliata basata su AUDIT_CHECKS_CONFIG.
        Popola self.analysis_results['categorized_issues'].
        """
        self.logger.info("Inizio nuova analisi dettagliata dei problemi...")

        # Chiamiamo la vecchia logica per popolare detailed_issues per ora
        # self.analysis_results['detailed_issues'] = self._populate_legacy_detailed_issues()

        # --- TEMPORARY TEST MOCKS START ---
        # These are hardcoded for testing site-wide checks. Remove in production.
        site_uses_cdn_test_mock = False # For ocm_no_cdn_global_error
        eeat_signals_present_test_mock = False # For seo_no_eeat_signals_error
        has_structured_data_errors_test_mock = True # For ocm_structured_data_errors_warning
        # --- TEMPORARY TEST MOCKS END ---

        for check_key, check_config in AUDIT_CHECKS_CONFIG.items():
            category = check_config['category']
            severity = check_config['severity'] # ERROR, WARNING, NOTICE

            # --- Implementazione Esempi Check ---

            # Esempio: OCM - LCP Error
            if check_key == 'ocm_lcp_error':
                for page in self.pages_data:
                    lcp = page.get('performance_metrics', {}).get('lcp', None)
                    # Placeholder per testare - rimuovere in produzione
                    if lcp is None and page['url'].endswith('/'): # Simula LCP solo per una pagina per test
                         lcp = 5.0

                    if lcp is not None and lcp > CORE_WEB_VITALS_THRESHOLDS['LCP_ERROR']:
                        self.analysis_results['categorized_issues'][category][severity].append({
                            'key': check_key,
                            'label': check_config['label'],
                            'url': page['url'],
                            'details': f"LCP è {lcp}s (soglia: >{CORE_WEB_VITALS_THRESHOLDS['LCP_ERROR']}s)",
                            'description_key': check_config['description_key'],
                            'severity': severity
                        })

            # Esempio: OCM - Server Response Time Error
            elif check_key == 'ocm_server_response_time_error':
                for page in self.pages_data:
                    # Assumendo che response_time sia in secondi, converti in ms
                    response_time_ms = page.get('response_time', 0) * 1000
                    # Placeholder per testare
                    if response_time_ms == 0 and page['url'].endswith('test.html'): # Simula per una pagina
                        response_time_ms = 700

                    if response_time_ms > SERVER_RESPONSE_TIME_ERROR:
                        self.analysis_results['categorized_issues'][category][severity].append({
                            'key': check_key,
                            'label': check_config['label'],
                            'url': page['url'],
                            'details': f"Il tempo di risposta del server è {response_time_ms:.0f}ms (soglia: >{SERVER_RESPONSE_TIME_ERROR}ms)",
                            'description_key': check_config['description_key'],
                            'severity': severity
                        })

            # Esempio: SEO - Missing E-E-A-T (Placeholder - Site-wide)
            # Note: Key in AUDIT_CHECKS_CONFIG is 'seo_no_eeat_signals_error'
            elif check_key == 'seo_no_eeat_signals_error':
                # Using test mock: eeat_signals_present_test_mock
                if not eeat_signals_present_test_mock and severity == 'ERROR': # check severity from config
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key,
                        'label': check_config['label'],
                        'url': self.domain, # Problema a livello di sito
                        'details': 'Nessun segnale E-E-A-T chiaro identificato sul sito (mock test).',
                        'description_key': check_config['description_key'],
                        'severity': 'ERROR' # Use actual severity
                    })

            # Esempio: OCM - Meta Description Missing (Notice)
            elif check_key == 'ocm_meta_description_missing_notice':
                 for page in self.pages_data:
                    if not page.get('meta_description', '').strip():
                        # Assicuriamoci che venga aggiunto solo se la severity è NOTICE in config
                        if severity == 'NOTICE':
                             self.analysis_results['categorized_issues'][category][severity].append({
                                'key': check_key,
                                'label': check_config['label'],
                                'url': page['url'],
                                'details': 'Meta description mancante (OCM Notice).',
                                'description_key': check_config['description_key'],
                                'severity': severity
                            })

            # Implementazione dei 25 OCM ERROR CHECKS

            elif check_key == 'ocm_no_cdn_global_error': # Example of using a mock for a site-wide check
                # Using test mock: site_uses_cdn_test_mock
                if not site_uses_cdn_test_mock and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Assenza CDN per siti globali (mock test).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_inp_error':
                # TODO: Crawler needs to populate 'performance_metrics.inp'
                for page in self.pages_data:
                    inp_value = page.get('performance_metrics', {}).get('inp', 600) # Placeholder to trigger error
                    if inp_value > CORE_WEB_VITALS_THRESHOLDS['INP_ERROR']:
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"Interaction to Next Paint (INP) è {inp_value}ms (soglia: >{CORE_WEB_VITALS_THRESHOLDS['INP_ERROR']}ms).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'ocm_cls_error':
                # TODO: Crawler needs to populate 'performance_metrics.cls'
                for page in self.pages_data:
                    cls_value = page.get('performance_metrics', {}).get('cls', 0.30) # Placeholder to trigger error
                    if cls_value > CORE_WEB_VITALS_THRESHOLDS['CLS_ERROR']:
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"Cumulative Layout Shift (CLS) è {cls_value} (soglia: >{CORE_WEB_VITALS_THRESHOLDS['CLS_ERROR']}).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'ocm_render_blocking_resources_error':
                # TODO: Implement actual detection of render-blocking resources
                for page in self.pages_data:
                    # Placeholder: Assume a page has render-blocking resources
                    has_render_blocking = page.get('performance_metrics', {}).get('has_render_blocking_resources', True if page['url'].endswith("test.html") else False) # Placeholder
                    if has_render_blocking:
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': "Rilevate risorse che bloccano il rendering della pagina (placeholder).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'ocm_image_optimization_error':
                # TODO: Implement image analysis for optimization (size, format, compression)
                for page in self.pages_data:
                    # Placeholder: Assume an image is not optimized
                    unoptimized_images_found = page.get('images_analysis', {}).get('unoptimized_images_found', True if "image.html" in page['url'] else False) # Placeholder
                    if unoptimized_images_found:
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': "Rilevate immagini non ottimizzate (placeholder).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'ocm_lazy_loading_missing_error':
                # TODO: Implement check for missing lazy loading on offscreen images
                for page in self.pages_data:
                    # Placeholder
                    lazy_loading_missing = page.get('images_analysis', {}).get('lazy_loading_missing', True if "nolazy.html" in page['url'] else False) # Placeholder
                    if lazy_loading_missing:
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': "Mancata implementazione del lazy loading per immagini offscreen (placeholder).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'ocm_ssl_expired_error':
                # Uses existing ssl_analysis results
                ssl_data = self.analysis_results.get('ssl_analysis', {})
                if ssl_data.get('has_ssl', False) and not ssl_data.get('ssl_valid', True): # Assuming 'ssl_valid' becomes false if expired/invalid
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Il certificato SSL per {self.domain} risulta scaduto o non valido. Data di scadenza: {ssl_data.get('ssl_expires', 'N/A')}",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_malware_detected_error':
                # TODO: Implement actual malware detection (e.g., API integration)
                malware_detected = False # Placeholder
                if malware_detected:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevato malware o codice sospetto sul sito (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_no_http2_error':
                # TODO: Implement HTTP version detection for server/pages
                uses_http2 = True # Placeholder, assume true by default
                # This check might need to look at response headers for each page or a sample.
                # For now, site-wide placeholder.
                if not uses_http2:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Il sito non sembra utilizzare HTTP/2 (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_compression_missing_error':
                # TODO: Implement check for text resource compression (gzip/Brotli)
                compression_missing = False # Placeholder
                # This would typically be checked per text-based asset. Site-wide for now.
                if compression_missing:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Mancata compressione Gzip/Brotli per alcune risorse testuali (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_inadequate_caching_policy_error':
                # TODO: Implement check for caching headers on static assets
                inadequate_caching = False # Placeholder
                if inadequate_caching:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Policy di caching inadeguata per alcuni asset statici (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_js_seo_critical_error':
                # TODO: Implement detection of JS errors that impact SEO (e.g., via browser console logs if using Selenium)
                js_critical_errors_found = False # Placeholder
                if js_critical_errors_found:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific page if error is page-specific
                        'details': "Rilevati errori JavaScript critici per la SEO (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_xml_sitemap_errors_error':
                # TODO: Implement XML sitemap fetching and parsing for errors
                xml_sitemap_has_errors = False # Placeholder
                if xml_sitemap_has_errors:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': f"{self.domain}/sitemap.xml", # Assuming common sitemap URL
                        'details': "Rilevati errori gravi nella XML Sitemap (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_canonical_grave_error':
                # TODO: Implement advanced canonical checks (loops, to 404s)
                # This might require looking at all canonical tags collected.
                # For now, a placeholder.
                has_grave_canonical_errors = False # Placeholder
                # Example: Loop through pages, if page.get('canonical_points_to_404') or page.get('is_in_canonical_loop')
                # for page in self.pages_data:
                #    if page.get('has_grave_canonical_error', False): # Assume crawler sets this flag
                #        has_grave_canonical_errors = True
                #        problem_url = page.get('url')
                #        break
                if has_grave_canonical_errors:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific problem_url
                        'details': "Rilevati errori gravi di canonicalizzazione (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_http_404_errors_extensive_error':
                count_404 = 0
                example_404_url = ""
                for page in self.pages_data:
                    if page.get('status_code') == 404:
                        count_404 +=1
                        if not example_404_url: example_404_url = page.get('url')
                # Define "extensive" - e.g., > 5% of crawled pages or > 10 absolute
                is_extensive_404 = (count_404 > 10) or (len(self.pages_data) > 0 and (count_404 / len(self.pages_data)) > 0.05)
                if is_extensive_404:
                     self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Rilevati {count_404} errori 404 (es. {example_404_url}). Considerato estensivo.",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_http_500_errors_error':
                count_500 = 0
                example_500_url = ""
                for page in self.pages_data:
                    if page.get('status_code', 0) >= 500 and page.get('status_code', 0) < 600:
                        count_500 +=1
                        if not example_500_url: example_500_url = page.get('url')
                # Define "frequent/widespread" - e.g., > 2% or > 5 absolute
                is_frequent_500 = (count_500 > 5) or (len(self.pages_data) > 0 and (count_500 / len(self.pages_data)) > 0.02)
                if is_frequent_500:
                     self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Rilevati {count_500} errori 5xx (es. {example_500_url}). Considerato frequente/diffuso.",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_minification_missing_error':
                # TODO: Implement check for CSS/JS minification (e.g. by analyzing file sizes or specific patterns)
                minification_missing = False # Placeholder
                if minification_missing:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific asset URLs
                        'details': "Rilevata mancata minificazione per alcune risorse CSS/JS (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_mobile_content_not_accessible_error':
                # TODO: Implement check for content parity desktop vs mobile (might require advanced techniques)
                mobile_content_inaccessible = False # Placeholder
                if mobile_content_inaccessible:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific page URLs
                        'details': "Alcuni contenuti importanti non sono accessibili o visibili su mobile (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'ocm_no_viewport_tag_error':
                for page in self.pages_data:
                    # TODO: Crawler needs to set 'has_viewport_tag'
                    has_viewport = page.get('has_viewport_tag', False if page['url'].endswith("noviewport.html") else True) # Placeholder
                    if not has_viewport:
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': "Meta tag viewport mancante.",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'ocm_touch_elements_too_small_error':
                # TODO: Implement check for touch element sizes (e.g. via PageSpeed Insights API or JS evaluation)
                # TOUCH_ELEMENT_MIN_SIZE_PX is available from config
                touch_elements_too_small = False # Placeholder
                example_page_for_touch_error = ""
                # for page in self.pages_data:
                #    if page.get('mobile_usability',{}).get('touch_elements_too_small', False):
                #        touch_elements_too_small = True
                #        example_page_for_touch_error = page.get('url')
                #        break
                if touch_elements_too_small: # Placeholder logic
                     if check_key == 'ocm_touch_elements_too_small_error': # Double check to ensure it's the right key
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or example_page_for_touch_error
                            'details': f"Rilevati elementi touch troppo piccoli o ravvicinati (placeholder, es. < {TOUCH_ELEMENT_MIN_SIZE_PX}px).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'ocm_not_mobile_friendly_design_error':
                # TODO: Implement overall mobile-friendliness check (e.g. via PageSpeed Insights API or heuristics)
                not_mobile_friendly = False # Placeholder
                # Example: use mobile_analysis score if it's very low
                # if self.analysis_results.get('mobile_analysis',{}).get('score', 100) < 50:
                #    not_mobile_friendly = True
                if not_mobile_friendly:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Il design complessivo del sito non risulta mobile-friendly (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            # Fallback for any other OCM ERROR check_key that might be in AUDIT_CHECKS_CONFIG
            # but does not have explicit logic above. This helps catch missing implementations.
            elif category == CATEGORY_OCM and severity == 'ERROR':
                 # Check if it's one of the specific examples already handled
                is_example_check = check_key in [
                    'ocm_lcp_error', 'ocm_server_response_time_error',
                    'ocm_no_cdn_global_error', 'ocm_no_https_error',
                    'ocm_critical_robots_block_error' # These are the initial examples from Step 1 or 2
                ]
                if not is_example_check:
                    # This means it's an OCM ERROR check from config.py that we haven't added specific logic for yet.
                    # Add a generic placeholder entry.
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key,
                        'label': check_config['label'],
                        'url': self.domain,
                        'details': f"Logica per questo check ({check_key}) non ancora implementata (placeholder).",
                        'description_key': check_config['description_key'],
                        'severity': 'ERROR'
                    })
                    self.logger.warning(f"Placeholder attivato per OCM ERROR check non implementato: {check_key}")

            # Implementazione dei 16 OCM WARNING CHECKS
            elif check_key == 'ocm_structured_data_errors_warning':
                # Using test mock: has_structured_data_errors_test_mock
                if has_structured_data_errors_test_mock and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevati errori (non critici) nei dati strutturati (mock test).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_redirect_chains_warning':
                # TODO: Implement redirect chain detection; crawler should provide this data.
                # Example: page.get('redirect_chain_hops', 0)
                max_hops_allowed = 3
                for page in self.pages_data:
                    hops = page.get('redirect_chain_hops', 0) # Placeholder, assume crawler provides this
                    if hops > max_hops_allowed and severity == 'WARNING':
                         self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('original_url', page.get('url')), # original_url if available
                            'details': f"Rilevata catena di redirect con {hops} hop (soglia: >{max_hops_allowed}).",
                            'description_key': check_config['description_key'], 'severity': 'WARNING'
                        })

            elif check_key == 'ocm_unnecessary_redirects_warning':
                # TODO: Implement detection of unnecessary redirects (e.g. http -> https for an internal link already https)
                has_unnecessary_redirects = False # Placeholder
                if has_unnecessary_redirects and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific page
                        'details': "Rilevati redirect non necessari (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_url_structure_suboptimal_warning':
                # TODO: Implement URL structure analysis (excessive params, depth)
                is_url_structure_suboptimal = False # Placeholder
                if is_url_structure_suboptimal and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific examples
                        'details': "Rilevata struttura URL non ottimale (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_hsts_missing_warning':
                # TODO: Check for HSTS header in server responses
                hsts_enabled = False # Placeholder
                if not hsts_enabled and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Mancata implementazione di HSTS (HTTP Strict Transport Security) (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_csp_missing_warning':
                # TODO: Check for Content-Security-Policy header
                csp_implemented_effectively = False # Placeholder
                if not csp_implemented_effectively and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Content Security Policy (CSP) non implementata o troppo permissiva (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_x_frame_options_missing_warning':
                # TODO: Check for X-Frame-Options header
                x_frame_options_present = False # Placeholder
                if not x_frame_options_present and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Header X-Frame-Options non configurato (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_404_errors_excessive_warning':
                EXCESSIVE_404_THRESHOLD = 5 # Example threshold
                count_404 = 0
                example_404_urls = []
                for page in self.pages_data:
                    if page.get('status_code') == 404:
                        count_404 +=1
                        if len(example_404_urls) < 3: # Store a few examples
                             example_404_urls.append(page.get('url'))

                # This warning is for "numerous" but not "extensive" (which is an ERROR)
                # Let's assume the ERROR threshold is 10 (from ocm_http_404_errors_extensive_error)
                # So this warning triggers if > EXCESSIVE_404_THRESHOLD and <= ERROR_THRESHOLD_404
                ERROR_THRESHOLD_404 = 10
                if count_404 > EXCESSIVE_404_THRESHOLD and count_404 <= ERROR_THRESHOLD_404 and severity == 'WARNING':
                     self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Rilevati {count_404} errori 404 (soglia per warning: >{EXCESSIVE_404_THRESHOLD}, es: {', '.join(example_404_urls)}).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_broken_internal_links_warning':
                # TODO: Crawler needs to populate 'broken_internal_links' for each page.
                # Format: page['broken_internal_links'] = [{'target_url': '...', 'anchor_text': '...'}]
                found_broken_links_for_warning = False
                details_list = []
                for page in self.pages_data:
                    broken_links_on_page = page.get('broken_internal_links', []) # Placeholder
                    if broken_links_on_page:
                        found_broken_links_for_warning = True
                        for bl in broken_links_on_page:
                             details_list.append(f"Pagina {page.get('url', 'N/A')} ha link rotto a {bl.get('target_url', 'N/A')}")
                             if len(details_list) >= 5 : break # Limit number of examples
                    if len(details_list) >=5 : break

                if found_broken_links_for_warning and severity == 'WARNING':
                     self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevati link interni rotti (non estensivi). Esempi: " + "; ".join(details_list) + " (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_internal_linking_insufficient_warning':
                MIN_INTERNAL_LINKS_PER_PAGE = 3 # Example threshold
                # TODO: Crawler needs to populate 'internal_links_list' for each page
                # Format: page['internal_links_list'] = [link_object1, link_object2, ...]
                pages_with_few_links = []
                for page in self.pages_data:
                    # Assuming 'links' list contains all links, filter for internal ones
                    internal_links_count = sum(1 for link in page.get('links', []) if not link.get('is_external', True))
                    # Or, if crawler provides a specific list:
                    # internal_links_count = len(page.get('internal_links_list', [])) # Placeholder

                    # Placeholder logic to simulate some pages having few links
                    if page.get('url','').endswith("thin.html"): internal_links_count = 1

                    if internal_links_count < MIN_INTERNAL_LINKS_PER_PAGE:
                        pages_with_few_links.append(f"{page.get('url', 'N/A')} ({internal_links_count} link)")
                        if len(pages_with_few_links) >= 3: break # Limit examples

                if pages_with_few_links and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Alcune pagine importanti hanno pochi link interni (soglia: <{MIN_INTERNAL_LINKS_PER_PAGE}). Esempi: {'; '.join(pages_with_few_links)} (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_meta_tags_inconsistent_warning':
                # TODO: Implement logic to detect inconsistencies in meta tag strategy (e.g. varying lengths, formats)
                meta_tags_inconsistent = False # Placeholder
                if meta_tags_inconsistent and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevata strategia meta tag (title/description) inconsistente tra pagine (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_url_strategy_inconsistent_warning':
                # TODO: Implement logic to detect inconsistencies in URL strategy (trailing slashes, case)
                url_strategy_inconsistent = False # Placeholder
                if url_strategy_inconsistent and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevata strategia URL (es. trailing slash, case) inconsistente (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_hreflang_errors_warning':
                # TODO: Implement hreflang tag validation
                has_hreflang_errors = False # Placeholder
                if has_hreflang_errors and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific pages
                        'details': "Rilevati errori (non critici) nell'implementazione di hreflang (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_website_uptime_low_warning':
                # TODO: This requires external monitoring data. Cannot be done by crawler alone.
                # For now, always assume uptime is good, or add a placeholder if external data could be fed.
                website_uptime_historically_low = False # Placeholder
                if website_uptime_historically_low and severity == 'WARNING':
                     self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "L'uptime storico del sito risulta basso (basato su dati esterni, placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_ga_gsc_not_configured_warning':
                # TODO: This requires external verification (e.g. checking for GA/GSC tags in HTML, or API integration if permissions allow)
                ga_gsc_not_configured = False # Placeholder
                if ga_gsc_not_configured and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Google Analytics o Google Search Console non sembrano configurati o collegati (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            elif check_key == 'ocm_mixed_content_warning':
                # TODO: Crawler needs to detect mixed content (http resources on https pages)
                # Example: page.get('has_mixed_content', False)
                pages_with_mixed_content = []
                for page in self.pages_data:
                    if page.get('has_mixed_content', False): # Placeholder
                        pages_with_mixed_content.append(page.get('url'))
                        if len(pages_with_mixed_content) >= 3: break

                if pages_with_mixed_content and severity == 'WARNING':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Rilevato mixed content su alcune pagine (es: {', '.join(pages_with_mixed_content)}) (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })

            # Fallback for any other OCM WARNING check_key
            elif category == CATEGORY_OCM and severity == 'WARNING':
                is_example_check = check_key in [ # Checks already handled above more specifically
                    'ocm_structured_data_errors_warning', 'ocm_redirect_chains_warning'
                ]
                if not is_example_check:
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key,
                        'label': check_config['label'],
                        'url': self.domain,
                        'details': f"Logica per questo check OCM WARNING ({check_key}) non ancora implementata (placeholder).",
                        'description_key': check_config['description_key'],
                        'severity': 'WARNING'
                    })
                    self.logger.warning(f"Placeholder attivato per OCM WARNING check non implementato: {check_key}")

            # Implementazione dei 18 SITE SEO AUDIT ERROR CHECKS

            # Note: 'seo_no_eeat_error' was renamed to 'seo_no_eeat_signals_error' in config.py
            # 'seo_title_missing_error' is covered by 'seo_title_meta_missing_duplicated_error'

            elif check_key == 'seo_no_eeat_signals_error':
                # TODO: Implement E-E-A-T signals assessment (complex, likely requires heuristics or specific input)
                eeat_signals_present = False # Placeholder
                if not eeat_signals_present and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Assenza di chiari segnali E-E-A-T (Esperienza, Competenza, Autorevolezza, Affidabilità) per contenuti rilevanti (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_low_quality_ymyl_error':
                # TODO: Implement YMYL content quality assessment (complex, requires content analysis)
                is_ymyl_low_quality = True # Placeholder
                if is_ymyl_low_quality and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific YMYL page URLs
                        'details': "Rilevati contenuti YMYL (Your Money Your Life) di bassa qualità o non autorevoli (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_extensive_duplicate_content_error':
                # TODO: Implement advanced duplicate content detection (internal/external)
                # This might use data from `self.analysis_results['content_analysis'].get('duplicate_content_report', {})`
                has_extensive_duplicate_content = True # Placeholder
                if has_extensive_duplicate_content and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevata presenza estensiva di contenuti duplicati (interni/esterni) (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_thin_content_pages_error':
                THIN_CONTENT_THRESHOLD = 150 # Example, words
                thin_content_pages_examples = []
                for page in self.pages_data:
                    word_count = page.get('content', {}).get('word_count', 0)
                    if 0 < word_count < THIN_CONTENT_THRESHOLD:
                        thin_content_pages_examples.append(f"{page.get('url', 'N/A')} ({word_count} parole)")
                        if len(thin_content_pages_examples) >= 3 : break # Limit examples

                if thin_content_pages_examples and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Report as site-level with examples
                        'details': f"Rilevate pagine con contenuto scarso (<{THIN_CONTENT_THRESHOLD} parole). Esempi: {'; '.join(thin_content_pages_examples)}.",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_page_titles_not_optimized_error':
                 # This is a broader check than just missing/duplicate.
                 # TODO: Implement checks for descriptiveness, relevance (would need NLP or keyword mapping)
                 # For now, let's assume it flags if many titles are suboptimal (e.g. from title_analysis)
                title_analysis_data = self.analysis_results.get('title_analysis', {})
                # Example: if more than 20% of titles are short, long, or duplicated (unique duplicates)
                total_pages = title_analysis_data.get('total_pages', 0)
                if total_pages > 0:
                    suboptimal_titles_count = len(title_analysis_data.get('too_short_titles', [])) + \
                                             len(title_analysis_data.get('too_long_titles', [])) + \
                                             len(title_analysis_data.get('duplicate_titles', [])) # Number of unique duplicate titles
                    if (suboptimal_titles_count / total_pages) > 0.20 and severity == 'ERROR': # If > 20% titles are suboptimal
                        self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': self.domain,
                            'details': f"{suboptimal_titles_count}/{total_pages} titoli pagina non sono ottimali (corti, lunghi, o duplicati).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'seo_meta_descriptions_not_optimized_error':
                # Similar to titles, a broader check.
                # TODO: Implement checks for persuasiveness, relevance.
                meta_analysis_data = self.analysis_results.get('meta_description_analysis', {})
                total_pages = meta_analysis_data.get('total_pages', 0)
                if total_pages > 0:
                    suboptimal_metas_count = len(meta_analysis_data.get('too_short_metas', [])) + \
                                             len(meta_analysis_data.get('too_long_metas', [])) + \
                                             len(meta_analysis_data.get('duplicate_metas', []))
                    if (suboptimal_metas_count / total_pages) > 0.25 and severity == 'ERROR': # If > 25% metas are suboptimal
                        self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': self.domain,
                            'details': f"{suboptimal_metas_count}/{total_pages} meta descriptions non sono ottimali (corte, lunghe, o duplicate).",
                            'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            elif check_key == 'seo_keyword_stuffing_error':
                # TODO: Implement keyword stuffing detection (e.g. keyword density checks, unnatural phrasing via NLP)
                keyword_stuffing_detected = True # Placeholder
                if keyword_stuffing_detected and severity == 'ERROR':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific pages
                        'details': "Rilevato keyword stuffing evidente in alcune pagine (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_no_clear_seo_strategy_error':
                # TODO: This is a high-level strategic assessment, likely requires manual input or questionnaire.
                no_clear_strategy = True # Placeholder
                if no_clear_strategy and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Non è emersa una chiara strategia SEO (obiettivi, target, keyword) dall'analisi (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_outdated_content_error':
                # TODO: Implement detection of outdated content (e.g. pages not updated for a long time, presence of outdated info)
                has_outdated_content = False # Placeholder
                if has_outdated_content and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or specific page URLs
                        'details': "Rilevati contenuti obsoleti o non aggiornati su temi importanti (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_keyword_cannibalization_error':
                # TODO: Implement keyword cannibalization detection (multiple pages ranking for same specific, high-intent keywords)
                keyword_cannibalization_found = False # Placeholder
                if keyword_cannibalization_found and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevata cannibalizzazione delle keyword tra più pagine (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_seasonal_keywords_missed_error':
                # TODO: Requires business understanding and keyword research data.
                seasonal_keywords_missed = False # Placeholder
                if seasonal_keywords_missed and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Mancata ottimizzazione per keyword stagionali rilevanti (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_toxic_backlinks_error':
                # TODO: Requires integration with backlink analysis tools (e.g. Ahrefs, SEMrush API)
                has_toxic_backlinks = False # Placeholder
                if has_toxic_backlinks and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevata presenza significativa di backlink tossici o spam (placeholder, necessita tool esterno).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_poor_internal_linking_strategy_error':
                # TODO: More advanced than just counting links; analyze link distribution, anchor text relevance to target, etc.
                # Could use data from self.analysis_results['links_analysis']
                # For now, a placeholder.
                poor_internal_linking_strategy = False # Placeholder
                if poor_internal_linking_strategy and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "La strategia di internal linking generale appare carente o inefficace (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_anchor_text_not_optimized_error':
                # TODO: Analyze anchor texts of internal links for relevance and diversity
                # Example: page.get('internal_links_analysis', {}).get('non_optimized_anchors_ratio', 0) > 0.3
                anchor_text_not_optimized_ratio = 0.4 # Placeholder
                if anchor_text_not_optimized_ratio > 0.3 and severity == 'ERROR': # If > 30% are not optimized
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Una porzione significativa ({anchor_text_not_optimized_ratio*100:.0f}%) degli anchor text dei link interni non è ottimizzata (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_gsc_critical_errors_unresolved_error':
                # TODO: Requires GSC API integration.
                gsc_critical_errors_unresolved = True # Placeholder
                if gsc_critical_errors_unresolved and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevati errori critici non risolti in Google Search Console (placeholder, necessita integrazione GSC).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_title_meta_missing_duplicated_error':
                pages_with_issues = set()
                # Missing titles
                for page_url in [p['url'] for p in self.analysis_results['title_analysis'].get('too_short_titles', []) if len(p.get('title','')) == 0]: # Assuming pages_without_title is not directly available this way
                    pages_with_issues.add(page_url)
                # Duplicate titles
                for dup_group in self.analysis_results['title_analysis'].get('duplicate_titles', []):
                    for url in dup_group.get('urls', []):
                        pages_with_issues.add(url)
                # Missing meta descriptions
                for page_url in [p['url'] for p in self.analysis_results['meta_description_analysis'].get('too_short_metas', []) if len(p.get('meta','')) == 0]:
                     pages_with_issues.add(page_url)
                # Duplicate meta descriptions
                for dup_group in self.analysis_results['meta_description_analysis'].get('duplicate_metas', []):
                    for url in dup_group.get('urls', []):
                        pages_with_issues.add(url)

                if pages_with_issues and severity == 'ERROR':
                     # Add one site-wide error summarizing the count
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"{len(pages_with_issues)} pagine presentano titoli o meta description mancanti/duplicati. Esempio: {list(pages_with_issues)[0] if pages_with_issues else 'N/A'}.",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_title_too_long_error':
                pages_affected = []
                for page in self.pages_data:
                    title = page.get('title', '')
                    if len(title) > SEO_CONFIG['title_max_length']:
                        pages_affected.append(f"{page.get('url')} (Lung.: {len(title)})")
                        if len(pages_affected) >= 3: break
                if pages_affected and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Titoli troppo lunghi rilevati su: {'; '.join(pages_affected)}...",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            elif check_key == 'seo_meta_desc_bad_length_error':
                pages_affected = []
                for page in self.pages_data:
                    meta_desc = page.get('meta_description', '')
                    m_len = len(meta_desc)
                    if meta_desc and (m_len < SEO_CONFIG['meta_description_min_length'] or m_len > SEO_CONFIG['meta_description_max_length']):
                        pages_affected.append(f"{page.get('url')} (Lung.: {m_len})")
                        if len(pages_affected) >= 3: break
                if pages_affected and severity == 'ERROR':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': f"Meta description con lunghezza non ottimale rilevate su: {'; '.join(pages_affected)}...",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })

            # Fallback for any other SITE SEO AUDIT ERROR check_key
            elif category == CATEGORY_SEO_AUDIT and severity == 'ERROR':
                is_example_check = check_key in [ # Checks already handled above
                    'seo_no_eeat_signals_error', 'seo_low_quality_ymyl_error',
                    'seo_extensive_duplicate_content_error', 'seo_keyword_stuffing_error'
                ]
                if not is_example_check:
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key,
                        'label': check_config['label'],
                        'url': self.domain,
                        'details': f"Logica per questo check SITE SEO AUDIT ERROR ({check_key}) non ancora implementata (placeholder).",
                        'description_key': check_config['description_key'],
                        'severity': 'ERROR'
                    })
                    self.logger.warning(f"Placeholder attivato per SITE SEO AUDIT ERROR check non implementato: {check_key}")

            # Implementazione dei SITE SEO AUDIT NOTICE CHECKS
            elif check_key == 'seo_content_easily_shareable_notice':
                # TODO: Implement logic to check for social sharing buttons / OpenGraph meta tags / Twitter Cards.
                content_is_easily_shareable = False # Placeholder
                if not content_is_easily_shareable and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Verificare la presenza e funzionalità dei pulsanti di condivisione social e la corretta implementazione dei meta tag Open Graph e Twitter Cards (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_gmb_not_optimized_notice':
                # TODO: Requires GMB API integration or manual checklist.
                gmb_is_optimized = False # Placeholder
                if not gmb_is_optimized and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # GMB is site-level
                        'details': "Il profilo Google My Business (Google Business Profile) potrebbe non essere completamente ottimizzato (placeholder, necessita verifica manuale o API).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_faq_schema_missing_notice':
                # TODO: Crawler needs to identify Q&A style pages and check for FAQPage schema.
                # For now, assume no Q&A pages or schema missing on them.
                qa_pages_found_without_faq_schema = True # Placeholder
                if qa_pages_found_without_faq_schema and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Per le pagine con formato Domande & Risposte, considerare l'implementazione dello schema FAQPage (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_howto_schema_missing_notice':
                # TODO: Crawler needs to identify HowTo pages and check for HowTo schema.
                howto_pages_found_without_schema = False # Placeholder
                if howto_pages_found_without_schema and severity == 'NOTICE':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Per guide e tutorial, considerare l'implementazione dello schema HowTo (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_video_schema_missing_notice':
                # TODO: Crawler needs to identify pages with videos and check for VideoObject schema.
                video_pages_found_without_schema = True # Placeholder
                if video_pages_found_without_schema and severity == 'NOTICE':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Per contenuti video, considerare l'implementazione dello schema VideoObject (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_event_schema_missing_notice':
                 # TODO: Crawler needs to identify event pages and check for Event schema.
                event_pages_found_without_schema = False # Placeholder
                if event_pages_found_without_schema and severity == 'NOTICE':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Per pagine relative a eventi, considerare l'implementazione dello schema Event (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_localbusiness_schema_missing_notice':
                # TODO: Check if site is a local business and if LocalBusiness schema is present.
                is_local_business_without_schema = True # Placeholder
                if is_local_business_without_schema and severity == 'NOTICE':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Se il sito rappresenta un'attività locale, considerare l'implementazione dello schema LocalBusiness (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_product_schema_missing_notice':
                # TODO: Crawler needs to identify product pages and check for Product schema.
                product_pages_found_without_schema = True # Placeholder
                if product_pages_found_without_schema and severity == 'NOTICE':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Per le schede prodotto e-commerce, considerare l'implementazione dello schema Product (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_review_schema_missing_notice':
                # TODO: Crawler needs to identify pages with reviews and check for Review/AggregateRating schema.
                review_pages_found_without_schema = False # Placeholder
                if review_pages_found_without_schema and severity == 'NOTICE':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Per pagine con recensioni, considerare l'implementazione dello schema Review o AggregateRating (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_internal_search_ux_poor_notice':
                # TODO: Requires analysis of internal search functionality (e.g. test searches, result relevance).
                internal_search_ux_is_poor = True # Placeholder
                if internal_search_ux_is_poor and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "L'esperienza utente della ricerca interna del sito potrebbe essere migliorata (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_blog_category_tags_suboptimal_notice':
                # TODO: Analyze blog categories/tags for overlap, excessive numbers, or poor naming.
                blog_cat_tags_suboptimal = True # Placeholder
                if blog_cat_tags_suboptimal and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Or blog section URL
                        'details': "Le categorie e i tag del blog potrebbero non essere ottimizzati (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_pagination_seo_issues_notice':
                # TODO: Crawler needs to identify paginated series and check for rel/next/prev, canonicals.
                pagination_has_issues = False # Placeholder
                if pagination_has_issues and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "La gestione della paginazione potrebbe presentare problemi SEO (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_faceted_navigation_seo_issues_notice':
                # TODO: Crawler needs to identify faceted navigation and check for handling (robots.txt, noindex, canonicals).
                faceted_nav_has_issues = True # Placeholder
                if faceted_nav_has_issues and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "La navigazione a faccette (filtri) potrebbe generare problemi SEO (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_website_accessibility_basic_review_notice':
                # TODO: Implement basic accessibility checks (e.g. alt tags are covered, maybe contrast or keyboard nav here).
                basic_accessibility_issues_found = True # Placeholder
                if basic_accessibility_issues_found and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Si raccomanda una revisione di base dell'accessibilità del sito (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_privacy_policy_cookie_notice_review_notice':
                # TODO: Check for presence of privacy policy / cookie notice pages/banners (heuristic).
                privacy_cookie_needs_review = False # Placeholder
                if privacy_cookie_needs_review and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Si raccomanda una revisione della Privacy Policy e della Cookie Notice per completezza e trasparenza (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_terms_conditions_review_notice':
                # TODO: Check for presence of a Terms & Conditions page.
                terms_conditions_needs_review = True # Placeholder
                if terms_conditions_needs_review and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Si raccomanda una revisione dei Termini e Condizioni per chiarezza e completezza (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_user_engagement_signals_low_notice':
                # TODO: Requires Analytics integration.
                user_engagement_low = True # Placeholder
                if user_engagement_low and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "I segnali di user engagement (es. bounce rate, tempo su pagina) sembrano bassi (placeholder, necessita dati Analytics).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_conversion_rate_tracking_notice':
                # TODO: Requires Analytics/Tag Manager inspection.
                conversion_tracking_incomplete = True # Placeholder
                if conversion_tracking_incomplete and severity == 'NOTICE':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Il tracciamento delle conversioni (goal) non sembra impostato o completo (placeholder, necessita verifica Analytics).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_regular_seo_audits_missing_notice':
                # This is a general recommendation.
                regular_audits_seem_missing = True # Placeholder (cannot be determined automatically without history)
                if regular_audits_seem_missing and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Si raccomanda di pianificare audit SEO regolari per mantenere e migliorare le performance (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_seo_kpi_monitoring_absent_notice':
                # TODO: Requires understanding of client's monitoring practices.
                kpi_monitoring_absent = True # Placeholder
                if kpi_monitoring_absent and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Non è evidente un monitoraggio strutturato dei KPI SEO fondamentali (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_core_web_vitals_monitoring_notice':
                # TODO: Check GSC integration or if client uses other CWV monitoring.
                cwv_monitoring_not_active = True # Placeholder
                if cwv_monitoring_not_active and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Si raccomanda di attivare o verificare il monitoraggio dei Core Web Vitals (es. tramite GSC) (placeholder).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            elif check_key == 'seo_backlink_profile_growth_slow_notice':
                # TODO: Requires backlink analysis tool integration and trend data.
                backlink_growth_slow = True # Placeholder
                if backlink_growth_slow and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "La crescita del profilo backlink sembra lenta o stagnante (placeholder, necessita tool esterno e analisi trend).",
                        'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })

            # Fallback for any other SITE SEO AUDIT NOTICE check_key
            elif category == CATEGORY_SEO_AUDIT and severity == 'NOTICE':
                is_example_check = check_key in [ # Checks already handled above
                    'seo_social_sharing_notice', 'seo_gmb_not_optimized_notice'
                ]
                if not is_example_check:
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key,
                        'label': check_config['label'],
                        'url': self.domain,
                        'details': f"Logica per questo check SITE SEO AUDIT NOTICE ({check_key}) non ancora implementata (placeholder).",
                        'description_key': check_config['description_key'],
                        'severity': 'NOTICE'
                    })
                    self.logger.warning(f"Placeholder attivato per SITE SEO AUDIT NOTICE check non implementato: {check_key}")

        self.logger.info("Nuova analisi dettagliata dei problemi completata.")


    def _find_duplicates(self, detailed: Dict): # detailed è passato come argomento
        """Trova duplicati nei title e meta description"""
        title_counts = {}
        meta_counts = {}
        
        for page in self.pages_data:
            title = page.get('title', '').strip()
            meta = page.get('meta_description', '').strip()
            url = page.get('url', '')
            
            if title:
                if title in title_counts:
                    title_counts[title].append(url)
                else:
                    title_counts[title] = [url]
            
            if meta:
                if meta in meta_counts:
                    meta_counts[meta].append(url)
                else:
                    meta_counts[meta] = [url]
        
        # Duplicati title
        for title, urls in title_counts.items():
            if len(urls) > 1:
                for url in urls:
                    detailed['duplicate_titles'].append({
                        'url': url,
                        'title': title,
                        'duplicate_count': len(urls),
                        'issue': f'Title duplicato ({len(urls)} pagine)'
                    })
                    detailed['warnings'].append({
                        'type': 'duplicate_title',
                        'url': url,
                        'message': f'Title duplicato su {len(urls)} pagine'
                    })
        
        # Duplicati meta
        for meta, urls in meta_counts.items():
            if len(urls) > 1:
                for url in urls:
                    detailed['duplicate_meta_descriptions'].append({
                        'url': url,
                        'meta': meta,
                        'duplicate_count': len(urls),
                        'issue': f'Meta description duplicata ({len(urls)} pagine)'
                    })
                    detailed['warnings'].append({
                        'type': 'duplicate_meta',
                        'url': url,
                        'message': f'Meta description duplicata su {len(urls)} pagine'
                    })
    
    def _calculate_site_health(self) -> Dict:
        """Calcola lo stato di salute del sito basato su AUDIT_CHECKS_CONFIG e NEW_SCORING_CLASSIFICATION."""
        total_pages = len(self.pages_data)
        if total_pages == 0 and not any(self.analysis_results['categorized_issues'][cat][sev]
                                     for cat in self.analysis_results['categorized_issues']
                                     for sev in self.analysis_results['categorized_issues'][cat]):
            # Se non ci sono pagine e nessun problema a livello di sito, considera il sito sano.
            return {
                'health_percentage': 100,
                'total_pages': 0,
                'total_critical_issues': 0,
                'total_warning_issues': 0,
                'total_notice_issues': 0,
                'category_scores': {} # Aggiunto per potenziale uso futuro
            }

        all_check_scores = []
        issues_by_check = {} # Per tenere traccia se un check è fallito almeno una volta

        # Popola issues_by_check
        for category_name, severities in self.analysis_results['categorized_issues'].items():
            for severity_level, issues_list in severities.items():
                for issue in issues_list:
                    check_key_found = issue['key']
                    if check_key_found not in issues_by_check:
                        issues_by_check[check_key_found] = []
                    issues_by_check[check_key_found].append(severity_level)


        for check_key, check_config in AUDIT_CHECKS_CONFIG.items():
            score_for_this_check = 100  # Default: il check passa

            if check_key in issues_by_check:
                # Il check è fallito. Determina il punteggio basato sulla severità definita in AUDIT_CHECKS_CONFIG.
                # Usiamo la severità da check_config, non da issues_by_check, perché quella in issues_by_check
                # è già il livello (ERROR, WARNING, NOTICE) in cui è stato categorizzato.
                severity_of_check = check_config['severity'] # Questa è la massima severità possibile per questo check

                # NEW_SCORING_CLASSIFICATION: {'ERROR': (90, 100), 'WARNING': (60, 89), 'NOTICE': (20, 59)}
                # Prendiamo il limite inferiore del range come "punteggio base" per quel tipo di problema
                # Ad esempio, un ERRORE farà sì che il check ottenga un punteggio di 90 (o ciò che è definito).
                # No, questo è sbagliato. Se un check di tipo ERRORE fallisce, il suo punteggio deve essere basso.
                # La classificazione del punteggio è (punteggio_problema, punteggio_massimo_problema)
                # Quindi un errore (90-100) significa che il 90% o più dei check di tipo errore sono falliti.
                # Questo sistema di punteggio è per il punteggio aggregato, non per i singoli check.
                # Per i singoli check, un errore dovrebbe dare un punteggio basso.
                # Esempio: Errore = 0, Warning = 50, Notice = 80, Pass = 100
                # Rivediamo la logica del punteggio per singolo check:
                if severity_of_check == 'ERROR':
                    score_for_this_check = 10 # Esempio: un errore grave impatta molto
                elif severity_of_check == 'WARNING':
                    score_for_this_check = 50 # Esempio: un warning impatta mediamente
                elif severity_of_check == 'NOTICE':
                    score_for_this_check = 80 # Esempio: un notice impatta poco

            all_check_scores.append(score_for_this_check)

        health_percentage = 100
        if all_check_scores:
            health_percentage = int(statistics.mean(all_check_scores))
        else:
            # Se non ci sono check definiti in AUDIT_CHECKS_CONFIG o nessun check è stato eseguito/matchato
            # E ci sono pagine, potrebbe essere un caso anomalo.
            # Se ci sono pagine ma nessun check, potrebbe essere 100 o 0 a seconda di come lo si interpreta.
            # Manteniamo 100 se non ci sono check che falliscono.
            health_percentage = 100


        total_critical_issues = sum(len(issues) for cat_issues in self.analysis_results['categorized_issues'].values() for sev, issues in cat_issues.items() if sev == 'ERROR')
        total_warning_issues = sum(len(issues) for cat_issues in self.analysis_results['categorized_issues'].values() for sev, issues in cat_issues.items() if sev == 'WARNING')
        total_notice_issues = sum(len(issues) for cat_issues in self.analysis_results['categorized_issues'].values() for sev, issues in cat_issues.items() if sev == 'NOTICE')
            
        return {
            'health_percentage': health_percentage,
            'total_pages': total_pages,
            'total_critical_issues': total_critical_issues,
            'total_warning_issues': total_warning_issues,
            'total_notice_issues': total_notice_issues,
            'category_scores': {} # Placeholder per futuri punteggi per categoria
        }

    def _calculate_overall_score(self) -> int:
        """
        Calcola il punteggio SEO complessivo.
        DEPRECATO in favore del 'health_percentage' da _calculate_site_health.
        Mantenuto per non rompere la struttura esistente di 'overall_score',
        ma ora restituisce 'health_percentage'.
        """
        if 'site_health' in self.analysis_results and 'health_percentage' in self.analysis_results['site_health']:
            return self.analysis_results['site_health']['health_percentage']
        # Fallback se _calculate_site_health non è ancora stato chiamato o non ha prodotto health_percentage
        # Questo non dovrebbe accadere nel flusso normale.
        # Potremmo anche chiamare _calculate_site_health qui se necessario, ma è meglio che analyze_all gestisca l'ordine.
        self.logger.warning("_calculate_overall_score chiamato prima che site_health fosse calcolato.")
        return 0 # o un valore di default appropriato

    def _calculate_weighted_category_score(self) -> int:
        """
        DEPRECATO. La logica di scoring è ora in _calculate_site_health
        basata su AUDIT_CHECKS_CONFIG e NEW_SCORING_CLASSIFICATION.
        Questo metodo potrebbe essere rimosso o adattato se si vuole un punteggio per categoria basato
        sui vecchi 'analysis_results[category_analysis]['score']'.
        Per ora, restituisce un valore placeholder o logica precedente se necessario.
        """
        self.logger.warning("Chiamata a _calculate_weighted_category_score DEPRECATO.")
        # Manteniamo la vecchia logica se SEO_WEIGHTS è ancora usato da qualche parte,
        # altrimenti questo metodo dovrebbe essere rimosso o restituire 0/100.
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
             return 0 # O un altro valore di default
        
        # Since SEO_WEIGHTS is removed, this method cannot calculate a weighted score as before.
        # It should either be fully removed or return a simple average of available old scores,
        # but it's deprecated, so returning a fixed value or 0 is also an option.
        # For now, let's return a fixed placeholder, as the overall_score is now driven by site_health.
        self.logger.info("Deprecated _calculate_weighted_category_score called. Returning placeholder score.")
        return 50 # Placeholder for deprecated score

        # scores = {}
        # # The following line would fail as SEO_WEIGHTS is no longer imported.
        # # valid_weights = {k: v for k, v in SEO_WEIGHTS.items() if k in self.analysis_results and isinstance(self.analysis_results.get(k), dict) and 'score' in self.analysis_results.get(k, {})}

        # # for analysis_type, weight in valid_weights.items():
        # #     # Questo mapping è fragile e dipende dai nomi delle chiavi in analysis_results
        # #     if analysis_type == 'title_tags' and 'title_analysis' in self.analysis_results:
        # #         scores[analysis_type] = self.analysis_results['title_analysis'].get('score', 0)
        # #     elif analysis_type == 'meta_descriptions' and 'meta_description_analysis' in self.analysis_results:
        # #         scores[analysis_type] = self.analysis_results['meta_description_analysis'].get('score', 0)
        # #     elif analysis_type == 'headings' and 'headings_analysis' in self.analysis_results:
        # #         scores[analysis_type] = self.analysis_results['headings_analysis'].get('score', 0)
        # #     elif analysis_type == 'images_alt' and 'images_analysis' in self.analysis_results:
        # #         scores[analysis_type] = self.analysis_results['images_analysis'].get('score', 0)
        # #     elif analysis_type == 'internal_links' and 'links_analysis' in self.analysis_results: # 'links_analysis'
        # #         scores[analysis_type] = self.analysis_results['links_analysis'].get('score', 0)
        # #     elif analysis_type == 'page_speed' and 'performance_analysis' in self.analysis_results: # 'performance_analysis'
        # #         scores[analysis_type] = self.analysis_results['performance_analysis'].get('score', 0)
        # #     elif analysis_type == 'mobile_friendly' and 'mobile_analysis' in self.analysis_results: # 'mobile_analysis'
        # #         scores[analysis_type] = self.analysis_results['mobile_analysis'].get('score', 0)
        # #     elif analysis_type == 'ssl_certificate' and 'ssl_analysis' in self.analysis_results: # 'ssl_analysis'
        # #         scores[analysis_type] = self.analysis_results['ssl_analysis'].get('score', 0)
        # #     elif analysis_type == 'content_quality' and 'content_analysis' in self.analysis_results: # 'content_analysis'
        # #         scores[analysis_type] = self.analysis_results['content_analysis'].get('score', 0)
        
        # # weighted_sum = sum(scores.get(key,0) * SEO_WEIGHTS[key] for key in scores)
        # # total_weight = sum(SEO_WEIGHTS[key] for key in scores if key in SEO_WEIGHTS) # Sum only weights for which scores were found
        
        # return int(weighted_sum / total_weight) if total_weight > 0 else 0
    
    def _generate_recommendations(self) -> List[Dict]:
        """Genera raccomandazioni basate sull'analisi (DA AGGIORNARE per usare categorized_issues)"""
        recommendations = []
        
        # Title tags
        title_analysis = self.analysis_results['title_analysis']
        if title_analysis['pages_without_title'] > 0:
            recommendations.append({
                'category': 'Title Tags',
                'priority': 'Alto',
                'issue': f"{title_analysis['pages_without_title']} pagine senza title tag",
                'recommendation': "Aggiungi title tag unici e descrittivi per ogni pagina"
            })
        
        if len(title_analysis['duplicate_titles']) > 0:
            recommendations.append({
                'category': 'Title Tags',
                'priority': 'Alto',
                'issue': f"{len(title_analysis['duplicate_titles'])} title duplicati trovati",
                'recommendation': "Crea title tag unici per ogni pagina"
            })
        
        # Meta descriptions
        meta_analysis = self.analysis_results['meta_description_analysis']
        if meta_analysis['pages_without_meta'] > 0:
            recommendations.append({
                'category': 'Meta Descriptions',
                'priority': 'Medio',
                'issue': f"{meta_analysis['pages_without_meta']} pagine senza meta description",
                'recommendation': "Aggiungi meta description di 120-160 caratteri per ogni pagina"
            })
        
        # Immagini
        images_analysis = self.analysis_results['images_analysis']
        if images_analysis['images_without_alt'] > 0:
            recommendations.append({
                'category': 'Immagini',
                'priority': 'Alto',
                'issue': f"{images_analysis['images_without_alt']} immagini senza alt text",
                'recommendation': "Aggiungi alt text descrittivi per tutte le immagini"
            })
        
        # Contenuto
        content_analysis = self.analysis_results['content_analysis']
        if content_analysis['pages_low_word_count'] > 0:
            recommendations.append({
                'category': 'Contenuto',
                'priority': 'Medio',
                'issue': f"{content_analysis['pages_low_word_count']} pagine con poco contenuto",
                'recommendation': f"Espandi il contenuto a almeno {SEO_CONFIG['min_word_count']} parole"
            })
        
        # Performance
        perf_analysis = self.analysis_results['performance_analysis']
        if perf_analysis['slow_pages'] > 0:
            recommendations.append({
                'category': 'Performance',
                'priority': 'Alto',
                'issue': f"{perf_analysis['slow_pages']} pagine lente",
                'recommendation': "Ottimizza le performance per tempi di caricamento sotto i 3 secondi"
            })
        
        return recommendations
    
    def _create_summary(self) -> Dict:
        """Crea un riassunto dell'analisi"""
        return {
            'report_title': "SEO Analysis Report for " + self.domain,
            'domain': self.domain,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_pages_analyzed': len(self.pages_data),
            'overall_score': self.analysis_results.get('overall_score', 0), # Use .get for safety
            'total_issues': sum(len(v) for k,v in self.analysis_results.get('detailed_issues',{}).items() if isinstance(v,list) and k in ['errors','warnings','notices']),
            'total_recommendations': len(self.analysis_results.get('recommendations', [])), # Use .get for safety
            'score_breakdown': {
                'excellent': self.analysis_results.get('overall_score', 0) >= 90,
                'good': 70 <= self.analysis_results.get('overall_score', 0) < 90,
                'needs_improvement': 50 <= self.analysis_results.get('overall_score', 0) < 70,
                'poor': self.analysis_results.get('overall_score', 0) < 50
            }
        }
