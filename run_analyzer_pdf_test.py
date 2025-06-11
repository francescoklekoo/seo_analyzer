import json
from utils.analyzer import SEOAnalyzer
from utils.pdf_generator import PDFGenerator
from config import CATEGORY_OCM, CATEGORY_SEO_AUDIT, AUDIT_CHECKS_CONFIG, PDF_ISSUE_DESCRIPTIONS, CORE_WEB_VITALS_THRESHOLDS, SERVER_RESPONSE_TIME_ERROR, TOUCH_ELEMENT_MIN_SIZE_PX

# Sample data for testing
sample_pages_data = [
    {
        "url": "https://example.com/page1",
        "title": "Page 1 Title",
        "meta_description": "Description for page 1.",
        "headings": {"h1": ["H1 Heading"], "h2": ["H2 Subheading"]},
        "content_length": 1500,
        "lcp": 2.8, "inp": 150, "cls": 0.05, # Good CWV
        "server_response_time": 300,
        "status_code": 200,
        "is_https": True,
        "robots_txt_blocks": [],
        "sitemap_referenced_in_robots_txt": True,
        "has_structured_data": True,
        "structured_data_errors": [], # No errors
        "redirect_chain": None,
        "alt_tags_missing_percentage": 10,
        "internal_links": 5, "external_links": 2,
        "broken_links_internal": 0, "broken_links_external": 0,
        "text_html_ratio": 30,
        "viewport_meta_tag_present": True,
        "uses_cdn": True,
        "compression_enabled": True,
        "image_formats_optimized": True,
        "defer_js_used": True,
        "touch_elements_adequate_size": True,
        "font_size_legible": True,
        "flash_used": False,
        "iframe_count": 0,
        "favicon_present": True,
        "is_mobile_friendly": True, # Placeholder
        "has_breadcrumbs": True, # Placeholder
        "social_sharing_buttons_present": True, # Placeholder
        "open_graph_tags_present": True, # Placeholder
        "twitter_cards_present": True, # Placeholder
        "canonical_url": "https://example.com/page1", # Placeholder
        "hreflang_tags": [], # Placeholder
        "word_count": 350, # Placeholder for thin content check
        "outgoing_links_nofollow_percentage": 5, # Placeholder
        "language": "it", # Placeholder
        "has_contact_info": True, # Placeholder
        "has_privacy_policy": True, # Placeholder
        "has_terms_of_service": True, # Placeholder
        "uses_analytics": True, # Placeholder
        "has_search_functionality": True, # Placeholder
        "custom_404_page_present": True, # Placeholder
        "url_structure_user_friendly": True, # Placeholder
        "core_web_vitals_data": {"LCP": 2.8, "INP": 150, "CLS": 0.05},
        "resource_load_times": {"main.js": 500, "style.css": 300, "image.jpg": 1200}, # in ms
        "third_party_scripts": [{"url": "https://example-tracker.com/track.js", "size_kb": 50, "load_time_ms": 300}],
        "js_execution_time": 200, # ms
        "dom_size": 1000, # number of elements
        "critical_css_used": True,
        "font_display_swap_used": True,
        "uses_http2_or_http3": True,
        "page_speed_insights_data": {"mobile": {"performance": 80}, "desktop": {"performance": 90}}, # Placeholder
        "backlinks_data": {"referring_domains": 10, "total_backlinks": 50, "domain_authority": 20}, # Placeholder
        "keyword_data": {"main_keyword": "example", "density": 2.5, "ranking": 5}, # Placeholder
        "e_e_a_t_signals": {"has_author_bio": True, "has_clear_contact_info": True, "has_about_us": True}, # Placeholder
        "ymyl_content_type": "None", # Placeholder: "None", "Financial", "Health", "News"
        "duplicate_content_percentage": 5, # Placeholder
        "text_readability_score": 65, # Placeholder (e.g., Flesch Reading Ease)
        "structured_data_types_present": ["Article", "BreadcrumbList"], # Placeholder
        "internal_link_distribution_ok": True, # Placeholder
        "external_link_quality_ok": True, # Placeholder
        "website_accessibility_score": 85, # Placeholder (e.g., WAVE, Lighthouse accessibility)
        "bounce_rate": 40, # Placeholder
        "avg_session_duration": 180, # Placeholder
        "conversion_rate": 3.5, # Placeholder
        "crawl_depth": 1, # Placeholder
        "url_length": 25, # Placeholder
        "has_xml_sitemap": True, # Placeholder (site-wide, but can be in page data for initial check)
        "is_indexed_google": True, # Placeholder
        "security_headers_present": ["Content-Security-Policy", "X-Content-Type-Options"], # Placeholder
        "mobile_usability_issues": [], # Placeholder
        "hreflang_errors": [], # Placeholder
        "mixed_content_issues": [], # Placeholder
        "browser_caching_policy_ok": True, # Placeholder
        "text_compression_enabled": True, # Placeholder (overlaps with compression_enabled)
        "content_freshness_score": 0.8, # Placeholder (0-1, higher is fresher)
        "link_rot_percentage": 2, # Placeholder
        "website_load_balancing_active": False, # Placeholder
        "firewall_protection_active": True, # Placeholder
        "ssl_certificate_valid_until": "2024-12-31", # Placeholder
        "dns_prefetch_preconnect_used": True, # Placeholder
        "lazy_loading_images_used": True, # Placeholder
        "js_minification_percentage": 90, # Placeholder
        "css_minification_percentage": 90, # Placeholder
        "html_minification_percentage": 80, # Placeholder
        " AMP_used": False, # Placeholder
        "progressive_web_app_features": [], # Placeholder
        "local_seo_signals_present": {"gmb_claimed": True, "local_citations_count": 20}, # Placeholder
        "site_architecture_quality_score": 7, # Placeholder (1-10)
        "user_experience_signals_score": 75, # Placeholder (0-100)
        "content_accuracy_verified": False, # Placeholder
        "click_through_rate_organic": 10, # Placeholder (percentage)
        "number_of_indexed_pages": 100, # Placeholder (site-wide)
        "server_location": "Italy", # Placeholder
        "hosting_provider_known_issues": False, # Placeholder
    },
    {
        "url": "https://example.com/page2-slow-lcp",
        "title": "Page 2 Slow LCP",
        "meta_description": "", # Missing meta description
        "headings": {"h1": ["Another H1"], "h2": []},
        "content_length": 500, # Potentially thin
        "lcp": 4.5, "inp": 600, "cls": 0.3, # Bad CWV
        "server_response_time": 700, # Slow server response
        "status_code": 200,
        "is_https": True,
        "robots_txt_blocks": [],
        "sitemap_referenced_in_robots_txt": True,
        "has_structured_data": False, # No structured data
        "structured_data_errors": [],
        "redirect_chain": None,
        "alt_tags_missing_percentage": 60, # High missing alt tags
        "internal_links": 2, "external_links": 1,
        "broken_links_internal": 0, "broken_links_external": 0,
        "text_html_ratio": 15, # Low text to HTML ratio
        "viewport_meta_tag_present": True,
        "uses_cdn": False, # Not using CDN
        "compression_enabled": False, # Compression not enabled
        "image_formats_optimized": False, # Images not optimized
        "defer_js_used": False, # JS not deferred
        "touch_elements_adequate_size": False, # Small touch elements
        "font_size_legible": True,
        "flash_used": False,
        "iframe_count": 0,
        "favicon_present": False, # Missing Favicon
        "is_mobile_friendly": False,
        "has_breadcrumbs": False,
        "social_sharing_buttons_present": False,
        "open_graph_tags_present": False,
        "twitter_cards_present": False,
        "canonical_url": "https://example.com/page2-slow-lcp",
        "hreflang_tags": [],
        "word_count": 100, # Thin content
        "outgoing_links_nofollow_percentage": 0,
        "language": "en",
        "has_contact_info": False,
        "has_privacy_policy": False,
        "has_terms_of_service": False,
        "uses_analytics": False,
        "has_search_functionality": False,
        "custom_404_page_present": False,
        "url_structure_user_friendly": False,
        "core_web_vitals_data": {"LCP": 4.5, "INP": 600, "CLS": 0.3},
        "resource_load_times": {"main.js": 1500, "style.css": 1300, "image.jpg": 2200},
        "third_party_scripts": [{"url": "https://another-tracker.com/track.js", "size_kb": 150, "load_time_ms": 1000}],
        "js_execution_time": 800,
        "dom_size": 2500,
        "critical_css_used": False,
        "font_display_swap_used": False,
        "uses_http2_or_http3": False,
        "page_speed_insights_data": {"mobile": {"performance": 40}, "desktop": {"performance": 50}},
        "backlinks_data": {"referring_domains": 2, "total_backlinks": 5, "domain_authority": 5},
        "keyword_data": {"main_keyword": "bad page", "density": 1.0, "ranking": 55},
        "e_e_a_t_signals": {"has_author_bio": False, "has_clear_contact_info": False, "has_about_us": False},
        "ymyl_content_type": "None",
        "duplicate_content_percentage": 25,
        "text_readability_score": 40,
        "structured_data_types_present": [],
        "internal_link_distribution_ok": False,
        "external_link_quality_ok": False,
        "website_accessibility_score": 50,
        "bounce_rate": 70,
        "avg_session_duration": 60,
        "conversion_rate": 0.5,
        "crawl_depth": 3,
        "url_length": 50,
        "has_xml_sitemap": True, # Assume site-wide check
        "is_indexed_google": False,
        "security_headers_present": [],
        "mobile_usability_issues": ["Content wider than screen", "Clickable elements too close together"],
        "hreflang_errors": ["Missing return tags"],
        "mixed_content_issues": ["http://example.com/image.jpg"],
        "browser_caching_policy_ok": False,
        "text_compression_enabled": False,
        "content_freshness_score": 0.2,
        "link_rot_percentage": 15,
        "website_load_balancing_active": False,
        "firewall_protection_active": False,
        "ssl_certificate_valid_until": "2023-01-01", # Expired
        "dns_prefetch_preconnect_used": False,
        "lazy_loading_images_used": False,
        "js_minification_percentage": 30,
        "css_minification_percentage": 20,
        "html_minification_percentage": 40,
        "AMP_used": False,
        "progressive_web_app_features": [],
        "local_seo_signals_present": {"gmb_claimed": False, "local_citations_count": 5},
        "site_architecture_quality_score": 3,
        "user_experience_signals_score": 30,
        "content_accuracy_verified": False,
        "click_through_rate_organic": 2,
        "number_of_indexed_pages": 100, # Site-wide
        "server_location": "USA",
        "hosting_provider_known_issues": True,
    }
]

