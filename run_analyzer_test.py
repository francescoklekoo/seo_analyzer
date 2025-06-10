import json
import os
import logging
from typing import Dict, List, Tuple, Any
import statistics # Needed for statistics.mean in the original _calculate_site_health

# Assuming utils.analyzer and config are in the PYTHONPATH or accessible
# For this test, we'll redefine parts of SEOAnalyzer to inject mocks easily
from utils.analyzer import SEOAnalyzer
from config import (
    SEO_CONFIG, PERFORMANCE_CONFIG,
    AUDIT_CHECKS_CONFIG, PDF_ISSUE_DESCRIPTIONS, CATEGORY_OCM, CATEGORY_SEO_AUDIT,
    CORE_WEB_VITALS_THRESHOLDS, SERVER_RESPONSE_TIME_ERROR,
    NEW_SCORING_CLASSIFICATION, TOUCH_ELEMENT_MIN_SIZE_PX # Removed SEO_WEIGHTS
)

# Configure basic logging for the analyzer part if it logs errors/warnings
logging.basicConfig(level=logging.INFO)

# 1. Define Sample pages_data
sample_pages_data = [
    {
        'url': 'http://example.com/', # Changed to end with / for LCP test
        'title': "Welcome", # Too short for SEO_CONFIG['title_min_length'] = 30
        'meta_description': "", # Missing
        'status_code': 200,
        'response_time': 0.7, # seconds -> 700ms, > SERVER_RESPONSE_TIME_ERROR (600ms)
        'performance_metrics': {'lcp': 4.5, 'inp': 550, 'cls': 0.30}, # LCP, INP, CLS errors
        'has_viewport_tag': False, # OCM Error: ocm_no_viewport_tag_error
        'headings': {'h1': ['Main Title', 'Another Main Title']}, # Multiple H1s -> seo_h1_missing_or_improper_use_warning
        'content': {'word_count': 100}, # Thin content -> seo_thin_content_pages_error (threshold 150)
                                        # Also triggers seo_content_length_inadequate_warning (threshold 300)
        'images': [{'src': 'img1.jpg', 'alt': None}], # Missing alt -> ocm_image_alt_attribute_usage_notice
        'schema_markup': [], # Triggers ocm_structured_data_implemented_notice
        'broken_internal_links': [{'target_url': 'http://example.com/brokenpage1', 'anchor_text': 'Broken Link 1'}], # ocm_broken_internal_links_warning
        'links': [{'url': 'http://example.com/pagex', 'is_external': False, 'text': 'Link X'}], # For ocm_internal_linking_insufficient_warning (1 link < 3)
        'has_mixed_content': True, # For ocm_mixed_content_warning
    },
    {
        'url': 'http://example.com/page2',
        'title': "Example Page 2 Title Which Is Definitely Long Enough And Optimized For SEO", # Good length
        'meta_description': "A good meta description for page 2 that is of optimal length and describes content well, hopefully exceeding the minimum character count for sure.", # Good length
        'status_code': 200,
        'response_time': 0.1, # 100ms
        'performance_metrics': {'lcp': 1.0, 'inp': 100, 'cls': 0.05}, # Good CWV
        'has_viewport_tag': True,
        'headings': {'h1': ['Page 2 Title'], 'h3': ['Sub-subheading without H2']}, # Inconsistent header structure
        'content': {'word_count': 400}, # Good word count
        'images': [{'src': 'img2.jpg', 'alt': 'Alt text for image 2'}],
        'schema_markup': [{'type': 'Article'}], # Has some schema
        'redirect_chain_hops': 4, # For ocm_redirect_chains_warning
    },
    {
        'url': 'http://example.com/nonexistent',
        'title': "Not Found", # Will be checked for length
        'meta_description': "This page was not found.",  # Will be checked for length
        'status_code': 404, # Triggers 404 related checks
        'response_time': 0.05,
        'performance_metrics': {'lcp': 0.5, 'inp': 50, 'cls': 0.01},
        'has_viewport_tag': True,
        'headings': {'h1': ['Not Found Page Title']},
        'content': {'word_count': 10}, # Thin content
        'images': [],
        'schema_markup': [],
    },
    { # To test duplicate titles/metas for seo_title_meta_missing_duplicated_error
        'url': 'http://example.com/another-welcome',
        'title': "Welcome", # Duplicate of homepage title
        'meta_description': "Another page also welcoming users.", # Assume this is unique for now
        'status_code': 200,
        'response_time': 0.2,
        'performance_metrics': {'lcp': 1.5, 'inp': 150, 'cls': 0.10},
        'has_viewport_tag': True,
        'headings': {'h1': ['Welcome Too']},
        'content': {'word_count': 350},
        'images': [],
        'schema_markup': [],
    }
]

