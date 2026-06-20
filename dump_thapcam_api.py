from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        matches = []
        
        def handle_response(response):
            if 'api' in response.url or 'json' in response.url or 'match' in response.url:
                try:
                    text = response.text()
                    if 'match' in text.lower() or 'room' in text.lower() or 'home' in text.lower():
                        print("API:", response.url)
                        print("Data:", text[:500])
                except:
                    pass

        page.on("response", handle_response)
        page.goto('https://thapcamtivi.app', timeout=15000)
        page.wait_for_timeout(5000)
        
        # also print any a tags with /truc-tiep or long links
        import bs4
        soup = bs4.BeautifulSoup(page.content(), 'html.parser')
        links = [a.get('href') for a in soup.find_all('a') if a.get('href') and ('truc-tiep' in a.get('href') or 'match' in a.get('href'))]
        print("Match Links on page:", set(links))
        
        browser.close()

if __name__ == '__main__':
    run()