# Site-wide mock data (can be refined or moved into analyzer for more complex scenarios)
site_wide_data = {
    "domain": "example.com",
    "uses_https_across_site": True, # Assume all pages checked confirm this, or a site-wide check
    "robots_txt_content": "User-agent: *\nDisallow: /admin\nSitemap: https://example.com/sitemap.xml",
    "sitemap_urls": ["https://example.com/page1", "https://example.com/page2-slow-lcp", "https://example.com/other-page"],
    "is_global_site": True, # For CDN check
    "has_blog": True,
    "e_e_a_t_signals_overall": {"about_us_page_exists": True, "contact_page_detailed": True, "expert_authors": False},
    "ymyl_site_overall_theme": "Technology Blog", # Example theme
    "uses_cdn_globally": False, # Mock this for testing ocm_no_cdn_global_error
    "robots_txt_critical_blocks": [], # No critical blocks for ocm_critical_robots_block_error
    "redirect_chains_found": {}, # No redirect chains for ocm_redirect_chains_warning
    "sitemap_errors_found": False, # For ocm_sitemap_errors_warning
    "broken_internal_links_site_wide_percentage": 5, # For ocm_broken_internal_links_warning
    "duplicate_content_overall_percentage": 15, # For seo_extensive_duplicate_content_error
    "keyword_cannibalization_issues_found": [], # For seo_keyword_cannibalization_warning
    "multiple_h1_on_pages_percentage": 0, # For seo_multiple_h1_tags_warning (assuming page-specific check handles this better)
    "low_word_count_pages_percentage": 10, # For seo_thin_content_overall_warning
    "orphan_pages_found": [], # For seo_orphan_pages_warning
    "mobile_friendliness_score_overall": 70, # For seo_poor_mobile_friendliness_overall_warning
    "site_speed_overall_desktop": 60, # For seo_slow_site_speed_desktop_warning
    "site_speed_overall_mobile": 50, # For seo_slow_site_speed_mobile_warning
    "backlink_profile_health_score": 40, # For seo_weak_backlink_profile_error
    "structured_data_site_wide_coverage_percentage": 60, # For ocm_structured_data_coverage_low_notice
    "website_accessibility_overall_score": 70, # For seo_accessibility_issues_notice
    "social_media_presence_active": True, # For seo_active_social_media_presence_notice
    "privacy_policy_accessible": True, # For seo_privacy_policy_notice
    "terms_conditions_accessible": True, # For seo_terms_conditions_link_notice
    "blog_content_freshness_avg_days": 90, # For seo_blog_content_stale_notice
    "secure_cookies_used": True, # For ocm_cookies_not_secure_notice
    "http_strict_transport_security_hsts_implemented": False, # For ocm_hsts_not_implemented_notice
    "xml_sitemap_submitted_google": True, # For ocm_xml_sitemap_not_submitted_notice
    "server_signature_exposed": True, # For ocm_server_signature_exposed_notice
    "unnecessary_headers_present": ["X-Powered-By"], # For ocm_unnecessary_headers_notice
    "content_delivery_network_used_effectively": False, # For ocm_cdn_not_effective_notice (different from global use)
    "javascript_error_rate_high": False, # For ocm_high_javascript_error_rate_notice
    "customer_reviews_present_and_positive": True, # For seo_positive_customer_reviews_notice
    "faqs_present_and_helpful": True, # For seo_helpful_faqs_notice
    "case_studies_present": False, # For seo_case_studies_missing_notice
    "testimonials_present": True, # For seo_testimonials_present_notice
    "portfolio_showcased": False, # For seo_portfolio_missing_notice
    "team_page_present_and_detailed": False, # For seo_team_page_inadequate_notice
    "awards_certifications_showcased": True, # For seo_awards_certifications_notice
    "press_mentions_showcased": False, # For seo_press_mentions_missing_notice
    "user_generated_content_strategy_in_place": False, # For seo_user_generated_content_notice
    "website_search_functionality_effective": True, # For seo_effective_site_search_notice
    "conversion_rate_optimization_elements_present": True, # For seo_cro_elements_notice
    "link_to_google_maps_if_local": True, # For seo_gmb_link_prominent_notice
    " NAP_consistency_across_platforms_score": 60, # For seo_nap_consistency_notice (0-100)
    "local_citations_quality_score": 50, # For seo_local_citations_quality_notice (0-100)
    "gmb_profile_completeness_score": 70, # For seo_gmb_completeness_notice (0-100)
    "online_reputation_sentiment_score": 0.6, # For seo_online_reputation_sentiment_notice (e.g., -1 to 1, or 0-1)
    "competitor_benchmarking_data_available": True, # For seo_competitor_gap_analysis_notice
}


