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
        
    def analyze_all(self) -> Dict:
        """Esegue tutte le analisi SEO"""
        self.logger.info("Inizio analisi SEO completa")
        
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
            'detailed_issues': self._analyze_detailed_issues(),  # Nuova analisi dettagliata
            'site_health': self._calculate_site_health(),  # Calcolo stato sito
            'overall_score': 0,
            'recommendations': [],
            'summary': {}
        }
        
        # Calcola il punteggio generale
        self.analysis_results['overall_score'] = self._calculate_overall_score()
        
        # Genera raccomandazioni
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
        """Analisi dettagliata dei problemi specifici"""
        detailed = {
            'errors': [],      # Errori gravi
            'warnings': [],    # Avvertimenti
            'notices': [],     # Informazioni/suggerimenti
            'missing_h1_pages': [],
            'missing_h2_pages': [],
            'missing_h3_pages': [],
            'images_without_alt': [],
            'images_without_title': [],
            'duplicate_titles': [],
            'duplicate_meta_descriptions': [],
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
                detailed['warnings'].append({
                    'type': 'multiple_h1',
                    'url': url,
                    'message': f'Multipli H1 trovati ({h1_count})'
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
                img_alt = img.get('alt', '').strip()
                img_title = img.get('title', '').strip()
                
                if not img_alt:
                    detailed['images_without_alt'].append({
                        'url': url,
                        'image_src': img_src,
                        'issue': 'Alt text mancante'
                    })
                    detailed['warnings'].append({
                        'type': 'missing_alt',
                        'url': url,
                        'image': img_src,
                        'message': 'Immagine senza alt text'
                    })
                
                if not img_title:
                    detailed['images_without_title'].append({
                        'url': url,
                        'image_src': img_src,
                        'issue': 'Title mancante'
                    })
                    detailed['notices'].append({
                        'type': 'missing_img_title',
                        'url': url,
                        'image': img_src,
                        'message': 'Immagine senza attributo title'
                    })
            
            # Contenuto
            word_count = content.get('word_count', 0)
            if word_count < SEO_CONFIG['min_word_count']:
                detailed['low_word_count_pages'].append({
                    'url': url,
                    'word_count': word_count,
                    'issue': f'Contenuto scarso ({word_count} parole)'
                })
                detailed['warnings'].append({
                    'type': 'low_content',
                    'url': url,
                    'message': f'Contenuto insufficiente ({word_count} parole)'
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
        self._find_duplicates(detailed)
        
        return detailed
    
    def _find_duplicates(self, detailed: Dict):
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
        
        # Calcola media ponderata
        weighted_sum = sum(scores[key] * SEO_WEIGHTS[key] for key in scores)
        total_weight = sum(SEO_WEIGHTS.values())
        
        return int(weighted_sum / total_weight) if total_weight > 0 else 0
    
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
        return {
            'domain': self.domain,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_pages_analyzed': len(self.pages_data),
            'overall_score': self.analysis_results['overall_score'],
            'total_issues': sum(len(analysis.get('issues', [])) for analysis in self.analysis_results.values() if isinstance(analysis, dict)),
            'total_recommendations': len(self.analysis_results['recommendations']),
            'score_breakdown': {
                'excellent': self.analysis_results['overall_score'] >= 90,
                'good': 70 <= self.analysis_results['overall_score'] < 90,
                'needs_improvement': 50 <= self.analysis_results['overall_score'] < 70,
                'poor': self.analysis_results['overall_score'] < 50
            }
        }