import unittest
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pdf_generator import PDFGenerator, Paragraph, Table, Spacer, Drawing, Pie, String, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

# Mock PDF_CONFIG directly in the test file if it's not easily importable or to override
# This is a simplified version for testing purposes
PDF_CONFIG_MOCK = {
    'font_family': 'Helvetica',
    'font_family_bold': 'Helvetica-Bold',
    'font_sizes': {'title': 20, 'heading': 15, 'body': 10, 'small': 8, 'table_header': 9, 'table_body': 9},
    'colors': {
        'primary': '#005A9C', 'primary_light': '#E6F0F8', 'primary_dark': '#003366',
        'secondary': '#D3DCE3', 'secondary_dark': '#A9B6C2',
        'text_primary': '#222222', 'text_secondary': '#555555',
        'background_light': '#F7F9FA', 'border': '#CCCCCC',
        'white': '#FFFFFF', 'black': '#000000',
        'success': '#28A745', 'warning': '#FFC107', 'error': '#DC3545',
        'table_header_bg': '#004080', 'table_header_text': '#FFFFFF',
        'table_row_bg_even': '#FFFFFF', 'table_row_bg_odd': '#F0F4F7',
    },
    'margin': {'top': 2.5, 'bottom': 2.5, 'left': 2.0, 'right': 2.0},
}


