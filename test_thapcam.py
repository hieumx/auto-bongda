from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('https://thapcamtivi.app', timeout=60000)
        
        page.wait_for_function('''document.querySelectorAll('a[href*="/truc-tiep"]').length > 0''', timeout=60000)
        
        raw = page.evaluate('''
            Array.from(document.querySelectorAll('a[href*="/truc-tiep"]')).map(a => {
                let img = a.querySelector('img');
                let parent = a.closest('.match-card') || a.closest('li') || a.closest('.item') || a.parentElement.parentElement;
                return {
                    url: a.href,
                    ten: parent ? parent.innerText.trim().replace(/\\n/g, ' - ') : a.innerText.trim(),
                }
            })
        ''')
        print('Total matches:', len(raw))
        for r in raw[:5]:
            print(r)
        
        browser.close()

if __name__ == '__main__':
    run()
