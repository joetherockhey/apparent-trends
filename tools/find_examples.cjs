// Usage: node tools/find_examples.cjs <tiktok discover slug or tag:name> ... -> prints top video URLs per page
const { chromium } = require(process.env.APPDATA + '/npm/node_modules/@playwright/cli/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch({ channel: 'msedge', args: ['--mute-audio'] });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 1400 }, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36' });
  for (const q of process.argv.slice(2)) {
    const p = await ctx.newPage();
    const url = q.startsWith('tag:') ? 'https://www.tiktok.com/tag/' + q.slice(4) : q.startsWith('music:') ? 'https://www.tiktok.com/music/' + q.slice(6) : 'https://www.tiktok.com/discover/' + q;
    try {
      await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await p.waitForTimeout(6000);
      const v = await p.$$eval('a[href*="/video/"]', as => [...new Set(as.map(a => a.href.split('?')[0]))]);
      console.log(q, '=>', v.slice(0, 5).join(' ') || '(none)');
    } catch (e) { console.log(q, 'fail', e.message.split('\n')[0]); }
    await p.close();
  }
  await b.close();
})();
