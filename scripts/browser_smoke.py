"""Real browser check against the unified service; no API mocks."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    outputs = ROOT / 'outputs'
    outputs.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.locator('#simulator form').wait_for()
        assert page.locator('section').count() == 5
        assert page.locator('html').get_attribute('lang') == 'en'
        assert page.locator('.chosen').count() >= 1
        page.screenshot(path=str(outputs / 'desktop-en.png'))
        page.get_by_label('Distribution', exact=True).select_option('bmi')
        page.get_by_label('Show', exact=True).select_option('rate')
        assert 'BMI' in page.locator('#explorer .chart').first.inner_text()
        slider = page.get_by_role('slider')
        before = page.locator('output').inner_text()
        slider.fill('45')
        assert page.locator('output').inner_text() != before
        page.locator('#explorer').screenshot(path=str(outputs / 'explorer-en.png'))
        page.get_by_role('button', name='Run the saved pipeline', exact=True).click()
        page.locator('.result .score').wait_for()
        assert page.locator('#explain .contribution').count() == 20
        score_a = page.locator('.result .score').inner_text()
        page.get_by_role('button', name='Example B · older adult', exact=True).click()
        page.get_by_role('button', name='Run the saved pipeline', exact=True).click()
        page.locator('.result .score').wait_for()
        assert page.locator('.result .score').inner_text() != score_a
        page.get_by_label('BMI (kg/m²; optional)', exact=True).fill('')
        page.get_by_role('button', name='Run the saved pipeline', exact=True).click()
        page.locator('.result .score').wait_for()
        assert 'fitted development median' in page.locator('.result').inner_text()
        page.get_by_label('Age (years)', exact=True).fill('188')
        page.get_by_role('button', name='Run the saved pipeline', exact=True).click()
        assert page.get_by_role('alert').is_visible()
        assert page.get_by_label('Age (years)', exact=True).get_attribute('aria-invalid') == 'true'
        page.get_by_role('button', name='VI', exact=True).click()
        assert page.locator('html').get_attribute('lang') == 'vi'
        assert 'Kiểm tra' in page.get_by_role('alert').inner_text()
        page.get_by_role('button', name='Ví dụ A · người trưởng thành', exact=True).click()
        page.get_by_role('button', name='Chạy pipeline đã lưu', exact=True).click()
        page.locator('.result .score').wait_for()
        assert 'xác suất' in page.locator('.result').inner_text()
        page.reload()
        page.locator('#simulator form').wait_for()
        assert page.locator('html').get_attribute('lang') == 'vi'
        page.screenshot(path=str(outputs / 'desktop-vi.png'))
        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path=str(outputs / 'mobile-vi.png'))
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1')
        for width in [320, 768]:
            page.set_viewport_size({'width': width, 'height': 844})
            # Recharts responds through ResizeObserver on a later browser frame.
            page.wait_for_function('document.documentElement.scrollWidth <= window.innerWidth + 1', timeout=5000)
            overflow = page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            if overflow:
                print('Overflow', width, page.evaluate("Array.from(document.querySelectorAll('main *')).filter(e => e.getBoundingClientRect().right > innerWidth + 1).slice(0, 12).map(e => ({tag:e.tagName,cls:e.className,right:e.getBoundingClientRect().right,text:e.textContent.slice(0,50)}))"))
            assert not overflow
        page.set_viewport_size({'width': 390, 'height': 844})
        page.get_by_label('Tuổi (năm)', exact=True).fill('30')
        page.get_by_role('button', name='Chạy pipeline đã lưu', exact=True).click()
        page.locator('.result .score').wait_for()
        page.screenshot(path=str(outputs / 'mobile-simulator.png'))
        assert not errors, errors
        browser.close()
    result = {'status': 'passed', 'checks': ['five sections', 'real predictions for distinct profiles',
               'EN/VI form and errors', 'language persistence', 'EDA controls', 'threshold exploration',
               'local contributions', 'null BMI', 'invalid age', '390px mobile no horizontal overflow',
               'no browser exceptions'], 'screenshots': ['desktop-en.png', 'desktop-vi.png', 'mobile-vi.png', 'mobile-simulator.png']}
    (outputs / 'browser-checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
