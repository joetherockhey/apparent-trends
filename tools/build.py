"""data/trends.draft.json + data/shots.json -> index.html (and an archive copy in data/weeks/)."""
import json, html, datetime, pathlib, shutil, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
trends = json.loads((ROOT / "data/trends.draft.json").read_text("utf-8"))
shots = json.loads((ROOT / "data/shots.json").read_text("utf-8"))
today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday())
wk = f"{monday.day} {monday:%B %Y}"
e = lambda s: html.escape(str(s or ""))


def host(u):
    return urllib.parse.urlparse(u).netloc.replace("www.", "")


def links(t, shot):
    seen, out = set(), []
    urls = list(t["examples"])
    if shot and shot.get("url") and "/@_/" not in shot["url"] and shot["kind"] != "source":
        urls.insert(0, shot["url"])
    if t.get("sound", "") and str(t["sound"]).startswith("http"):
        urls.append(t["sound"])
    for u in [u.rstrip("/") for u in urls]:
        if u in seen: continue
        seen.add(u)
        kind = "Sound" if "/music/" in u or "/audio/" in u else "Example"
        out.append(f'<a href="{e(u)}" target="_blank" rel="noopener">{kind} · {e(host(u))}</a>')
    q = urllib.parse.quote(t["name"].split("(")[0].strip())
    out.append(f'<a href="https://www.tiktok.com/search?q={q}" target="_blank" rel="noopener">Search TikTok</a>')
    if any("insta" in p.lower() for p in t["platforms"]):
        out.append(f'<a href="https://www.instagram.com/explore/search/keyword/?q={q}" target="_blank" rel="noopener">Search Instagram</a>')
    return "".join(out)


cards = []
for i, t in enumerate(trends, 1):
    shot = shots.get(str(i))
    img = (f'<figure><img src="img/{i}.jpg?v={monday}" alt="Example of {e(t["name"])}" loading="lazy">'
           f'<figcaption>{"Example post" if shot["kind"] != "source" else "From the source write-up"} · '
           f'<a href="{e(shot["url"])}" target="_blank" rel="noopener">{e(host(shot["url"]))}</a></figcaption></figure>'
           if shot else f'<figure class="noimg"><span>{e(t["name"])}</span></figure>')
    sound = "" if not t.get("sound") or str(t["sound"]).startswith("http") else f'<p><b>Sound</b>{e(t["sound"])}</p>'
    risk = f'<p class="risk"><b>Watch out</b>{e(t["risk"])}</p>' if t.get("risk") else ""
    srcs = " ".join(f'<a href="{e(u)}" target="_blank" rel="noopener">{e(host(u))}</a>' for u in t["sources"])
    cards.append(f"""
<article class="trend" id="t{i}">
  {img}
  <div class="body">
    <div class="meta"><span class="num">{i:02d}</span>{"".join(f'<span class="tag">{e(p)}</span>' for p in t["platforms"])}</div>
    <h2>{e(t["name"])}</h2>
    <p class="what">{e(t["what"])}</p>
    <div class="facts"><p><b>Format</b>{e(t["format"])}</p>{sound}<p><b>Why now</b>{e(t["why_now"])}</p></div>
    <div class="use"><b>How a brand could use it</b><p>{e(t["brand_use"])}</p><p class="brief">{e(t["example_brief"])}</p></div>
    {risk}
    <nav class="links">{links(t, shot)}</nav>
    <p class="src">Sources: {srcs}</p>
  </div>
</article>""")

