import unittest
from unittest.mock import MagicMock # Or patch if more complex mocking is needed

# Assuming utils and config are accessible from the test environment
# This might require adjusting PYTHONPATH or the test runner setup
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.analyzer import SEOAnalyzer
from config import SEO_CONFIG, PERFORMANCE_CONFIG # For referencing thresholds if needed in tests

class TestSEOAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.mock_pages_data = [] # Placeholder, to be filled by specific tests
        # Initialize SEOAnalyzer with minimal data for methods that don't rely on full crawl data
        self.analyzer = SEOAnalyzer(pages_data=[], domain="example.com")
        # Mock logger if its output is not desired during tests
        self.analyzer.logger = MagicMock()
        # Ensure detailed_issues is initialized for _calculate_site_health tests
        self.analyzer.analysis_results['detailed_issues'] = {
            'errors': [], 'warnings': [], 'notices': []
        }


    def test_calculate_site_health_logic(self):
        """Test the _calculate_site_health method with various scenarios."""
        # Scenario 1: No issues
        self.analyzer.analysis_results['detailed_issues'] = {'errors': [], 'warnings': [], 'notices': []}
        health_results = self.analyzer._calculate_site_health()
        self.assertEqual(health_results['health_percentage'], 100)
        self.assertEqual(health_results['total_critical_issues'], 0)
        self.assertEqual(health_results['total_warning_issues'], 0)
        self.assertEqual(health_results['total_notice_issues'], 0)

        # Scenario 2: Only errors
        self.analyzer.analysis_results['detailed_issues']['errors'] = [{'type': 'e1'}, {'type': 'e2'}]
        health_results = self.analyzer._calculate_site_health()
        self.assertEqual(health_results['health_percentage'], 90) # 100 - 2*5
        self.assertEqual(health_results['total_critical_issues'], 2)

        # Scenario 3: Only warnings
        self.analyzer.analysis_results['detailed_issues'] = {'errors': [], 'warnings': [{'type': 'w1'}]*3, 'notices': []}
        health_results = self.analyzer._calculate_site_health()
        self.assertEqual(health_results['health_percentage'], 94) # 100 - 3*2
        self.assertEqual(health_results['total_warning_issues'], 3)
        
        # Scenario 4: Only notices
        self.analyzer.analysis_results['detailed_issues'] = {'errors': [], 'warnings': [], 'notices': [{'type': 'n1'}]*4}
        health_results = self.analyzer._calculate_site_health()
        self.assertEqual(health_results['health_percentage'], 98) # 100 - 4*0.5
        self.assertEqual(health_results['total_notice_issues'], 4)

        # Scenario 5: Mixed issues
        self.analyzer.analysis_results['detailed_issues'] = {
            'errors': [{'type': 'e1'}],
            'warnings': [{'type': 'w1'}, {'type': 'w2'}],
            'notices': [{'type': 'n1'}, {'type': 'n2'}, {'type': 'n3'}]
        }
        health_results = self.analyzer._calculate_site_health()
        # 100 - (1*5) - (2*2) - (3*0.5) = 100 - 5 - 4 - 1.5 = 89.5, rounds to 90
        self.assertEqual(health_results['health_percentage'], 90) 
        self.assertEqual(health_results['total_critical_issues'], 1)
        self.assertEqual(health_results['total_warning_issues'], 2)
        self.assertEqual(health_results['total_notice_issues'], 3)

        # Scenario 6: Score capping at 0
        self.analyzer.analysis_results['detailed_issues']['errors'] = [{'type': 'e'}] * 30 # 30 * 5 = 150 penalty
        self.analyzer.analysis_results['detailed_issues']['warnings'] = []
        self.analyzer.analysis_results['detailed_issues']['notices'] = []
        health_results = self.analyzer._calculate_site_health()
        self.assertEqual(health_results['health_percentage'], 0)
        self.assertEqual(health_results['total_critical_issues'], 30)
        
        # Scenario 7: Empty pages_data (should also be handled by the initial check in the method)
        self.analyzer.pages_data = []
        health_results_empty_pages = self.analyzer._calculate_site_health()
        self.assertEqual(health_results_empty_pages['health_percentage'], 100) # As per current logic
        self.assertEqual(health_results_empty_pages['total_critical_issues'], 0)


    def test_analyze_images_attributes(self):
        """Test _analyze_images for alt and title attribute counting."""
        self.analyzer.pages_data = [
            {'url': 'page1', 'images': [
                {'src': 'img1.png', 'alt': 'Alt text', 'title': 'Title text'}, # Both present
                {'src': 'img2.png', 'alt': None, 'title': 'Title text'},       # Alt missing, title present
                {'src': 'img3.png', 'alt': 'Alt text', 'title': None},       # Alt present, title missing
                {'src': 'img4.png', 'alt': None, 'title': None},             # Both missing
                {'src': 'img5.png', 'alt': '', 'title': 'Title text'},        # Alt empty, title present
                {'src': 'img6.png', 'alt': 'Alt text', 'title': ''},         # Alt present, title empty
                {'src': 'img7.png', 'alt': '  ', 'title': '  '},           # Alt whitespace, title whitespace (counts as empty)
            ]}
        ]
        image_analysis_results = self.analyzer._analyze_images()

        self.assertEqual(image_analysis_results['total_images'], 7)
        self.assertEqual(image_analysis_results['images_with_alt'], 2) # img1, img6
        self.assertEqual(image_analysis_results['images_without_alt'], 2) # img2, img4 (None)
        self.assertEqual(image_analysis_results['images_with_empty_alt'], 2) # img5 (''), img7 ('  ')
        
        self.assertEqual(image_analysis_results['images_with_title_attr'], 2) # img1, img5
        self.assertEqual(image_analysis_results['images_without_title_attr'], 2) # img3, img4 (None)
        self.assertEqual(image_analysis_results['images_with_empty_title_attr'], 2) # img6 (''), img7 ('  ')


    def test_analyze_detailed_issues_for_images(self):
        """Test _analyze_detailed_issues for correct population of image issues."""
        self.analyzer.pages_data = [
            {'url': 'page_a', 'images': [
                {'src': 'img_no_alt.png', 'title': 'Present Title'}, # Alt missing
                {'src': 'img_empty_alt.png', 'alt': '', 'title': 'Present Title'}, # Alt empty
            ]},
            {'url': 'page_b', 'images': [
                {'src': 'img_no_title.png', 'alt': 'Present Alt'}, # Title missing
                {'src': 'img_empty_title.png', 'alt': 'Present Alt', 'title': ''}, # Title empty
            ]}
        ]
        
        # _analyze_detailed_issues populates self.analysis_results['detailed_issues']
        # It's called within analyze_all, or can be called directly if other results are mocked/not needed
        # For this test, directly call it and then inspect the results.
        # Need to ensure 'detailed_issues' is part of 'analysis_results' before calling.
        self.analyzer.analysis_results['detailed_issues'] = {} # Reset for this specific test call
        detailed_issues = self.analyzer._analyze_detailed_issues() # This method returns the dict

        # Check images_without_alt
        self.assertIn('images_without_alt', detailed_issues)
        self.assertEqual(len(detailed_issues['images_without_alt']), 1)
        self.assertEqual(detailed_issues['images_without_alt'][0]['url'], 'page_a')
        self.assertEqual(detailed_issues['images_without_alt'][0]['image_src'], 'img_no_alt.png')
        self.assertEqual(detailed_issues['images_without_alt'][0]['issue'], 'Attributo ALT HTML mancante')

        # Check images_with_empty_alt
        self.assertIn('images_with_empty_alt', detailed_issues)
        self.assertEqual(len(detailed_issues['images_with_empty_alt']), 1)
        self.assertEqual(detailed_issues['images_with_empty_alt'][0]['url'], 'page_a')
        self.assertEqual(detailed_issues['images_with_empty_alt'][0]['image_src'], 'img_empty_alt.png')
        self.assertEqual(detailed_issues['images_with_empty_alt'][0]['issue'], 'Attributo ALT vuoto')
        
        # Check images_without_title_attr
        self.assertIn('images_without_title_attr', detailed_issues)
        self.assertEqual(len(detailed_issues['images_without_title_attr']), 1)
        self.assertEqual(detailed_issues['images_without_title_attr'][0]['url'], 'page_b')
        self.assertEqual(detailed_issues['images_without_title_attr'][0]['image_src'], 'img_no_title.png')
        self.assertEqual(detailed_issues['images_without_title_attr'][0]['issue'], 'Attributo Title HTML mancante')

        # Check images_with_empty_title_attr
        self.assertIn('images_with_empty_title_attr', detailed_issues)
        self.assertEqual(len(detailed_issues['images_with_empty_title_attr']), 1)
        self.assertEqual(detailed_issues['images_with_empty_title_attr'][0]['url'], 'page_b')
        self.assertEqual(detailed_issues['images_with_empty_title_attr'][0]['image_src'], 'img_empty_title.png')
        self.assertEqual(detailed_issues['images_with_empty_title_attr'][0]['issue'], 'Attributo Title vuoto')

        # Check 'warnings' list for alt issues
        warnings = detailed_issues.get('warnings', [])
        missing_alt_warning = next((w for w in warnings if w['type'] == 'missing_alt_attr' and w['image'] == 'img_no_alt.png'), None)
        empty_alt_warning = next((w for w in warnings if w['type'] == 'empty_alt_attr' and w['image'] == 'img_empty_alt.png'), None)
        self.assertIsNotNone(missing_alt_warning)
        self.assertEqual(missing_alt_warning['url'], 'page_a')
        self.assertIsNotNone(empty_alt_warning)
        self.assertEqual(empty_alt_warning['url'], 'page_a')
        
        # Check 'notices' list for title issues
        notices = detailed_issues.get('notices', [])
        missing_title_notice = next((n for n in notices if n['type'] == 'missing_title_attr' and n['image'] == 'img_no_title.png'), None)
        empty_title_notice = next((n for n in notices if n['type'] == 'empty_title_attr' and n['image'] == 'img_empty_title.png'), None)
        self.assertIsNotNone(missing_title_notice)
        self.assertEqual(missing_title_notice['url'], 'page_b')
        self.assertIsNotNone(empty_title_notice)
        self.assertEqual(empty_title_notice['url'], 'page_b')

if __name__ == '__main__':
    unittest.main()