class MockedSEOAnalyzer(SEOAnalyzer):
    def _analyze_detailed_issues(self):
        self.logger.info("Inizio MOCKED analisi dettagliata dei problemi...")

        # --- TEMPORARY TEST MOCKS START ---
        # These are hardcoded for testing site-wide checks.
        site_uses_cdn_test_mock = False # For ocm_no_cdn_global_error
        eeat_signals_present_test_mock = False # For seo_no_eeat_signals_error
        has_structured_data_errors_test_mock = True # For ocm_structured_data_errors_warning
        # --- TEMPORARY TEST MOCKS END ---

        # This is a simplified version of the loop in the actual analyzer,
        # focusing on ensuring the mocks are used and some sample checks are processed.
        # In a real test environment, you might not override the method this way,
        # or you'd call super()._analyze_detailed_issues() and then assert.
        # For this subtask, we are directly inserting the logic with mocks.

        for check_key, check_config in AUDIT_CHECKS_CONFIG.items():
            category = check_config['category']
            severity = check_config['severity']

            # OCM ERROR CHECKS
            if check_key == 'ocm_lcp_error':
                for page in self.pages_data:
                    lcp = page.get('performance_metrics', {}).get('lcp', 0)
                    if lcp > CORE_WEB_VITALS_THRESHOLDS['LCP_ERROR']:
                        self.analysis_results['categorized_issues'][category][severity].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"LCP è {lcp}s.", 'description_key': check_config['description_key'], 'severity': severity
                        })
            elif check_key == 'ocm_server_response_time_error':
                for page in self.pages_data:
                    response_time_ms = page.get('response_time', 0) * 1000
                    if response_time_ms > SERVER_RESPONSE_TIME_ERROR:
                        self.analysis_results['categorized_issues'][category][severity].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"Tempo di risposta del server è {response_time_ms:.0f}ms.", 'description_key': check_config['description_key'], 'severity': severity
                        })
            elif check_key == 'ocm_no_cdn_global_error':
                if not site_uses_cdn_test_mock and severity == 'ERROR': # Mocked
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Assenza CDN per siti globali (mock test).",
                        'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })
            elif check_key == 'ocm_no_https_error':
                 # Using existing ssl_analysis results which should be populated by analyze_all() before this
                if self.analysis_results.get('ssl_analysis', {}).get('has_ssl') is False and severity == 'ERROR':
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Assenza implementazione HTTPS.", 'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })
            elif check_key == 'ocm_no_viewport_tag_error':
                for page in self.pages_data:
                    if not page.get('has_viewport_tag', True) and severity == 'ERROR':
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': "Meta tag viewport mancante.", 'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })

            # OCM WARNING CHECKS
            elif check_key == 'ocm_structured_data_errors_warning':
                if has_structured_data_errors_test_mock and severity == 'WARNING': # Mocked
                    self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Rilevati errori (non critici) nei dati strutturati (mock test).",
                        'description_key': check_config['description_key'], 'severity': 'WARNING'
                    })
            elif check_key == 'ocm_redirect_chains_warning':
                max_hops_allowed = 3
                for page in self.pages_data:
                    hops = page.get('redirect_chain_hops', 0)
                    if hops > max_hops_allowed and severity == 'WARNING':
                         self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'), # page.get('original_url', page.get('url')),
                            'details': f"Rilevata catena di redirect con {hops} hop.", 'description_key': check_config['description_key'], 'severity': 'WARNING'
                        })
            elif check_key == 'ocm_broken_internal_links_warning':
                for page in self.pages_data:
                    broken_links_on_page = page.get('broken_internal_links', [])
                    if broken_links_on_page and severity == 'WARNING':
                        for bl in broken_links_on_page:
                             self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                                'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                                'details': f"Link rotto interno a {bl.get('target_url', 'N/A')}.", 'description_key': check_config['description_key'], 'severity': 'WARNING'
                            })
            elif check_key == 'ocm_internal_linking_insufficient_warning':
                MIN_INTERNAL_LINKS_PER_PAGE = 3
                for page in self.pages_data:
                    internal_links_count = sum(1 for link in page.get('links', []) if not link.get('is_external', True))
                    if internal_links_count < MIN_INTERNAL_LINKS_PER_PAGE and severity == 'WARNING':
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"Pagina con solo {internal_links_count} link interni.", 'description_key': check_config['description_key'], 'severity': 'WARNING'
                        })
            elif check_key == 'ocm_mixed_content_warning':
                for page in self.pages_data:
                    if page.get('has_mixed_content', False) and severity == 'WARNING':
                        self.analysis_results['categorized_issues'][CATEGORY_OCM]['WARNING'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': "Rilevato mixed content sulla pagina.", 'description_key': check_config['description_key'], 'severity': 'WARNING'
                        })


            # OCM NOTICE CHECKS
            elif check_key == 'ocm_meta_description_missing_notice':
                 for page in self.pages_data:
                    if not page.get('meta_description', '').strip() and severity == 'NOTICE':
                         self.analysis_results['categorized_issues'][CATEGORY_OCM]['NOTICE'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': 'Meta description mancante.', 'description_key': check_config['description_key'], 'severity': 'NOTICE'
                        })
            elif check_key == 'ocm_image_alt_attribute_usage_notice':
                for page in self.pages_data:
                    for img in page.get('images', []):
                        if img.get('alt') is None or img.get('alt', '').strip() == '':
                            if severity == 'NOTICE':
                                self.analysis_results['categorized_issues'][CATEGORY_OCM]['NOTICE'].append({
                                    'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                                    'details': f"Immagine ({img.get('src','N/A')}) senza ALT text o con ALT vuoto.", 'description_key': check_config['description_key'], 'severity': 'NOTICE'
                                })
                                break # Only one notice per page for this example
                    else: continue
                    break


            # SITE SEO AUDIT ERROR CHECKS
            elif check_key == 'seo_no_eeat_signals_error':
                if not eeat_signals_present_test_mock and severity == 'ERROR': # Mocked
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Assenza segnali E-E-A-T (mock test).", 'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })
            elif check_key == 'seo_thin_content_pages_error':
                THIN_CONTENT_THRESHOLD = 150
                for page in self.pages_data:
                    word_count = page.get('content', {}).get('word_count', 0)
                    if 0 < word_count < THIN_CONTENT_THRESHOLD and severity == 'ERROR':
                        self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"Contenuto scarso: {word_count} parole.", 'description_key': check_config['description_key'], 'severity': 'ERROR'
                        })
            elif check_key == 'seo_title_meta_missing_duplicated_error':
                # This logic is simplified for the test; actual would use self.analysis_results['title_analysis'] etc.
                # For this test, we'll just check the first page for missing meta, and duplicate title with page 4
                if not sample_pages_data[0].get('meta_description') and severity == 'ERROR':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': sample_pages_data[0]['url'],
                        'details': "Meta description mancante su homepage.", 'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })
                if sample_pages_data[0]['title'] == sample_pages_data[3]['title'] and severity == 'ERROR':
                     self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['ERROR'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain, # Site-level for duplicate
                        'details': f"Titolo '{sample_pages_data[0]['title']}' duplicato.", 'description_key': check_config['description_key'], 'severity': 'ERROR'
                    })


            # SITE SEO AUDIT WARNING CHECKS
            elif check_key == 'seo_h1_missing_or_improper_use_warning':
                for page in self.pages_data:
                    h1_list = page.get('headings', {}).get('h1', [])
                    if (len(h1_list) == 0 or len(h1_list) > 1) and severity == 'WARNING':
                        self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['WARNING'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"Numero H1 non ottimale: {len(h1_list)}.", 'description_key': check_config['description_key'], 'severity': 'WARNING'
                        })
            elif check_key == 'seo_content_length_inadequate_warning':
                for page in self.pages_data:
                    word_count = page.get('content', {}).get('word_count', 0)
                    # Trigger if word count is > thin threshold (150) but < general min_word_count (300)
                    if 150 <= word_count < SEO_CONFIG['min_word_count'] and severity == 'WARNING':
                        self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['WARNING'].append({
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': f"Lunghezza contenuto {word_count} parole (sotto best practice di {SEO_CONFIG['min_word_count']}).",
                            'description_key': check_config['description_key'], 'severity': 'WARNING'
                        })

            # SITE SEO AUDIT NOTICE CHECKS
            elif check_key == 'seo_gmb_not_optimized_notice':
                gmb_is_optimized_mock = False # Placeholder
                if not gmb_is_optimized_mock and severity == 'NOTICE':
                    self.analysis_results['categorized_issues'][CATEGORY_SEO_AUDIT]['NOTICE'].append({
                        'key': check_key, 'label': check_config['label'], 'url': self.domain,
                        'details': "Profilo GMB non ottimizzato (mock test).", 'description_key': check_config['description_key'], 'severity': 'NOTICE'
                    })
            elif check_key == 'seo_structured_data_implemented_notice': # This is from OCM list but used as an example
                 for page in self.pages_data:
                    if not page.get('schema_markup', []) and severity == 'NOTICE':
                         self.analysis_results['categorized_issues'][CATEGORY_OCM]['NOTICE'].append({ # Changed to OCM as per original intent
                            'key': check_key, 'label': check_config['label'], 'url': page.get('url', 'N/A'),
                            'details': "Nessun dato strutturato rilevato sulla pagina.", 'description_key': check_config['description_key'], 'severity': 'NOTICE'
                        })

        self.logger.info("MOCKED analisi dettagliata dei problemi completata.")