page = f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trend Report · Week of {wk}</title>
<meta name="description" content="{len(trends)} brand-usable social media trends for the week of {wk}.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;800&family=DM+Mono:wght@400;500&family=Oswald:wght@600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f7f4f2;--card:#f1efed;--line:#e2dfd8;--ink:#232322;--soft:#3a3938;--muted:#6f6c68;--red:#ef4123;--hot:#fa0500}}
*{{box-sizing:border-box;margin:0}}
body{{background:var(--bg);color:var(--ink);font:300 17px/1.55 "Inter Tight",system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
a{{color:inherit}}
header{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:22px 48px}}
.mark{{grid-column:2;font:600 44px/1 Oswald,"Inter Tight",sans-serif;color:var(--hot);letter-spacing:-.02em;text-decoration:none;display:flex;align-items:center;gap:8px}}
.mark i{{width:26px;height:26px;border-radius:50% 50% 50% 8%;background:var(--hot);display:inline-block}}
.mono,header nav a,.tag,.num,figcaption,.links a,.src{{font-family:"DM Mono",monospace;text-transform:uppercase;letter-spacing:.08em;font-size:11.5px}}
header nav{{justify-self:end;display:flex;gap:20px}}
header nav a{{color:var(--hot);text-underline-offset:3px}}
.intro{{padding:40px 64px 8px;max-width:980px}}
.intro p{{font-size:19px}}
.intro h1{{font:800 clamp(44px,8vw,112px)/.92 "Inter Tight",sans-serif;letter-spacing:-.045em;margin:18px 0 26px}}
.intro h1 span{{color:var(--red)}}
.intro .mono{{color:var(--muted)}}
.index{{padding:24px 64px 8px;display:flex;flex-wrap:wrap;gap:8px}}
.index a{{font:500 14px/1 "Inter Tight";text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:9px 14px;background:#fff8}}
.index a:hover{{border-color:var(--red);color:var(--red)}}
main{{padding:24px 48px 64px;display:grid;gap:28px}}
.trend{{display:grid;grid-template-columns:minmax(260px,420px) 1fr;gap:40px;background:var(--card);border-radius:28px;padding:28px;scroll-margin-top:16px}}
figure{{align-self:start;position:sticky;top:20px}}
figure img{{width:100%;max-height:640px;object-fit:cover;object-position:top;border-radius:20px;display:block;background:var(--line)}}
figcaption{{margin-top:10px;color:var(--muted)}}
.noimg{{aspect-ratio:4/5;border-radius:20px;background:var(--red);display:grid;place-items:end start;padding:28px}}
.noimg span{{font:800 40px/.95 "Inter Tight";letter-spacing:-.04em;color:var(--bg)}}
.meta{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
.num{{color:var(--red);font-size:13px;margin-right:6px}}
.tag{{border:1px solid var(--line);border-radius:999px;padding:4px 10px;background:var(--bg)}}
h2{{font:800 clamp(30px,4vw,52px)/1 "Inter Tight";letter-spacing:-.035em;margin:16px 0 14px}}
.what{{font-size:20px;color:var(--soft);max-width:60ch}}
.facts{{display:grid;gap:10px;margin:22px 0;padding:18px 0;border-block:1px solid var(--line)}}
.facts b,.use b,.risk b{{display:block;font:500 11.5px "DM Mono",monospace;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:3px}}
.use{{background:var(--ink);color:var(--bg);border-radius:20px;padding:22px 24px}}
.use b{{color:var(--red)}}
.use p{{font-size:18px}}
.use .brief{{margin-top:12px;padding-top:12px;border-top:1px solid #ffffff22;font-style:italic;color:#e2dfd8}}
.risk{{margin-top:16px;font-size:15px;color:var(--soft)}}
.links{{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}}
.links a{{text-decoration:none;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:8px 12px}}
.links a:hover{{background:var(--red);border-color:var(--red);color:#fff}}
.src{{margin-top:14px;color:var(--muted);font-size:10.5px}}
footer{{padding:40px 64px 56px;border-top:1px solid var(--line);color:var(--muted);font-size:14px;display:grid;gap:10px;max-width:1100px}}
@media (max-width:820px){{
  header{{padding:16px}} .mark{{font-size:34px}} .intro,.index,footer{{padding-left:16px;padding-right:16px}}
  main{{padding:16px}} .trend{{grid-template-columns:1fr;padding:16px;gap:20px;border-radius:22px}}
  figure{{position:static}} figure img{{max-height:520px}} .what{{font-size:18px}}
}}
</style>
</head>
<body>
<header><a class="mark" href="./"><i></i>apparent</a><nav><a href="#how">How this works</a></nav></header>
<section class="intro">
  <p class="mono">Social trend report · Week of {wk}</p>
  <h1>{len(trends)} trends brands can <span>actually use</span> this week.</h1>
  <p>What's moving on TikTok, Instagram Reels and YouTube Shorts right now. We only kept trends a brand or client could plausibly run, and each one comes with examples and a suggested way in.</p>
</section>
<nav class="index">{"".join(f'<a href="#t{i}">{i:02d} {e(t["name"])}</a>' for i, t in enumerate(trends, 1))}</nav>
<main>{"".join(cards)}</main>
<footer id="how">
  <p class="mono">How this works</p>
  <p>Each Monday, trend round-ups from New Engen, Later, SocialPilot, Gelato, Ramdam and others are read and merged into one list. Anything stale or hard to use for a brand is dropped. Example posts link to the original creators, and screenshots are there for reference only.</p>
  <p>The descriptions and brand ideas are a starting point. Check a trend's sound and licensing before using it on a brand account.</p>
  <p class="mono">Compiled {today.day} {today:%B %Y}</p>
</footer>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, "utf-8")
(ROOT / "data/weeks").mkdir(exist_ok=True)
shutil.copy(ROOT / "data/trends.draft.json", ROOT / f"data/weeks/{monday}.json")
print("built", len(trends), "trends")
