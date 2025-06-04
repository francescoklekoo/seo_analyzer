try:
    from utils.crawler import WebCrawler
    print("Syntax check for utils.crawler.py: PASSED (WebCrawler imported successfully)")
except ImportError as e:
    print(f"Syntax check for utils.crawler.py: FAILED (ImportError: {e})")
    import traceback
    traceback.print_exc()
except SyntaxError as e:
    print(f"Syntax check for utils.crawler.py: FAILED (SyntaxError: {e})")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"Syntax check for utils.crawler.py: FAILED (Unexpected error: {e})")
    import traceback
    traceback.print_exc()
