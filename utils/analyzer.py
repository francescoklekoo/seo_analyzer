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

from config import *

class SEOAnalyzer:
    """
    Classe principale per l'analisi SEO dei dati crawlati
    """
    
    def __init__(self, pages_data: List[Dict], domain: str):
        self.pages_data = pages_data
        self.domain = domain
        self.analysis_results = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize new_detailed_results structure
        self.new_detailed_results = {
            CATEGORY_OCM: {
                IMPACT_ERROR: {},
                IMPACT_WARNING: {},
                IMPACT_NOTICE: {}
            },
            CATEGORY_SEO_AUDIT: {
                IMPACT_ERROR: {},
                IMPACT_WARNING: {},
                IMPACT_NOTICE: {}
            }
        }
        # Pre-populate with check details
        for category, impacts in DETAILED_SEO_CHECKS.items():
            for impact_level, checks in impacts.items():
                for check_details in checks:
                    self.new_detailed_results[category][impact_level][check_details['id']] = {
                        "description": check_details['description'],
                        "weight": check_details['weight'],
                        "impact": check_details['impact'], # Storing impact level string as well
                        "findings": [],
                        "count": 0
                    }

    def analyze_all(self) -> Dict:
        """Esegue tutte le analisi SEO"""
        self.logger.info("Inizio analisi SEO completa")
        
        # Initialize new_detailed_results for this run (if analyzer is reused)
        # This is already handled by pre-populating in __init__ and clearing findings per run if needed
        # For now, assuming __init__ is called for each new analysis set (pages_data)

        # Analisi individuali
        self.analysis_results = {
            'title_analysis': self._analyze_titles(),
            'meta_description_analysis': self._analyze_meta_descriptions(),
            'headings_analysis': self._analyze_headings(),
            'images_analysis': self._analyze_images(),
            'content_analysis': self._analyze_content(),
            'links_analysis': self._analyze_links(),
            'technical_analysis': self._analyze_technical(),
            'performance_analysis': self._analyze_performance(),
            'mobile_analysis': self._analyze_mobile_friendly(),
            'ssl_analysis': self._analyze_ssl(),
            'classified_detailed_issues': self._analyze_detailed_issues(), # New analysis used here
            'site_health': self._calculate_site_health(),  # Calcolo stato sito
            # overall_score will be calculated after category scores
            'ocm_category_score': 0, # Placeholder, will be calculated
            'seo_audit_category_score': 0, # Placeholder, will be calculated
            'overall_score': 0,
            'recommendations': [],
            'summary': {}
        }
        
        # Calcola i punteggi delle categorie dettagliate (OCM, SEO_AUDIT)
        # This needs to be done after 'classified_detailed_issues' is populated.
        self._calculate_detailed_category_scores()

        # Calcola il punteggio SEO generale complessivo
        # This must be after individual scores and category scores are calculated.
        self.analysis_results['overall_score'] = self._calculate_overall_score()
        
        # Genera raccomandazioni basate su tutte le analisi e punteggi
        self.analysis_results['recommendations'] = self._generate_recommendations()
        
        # Crea il riassunto
        self.analysis_results['summary'] = self._create_summary()
        
        self.logger.info("Analisi SEO completata")
        return self.analysis_results

    def _calculate_detailed_category_scores(self):
        """
        Calculates scores for OCM and SEO_AUDIT categories based on DETAILED_SEO_CHECKS findings.
        """
        self.logger.info("Calcolo punteggi categorie dettagliate...")
        if 'classified_detailed_issues' not in self.analysis_results:
            self.logger.warning("Risultati dettagliati classificati non trovati. Impossibile calcolare i punteggi delle categorie.")
            self.analysis_results['ocm_category_score'] = 0
            self.analysis_results['seo_audit_category_score'] = 0
            return

        detailed_findings = self.analysis_results['classified_detailed_issues']

        for category_key in [CATEGORY_OCM, CATEGORY_SEO_AUDIT]:
            max_possible_score_category = 0
            total_penalty_score_category = 0

            # Calculate max possible score for the category from DETAILED_SEO_CHECKS
            if category_key in DETAILED_SEO_CHECKS:
                for impact_level, checks in DETAILED_SEO_CHECKS[category_key].items():
                    for check_config in checks:
                        max_possible_score_category += check_config['weight']

            if max_possible_score_category == 0: # Avoid division by zero if no checks defined for a category
                category_score_percentage = 100 # Or 0, depending on desired behavior. 100 means no issues if no checks.
                if category_key == CATEGORY_OCM:
                    self.analysis_results['ocm_category_score'] = category_score_percentage
                elif category_key == CATEGORY_SEO_AUDIT:
                    self.analysis_results['seo_audit_category_score'] = category_score_percentage
                self.logger.info(f"Punteggio per {category_key}: {category_score_percentage}% (max score 0)")
                continue

            # Calculate penalty from findings
            if category_key in detailed_findings:
                for impact_level, checks_found in detailed_findings[category_key].items():
                    for check_id, check_data in checks_found.items():
                        if check_data['count'] > 0:
                            # The weight for penalty is the check's defined weight
                            penalty_per_finding = check_data['weight']
                            total_penalty_score_category += (penalty_per_finding * check_data['count'])

            achieved_score_category = max(0, max_possible_score_category - total_penalty_score_category)
            category_score_percentage = (achieved_score_category / max_possible_score_category) * 100

            if category_key == CATEGORY_OCM:
                self.analysis_results['ocm_category_score'] = round(category_score_percentage)
                self.logger.info(f"Punteggio OCM: {achieved_score_category}/{max_possible_score_category} = {self.analysis_results['ocm_category_score']}%")
            elif category_key == CATEGORY_SEO_AUDIT:
                self.analysis_results['seo_audit_category_score'] = round(category_score_percentage)
                self.logger.info(f"Punteggio SEO Audit: {achieved_score_category}/{max_possible_score_category} = {self.analysis_results['seo_audit_category_score']}%")

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
                        'length': title_length
                    })
                elif title_length > SEO_CONFIG['title_max_length']:
                    analysis['too_long_titles'].append({
                        'url': url,
                        'title': title,
                        'length': title_length
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
        if analysis['total_pages'] > 0:
            optimal_ratio = len(analysis['optimal_titles']) / analysis['total_pages']
            duplicate_penalty = len(analysis['duplicate_titles']) / analysis['total_pages']
            missing_penalty = analysis['pages_without_title'] / analysis['total_pages']
            
            analysis['score'] = max(0, int((optimal_ratio - duplicate_penalty - missing_penalty) * 100))
        
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
                        'length': meta_length
                    })
                elif meta_length > SEO_CONFIG['meta_description_max_length']:
                    analysis['too_long_metas'].append({
                        'url': url,
                        'meta': meta_desc,
                        'length': meta_length
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
        if analysis['total_pages'] > 0:
            optimal_ratio = len(analysis['optimal_metas']) / analysis['total_pages']
            duplicate_penalty = len(analysis['duplicate_metas']) / analysis['total_pages']
            missing_penalty = analysis['pages_without_meta'] / analysis['total_pages']
            
            analysis['score'] = max(0, int((optimal_ratio - duplicate_penalty - missing_penalty) * 100))
        
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
        if analysis['total_pages'] > 0:
            h1_score = analysis['pages_with_h1'] / analysis['total_pages']
            multiple_h1_penalty = analysis['pages_multiple_h1'] / analysis['total_pages']
            
            analysis['score'] = max(0, int((h1_score - multiple_h1_penalty) * 100))
        
        return analysis
    
    def _analyze_images(self) -> Dict:
        """Analizza le immagini e gli alt text"""
        analysis = {
            'total_images': 0,
            'images_with_alt': 0,
            'images_without_alt': 0,
            'images_with_empty_alt': 0,
            'images_with_title': 0,
            'alt_text_lengths': [],
            'issues': [],
            'score': 0
        }
        
        for page in self.pages_data:
            images = page.get('images', [])
            url = page.get('url', '')
            
            for img in images:
                analysis['total_images'] += 1
                alt_text = img.get('alt', '').strip()
                title_text = img.get('title', '').strip()
                
                if alt_text:
                    analysis['images_with_alt'] += 1
                    analysis['alt_text_lengths'].append(len(alt_text))
                elif alt_text == '':
                    analysis['images_with_empty_alt'] += 1
                else:
                    analysis['images_without_alt'] += 1
                    analysis['issues'].append(f"Immagine senza alt: {img.get('src', '')} in {url}")
                
                if title_text:
                    analysis['images_with_title'] += 1
        
        # Calcola il punteggio
        if analysis['total_images'] > 0:
            alt_ratio = analysis['images_with_alt'] / analysis['total_images']
            analysis['score'] = int(alt_ratio * 100)
        else:
            analysis['score'] = 100  # Nessuna immagine = nessun problema
        
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
        if analysis['total_pages'] > 0:
            good_content_ratio = analysis['pages_good_word_count'] / analysis['total_pages']
            good_ratio_pages = (analysis['total_pages'] - analysis['pages_low_text_ratio']) / analysis['total_pages']
            
            analysis['score'] = int((good_content_ratio + good_ratio_pages) / 2 * 100)
        
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
        internal_ratio = analysis['internal_links'] / max(1, analysis['total_links'])
        few_links_penalty = analysis['pages_with_few_internal_links'] / max(1, len(self.pages_data))
        
        analysis['score'] = max(0, int((internal_ratio - few_links_penalty) * 100))
        
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
            canonical_score = analysis['pages_with_canonical'] / total_pages
            lang_score = analysis['pages_with_lang'] / total_pages
            schema_score = analysis['pages_with_schema'] / total_pages
            
            analysis['score'] = int((canonical_score + lang_score + schema_score) / 3 * 100)
        
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
        if analysis['total_pages'] > 0:
            fast_ratio = analysis['fast_pages'] / analysis['total_pages']
            large_penalty = analysis['large_pages'] / analysis['total_pages']
            
            analysis['score'] = max(0, int((fast_ratio - large_penalty) * 100))
        
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
    
    def _analyze_detailed_issues(self) -> Dict:
        """Analisi dettagliata dei problemi specifici basata su DETAILED_SEO_CHECKS."""
        # Reset findings for the current analysis run
        for category_key, impacts_dict in self.new_detailed_results.items():
            for impact_key, checks_dict in impacts_dict.items():
                for check_id, check_data in checks_dict.items():
                    check_data["findings"] = []
                    check_data["count"] = 0

        # --- Helper functions for individual checks ---
        def _add_finding(cat, imp, c_id, page_url, message_detail):
            """Adds a finding to the self.new_detailed_results structure."""
            try:
                target_check = self.new_detailed_results[cat][imp][c_id]
                target_check["findings"].append({"url": page_url, "message": message_detail})
                target_check["count"] += 1
            except KeyError:
                self.logger.error(f"Check ID '{c_id}' not found in DETAILED_SEO_CHECKS for category '{cat}' and impact '{imp}'. Skipping finding.")

        # --- Iterate through pages for page-specific checks ---
        titles_for_duplication_check = {} # url: title
        meta_descriptions_for_duplication_check = {} # url: meta_description
        h1s_for_duplication_check = {} # url: list_of_h1s

        for page_data in self.pages_data:
            url = page_data.get('url', 'N/A')
            title = page_data.get('title', '').strip()
            meta_description = page_data.get('meta_description', '').strip()
            headings = page_data.get('headings', {}) # {'h1': ['H1 text'], 'h2': [...]}
            images = page_data.get('images', []) # [{'src': 'img.jpg', 'alt': 'Alt text'}]
            content_data = page_data.get('content', {}) # {'word_count': 0}
            
            # Collect data for cross-page checks
            if title:
                titles_for_duplication_check[url] = title
            if meta_description:
                meta_descriptions_for_duplication_check[url] = meta_description
            if headings.get('h1'):
                 h1s_for_duplication_check[url] = headings.get('h1')


            # OCM - ERRORI
            if not title:
                _add_finding(CATEGORY_OCM, IMPACT_ERROR, "ocm_missing_title", url, f"Tag title mancante sulla pagina: {url}")
            
            if len(title) > SEO_CONFIG.get('title_max_length', 60) and DETAILED_SEO_CHECKS[CATEGORY_OCM][IMPACT_WARNING][0]["id"] == "ocm_title_too_long": # Check if the ID matches
                 # This check ID "ocm_title_too_long" is actually a WARNING in config, but example says ERRORI for "Title tag oltre 60 caratteri"
                 # For now, I'll map it to the ocm_title_too_long (warning) as per current config.
                 # If it should be an ERROR, the config or this logic needs adjustment.
                 # Based on subtask description, "ocm_title_too_long" is an OCM ERROR. Let's assume there's a mismatch and treat it as error for now.
                 # The original config has ocm_title_too_long as WARNING. I will stick to the config for now.
                 # The subtask description has "OCM - ERRORI - title_too_long". This is a conflict.
                 # I will create the finding if the ID is "ocm_title_too_long" under WARNINGS as per current config.
                 # To adhere to subtask example "OCM - ERRORI - title_too_long", I'd need to change its category or ID.
                 # Let's proceed by finding the check by its ID, regardless of its pre-defined category/impact for adding findings.
                 # This means _add_finding needs to be robust or checks should be uniquely named if their category/impact can shift.
                 # For now, the subtask implies I should implement the logic for the *description* "Title tag oltre 60 caratteri" as an OCM ERROR.
                 # The closest ID is "ocm_title_too_long". I will add it to OCM/AVVERTIMENTI as per config.
                 # If a different ID like "ocm_error_title_too_long" was defined in config for errors, that would be used.
                 # Sticking to the defined DETAILED_SEO_CHECKS structure.
                pass # This logic will be handled by its own check ID "ocm_title_too_long" under AVVERTIMENTI


            if not meta_description:
                _add_finding(CATEGORY_OCM, IMPACT_ERROR, "ocm_missing_meta_description", url, f"Meta description mancante sulla pagina: {url}")

            if not headings.get('h1'):
                _add_finding(CATEGORY_OCM, IMPACT_ERROR, "ocm_missing_h1", url, f"Tag H1 mancante sulla pagina: {url}")
            elif len(headings.get('h1', [])) > 1: # As per subtask: OCM - ERRORI - duplicate_h1_same_page (mapped to ocm_multiple_h1)
                _add_finding(CATEGORY_OCM, IMPACT_ERROR, "ocm_multiple_h1", url, f"Tag H1 multipli ({len(headings.get('h1', []))}) sulla pagina: {url}")

            for img in images:
                alt_text = img.get('alt') # Keep None if not present
                if alt_text is None or alt_text.strip() == '':
                    _add_finding(CATEGORY_OCM, IMPACT_ERROR, "ocm_missing_alt_text", url, f"Attributo ALT mancante/vuoto per immagine '{img.get('src', 'N/A')}' sulla pagina: {url}")
            
            # OCM - AVVERTIMENTI
            if 0 < len(title) < SEO_CONFIG.get('title_min_length', 30):
                _add_finding(CATEGORY_OCM, IMPACT_WARNING, "ocm_title_too_short", url, f"Tag title troppo corto ({len(title)} caratteri) sulla pagina: {url}. Min: {SEO_CONFIG.get('title_min_length', 30)}")
            
            # This is specifically for ocm_title_too_long under AVVERTIMENTI
            if len(title) > SEO_CONFIG.get('title_max_length', 60):
                 _add_finding(CATEGORY_OCM, IMPACT_WARNING, "ocm_title_too_long", url, f"Tag title troppo lungo ({len(title)} caratteri) sulla pagina: {url}. Max: {SEO_CONFIG.get('title_max_length', 60)}")


            if 0 < len(meta_description) < SEO_CONFIG.get('meta_description_min_length', 120):
                _add_finding(CATEGORY_OCM, IMPACT_WARNING, "ocm_meta_description_too_short", url, f"Meta description troppo corta ({len(meta_description)} caratteri) sulla pagina: {url}. Min: {SEO_CONFIG.get('meta_description_min_length', 120)}")
            
            if len(meta_description) > SEO_CONFIG.get('meta_description_max_length', 160):
                _add_finding(CATEGORY_OCM, IMPACT_WARNING, "ocm_meta_description_too_long", url, f"Meta description troppo lunga ({len(meta_description)} caratteri) sulla pagina: {url}. Max: {SEO_CONFIG.get('meta_description_max_length', 160)}")

            # OCM - AVVERTIMENTI - inconsistent_header_structure (simplified)
            # If H3s exist but no H2s, flag it.
            if headings.get('h3') and not headings.get('h2'):
                 # Assuming an ID like "ocm_inconsistent_headings" exists or should be added to config.
                 # For now, let's use a placeholder ID or skip if not in DETAILED_SEO_CHECKS.
                 # The provided config does not have "ocm_inconsistent_headings".
                 # It has "ocm_h_tags_order_incorrect" under AVVISI.
                 # Let's map this simplified logic to "ocm_h_tags_order_incorrect" for now.
                _add_finding(CATEGORY_OCM, IMPACT_NOTICE, "ocm_h_tags_order_incorrect", url, f"Struttura heading potenzialmente inconsistente: H3 presenti senza H2 sulla pagina: {url}")


            # SEO_AUDIT - ERRORI
            # SEO_AUDIT - ERRORI - thin_content_pages
            word_count = content_data.get('word_count', 0)
            min_word_count_config = SEO_CONFIG.get('min_word_count', 300)
            if word_count < min_word_count_config:
                # This ID "seo_audit_thin_content" is a WARNING in config, subtask says ERROR.
                # I will add to WARNINGS as per config.
                _add_finding(CATEGORY_SEO_AUDIT, IMPACT_WARNING, "seo_audit_thin_content", url, f"Contenuto potenzialmente 'thin' ({word_count} parole) sulla pagina: {url}. Minimo raccomandato: {min_word_count_config}")


        # --- Cross-page checks (duplicates) ---
        # OCM - ERRORI - ocm_duplicate_title
        title_val_to_urls = {}
        for url, title_text in titles_for_duplication_check.items():
            if title_text not in title_val_to_urls:
                title_val_to_urls[title_text] = []
            title_val_to_urls[title_text].append(url)

        for title_text, urls_with_title in title_val_to_urls.items():
            if len(urls_with_title) > 1:
                msg = f"Tag title duplicato '{title_text}' trovato sulle seguenti URLs: {', '.join(urls_with_title)}"
                # Add this finding for each involved URL
                for u in urls_with_title:
                    _add_finding(CATEGORY_OCM, IMPACT_ERROR, "ocm_duplicate_title", u, msg)

        # OCM - ERRORI - ocm_duplicate_meta_description
        meta_val_to_urls = {}
        for url, meta_text in meta_descriptions_for_duplication_check.items():
            if meta_text not in meta_val_to_urls:
                meta_val_to_urls[meta_text] = []
            meta_val_to_urls[meta_text].append(url)

        for meta_text, urls_with_meta in meta_val_to_urls.items():
            if len(urls_with_meta) > 1:
                msg = f"Meta description duplicata '{meta_text}' trovata sulle seguenti URLs: {', '.join(urls_with_meta)}"
                for u in urls_with_meta:
                    _add_finding(CATEGORY_OCM, IMPACT_ERROR, "ocm_duplicate_meta_description", u, msg)

        # OCM - ERRORI - ocm_duplicate_h1 (Note: config has this as Medio impact, not Alto)
        # This check is about "Evita H1 identici su pagine diverse"
        # The subtask also lists "OCM - ERRORI - duplicate_h1_same_page", which I mapped to "ocm_multiple_h1"
        # For "ocm_duplicate_h1" (across pages):
        h1_text_to_urls = {}
        for url, h1_list in h1s_for_duplication_check.items():
            # Consider only the first H1 for duplication across pages if multiple H1s exist on one page
            # (multiple H1s on the same page is a separate check: ocm_multiple_h1)
            if h1_list:
                first_h1 = h1_list[0].strip() # Use the text of the first H1
                if first_h1: # Ensure it's not empty
                    if first_h1 not in h1_text_to_urls:
                        h1_text_to_urls[first_h1] = []
                    h1_text_to_urls[first_h1].append(url)

        for h1_text, urls_with_h1 in h1_text_to_urls.items():
            if len(urls_with_h1) > 1:
                msg = f"Tag H1 duplicato (testo: '{h1_text}') trovato sulle seguenti URLs: {', '.join(urls_with_h1)}"
                for u in urls_with_h1:
                     # "ocm_duplicate_h1" is Medio/Warning in config.
                    _add_finding(CATEGORY_OCM, IMPACT_WARNING, "ocm_duplicate_h1", u, msg)


        # SEO_AUDIT - ERRORI - extensive_duplicate_content (Placeholder)
        # This is complex. For now, a placeholder comment or a very simple check.
        # If text_content is available and comparable:
        # For now, let's assume 'text_content' is not readily available in a comparable format in pages_data
        # or that robust text similarity is too complex for this subtask.
        # Add a note to the findings for this check if it exists in self.new_detailed_results.
        check_id_dup_content = "seo_audit_duplicate_content_across_domains" # This is ALTO in config
        if CATEGORY_SEO_AUDIT in self.new_detailed_results and \
           IMPACT_ERROR in self.new_detailed_results[CATEGORY_SEO_AUDIT] and \
           check_id_dup_content in self.new_detailed_results[CATEGORY_SEO_AUDIT][IMPACT_ERROR]:
            
            # Simplified: check if any two pages have identical 'meta_description' (already covered by ocm_duplicate_meta_description)
            # or identical 'title' (covered by ocm_duplicate_title).
            # This check is more about full content duplication.
            # For now, just adding a placeholder message to the results of this check.
            # Actual implementation would require comparing page.get('text_content') or similar.
             self.new_detailed_results[CATEGORY_SEO_AUDIT][IMPACT_ERROR][check_id_dup_content]["findings"].append({
                 "url": "N/A", # This check is site-wide or compares multiple pages
                 "message": "Implementazione della logica per 'extensive_duplicate_content' (es. similarità testuale >80%) è complessa e richiede ulteriore sviluppo. Controllare manualmente per ora."
             })
             self.new_detailed_results[CATEGORY_SEO_AUDIT][IMPACT_ERROR][check_id_dup_content]["count"] = 1 # Mark as 1 to show it's noted.


        return self.new_detailed_results

    # _find_duplicates method removed as its functionality is integrated into _analyze_detailed_issues
    
    def _calculate_site_health(self) -> Dict:
        """Calcola lo stato di salute del sito con algoritmo migliorato"""
        total_pages = len(self.pages_data)
        if total_pages == 0:
            return {
                'healthy_pages': 0,
                'broken_pages': 0,
                'problematic_pages': 0,
                'redirected_pages': 0,
                'blocked_pages': 0,
                'health_percentage': 0,
                'total_pages': 0
            }
        
        # Contatori per stato pagine
        healthy = 0
        broken = 0
        problematic = 0
        redirected = 0
        blocked = 0
        
        # Contatori per problemi complessivi
        total_critical_issues = 0  # Errori gravi
        total_warning_issues = 0   # Avvertimenti
        total_minor_issues = 0     # Avvisi minori
        
        for page in self.pages_data:
            status_code = page.get('status_code', 200)
            title = page.get('title', '').strip()
            meta = page.get('meta_description', '').strip()
            word_count = page.get('content', {}).get('word_count', 0)
            headings = page.get('headings', {})
            images = page.get('images', [])
            
            # Classifica stato pagina
            page_issues = 0
            
            # Errori gravi (influenzano molto la salute)
            if status_code >= 400:
                if status_code >= 500:
                    broken += 1
                    total_critical_issues += 3  # Peso alto per errori server
                else:
                    broken += 1
                    total_critical_issues += 2  # Peso medio per errori client
                continue
            elif status_code >= 300:
                redirected += 1
                total_warning_issues += 1
                page_issues += 1
            
            # Problemi SEO che influenzano la salute
            if not title:
                total_critical_issues += 2
                page_issues += 2
            
            if not meta:
                total_warning_issues += 1
                page_issues += 1
            
            if word_count < SEO_CONFIG['min_word_count']:
                total_warning_issues += 1
                page_issues += 1
            
            # Problemi strutturali
            h1_count = len(headings.get('h1', []))
            if h1_count == 0:
                total_warning_issues += 1
                page_issues += 1
            elif h1_count > 1:
                total_warning_issues += 1
                page_issues += 1
            
            # Problemi immagini (peso minore)
            for img in images:
                if not img.get('alt', '').strip():
                    total_warning_issues += 1
                if not img.get('title', '').strip():
                    total_minor_issues += 1
            
            # Schema markup e aspetti tecnici minori
            if not page.get('canonical_url', '').strip():
                total_minor_issues += 1
            
            if not page.get('lang', '').strip():
                total_minor_issues += 1
            
            if not page.get('schema_markup', []):
                total_minor_issues += 1
            
            # Classifica la pagina
            if page_issues >= 3:
                problematic += 1
            elif page_issues >= 1:
                # Pagina con problemi minori ma non critici
                healthy += 1
            else:
                healthy += 1
        
        # Calcola percentuale di salute più precisa
        # Formula migliorata che considera tutti i tipi di problemi
        base_health = (healthy / total_pages) * 100 if total_pages > 0 else 0
        
        # Penalità per problemi (scalate in base alla gravità)
        critical_penalty = min((total_critical_issues * 5), 30)  # Max 30% di penalità per errori critici
        warning_penalty = min((total_warning_issues * 2), 25)    # Max 25% per avvertimenti
        minor_penalty = min((total_minor_issues * 0.5), 15)      # Max 15% per problemi minori
        
        # Applica le penalità
        adjusted_health = base_health - critical_penalty - warning_penalty - minor_penalty
        
        # Assicurati che non vada sotto 0 o sopra 100
        health_percentage = max(0, min(100, int(adjusted_health)))
        
        return {
            'healthy_pages': healthy,
            'broken_pages': broken,
            'problematic_pages': problematic,
            'redirected_pages': redirected,
            'blocked_pages': blocked,
            'health_percentage': health_percentage,
            'total_pages': total_pages,
            'critical_issues': total_critical_issues,
            'warning_issues': total_warning_issues,
            'minor_issues': total_minor_issues
        }
    
    def _calculate_overall_score(self) -> int:
        """Calcola il punteggio SEO complessivo"""
        scores = {}
        
        # Raccogli tutti i punteggi
        for analysis_type, weight in SEO_WEIGHTS.items():
            if analysis_type == 'title_tags':
                scores[analysis_type] = self.analysis_results['title_analysis']['score']
            elif analysis_type == 'meta_descriptions':
                scores[analysis_type] = self.analysis_results['meta_description_analysis']['score']
            elif analysis_type == 'headings':
                scores[analysis_type] = self.analysis_results['headings_analysis']['score']
            elif analysis_type == 'images_alt':
                scores[analysis_type] = self.analysis_results['images_analysis']['score']
            elif analysis_type == 'internal_links':
                scores[analysis_type] = self.analysis_results['links_analysis']['score']
            elif analysis_type == 'page_speed':
                scores[analysis_type] = self.analysis_results['performance_analysis']['score']
            elif analysis_type == 'mobile_friendly':
                scores[analysis_type] = self.analysis_results['mobile_analysis']['score']
            elif analysis_type == 'ssl_certificate':
                scores[analysis_type] = self.analysis_results['ssl_analysis']['score']
            elif analysis_type == 'content_quality':
                scores[analysis_type] = self.analysis_results['content_analysis']['score']
            elif analysis_type == 'ocm_score':
                scores[analysis_type] = self.analysis_results.get('ocm_category_score', 0) # Use .get for safety
            elif analysis_type == 'seo_audit_score':
                scores[analysis_type] = self.analysis_results.get('seo_audit_category_score', 0) # Use .get for safety
        
        # Calcola media ponderata
        weighted_sum = 0
        current_total_weight = 0
        for key, score_value in scores.items():
            if key in SEO_WEIGHTS: # Ensure the key exists in SEO_WEIGHTS
                weighted_sum += score_value * SEO_WEIGHTS[key]
                current_total_weight += SEO_WEIGHTS[key]
            else:
                self.logger.warning(f"Ponderazione per '{key}' non trovata in SEO_WEIGHTS. Sarà ignorato nel calcolo del punteggio generale.")

        self.logger.info(f"Somma ponderata: {weighted_sum}, Peso totale considerato: {current_total_weight}")
        
        # Log details of scores and weights used
        for key in SEO_WEIGHTS:
            score_val = scores.get(key, "N/A (non calcolato o mancante)")
            weight_val = SEO_WEIGHTS[key]
            self.logger.debug(f"Overall Score Component: {key} - Score: {score_val}, Weight: {weight_val}")

        if current_total_weight == 0:
             self.logger.warning("Il peso totale per il calcolo del punteggio generale è 0. Il punteggio generale sarà 0.")
             return 0

        # Ensure the sum of SEO_WEIGHTS used matches 100 if that's the convention.
        # If current_total_weight is not 100 (e.g. some scores were not found), this will normalize.
        # However, it's better if all components are present.
        # For now, let's assume total_weight should be the sum of all defined weights in SEO_WEIGHTS
        expected_total_weight = sum(SEO_WEIGHTS.values())
        if current_total_weight != expected_total_weight:
            self.logger.warning(f"Il peso totale corrente ({current_total_weight}) non corrisponde al peso totale atteso ({expected_total_weight}) da SEO_WEIGHTS.")
            # Decide handling: either use current_total_weight or expected_total_weight.
            # Using current_total_weight makes sense if some scores legitimately cannot be calculated.
            # If all scores *should* be there, then expected_total_weight might be better to highlight missing parts.
            # For robustness, using current_total_weight for scores actually present.

        return int(weighted_sum / current_total_weight) if current_total_weight > 0 else 0
    
    def _generate_recommendations(self) -> List[Dict]:
        """Genera raccomandazioni basate sull'analisi"""
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
        # Calculate total issues from the new structure
        total_new_issues = 0
        if 'classified_detailed_issues' in self.analysis_results:
            classified_issues = self.analysis_results['classified_detailed_issues']
            if isinstance(classified_issues, dict): # Ensure it's a dict before iterating
                for category_data in classified_issues.values():
                    if isinstance(category_data, dict): # Ensure it's a dict
                        for impact_data in category_data.values():
                            if isinstance(impact_data, dict): # Ensure it's a dict
                                for check_id_data in impact_data.values():
                                    if isinstance(check_id_data, dict): # Ensure it's a dict
                                        total_new_issues += check_id_data.get('count', 0)

        return {
            'domain': self.domain,
            'report_title': f"SEO Analysis Report for {self.domain}", # Added this line
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_pages_analyzed': len(self.pages_data),
            'overall_score': self.analysis_results['overall_score'],
            'total_issues': total_new_issues, # Updated to count from new structure
            'total_recommendations': len(self.analysis_results.get('recommendations', [])), # Ensure recommendations exist
            'score_breakdown': {
                'excellent': self.analysis_results['overall_score'] >= 90,
                'good': 70 <= self.analysis_results['overall_score'] < 90,
                'needs_improvement': 50 <= self.analysis_results['overall_score'] < 70,
                'poor': self.analysis_results['overall_score'] < 50
            }
        }