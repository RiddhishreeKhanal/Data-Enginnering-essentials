import json
from playwright.sync_api import sync_playwright

def scrape_ekantipur():
    """Main function to scrape ekantipur.com"""
    
    # Start browser
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=False,
            args=[
                '--lang=ne-NP',
                '--accept-lang=ne',
                '--disable-translate',
            ]
        )
        
        page = browser.new_page()
        
        # Block translate popups
        try:
            page.route('**/*translate.googleapis.com/*', lambda route: route.abort())
        except Exception as e:
            print(f"Warning: Could not block translate popups: {e}")
        
        # Go to main page
        try:
            page.goto("https://ekantipur.com/")
        except Exception as e:
            print(f"Error loading main page: {e}")
            browser.close()
            return
        
        # Click entertainment section
        try:
            page.click('a[href="https://ekantipur.com/entertainment"]')
            page.wait_for_load_state('networkidle')
        except Exception as e:
            print(f"Error navigating to entertainment section: {e}")
            browser.close()
            return
        
        # Scrape entertainment articles
        entertainment_articles = scrape_entertainment(page)
        
        # Go back to main page for cartoon
        print("Going back to main page for cartoon...")
        try:
            page.goto("https://ekantipur.com/")
        except Exception as e:
            print(f"Error going back to main page: {e}")
        
        # Scrape cartoon
        print("Scraping cartoon:")
        cartoon = scrape_cartoon(page)
        
        # Combine everything to a dictionary for JSON
        final_data = {
            "entertainment_news": entertainment_articles,
            "cartoon_of_the_day": cartoon
        }
        
        # Save to JSON
        try:
            with open('ekantipur_data.json', 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)
            print(f"\nSuccess! Scraped {len(entertainment_articles)} articles and 1 cartoon")
            print("Saved to 'ekantipur_data.json'")
        except Exception as e:
            print(f"Error saving to JSON file: {e}")
        finally:
            browser.close()


