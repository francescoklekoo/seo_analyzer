import matplotlib
matplotlib.use('Agg') # Ensure backend is set
from utils.pdf_generator import PDFGenerator
from datetime import datetime
import os

# Ensure the reports directory exists
if not os.path.exists("reports"):
    os.makedirs("reports")

dummy_analysis_results = {
    'overall_score': 78,
    'summary': {
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_pages_analyzed': 12,
        'total_issues': 6,
        'total_recommendations': 4
    },
    'detailed_issues': {
        'errors': [
            {'type': 'duplicate_meta', 'url': 'https://example.com/errorpage1', 'details': 'Error: Duplicate meta', 'issue': 'Duplicate meta content found'},
        ],
        'warnings': [
            {'type': 'low_text_html_ratio', 'url': 'https://example.com/warning_low_ratio', 'details': 'Low text ratio here', 'issue': 'Text to HTML ratio is below threshold'},
            {'type': 'slow_page_load', 'url': 'https://example.com/warning_slow_page', 'details': 'Page loads slowly', 'issue': 'Response time exceeds 3 seconds'},
            {'type': 'hypothetical_warning_type', 'url': 'https://example.com/warning_hypothetical', 'details': 'A made-up warning', 'issue': 'This is a test warning.'}
        ],
        'notices': [
            {'type': 'images_without_alt', 'url': 'https://example.com/notice_img_alt', 'image_src': 'no_alt.jpg', 'details': 'Image missing alt text', 'issue': 'Missing alt attribute for an image'},
            {'type': 'images_with_empty_title_attr', 'url': 'https://example.com/notice_empty_title', 'image_src': 'empty_title.jpg', 'details': 'Image has empty title', 'issue': 'Image title attribute is empty'},
            {'type': 'another_hypothetical_notice', 'url': 'https://example.com/notice_hypothetical', 'details': 'A made-up notice', 'issue': 'This is a test notice.'}
        ],
        'pages_without_title': [], 'duplicate_titles': [], 'pages_without_meta': [],
        'duplicate_meta_descriptions': [], 'missing_h1_pages': [], 'multiple_h1_pages': [],
        'missing_h2_pages': [], 'missing_h3_pages': [],
        'images_with_empty_alt': [], 'images_without_title_attr': [],
        'broken_images': [], 'low_word_count_pages': [], 'large_html_pages': [],
        'status_4xx_pages': [], 'status_5xx_pages': [], 'pages_without_canonical': [],
        'pages_without_lang': [], 'pages_without_schema': [],
    },
    'title_analysis': {'score': 60, 'pages_with_title': 8, 'total_pages': 12, 'too_short_titles': [], 'too_long_titles': []},
    'meta_description_analysis': {'score': 70, 'pages_with_meta': 7, 'total_pages': 12, 'too_short_metas': [], 'too_long_metas': []},
    'headings_analysis': {'score': 80, 'total_pages': 12},
    'images_analysis': {'score': 50, 'total_images': 20, 'images_with_alt': 15, 'images_without_alt': 1, 'images_with_empty_alt': 1, 'images_with_title_attr': 10, 'images_without_title_attr':1, 'images_with_empty_title_attr':1, 'total_pages': 12},
    'content_analysis': {'score': 65, 'total_pages': 12},
    'links_analysis': {'score': 70, 'total_pages': 12},
    'performance_analysis': {
        'score': 75, 'fast_pages': 5, 'slow_pages': 1,
        'average_response_time': 1.5, 'average_page_size': 1024*500,
        'total_pages': 12
    },
    'technical_analysis': {'score': 85, 'total_pages': 12},
    'ssl_analysis': {'score': 90, 'has_ssl': True, 'ssl_valid': True, 'ssl_expires': '2024-12-31', 'total_pages': 12},
    'recommendations': [
        {'priority': 'Alto', 'category': 'Overall', 'issue': 'General site health', 'recommendation': 'Review all identified issues.'},
    ]
}

all_detailed_issue_keys_expected = [
    'pages_without_title', 'duplicate_titles', 'pages_without_meta', 'duplicate_meta_descriptions',
    'missing_h1_pages', 'multiple_h1_pages', 'missing_h2_pages', 'missing_h3_pages',
    'images_without_alt', 'images_with_empty_alt', 'images_without_title_attr',
    'images_with_empty_title_attr', 'broken_images', 'low_word_count_pages',
    'large_html_pages', 'slow_pages', 'status_4xx_pages', 'status_5xx_pages',
    'pages_without_canonical', 'pages_without_lang', 'pages_without_schema'
]
for key in all_detailed_issue_keys_expected:
    if key not in dummy_analysis_results['detailed_issues']:
        dummy_analysis_results['detailed_issues'][key] = []

generator = PDFGenerator(analysis_results=dummy_analysis_results, domain="testdomain_recs.com")
output_filename = "reports/test_report_with_recs.pdf"

try:
    print(f"Attempting to generate PDF: {output_filename}")
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    if 'Normal' not in generator.styles:
        generator.styles.add(styles['Normal'])
    if 'Bullet' not in generator.styles:
        generator.styles.add(styles['Bullet'])

    success = generator.generate_pdf(output_filename)
    if success:
        print(f"PDF generated successfully: {output_filename}")
        if os.path.exists(output_filename):
            print(f"File {output_filename} confirmed to exist. Size: {os.path.getsize(output_filename)} bytes.")
        else:
            print(f"Error: PDF generation reported success, but file {output_filename} does not exist.")
    else:
        print(f"PDF generation failed for {output_filename}")

except Exception as e:
    print(f"An exception occurred during PDF generation: {e}")
    import traceback
    traceback.print_exc()
