// One picture per trend -> img/<n>.jpg, plus data/shots.json saying what each picture is.
// Order: TikTok oEmbed thumbnail of an example > screenshot of the example post > the trend's
// section in the source article (those embed the example posts).
const fs = require('fs'), path = require('path');
const { chromium } = require(process.env.APPDATA + '/npm/node_modules/@playwright/cli/node_modules/playwright-core');
const ROOT = path.resolve(__dirname, '..');
const trends = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/trends.draft.json'), 'utf8'));
const only = process.argv[2] ? process.argv[2].split(',').map(Number) : null;
fs.mkdirSync(path.join(ROOT, 'img'), { recursive: true });

async function thumb(u, out) {
  try {
    const o = await (await fetch('https://www.tiktok.com/oembed?url=' + encodeURIComponent(u))).json();
    if (!o.thumbnail_url) return null;
    fs.writeFileSync(out, Buffer.from(await (await fetch(o.thumbnail_url)).arrayBuffer()));
    return { kind: 'example', url: u.replace('/@_/', '/@' + o.author_unique_id + '/'), by: o.author_name };
  } catch { return null; }
}

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', args: ['--mute-audio'] });
  const ctx = await browser.newContext({ viewport: { width: 1100, height: 1300 }, deviceScaleFactor: 2, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36' });
  await ctx.addInitScript(() => { window.speechSynthesis && (window.speechSynthesis.speak = () => {}); });
  const shotsFile = path.join(ROOT, 'data/shots.json');
  const shots = fs.existsSync(shotsFile) ? JSON.parse(fs.readFileSync(shotsFile, 'utf8')) : {};
  for (const [i, t] of trends.entries()) {
    const n = i + 1, out = path.join(ROOT, `img/${n}.jpg`);
    if (only && !only.includes(n)) continue;
    let done = null;
    for (const u of t.examples.filter(u => /tiktok\.com\/@/.test(u))) if ((done = await thumb(u, out))) break;
    for (const src of done ? [] : t.sources) {
      const page = await ctx.newPage();
      try {
        await page.goto(src, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(2500);
        // find the heading for this trend (first 2 words of its name are the most stable match)
        const key = t.name.replace(/[(\[].*$/, '').replace(/['‘’"“”]/g, '').trim().split(/\s+/).slice(0, 2).join(' ');
        const esc = s => new RegExp(s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
        let h = page.locator('h2, h3, h4').filter({ hasText: esc(key) }).first();
        if (!(await h.count())) {  // fall back to any text block holding the trend's sound or name
          const alt = (t.sound && !/^https?:/.test(t.sound) ? t.sound.split(/ [-—] | by /)[0] : key.split(' ')[0]).trim();
          h = page.locator('h2, h3, h4, p, li, strong').filter({ hasText: esc(alt) }).first();
          if (!(await h.count())) throw new Error('not found: ' + key + ' / ' + alt);
        }
        // hide cookie banners / sticky bars, then crop to the first embedded post after the heading
        await page.addStyleTag({ content: '[class*=cookie i],[id*=cookie i],[class*=consent i],[id*=onetrust i],[class*=banner i]{display:none!important}' });
        const embed = await h.evaluateHandle(el => {
          const tag = el.tagName, all = [...document.querySelectorAll('h2,h3,h4,iframe,blockquote,video,div[class*=embed]')];
          for (const n of all.slice(all.indexOf(el) + 1)) {
            if (/^H\d/.test(tag) ? /^H/.test(n.tagName) && n.tagName <= tag : n.getBoundingClientRect().top - el.getBoundingClientRect().top > 1400) return null;  // next section: no embed here
            const s = (n.src || '') + (n.className || '') + (n.getAttribute('cite') || '');
            if (n.tagName === 'VIDEO' || /tiktok|instagram|youtube/i.test(s)) return n;
          }
          return null;
        });
        const el = embed.asElement();
        if (el) {
          // the post behind the embed: TikTok ones get a clean oEmbed thumbnail, the rest a crop
          let post = await el.evaluate(e => (e.outerHTML.match(/https:\/\/www\.(?:tiktok\.com\/@[\w.-]+\/video\/\d+|instagram\.com\/(?:p|reel)\/[\w-]+)/) || [])[0]
            || (e.dataset.videoId && 'https://www.tiktok.com/@_/video/' + e.dataset.videoId) || null);
          if (!post) {  // script-built embeds (Later): scroll to it and read the video id off the iframe it injects
            await el.scrollIntoViewIfNeeded();
            const f = await el.waitForSelector('iframe', { timeout: 15000 }).then(x => x.getAttribute('src')).catch(() => '');
            const id = (f || '').match(/(\d{17,20})/);
            if (id) post = 'https://www.tiktok.com/@_/video/' + id[1];
          }
          if (post && /tiktok/.test(post)) done = await thumb(post, out);
          if (!done) {
            await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(6000);
            await el.screenshot({ path: out, type: 'jpeg', quality: 85 });
            if (fs.statSync(out).size > 20000) done = { kind: 'embed', url: post || src, source: src };
            // else: embed never rendered, fall back to the text crop below
          }
        }
        if (!done) {
          await h.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollBy(0, -20)); await page.waitForTimeout(1500);
          const b = await h.boundingBox();
          await page.screenshot({ path: out, type: 'jpeg', quality: 85, clip: { x: Math.max(0, b.x - 20), y: b.y - 20, width: Math.min(760, 1100 - b.x + 20), height: 520 } });
          done = { kind: 'source', url: src };
        }
      } catch (e) { console.log(n, 'source fail', src, e.message.split('\n')[0]); }
      await page.close();
      if (done) break;
    }
    shots[n] = done;
    console.log(n, done ? done.kind : 'NONE', t.name);
  }
  fs.writeFileSync(shotsFile, JSON.stringify(shots, null, 1));
  await browser.close();
})();
