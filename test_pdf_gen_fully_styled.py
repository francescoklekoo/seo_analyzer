import matplotlib
matplotlib.use('Agg')
from utils.pdf_generator import PDFGenerator
from datetime import datetime
import os

# Ensure the reports directory exists
if not os.path.exists("reports"):
    os.makedirs("reports")

dummy_analysis_results = {
    'overall_score': 72,
    'summary': {
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_pages_analyzed': 25,
        'total_issues': 15,
        'total_recommendations': 5
    },
    'detailed_issues': {
        'errors': [
            {'type': 'missing_h1', 'url': 'https://example.com/error/no-h1', 'details': 'H1 tag is completely missing from this page.', 'issue': 'Missing H1 tag'},
            {'type': 'duplicate_title', 'url': 'https://example.com/error/dup-title', 'details': 'Title tag is duplicated on another page.', 'issue': 'Duplicate title tag'}
        ],
        'warnings': [
            {'type': 'low_text_html_ratio', 'url': 'https://example.com/warning/low-ratio', 'details': 'Low text to HTML ratio detected.', 'issue': 'Low text/HTML ratio'},
            {'type': 'images_without_alt', 'url': 'https://example.com/warning/img-no-alt', 'details': 'Image found without alt text.', 'issue': 'Image missing alt text'},
            {'type': 'short_meta_description', 'url': 'https://example.com/warning/short-meta', 'details': 'Meta description is too short.', 'issue': 'Short meta description'}
        ],
        'notices': [
            {'type': 'images_with_empty_title_attr', 'url': 'https://example.com/notice/empty-title', 'image_src': 'img_empty_title.jpg', 'details': 'Image has an empty title attribute.', 'issue': 'Empty image title attribute'},
            {'type': 'no_schema_markup', 'url': 'https://example.com/notice/no-schema', 'details': 'No schema.org markup found.', 'issue': 'Missing schema.org markup'}
        ],
        'pages_without_title': [{'url': 'https://example.com/detail/no-title', 'issue': 'Page has no title tag'}],
        'duplicate_titles': [{'title': 'Duplicated Main Title', 'url': 'https://example.com/detail/dup-title-1', 'duplicate_count': 2}, {'title': 'Duplicated Main Title', 'url': 'https://example.com/detail/dup-title-2', 'duplicate_count': 2}],
        'pages_without_meta': [{'url': 'https://example.com/detail/no-meta', 'issue': 'Page is missing meta description'}],
        'duplicate_meta_descriptions': [{'meta': 'Duplicated Meta Description', 'url': 'https://example.com/detail/dup-meta-1', 'duplicate_count': 2}],
        'missing_h1_pages': [{'url': 'https://example.com/detail/no-h1-again', 'issue': 'H1 tag is missing'}],
        'multiple_h1_pages': [{'url': 'https://example.com/detail/multi-h1', 'issue': 'Page has multiple H1 tags'}],
        'missing_h2_pages': [{'url': 'https://example.com/detail/no-h2', 'issue': 'No H2 tags found'}],
        'missing_h3_pages': [{'url': 'https://example.com/detail/no-h3', 'issue': 'No H3 tags found'}],
        'images_with_empty_alt': [{'url': 'https://example.com/detail/img-empty-alt', 'image_src': 'empty_alt.jpg', 'issue': 'Image has empty alt text'}],
        'images_without_title_attr': [{'url': 'https://example.com/detail/img-no-title-attr', 'image_src': 'no_title_attr.jpg', 'issue': 'Image missing title attribute'}],
        'broken_images': [{'url': 'https://example.com/detail/broken-img', 'image_src': 'broken.jpg', 'issue': 'Link to image is broken'}],
        'low_word_count_pages': [{'url': 'https://example.com/detail/low-words', 'word_count': 150, 'issue': 'Content is too short'}],
        'large_html_pages': [{'url': 'https://example.com/detail/large-html', 'size_mb': 3.5, 'issue': 'HTML document size is large'}],
        'slow_pages': [{'url': 'https://example.com/detail/slow-loading', 'response_time': 4.1, 'issue': 'Page response time is slow'}],
        'status_4xx_pages': [{'url': 'https://example.com/detail/404-error', 'status_code': 404, 'issue': 'Client error: Not Found'}],
        'status_5xx_pages': [{'url': 'https://example.com/detail/500-error', 'status_code': 500, 'issue': 'Server error: Internal Server Error'}],
        'pages_without_canonical': [{'url': 'https://example.com/detail/no-canonical', 'issue': 'Canonical tag missing'}],
        'pages_without_lang': [{'url': 'https://example.com/detail/no-lang', 'issue': 'HTML lang attribute missing'}],
    },
    'title_analysis': {'score': 55, 'pages_with_title': 23, 'total_pages': 25, 'too_short_titles': [{'url': 'https://example.com/short-title', 'title':'Hi', 'length':2}], 'too_long_titles': []},
    'meta_description_analysis': {'score': 65, 'pages_with_meta': 20, 'total_pages': 25, 'too_short_metas': [{'url': 'https://example.com/short-meta', 'meta':'Desc', 'length':4}], 'too_long_metas': []},
    'headings_analysis': {'score': 70, 'total_pages': 25},
    'images_analysis': {'score': 60, 'total_images': 50, 'images_with_alt': 40, 'images_without_alt': 5, 'images_with_empty_alt': 2, 'images_with_title_attr': 30, 'images_without_title_attr': 10, 'images_with_empty_title_attr': 3, 'total_pages': 25},
    'content_analysis': {'score': 75, 'total_pages': 25},
    'links_analysis': {'score': 80, 'total_pages': 25},
    'performance_analysis': {
        'score': 68, 'fast_pages': 15, 'slow_pages': 5,
        'average_response_time': 2.1, 'average_page_size': 1200*1024,
        'total_pages': 25
    },
    'technical_analysis': {'score': 82, 'total_pages': 25},
    'ssl_analysis': {'score': 95, 'has_ssl': True, 'ssl_valid': True, 'ssl_expires': '2025-01-10', 'total_pages': 25},
    'recommendations': [
        {'priority': 'Alto', 'category': 'Contenuto', 'issue': 'Migliorare la qualità e profondità dei contenuti.', 'recommendation': 'Espandi i contenuti chiave, aggiungi dettagli e multimedia.'},
        {'priority': 'Medio', 'category': 'Tecnico', 'issue': 'Verificare periodicamente robots.txt.', 'recommendation': 'Assicurati che robots.txt non blocchi risorse importanti.'},
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


generator = PDFGenerator(analysis_results=dummy_analysis_results, domain="fullystyled.com")
output_filename = "reports/test_report_fully_styled.pdf" # Using a new name for this comprehensive test

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
