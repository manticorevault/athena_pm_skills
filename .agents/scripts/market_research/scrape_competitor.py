import sys
import json
import asyncio
from playwright.async_api import async_playwright

async def scrape_competitor(url):
    results = {
        "url": url,
        "title": "",
        "headings": [],
        "pricing_data": [],
        "feature_statements": [],
        "error": None
    }
    
    try:
        async with async_playwright() as p:
            # Using chromium for broader compatibility
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Go to the URL and wait for DOM content (networkidle often times out on noisy SaaS sites)
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Wait a brief moment for dynamic client-side react/vue hydration to finish
            await page.wait_for_timeout(3000)
            
            # 1. Get Title
            results["title"] = await page.title()
            
            # 2. Extract primary headings (H1 and H2)
            h1s = await page.locator("h1").all_inner_texts()
            h2s = await page.locator("h2").all_inner_texts()
            results["headings"] = [h.strip() for h in h1s + h2s if h and h.strip()]
            
            # 3. Extract Pricing-related text (look for elements containing $ or "price")
            # We look for common pricing table structures or elements with dollar signs
            pricing_elements = await page.locator("text=/$|price|monthly|annual|tier/i").all_inner_texts()
            
            # Filter and deduplicate pricing texts
            clean_pricing = []
            for text in pricing_elements:
                if text:
                    cleaned = text.strip()
                    if cleaned and len(cleaned) < 500 and cleaned not in clean_pricing:
                        clean_pricing.append(cleaned)
            results["pricing_data"] = clean_pricing[:20]  # Cap at 20 segments to prevent JSON bloat
            
            # 4. Extract Feature statements (lists or common feature grid items)
            li_elements = await page.locator("li").all_inner_texts()
            clean_features = []
            for li in li_elements:
                if li:
                    cleaned = li.strip()
                    if cleaned and 10 < len(cleaned) < 300 and cleaned not in clean_features:
                        clean_features.append(cleaned)
            results["feature_statements"] = clean_features[:30] # Cap at 30 features
            
            await browser.close()
            
    except Exception as e:
        results["error"] = str(e)
        
    return results

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Please provide a URL as an argument."}))
        sys.exit(1)
        
    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url
        
    # Run the async Playwright script
    results = asyncio.run(scrape_competitor(url))
    
    # Print the JSON output for Antigravity to consume
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
