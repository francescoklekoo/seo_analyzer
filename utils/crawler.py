"""
Web Crawler per l'analisi SEO
"""

import requests
import time
import logging
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
from typing import List, Dict, Set, Optional
from tqdm import tqdm
import threading
from queue import Queue

from config import *

class WebCrawler:
    """
    Classe principale per il crawling di siti web
    """
    
    def __init__(self, start_url: str, callback=None):
        self.start_url = self._normalize_url(start_url)
        self.domain = urlparse(self.start_url).netloc
        self.visited_urls: Set[str] = set()
        self.to_visit: Queue = Queue()
        self.pages_data: List[Dict] = []
        self.robots_txt = None
        self.sitemap_urls = []
        self.callback = callback  # Callback per aggiornare la GUI
        self.is_running = False
        self.session = requests.Session()
        self.driver = None
        
        # Configura la sessione HTTP
        self.session.headers.update(HTTP_HEADERS)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format']
        )
        
    def _normalize_url(self, url: str) -> str:
        """Normalizza l'URL aggiungendo https se mancante"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    
    def _is_valid_url(self, url: str) -> bool:
        """Controlla se l'URL è valido"""
        return bool(re.match(URL_REGEX, url))
    
    def _should_crawl_url(self, url: str) -> bool:
        """Determina se un URL dovrebbe essere crawlato"""
        parsed_url = urlparse(url)
        
        # Controlla se è dello stesso dominio
        if not CRAWL_CONFIG['follow_external'] and parsed_url.netloc != self.domain:
            return False
        
        # Controlla le estensioni ignorate
        path = parsed_url.path.lower()
        if any(path.endswith(ext) for ext in IGNORED_EXTENSIONS):
            return False
        
        # Controlla robots.txt
        if CRAWL_CONFIG['respect_robots'] and self.robots_txt:
            try:
                if not self.robots_txt.can_fetch('*', url):
                    return False
            except:
                pass
        
        return True
    
    def _setup_selenium(self):
        """Configura il driver Selenium"""
        try:
            chrome_options = Options()
            
            if SELENIUM_CONFIG['headless']:
                chrome_options.add_argument('--headless')
            
            for option in SELENIUM_CONFIG['chrome_options']:
                chrome_options.add_argument(option)
            
            chrome_options.add_argument(f"--window-size={SELENIUM_CONFIG['window_size'][0]},{SELENIUM_CONFIG['window_size'][1]}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.set_page_load_timeout(SELENIUM_CONFIG['page_load_timeout'])
            self.driver.implicitly_wait(SELENIUM_CONFIG['implicit_wait'])
            
            return True
        except Exception as e:
            self.logger.error(f"Errore configurazione Selenium: {e}")
            return False
    
    def _load_robots_txt(self):
        """Carica e analizza robots.txt"""
        try:
            robots_url = urljoin(self.start_url, '/robots.txt')
            self.robots_txt = RobotFileParser()
            self.robots_txt.set_url(robots_url)
            self.robots_txt.read()
            
            # Estrai sitemap da robots.txt
            if hasattr(self.robots_txt, 'site_maps'):
                self.sitemap_urls.extend(self.robots_txt.site_maps())
                
        except Exception as e:
            self.logger.warning(f"Impossibile caricare robots.txt: {e}")
    
    def _fetch_page(self, url: str) -> Optional[Dict]:
        """Scarica e analizza una singola pagina"""
        try:
            # Usa requests per il contenuto base
            response = self.session.get(
                url, 
                timeout=CRAWL_CONFIG['timeout'],
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Dati base della pagina
            page_data = {
                'url': url,
                'status_code': response.status_code,
                'title': self._extract_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'headings': self._extract_headings(soup),
                'images': self._extract_images(soup, url),
                'links': self._extract_links(soup, url),
                'content': self._extract_content(soup),
                'html_size': len(response.text),
                'response_time': response.elapsed.total_seconds(),
                'content_type': response.headers.get('content-type', ''),
                'last_modified': response.headers.get('last-modified', ''),
                'canonical_url': self._extract_canonical(soup),
                'lang': self._extract_language(soup),
                'schema_markup': self._extract_schema(soup),
            }
            
            # Se Selenium è disponibile, ottieni metriche aggiuntive
            if self.driver:
                page_data.update(self._get_selenium_data(url))
            
            return page_data
            
        except Exception as e:
            self.logger.error(f"Errore nel fetch di {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Estrae il titolo della pagina"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Estrae la meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict:
        """Estrae tutti i tag di heading"""
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [h.get_text().strip() for h in h_tags]
        return headings
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Estrae informazioni sulle immagini"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                images.append({
                    'src': urljoin(base_url, src),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                })
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Estrae tutti i link dalla pagina"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'url': absolute_url,
                'text': link.get_text().strip(),
                'title': link.get('title', ''),
                'rel': link.get('rel', []),
                'is_external': urlparse(absolute_url).netloc != self.domain
            })
            
            # Aggiungi alla coda se è interno e non ancora visitato
            if (self._should_crawl_url(absolute_url) and 
                absolute_url not in self.visited_urls and
                len(self.visited_urls) < CRAWL_CONFIG['max_pages']):
                self.to_visit.put(absolute_url)
        
        return links
    
    def _extract_content(self, soup: BeautifulSoup) -> Dict:
        """Estrae il contenuto testuale della pagina"""
        # Rimuovi script e style
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        words = text.split()
        
        return {
            'text': text,
            'word_count': len(words),
            'character_count': len(text),
            'text_html_ratio': len(text) / len(str(soup)) if len(str(soup)) > 0 else 0
        }
    
    def _extract_canonical(self, soup: BeautifulSoup) -> str:
        """Estrae l'URL canonico"""
        canonical = soup.find('link', rel='canonical')
        return canonical.get('href', '') if canonical else ""
    
    def _extract_language(self, soup: BeautifulSoup) -> str:
        """Estrae la lingua della pagina"""
        html_tag = soup.find('html')
        return html_tag.get('lang', '') if html_tag else ""
    
    def _extract_schema(self, soup: BeautifulSoup) -> List[Dict]:
        """Estrae markup schema.org"""
        schemas = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                schemas.append({
                    'type': 'json-ld',
                    'content': json.loads(script.string)
                })
            except:
                pass
        
        # Microdata
        for item in soup.find_all(attrs={'itemscope': True}):
            schemas.append({
                'type': 'microdata',
                'itemtype': item.get('itemtype', ''),
                'properties': {}
            })
        
        return schemas
    
    def _get_selenium_data(self, url: str) -> Dict:
        """Ottiene dati aggiuntivi usando Selenium"""
        try:
            self.driver.get(url)
            
            # Tempo di caricamento
            navigation_start = self.driver.execute_script("return window.performance.timing.navigationStart")
            dom_complete = self.driver.execute_script("return window.performance.timing.domComplete")
            page_load_time = (dom_complete - navigation_start) / 1000.0
            
            # Dimensioni viewport
            viewport_size = self.driver.execute_script("return {width: window.innerWidth, height: window.innerHeight}")
            
            # JavaScript errors (se presenti nei log)
            js_errors = []
            try:
                logs = self.driver.get_log('browser')
                js_errors = [log for log in logs if log['level'] == 'SEVERE']
            except:
                pass
            
            return {
                'page_load_time': page_load_time,
                'viewport_size': viewport_size,
                'js_errors': js_errors,
                'has_javascript': True
            }
            
        except Exception as e:
            self.logger.warning(f"Errore Selenium per {url}: {e}")
            return {'has_javascript': False}
    
    def crawl(self) -> List[Dict]:
        """Esegue il crawling completo del sito"""
        self.is_running = True
        self.logger.info(f"Inizio crawling di {self.start_url}")
        
        if self.callback:
            self.callback("Inizializzazione crawler...")
        
        # Setup iniziale
        self._load_robots_txt()
        selenium_available = self._setup_selenium()
        
        # Aggiungi URL di partenza
        self.to_visit.put(self.start_url)
        
        try:
            with tqdm(total=CRAWL_CONFIG['max_pages'], desc="Crawling pagine") as pbar:
                while (not self.to_visit.empty() and 
                       len(self.visited_urls) < CRAWL_CONFIG['max_pages'] and
                       self.is_running):
                    
                    current_url = self.to_visit.get()
                    
                    if current_url in self.visited_urls:
                        continue
                    
                    if self.callback:
                        self.callback(f"Analizzando: {current_url}")
                    
                    # Fetch della pagina
                    page_data = self._fetch_page(current_url)
                    
                    if page_data:
                        self.pages_data.append(page_data)
                        self.visited_urls.add(current_url)
                        pbar.update(1)
                        
                        if self.callback:
                            self.callback(f"Completate {len(self.visited_urls)} pagine su {CRAWL_CONFIG['max_pages']}")
                    
                    # Delay tra le richieste
                    time.sleep(CRAWL_CONFIG['delay'])
                    
        except KeyboardInterrupt:
            self.logger.info("Crawling interrotto dall'utente")
        
        finally:
            if self.driver:
                self.driver.quit()
            
            self.is_running = False
            
        self.logger.info(f"Crawling completato. Analizzate {len(self.pages_data)} pagine")
        
        if self.callback:
            self.callback(f"Crawling completato! Analizzate {len(self.pages_data)} pagine")
        
        return self.pages_data
    
    def stop_crawling(self):
        """Ferma il crawling"""
        self.is_running = False
        if self.driver:
            self.driver.quit()
    
    def get_crawl_summary(self) -> Dict:
        """Restituisce un riassunto del crawling"""
        if not self.pages_data:
            return {}
        
        total_pages = len(self.pages_data)
        total_images = sum(len(page.get('images', [])) for page in self.pages_data)
        total_links = sum(len(page.get('links', [])) for page in self.pages_data)
        avg_response_time = sum(page.get('response_time', 0) for page in self.pages_data) / total_pages
        
        return {
            'total_pages': total_pages,
            'total_images': total_images,
            'total_links': total_links,
            'average_response_time': avg_response_time,
            'domain': self.domain,
            'start_url': self.start_url,
            'pages_with_title': sum(1 for page in self.pages_data if page.get('title')),
            'pages_with_meta_desc': sum(1 for page in self.pages_data if page.get('meta_description')),
        }