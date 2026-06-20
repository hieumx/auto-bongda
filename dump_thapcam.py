from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://thapcamtivi.app', timeout=15000)
    page.wait_for_timeout(3000)
    with open('thapcam.html', 'w', encoding='utf-8') as f:
        f.write(page.content())
    browser.close()
