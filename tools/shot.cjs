// Usage: node shot.cjs <url> <out.png> [width] [height]
const { chromium } = require(process.env.APPDATA + '/npm/node_modules/@playwright/cli/node_modules/playwright-core');
(async () => {
  const [url, out, w = 1280, h = 800] = process.argv.slice(2);
  const browser = await chromium.launch({ channel: 'msedge', args: ['--mute-audio'] });
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36' });
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3500);
    await page.screenshot({ path: out });
    console.log('ok', out);
  } catch (e) { console.log('fail', url, e.message.split('\n')[0]); }
  await browser.close();
})();
