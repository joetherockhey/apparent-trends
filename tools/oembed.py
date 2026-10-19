"""Check TikTok URLs: posted date (from the video id) + oEmbed author/title. Usage: python tools/oembed.py <url>..."""
import sys, json, time, datetime, urllib.request, urllib.parse, re
for u in sys.argv[1:]:
    vid = int(re.search(r"/video/(\d+)", u).group(1))
    posted = datetime.datetime.fromtimestamp(vid >> 32, datetime.UTC).date()
    try:
        o = json.load(urllib.request.urlopen("https://www.tiktok.com/oembed?url=" + urllib.parse.quote(u, safe=""), timeout=20))
        print(posted, "|", o.get("author_name"), "|", (o.get("title") or "")[:90].replace("\n", " "), "|", u)
    except Exception as e:
        print(posted, "| oembed fail", e, "|", u)
    time.sleep(1.5)
