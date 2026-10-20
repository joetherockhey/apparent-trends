"""AI stand-in images for trends with no capturable example post (Cloudflare Workers AI, FLUX.1 schnell).

Uses wrangler's OAuth token (run `npx wrangler whoami` first if it has expired).
Usage: python tools/ai_images.py   -> img/<n>.jpg for every trend missing from data/shots.json
Cost: a few neurons per image, inside Workers AI's free daily allocation.
"""
import json, base64, os, re, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ACCOUNT = "cb6c38738659e84f161acc1a035c97b0"
TOKEN = re.search(r'oauth_token\s*=\s*"([^"]+)"', (pathlib.Path(os.environ["APPDATA"]) / "xdg.config/.wrangler/config/default.toml").read_text()).group(1)
trends = json.loads((ROOT / "data/trends.json").read_text("utf-8"))
shots_file = ROOT / "data/shots.json"
shots = json.loads(shots_file.read_text("utf-8"))

STYLE = ("vertical 9:16 smartphone video still, natural light, candid social media look, "
         "photorealistic, no text, no logos, no watermarks")

for n, t in enumerate(trends, 1):
    if shots.get(str(n)):
        continue
    prompt = f"{t['what']} Scene idea: {t['brand_use']} {STYLE}"
    body = json.dumps({"prompt": prompt, "steps": 8}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        body, {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    (ROOT / f"img/{n}.jpg").write_bytes(base64.b64decode(r["result"]["image"]))
    shots[str(n)] = {"kind": "ai", "model": "FLUX.1 schnell (Cloudflare Workers AI)"}
    print(n, "ai image", t["name"])

shots_file.write_text(json.dumps(shots, indent=1), "utf-8")