def scrape_entertainment(page):
    """Scrape entertainment articles"""
    
    # Wait for the container that holds articles
    try:
        page.wait_for_selector('.col-xs-10.col-sm-10.col-md-10')
    except Exception as e:
        print(f"Error waiting for container: {e}")
        return []
    
    # Get the container
    try:
        container = page.query_selector('.col-xs-10.col-sm-10.col-md-10')
        if not container:
            raise AttributeError("Container not found")
    except AttributeError:
        print("Container not found!")
        return []
    
    # Get all articles inside container
    try:
        all_articles = container.query_selector_all('article.normal')
    except (AttributeError, TypeError):
        print("No articles found in container!")
        return []
    
    # Take only first 5 articles
    articles = []
    
    for article in all_articles[:5]:
        # Get title
        try:
            title_elem = article.query_selector('h2')
            title = title_elem.text_content().strip()
        except (AttributeError, TypeError):
            title = None
        
        # Get author
        try:
            author_elem = article.query_selector('div.author a')
            author = author_elem.text_content().strip()
        except (AttributeError, TypeError):
            author = None
        
        # Get image - try multiple selectors and methods
        image_url = None
        
        # Method 1: Try img tag with src attribute
        try:
            img_elem = article.query_selector('div.image img')
            if img_elem:
                image_url = img_elem.get_attribute('src')
                if not image_url or image_url.strip() == '':
                    image_url = None
        except (AttributeError, TypeError):
            pass
        
        # Method 2: Try figure a tag with href attribute
        if not image_url:
            try:
                a_elem = article.query_selector('div.image figure a')
                if a_elem:
                    image_url = a_elem.get_attribute('href')
                    if not image_url or image_url.strip() == '':
                        image_url = None
            except (AttributeError, TypeError):
                pass
        
        # Method 3: Try direct img tag anywhere in article
        if not image_url:
            try:
                img_elem = article.query_selector('img')
                if img_elem:
                    image_url = img_elem.get_attribute('src')
                    if not image_url or image_url.strip() == '':
                        image_url = None
            except (AttributeError, TypeError):
                pass
        
        # Method 4: Try data-src or data-lazy-src (lazy loading)
        if not image_url:
            try:
                img_elem = article.query_selector('div.image img')
                if img_elem:
                    image_url = img_elem.get_attribute('data-src') or img_elem.get_attribute('data-lazy-src')
                    if not image_url or image_url.strip() == '':
                        image_url = None
            except (AttributeError, TypeError):
                pass
        
        # Method 5: Try any img tag within article with various attributes
        if not image_url:
            try:
                all_imgs = article.query_selector_all('img')
                for img in all_imgs:
                    if img:
                        # Try src first
                        img_src = img.get_attribute('src')
                        if img_src and img_src.strip():
                            image_url = img_src
                            break
                        # Try data-src
                        img_src = img.get_attribute('data-src')
                        if img_src and img_src.strip():
                            image_url = img_src
                            break
                        # Try data-lazy-src
                        img_src = img.get_attribute('data-lazy-src')
                        if img_src and img_src.strip():
                            image_url = img_src
                            break
            except (AttributeError, TypeError):
                pass
        
        # Method 6: Try any anchor tag with image-related href
        if not image_url:
            try:
                all_links = article.query_selector_all('a')
                for link in all_links:
                    if link:
                        href = link.get_attribute('href')
                        if href and (href.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) or 'image' in href.lower() or 'img' in href.lower()):
                            image_url = href
                            break
            except (AttributeError, TypeError):
                pass
        
        # Get category - try multiple selectors
        category = None
        try:
            category_elem = article.query_selector('div.catName')
            category_text = category_elem.text_content()
            if category_text:
                category = category_text.strip()
        except (AttributeError, TypeError):
            pass
        
        # Try alternative selectors if first one didn't work
        if not category:
            try:
                category_elem = article.query_selector('a.catName, .category, [class*="cat"]')
                category_text = category_elem.text_content()
                if category_text:
                    category = category_text.strip()
            except (AttributeError, TypeError):
                pass
        
        # Use fallback value instead of None to avoid "null" in JSON
        # Since we're on entertainment page, default to "Entertainment" if not found
        category = category if category else "मनोरञ्जन"
        
        # Add to list
        articles.append({
            "title": title,
            "author": author,
            "image_url": image_url,
            "category": category
        })
        
        image_status = "✓" if image_url else "✗"
        print(f"  - Found: {title[:50] if title else 'No title'}... [Image: {image_status}]")
    
    return articles


def scrape_cartoon(page):
    """Scrape cartoon of the day"""
    
    # Scroll down to find cartoon section
    page.evaluate("window.scrollTo(0, 1000)")
    page.wait_for_timeout(1000)  # Wait for scroll
    
    # Find cartoon section
    try:
        cartoon_section = page.query_selector('.cartoon-section')
        if not cartoon_section:
            raise AttributeError("Cartoon section not found")
    except AttributeError:
        print("Cartoon section not found!")
        return {"title": None, "image_url": None, "author": None}
    
    # Get cartoon image
    try:
        cartoon_img = cartoon_section.query_selector('.cartoon-img img')
        cartoon_image_url = cartoon_img.get_attribute('src')
    except (AttributeError, TypeError):
        cartoon_image_url = None
    
    # Get caption and split into title and author
    try:
        caption_elem = cartoon_section.query_selector('.cartoon-caption')
        caption_text = caption_elem.text_content().strip()
        
        # Split by hyphen to get title and author
        if '-' in caption_text:
            parts = caption_text.split('-', 1)
            cartoon_title = parts[0].strip()
            cartoon_author = parts[1].strip()
        else:
            cartoon_title = caption_text
            cartoon_author = None
    except (AttributeError, TypeError):
        cartoon_title = None
        cartoon_author = None
    
    print(f"  - Cartoon: {cartoon_title if cartoon_title else 'No title found'}")
    
    return {
        "title": cartoon_title,
        "image_url": cartoon_image_url,
        "author": cartoon_author
    }


if __name__ == "__main__":
    scrape_ekantipur()