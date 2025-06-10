import json
from utils.analyzer import SEOAnalyzer
from config import (
    CATEGORY_OCM, CATEGORY_SEO_AUDIT, AUDIT_CHECKS_CONFIG, PDF_ISSUE_DESCRIPTIONS,
    CORE_WEB_VITALS_THRESHOLDS, SERVER_RESPONSE_TIME_ERROR, SEO_CONFIG,
    NEW_SCORING_CLASSIFICATION, TOUCH_ELEMENT_MIN_SIZE_PX
)

# 1. Define Sample pages_data
sample_pages_data = [
    {
        'url': 'http://example.com/', # Changed to end with / for LCP test
        'title': "Welcome", # Too short for SEO_CONFIG['title_min_length'] = 30
        'meta_description': "", # Missing
        'status_code': 200,
        'response_time': 0.7, # seconds -> 700ms, > SERVER_RESPONSE_TIME_ERROR (600ms)
        'performance_metrics': {'lcp': 4.5, 'inp': 550, 'cls': 0.30}, # LCP, INP, CLS errors
        'has_viewport_tag': False, # OCM Error
        'headings': {'h1': ['Main Title', 'Another Main Title']}, # Multiple H1s
        'content': {'word_count': 100}, # Thin content (SITE SEO ERROR if < 150, OCM WARNING if < 300)
        'images': [{'src': 'img1.jpg', 'alt': None}], # Missing alt
        'schema_markup': [], # To trigger 'ocm_structured_data_implemented_notice' (if it's an error/warning for absence)
        # For ocm_broken_internal_links_warning
        'broken_internal_links': [{'target_url': 'http://example.com/brokenpage1', 'anchor_text': 'Broken Link 1'}],
        # For ocm_internal_linking_insufficient_warning (assuming 'links' is used, or 'internal_links_list')
        'links': [{'url': 'http://example.com/pagex', 'is_external': False, 'text': 'Link X'}], # Only 1 internal link
        'has_mixed_content': True, # For ocm_mixed_content_warning
    },
    {
        'url': 'http://example.com/page2',
        'title': "Example Page 2 Title Which Is Definitely Long Enough And Optimized",
        'meta_description': "A good meta description for page 2 that is of optimal length and describes content well.",
        'status_code': 200,
        'response_time': 0.1, # 100ms
        'performance_metrics': {'lcp': 1.0, 'inp': 100, 'cls': 0.05}, # Good CWV
        'has_viewport_tag': True,
        'headings': {'h1': ['Page 2 Title'], 'h3': ['Sub-subheading without H2']}, # Inconsistent header
        'content': {'word_count': 400}, # Good word count
        'images': [{'src': 'img2.jpg', 'alt': 'Alt text for image 2'}],
        'schema_markup': [{'type': 'Article'}], # Has some schema
        'redirect_chain_hops': 4, # For ocm_redirect_chains_warning
    },
    {
        'url': 'http://example.com/nonexistent',
        'title': "Not Found",
        'meta_description': "This page was not found.", # Will be checked for length if considered for meta checks
        'status_code': 404, # Triggers 404 related checks
        'response_time': 0.05,
        'performance_metrics': {'lcp': 0.5, 'inp': 50, 'cls': 0.01},
        'has_viewport_tag': True,
        'headings': {'h1': ['Not Found Page Title']},
        'content': {'word_count': 10}, # Thin content
        'images': [],
        'schema_markup': [],
    },
    # Page to test title duplication
    {
        'url': 'http://example.com/another-welcome',
        'title': "Welcome", # Duplicate of homepage title
        'meta_description': "Another page also welcoming users.",
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

# 2. Instantiate and Run SEOAnalyzer
# Ensure all necessary config variables are available if not directly imported by analyzer.py
# (analyzer.py imports most of what it needs from config)

analyzer = SEOAnalyzer(pages_data=sample_pages_data, domain="example.com")
analysis_results = analyzer.analyze_all()

# 3. Prepare Output for Verification
categorized_issues = analysis_results.get('categorized_issues')
site_health_info = analysis_results.get('site_health')
overall_score = analysis_results.get('overall_score')

# Save to files
output_dir = "/tmp"
categorized_issues_file = f"{output_dir}/categorized_issues.json"
site_health_info_file = f"{output_dir}/site_health_info.json"
overall_score_file = f"{output_dir}/overall_score.txt"

# Create /tmp if it doesn't exist (useful in some sandboxed environments)
import os
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

# For direct inspection if possible:
# print("\nCategorized Issues:")
# print(json.dumps(categorized_issues, indent=4, ensure_ascii=False))
# print("\nSite Health Info:")
# print(json.dumps(site_health_info, indent=4, ensure_ascii=False))
# print(f"\nOverall Score: {overall_score}")

print("\n--- Example Check Keys Found ---")
if categorized_issues:
    examples_found = 0
    for category, severities in categorized_issues.items():
        if examples_found >= 5: break
        for severity, issues in severities.items():
            if examples_found >= 5: break
            if issues:
                print(f"Found in {category} - {severity}:")
                for issue in issues[:2]: # Print first 2 from this list
                    if examples_found < 5:
                        print(f"  - {issue['key']}")
                        examples_found += 1
                    else:
                        break
else:
    print("No categorized issues found.")

print(f"\nCalculated Health Percentage: {site_health_info.get('health_percentage') if site_health_info else 'N/A'}")
