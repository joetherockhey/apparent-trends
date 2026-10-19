"""data/trends.json + data/shots.json -> index.html (and an archive copy in data/weeks/)."""
import json, html, datetime, pathlib, shutil, urllib.parse, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
trends = json.loads((ROOT / "data/trends.json").read_text("utf-8"))
shots = json.loads((ROOT / "data/shots.json").read_text("utf-8"))
today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday())
wk = f"{monday.day} {monday:%B %Y}"
e = lambda s: html.escape(str(s or ""))
STATUS = {"Rising": "rise", "Peaking": "peak", "Seasonal": "peak", "Second wave": "rise", "Steady": "flat", "Past peak": "fade"}


def host(u):
    return urllib.parse.urlparse(u).netloc.replace("www.", "")


def posted(u):
    """TikTok video ids carry their upload time in the top 32 bits."""
    m = re.search(r"tiktok\.com/@([^/]+)/video/(\d+)", u)
    if not m: return ""
    d = datetime.datetime.fromtimestamp(int(m.group(2)) >> 32, datetime.UTC).date()
    return f" · @{m.group(1)}, {d.day} {d:%b %Y}"


def links(t):
    out = []
    for u in t["examples"]:
        kind = "Sound" if "/music/" in u or "/audio/" in u else "Example"
        out.append(f'<a href="{e(u)}" target="_blank" rel="noopener">{kind} · {e(host(u))}{e(posted(u))}</a>')
    q = urllib.parse.quote(re.sub(r"[(:\"'“”‘’…].*$", "", t["name"]).strip() or t["name"])
    out.append(f'<a href="https://www.tiktok.com/search?q={q}" target="_blank" rel="noopener">Search TikTok</a>')
    if "Instagram" in t["platforms"]:
        out.append(f'<a href="https://www.instagram.com/explore/search/keyword/?q={q}" target="_blank" rel="noopener">Search Instagram</a>')
    return "".join(out)


cards = []
for i, t in enumerate(trends, 1):
    shot = shots.get(str(i))
    if shot and shot["kind"] == "ai":
        cap = f'<span class="ai">AI-generated illustration</span> · no example post could be captured ({e(shot["model"])})'
    elif shot:
        cap = f'Example post · <a href="{e(shot["url"])}" target="_blank" rel="noopener">{e(host(shot["url"]))}{e(posted(shot["url"]))}</a>'
    img = (f'<figure><img src="img/{i}.jpg?v={today}" alt="{"AI illustration" if shot["kind"] == "ai" else "Example post"} for {e(t["name"])}" loading="lazy">'
           f'<figcaption>{cap}</figcaption></figure>' if shot else f'<figure class="noimg"><span>{e(t["name"])}</span></figure>')
    sound = f'<p><b>Sound</b>{e(t["sound"])}</p>' if t.get("sound") else ""
    risk = f'<p class="risk"><b>Watch out</b>{e(t["risk"])}</p>' if t.get("risk") else ""
    srcs = " ".join(f'<a href="{e(u)}" target="_blank" rel="noopener">{e(host(u))}</a>' for u in t["sources"])
    cards.append(f"""
<article class="trend" id="t{i}">
  {img}
  <div class="body">
    <div class="meta"><span class="num">{i:02d}</span><span class="status {STATUS.get(t["status"], "flat")}">{e(t["status"])}</span>{"".join(f'<span class="tag">{e(p)}</span>' for p in t["platforms"])}</div>
    <h2>{e(t["name"])}</h2>
    <p class="peakline"><b>Peak</b>{e(t["peak"])}</p>
    <p class="what">{e(t["what"])}</p>
    <div class="facts"><p><b>Format</b>{e(t["format"])}</p>{sound}<p><b>Why now</b>{e(t["why_now"])}</p><p><b>Timeline</b>{e(t["timeline"])}</p></div>
    <div class="use"><b>How a brand could use it</b><p>{e(t["brand_use"])}</p><p class="brief">{e(t["example_brief"])}</p></div>
    {risk}
    <nav class="links">{links(t)}</nav>
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
.mono,header nav a,.tag,.num,.status,figcaption,.links a,.src{{font-family:"DM Mono",monospace;text-transform:uppercase;letter-spacing:.08em;font-size:11.5px}}
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
.status{{border-radius:999px;padding:4px 10px;color:#fff;background:var(--muted)}}
.status.rise{{background:#1f7a4d}} .status.peak{{background:var(--red)}} .status.fade{{background:#8a8580}}
.peakline{{font-size:17px;font-weight:500;margin:-4px 0 14px}}
.peakline b{{font:500 11.5px "DM Mono",monospace;text-transform:uppercase;letter-spacing:.08em;color:var(--red);margin-right:10px}}
.ai{{color:var(--red)}}
.intro .legend{{font-size:11.5px;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;color:var(--muted);margin-top:18px}}
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
  <p>What's moving on TikTok and Instagram Reels right now, with when each trend peaked, examples and a suggested way in for brands. Only trends a brand or client could plausibly run made the list.</p>
  <p class="legend mono"><span class="status rise">Rising</span> still climbing, get in early <span class="status peak">Peaking</span> at its height now <span class="status fade">Past peak</span> post this week or skip <span class="status">Steady</span> evergreen</p>
</section>
<nav class="index">{"".join(f'<a href="#t{i}">{i:02d} {e(t["name"])}</a>' for i, t in enumerate(trends, 1))}</nav>
<main>{"".join(cards)}</main>
<footer id="how">
  <p class="mono">How this works</p>
  <p>Each Monday, the latest round-ups from New Engen, Later, SocialPilot, SocialBee, Ramdam and others are cross-checked against each other and against live TikTok sound pages. Anything stale or hard to use for a brand is dropped. Peak dates come from the round-ups' own dates, sound-stage data and the upload dates of example posts.</p>
  <p>Example images are the cover frames of the linked posts, shown for reference only. Where no example post could be captured, the image is an AI-generated illustration and labelled as one.</p>
  <p>The descriptions and brand ideas are a starting point. Check a trend's sound and licensing before using it on a brand account.</p>
  <p class="mono">Compiled {today.day} {today:%B %Y}</p>
</footer>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, "utf-8")
(ROOT / "data/weeks").mkdir(exist_ok=True)
shutil.copy(ROOT / "data/trends.json", ROOT / f"data/weeks/{monday}.json")
print("built", len(trends), "trends")