# Instantiate and Run MockedSEOAnalyzer
analyzer = MockedSEOAnalyzer(pages_data=sample_pages_data, domain="example.com")
analysis_results = analyzer.analyze_all()

# Prepare Output for Verification
categorized_issues = analysis_results.get('categorized_issues')
site_health_info = analysis_results.get('site_health')
overall_score = analysis_results.get('overall_score')

# Save to files
output_dir = "/tmp"
categorized_issues_file = f"{output_dir}/categorized_issues.json"
site_health_info_file = f"{output_dir}/site_health_info.json"
overall_score_file = f"{output_dir}/overall_score.txt"

os.makedirs(output_dir, exist_ok=True)

with open(categorized_issues_file, "w") as f:
    json.dump(categorized_issues, f, indent=4, ensure_ascii=False)

with open(site_health_info_file, "w") as f:
    json.dump(site_health_info, f, indent=4, ensure_ascii=False)

with open(overall_score_file, "w") as f:
    f.write(str(overall_score))

print(f"Analysis complete. Outputs saved to:")
print(f"Categorized Issues: {categorized_issues_file}")
print(f"Site Health Info: {site_health_info_file}")
print(f"Overall Score: {overall_score_file}")

health_percentage_value = site_health_info.get('health_percentage') if site_health_info else 'N/A'
print(f"CALCULATED_HEALTH_PERCENTAGE_FOR_REPORT:{health_percentage_value}")

print("--- Example Check Keys Found ---")
if categorized_issues:
    examples_found_count = 0
    for category_key_name, severities_map in categorized_issues.items():
        if examples_found_count >= 5: break
        for severity_key_name, issues_list_found in severities_map.items():
            if examples_found_count >= 5: break
            if issues_list_found:
                for issue_item in issues_list_found:
                    if examples_found_count < 5:
                        print(f"CHECK_KEY_FOR_REPORT:{issue_item['key']}")
                        examples_found_count += 1
                    else:
                        break
else:
    print("No categorized issues found for examples.")