def main():
    print("Starting SEO Analysis and PDF Generation Test...")

    # --- Initialize and run SEOAnalyzer ---
    print("\nInitializing SEOAnalyzer...")
    # Pass both page-specific and site-wide data to the analyzer
    analyzer = SEOAnalyzer(pages_data=sample_pages_data,
                           domain=site_wide_data.get("domain", "example.com"), # Ensure domain is passed
                           site_wide_data=site_wide_data)

    print("Running analyze_all()...")
    analyzer.analyze_all()
    results = analyzer.analysis_results

    print(f"\n--- SEO Analyzer Results ---")
    print(f"Overall Site Health: {results.get('health_percentage', 'N/A')}%")

    # Save categorized_issues to a file for easier inspection
    output_path_categorized = "/tmp/categorized_issues.json"
    output_path_health = "/tmp/site_health.json"

    try:
        with open(output_path_categorized, 'w') as f:
            json.dump(results.get('categorized_issues', {}), f, indent=4)
        print(f"\nCategorized issues saved to: {output_path_categorized}")

        with open(output_path_health, 'w') as f:
            json.dump({"health_percentage": results.get('health_percentage', 'N/A')}, f, indent=4)
        print(f"Site health saved to: {output_path_health}")
    except Exception as e:
        print(f"Error saving analysis results: {e}")

    # --- Initialize and run PDFGenerator ---
    print("\nInitializing PDFGenerator...")
    pdf_gen = PDFGenerator(analysis_results=results,
                           domain=site_wide_data.get("domain", "example.com")) # Pass domain

    pdf_filename = "/tmp/test_seo_report.pdf"
    print(f"Generating PDF: {pdf_filename}...")
    try:
        pdf_gen.generate_pdf(pdf_filename)
        print(f"PDF generated successfully: {pdf_filename}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # You might want to print more details from e for debugging
        import traceback
        traceback.print_exc()


    print("\n--- Test Script Finished ---")
    print("Check the /tmp/ directory for categorized_issues.json, site_health.json, and test_seo_report.pdf")

if __name__ == "__main__":
    main()
