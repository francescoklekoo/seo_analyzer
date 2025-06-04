import matplotlib
matplotlib.use('Agg') # Ensure backend is set, though pdf_generator should also do this
from utils.pdf_generator import PDFGenerator
from datetime import datetime
import os

# Ensure the reports directory exists
if not os.path.exists("reports"):
    os.makedirs("reports")

dummy_analysis_results = {
    'overall_score': 75,
    'summary': {
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_pages_analyzed': 10,
        'total_issues': 5,
        'total_recommendations': 3
    },
    'detailed_issues': {
        'errors': [
            {'type': 'duplicate_meta', 'url': 'https://example.com/page1', 'details': 'Duplicate meta on page 1', 'issue': 'Some issue text for duplicate meta'},
            {'type': 'missing_h1', 'url': 'https://example.com/page2', 'details': 'Missing H1 on page 2', 'issue': 'Some issue text for missing H1'}
        ],
        'warnings': [
            {'type': 'low_text_html_ratio', 'url': 'https://example.com/page3', 'details': 'Low text ratio on page 3', 'issue': 'Some issue text for low ratio'}
        ],
        'notices': [
            {'type': 'images_without_alt', 'url': 'https://example.com/page4', 'image_src': 'img.jpg', 'details': 'Image missing alt text', 'issue': 'Some issue text for missing alt'}
        ],
        'pages_without_title': [{'url': 'https://example.com/no-title', 'issue': 'Page has no title tag'}],
        'duplicate_titles': [{'title': 'Duplicate Title', 'url': 'https://example.com/dup-title', 'duplicate_count': 2}],
        'pages_without_meta': [{'url': 'https://example.com/no-meta', 'issue': 'Page has no meta description'}],
        'duplicate_meta_descriptions': [{'meta': 'Duplicate Meta', 'url': 'https://example.com/dup-meta', 'duplicate_count': 2}],
        'missing_h1_pages': [{'url': 'https://example.com/no-h1', 'issue': 'Page has no H1'}],
        'multiple_h1_pages': [{'url': 'https://example.com/multi-h1', 'issue': 'Page has multiple H1s'}],
        'missing_h2_pages': [{'url': 'https://example.com/no-h2', 'issue': 'Page has no H2s'}],
        'missing_h3_pages': [{'url': 'https://example.com/no-h3', 'issue': 'Page has no H3s'}],
        'images_without_alt': [{'url': 'https://example.com/img-no-alt', 'image_src': 'image1.jpg', 'issue': 'Image missing alt'}],
        'images_with_empty_alt': [{'url': 'https://example.com/img-empty-alt', 'image_src': 'image2.jpg', 'issue': 'Image has empty alt'}],
        'images_without_title_attr': [{'url': 'https://example.com/img-no-title', 'image_src': 'image3.jpg', 'issue': 'Image missing title attr'}],
        'images_with_empty_title_attr': [{'url': 'https://example.com/img-empty-title', 'image_src': 'image4.jpg', 'issue': 'Image has empty title attr'}],
        'broken_images': [{'url': 'https://example.com/broken-img', 'image_src': 'broken.jpg', 'issue': 'Image is broken'}],
        'low_word_count_pages': [{'url': 'https://example.com/low-words', 'word_count': 100, 'issue': 'Low word count'}],
        'large_html_pages': [{'url': 'https://example.com/large-html', 'size_mb': 5, 'issue': 'Large HTML size'}],
        'slow_pages': [{'url': 'https://example.com/slow-page', 'response_time': 5, 'issue': 'Slow page load'}],
        'status_4xx_pages': [{'url': 'https://example.com/404', 'status_code': 404, 'issue': 'Client error'}],
        'status_5xx_pages': [{'url': 'https://example.com/500', 'status_code': 500, 'issue': 'Server error'}],
        'pages_without_canonical': [{'url': 'https://example.com/no-canon', 'issue': 'No canonical tag'}],
        'pages_without_lang': [{'url': 'https://example.com/no-lang', 'issue': 'No lang attribute'}],
        'pages_without_schema': [{'url': 'https://example.com/no-schema', 'issue': 'No schema markup'}],
    },
    'title_analysis': {'score': 60, 'pages_with_title': 8, 'total_pages': 10, 'too_short_titles': [], 'too_long_titles': []},
    'meta_description_analysis': {'score': 70, 'pages_with_meta': 7, 'total_pages': 10, 'too_short_metas': [], 'too_long_metas': []},
    'headings_analysis': {'score': 80, 'total_pages': 10},
    'images_analysis': {'score': 50, 'total_images': 20, 'images_with_alt': 15, 'images_without_alt': 5, 'images_with_empty_alt': 0, 'images_with_title_attr': 10, 'images_without_title_attr': 5, 'images_with_empty_title_attr': 0, 'total_pages': 10},
    'content_analysis': {'score': 65, 'total_pages': 10},
    'links_analysis': {'score': 70, 'total_pages': 10},
    'performance_analysis': {
        'score': 75, 'fast_pages': 5, 'slow_pages': 2,
        'average_response_time': 1.5, 'average_page_size': 1024*500,
        'total_pages': 10
    },
    'technical_analysis': {'score': 85, 'total_pages': 10},
    'ssl_analysis': {'score': 90, 'has_ssl': True, 'ssl_valid': True, 'ssl_expires': '2024-12-31', 'total_pages': 10},
    'recommendations': [
        {'priority': 'Alto', 'category': 'Meta Tags', 'issue': 'Missing meta descriptions', 'recommendation': 'Add meta descriptions to all pages.'},
        {'priority': 'Medio', 'category': 'Performance', 'issue': 'Slow page load', 'recommendation': 'Optimize images and leverage browser caching.'},
    ]
}

