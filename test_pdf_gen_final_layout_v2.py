import matplotlib
matplotlib.use('Agg')
from utils.pdf_generator import PDFGenerator
from datetime import datetime
import os

# Ensure the reports directory exists
if not os.path.exists("reports"):
    os.makedirs("reports")

dummy_analysis_results = {
    'overall_score': 76, # Slightly different score for this version
    'summary': {
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_pages_analyzed': 30,
        'total_issues': 18, # Sum of errors, warnings, notices below
        'total_recommendations': 6 # General recommendations count
    },
    'detailed_issues': {
        # For "Aree di Miglioramento" (Executive Summary) & "Tabella Riepilogativa"
        'errors': [
            {'type': 'missing_h1', 'url': 'https://example.com/error/no-h1-v2', 'details': 'H1 tag is completely missing.', 'issue': 'Missing H1 tag'},
            {'type': 'duplicate_title', 'url': 'https://example.com/error/dup-title-v2', 'details': 'Title tag is duplicated elsewhere.', 'issue': 'Duplicate title tag'}
        ],
        'warnings': [
            {'type': 'low_text_html_ratio', 'url': 'https://example.com/warning/low-ratio-v2', 'details': 'Low text to HTML ratio.', 'issue': 'Low text/HTML ratio'},
            {'type': 'images_without_alt', 'url': 'https://example.com/warning/img-no-alt-v2', 'details': 'Image missing alt text.', 'issue': 'Image missing alt text'},
            {'type': 'short_meta_description', 'url': 'https://example.com/warning/short-meta-v2', 'details': 'Meta description too short.', 'issue': 'Short meta description'}
        ],
        'notices': [
            {'type': 'images_with_empty_title_attr', 'url': 'https://example.com/notice/empty-title-v2', 'image_src': 'img_empty_title_v2.jpg', 'details': 'Image has empty title attr.', 'issue': 'Empty image title attribute'},
            {'type': 'no_schema_markup', 'url': 'https://example.com/notice/no-schema-v2', 'details': 'No schema.org markup.', 'issue': 'Missing schema.org markup'},
            {'type': 'hypothetical_notice_type', 'url': 'https://example.com/notice/hypothetical-v2', 'details': 'A new made-up notice for testing fallback.', 'issue': 'This is a test notice for fallback.'}
        ],

        # For "Analisi Dettagliata" section's individual tables
        'pages_without_title': [{'url': 'https://example.com/detail/no-title-v2', 'issue': 'Page has no title tag'}],
        'duplicate_titles': [{'title': 'Duplicated Main Title v2', 'url': 'https://example.com/detail/dup-title-1-v2', 'duplicate_count': 2}],
        'pages_without_meta': [{'url': 'https://example.com/detail/no-meta-v2', 'issue': 'Page is missing meta description'}],
        'duplicate_meta_descriptions': [{'meta': 'Duplicated Meta Desc v2', 'url': 'https://example.com/detail/dup-meta-1-v2', 'duplicate_count': 2}],
        'missing_h1_pages': [{'url': 'https://example.com/detail/no-h1-again-v2', 'issue': 'H1 tag is missing here'}],
        'multiple_h1_pages': [{'url': 'https://example.com/detail/multi-h1-v2', 'issue': 'Page has multiple H1 tags here'}],
        'missing_h2_pages': [{'url': 'https://example.com/detail/no-h2-v2', 'issue': 'No H2 tags found here'}],
        'missing_h3_pages': [{'url': 'https://example.com/detail/no-h3-v2', 'issue': 'No H3 tags found here'}],
        'images_with_empty_alt': [{'url': 'https://example.com/detail/img-empty-alt-v2', 'image_src': 'empty_alt_v2.jpg', 'issue': 'Image has empty alt text here'}],
        'images_without_title_attr': [{'url': 'https://example.com/detail/img-no-title-attr-v2', 'image_src': 'no_title_attr_v2.jpg', 'issue': 'Image missing title attribute here'}],
        'broken_images': [{'url': 'https://example.com/detail/broken-img-v2', 'image_src': 'broken_v2.jpg', 'issue': 'Link to image is broken here'}],
        'low_word_count_pages': [{'url': 'https://example.com/detail/low-words-v2', 'word_count': 120, 'issue': 'Content is too short here'}],
        'large_html_pages': [{'url': 'https://example.com/detail/large-html-v2', 'size_mb': 4.0, 'issue': 'HTML document size is large here'}],
        'slow_pages': [{'url': 'https://example.com/detail/slow-loading-v2', 'response_time': 4.5, 'issue': 'Page response time is slow here'}],
        'status_4xx_pages': [{'url': 'https://example.com/detail/404-error-v2', 'status_code': 404, 'issue': 'Client error: Not Found here'}],
        'status_5xx_pages': [{'url': 'https://example.com/detail/500-error-v2', 'status_code': 500, 'issue': 'Server error: Internal Server Error here'}],
        'pages_without_canonical': [{'url': 'https://example.com/detail/no-canonical-v2', 'issue': 'Canonical tag missing here'}],
        'pages_without_lang': [{'url': 'https://example.com/detail/no-lang-v2', 'issue': 'HTML lang attribute missing here'}],
    },
    'title_analysis': {'score': 60, 'pages_with_title': 28, 'total_pages': 30, 'too_short_titles': [{'url': 'https://example.com/short-title-v2', 'title':'New', 'length':3}], 'too_long_titles': []},
    'meta_description_analysis': {'score': 70, 'pages_with_meta': 22, 'total_pages': 30, 'too_short_metas': [{'url': 'https://example.com/short-meta-v2', 'meta':'New Desc', 'length':8}], 'too_long_metas': []},
    'headings_analysis': {'score': 72, 'total_pages': 30},
    'images_analysis': {'score': 62, 'total_images': 55, 'images_with_alt': 42, 'images_without_alt': 6, 'images_with_empty_alt': 3, 'images_with_title_attr': 32, 'images_without_title_attr': 12, 'images_with_empty_title_attr': 4, 'total_pages': 30},
    'content_analysis': {'score': 77, 'total_pages': 30},
    'links_analysis': {'score': 81, 'total_pages': 30},
    'performance_analysis': {
        'score': 65, 'fast_pages': 18, 'slow_pages': 6,
        'average_response_time': 2.3, 'average_page_size': 1300*1024,
        'total_pages': 30
    },
    'technical_analysis': {'score': 85, 'total_pages': 30},
    'ssl_analysis': {'score': 92, 'has_ssl': True, 'ssl_valid': True, 'ssl_expires': '2025-02-15', 'total_pages': 30},
    'recommendations': [
        {'priority': 'Alto', 'category': 'Performance', 'issue': 'Ottimizzare immagini per ridurre peso.', 'recommendation': 'Utilizza formati moderni come WebP e comprimi le immagini.'},
        {'priority': 'Medio', 'category': 'Accessibilità', 'issue': 'Migliorare contrasto colori.', 'recommendation': 'Verifica il contrasto tra testo e sfondo per leggibilità.'},
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
    if key not in dummy_analysis_results['detailed_issues']: # Ensure all keys exist
        dummy_analysis_results['detailed_issues'][key] = []


generator = PDFGenerator(analysis_results=dummy_analysis_results, domain="final_layout_test.com")
output_filename = "reports/test_report_final_layout_v2.pdf"

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