class TestPDFGenerator(unittest.TestCase):

    def setUp(self):
        self.mock_analysis_results = {
            'summary': {
                'report_title': 'Test SEO Report',
                'domain': 'testdomain.com',
                'analysis_date': '2023-10-26',
                'total_pages_analyzed': 0, # Default, can be overridden
                'total_issues': 0,
                'total_recommendations': 0,
            },
            'overall_score': 80, # Default
            'detailed_issues': {}, # Default
            'images_analysis': {}, # Default
            'title_analysis': {'score': 0, 'pages_with_title':0, 'total_pages':0, 'too_short_titles':[], 'too_long_titles':[]}, # Add all keys accessed
            'meta_description_analysis': {'score': 0, 'pages_with_meta':0, 'total_pages':0, 'too_short_metas':[], 'too_long_metas':[]},
            'headings_analysis': {'score': 0},
            'content_analysis': {'score': 0},
            'links_analysis': {'score': 0},
            'performance_analysis': {'score': 0, 'fast_pages':0, 'slow_pages':0, 'average_response_time':0, 'average_page_size':0},
            'technical_analysis': {'score': 0},
            'ssl_analysis': {'score': 0, 'has_ssl': False, 'ssl_valid': False, 'ssl_expires': None},
            'recommendations': [] # Add default for recommendations
            # Add other necessary default keys that _add_detailed_analysis_section might access in summary lists
        }
        # Patch the PDF_CONFIG used by the module with our mock
        # This is tricky as PDF_CONFIG is imported from config directly at module level.
        # A better way would be dependency injection, but for now, we assume PDF_CONFIG_MOCK values
        # are conceptually what the generator would use due to previous styling steps.
        # For tests, we'll often check for structure rather than exact styling values if they are complex.
        self.pdf_generator = PDFGenerator(self.mock_analysis_results, "testdomain.com")
        self.pdf_generator.styles = getSampleStyleSheet() # Ensure styles are loaded for Paragraphs
        self.pdf_generator._setup_custom_styles() # Apply custom styles that use conceptual new PDF_CONFIG


    def test_add_detailed_analysis_image_tables(self):
        """Test that tables for image issues are added to the story."""
        self.mock_analysis_results['detailed_issues']['images_without_alt'] = [
            {'url': 'page1.html', 'image_src': 'img_no_alt.png', 'issue': 'Attributo ALT HTML mancante'}
        ]
        self.mock_analysis_results['detailed_issues']['images_without_title_attr'] = [
            {'url': 'page2.html', 'image_src': 'img_no_title.png', 'issue': 'Attributo Title HTML mancante'}
        ]
        # Update images_analysis summary counts to match detailed_issues
        self.mock_analysis_results['images_analysis'] = {
            'total_images': 2, 'images_with_alt': 0, 'images_without_alt': 1, 
            'images_with_empty_alt': 0, 'images_with_title_attr': 0, 
            'images_without_title_attr': 1, 'images_with_empty_title_attr': 0, 'score': 50
        }

        self.pdf_generator.story = [] # Clear story before calling the method
        self.pdf_generator._add_detailed_analysis_section()

        table_titles_found = []
        table_data_checked = {}

        for item in self.pdf_generator.story:
            if isinstance(item, Paragraph) and hasattr(item, 'text'):
                if "Immagini senza Attributo ALT HTML" in item.text:
                    table_titles_found.append("alt")
                elif "Immagini senza Attributo Title HTML" in item.text:
                    table_titles_found.append("title")
            
            if isinstance(item, Table):
                headers = [cell.text for cell in item._cellvalues[0]] # Assuming Paragraphs in headers
                
                if table_titles_found and table_titles_found[-1] == "alt" and "alt" not in table_data_checked :
                    self.assertEqual(headers, ['Pagina URL', 'URL Immagine', 'Problema'])
                    # Check first data row (second row of table)
                    row_values = [cell.text for cell in item._cellvalues[1]]
                    self.assertEqual(row_values[0], 'page1.html')
                    self.assertEqual(row_values[1], 'img_no_alt.png')
                    self.assertEqual(row_values[2], 'Attributo ALT HTML mancante')
                    table_data_checked["alt"] = True
                elif table_titles_found and table_titles_found[-1] == "title" and "title" not in table_data_checked:
                    self.assertEqual(headers, ['Pagina URL', 'URL Immagine', 'Problema'])
                    row_values = [cell.text for cell in item._cellvalues[1]]
                    self.assertEqual(row_values[0], 'page2.html')
                    self.assertEqual(row_values[1], 'img_no_title.png')
                    self.assertEqual(row_values[2], 'Attributo Title HTML mancante')
                    table_data_checked["title"] = True
        
        self.assertIn("alt", table_data_checked, "Table for missing alt text not found or data incorrect.")
        self.assertIn("title", table_data_checked, "Table for missing title attribute not found or data incorrect.")


    def test_site_health_chart_content(self):
        """Test the site health pie chart data and text elements."""
        self.mock_analysis_results['overall_score'] = 75
        # These are required by _add_header, which might be part of a full build,
        # but _add_site_health_chart itself doesn't directly use them.
        # If testing _add_site_health_chart in isolation, these might not be strictly needed
        # unless _setup_custom_styles or other prep methods are called.
        self.mock_analysis_results['summary']['report_title'] = 'Test Report'
        self.mock_analysis_results['summary']['analysis_date'] = '2023-10-27'


        self.pdf_generator.story = [] # Clear story
        self.pdf_generator._add_site_health_chart()

        drawing_found = None
        for item in self.pdf_generator.story:
            if isinstance(item, Drawing):
                drawing_found = item
                break
        
        self.assertIsNotNone(drawing_found, "Drawing object for chart not found in story.")

        pie_chart_found = None
        score_string_found = None
        title_string_found = None

        for element in drawing_found.getContents():
            if isinstance(element, Pie):
                pie_chart_found = element
            elif isinstance(element, String):
                if "%" in element.text:
                    score_string_found = element
                elif "Site Health" in element.text:
                    title_string_found = element
        
        self.assertIsNotNone(pie_chart_found, "Pie chart not found in Drawing.")
        self.assertEqual(pie_chart_found.data, [75, 25])
        # Check colors based on conceptual PDF_CONFIG
        self.assertEqual(pie_chart_found.slices[0].fillColor, HexColor('#28A745')) # Success
        self.assertEqual(pie_chart_found.slices[1].fillColor, HexColor('#DC3545')) # Error

        self.assertIsNotNone(score_string_found, "Score string not found.")
        self.assertEqual(score_string_found.text, "75%")
        self.assertEqual(score_string_found.fontName, 'Helvetica-Bold') # From conceptual config
        self.assertEqual(score_string_found.fillColor, HexColor('#005A9C')) # Primary color for score

        self.assertIsNotNone(title_string_found, "Site Health title string not found.")
        self.assertEqual(title_string_found.text, "Site Health")
        self.assertEqual(title_string_found.fontName, 'Helvetica') # From conceptual config
        self.assertEqual(title_string_found.fillColor, HexColor('#222222')) # Text primary color

if __name__ == '__main__':
    unittest.main()