default_score_details = {'score': 0, 'total_pages': 0}
list_based_details = [
    'too_short_titles', 'too_long_titles', 'too_short_metas', 'too_long_metas'
]
page_count_details = {
    'pages_with_title': 0, 'pages_with_meta': 0,
}

for analysis_key in ['title_analysis', 'meta_description_analysis', 'headings_analysis',
                     'images_analysis', 'content_analysis', 'links_analysis',
                     'performance_analysis', 'technical_analysis', 'ssl_analysis']:
    if analysis_key not in dummy_analysis_results:
        dummy_analysis_results[analysis_key] = {}

    for k, v in default_score_details.items():
        if k not in dummy_analysis_results[analysis_key]:
            dummy_analysis_results[analysis_key][k] = v

    if analysis_key in ['title_analysis', 'meta_description_analysis']:
        for list_key in list_based_details:
            if list_key not in dummy_analysis_results[analysis_key]:
                dummy_analysis_results[analysis_key][list_key] = []
        for page_count_key, default_val in page_count_details.items():
            if page_count_key not in dummy_analysis_results[analysis_key]:
                 dummy_analysis_results[analysis_key][page_count_key] = default_val

all_detailed_issue_keys = [
    'pages_without_title', 'duplicate_titles', 'pages_without_meta', 'duplicate_meta_descriptions',
    'missing_h1_pages', 'multiple_h1_pages', 'missing_h2_pages', 'missing_h3_pages',
    'images_without_alt', 'images_with_empty_alt', 'images_without_title_attr',
    'images_with_empty_title_attr', 'broken_images', 'low_word_count_pages',
    'large_html_pages', 'slow_pages', 'status_4xx_pages', 'status_5xx_pages',
    'pages_without_canonical', 'pages_without_lang', 'pages_without_schema'
]
if 'detailed_issues' not in dummy_analysis_results:
    dummy_analysis_results['detailed_issues'] = {}
for key in all_detailed_issue_keys:
    if key not in dummy_analysis_results['detailed_issues']:
        dummy_analysis_results['detailed_issues'][key] = []


generator = PDFGenerator(analysis_results=dummy_analysis_results, domain="testdomain.com")
output_filename = "reports/test_report_final.pdf" # Changed output filename

try:
    print(f"Attempting to generate PDF: {output_filename}")
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    if 'Normal' not in generator.styles: # Ensure 'Normal' style exists
        generator.styles.add(styles['Normal'])
    if 'Bullet' not in generator.styles: # Ensure 'Bullet' style exists for lists
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
