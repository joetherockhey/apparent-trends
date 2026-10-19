# Apparent social trend report

Weekly list of brand-usable TikTok / Instagram / YouTube trends, styled after apparent.com.au.
Live: https://joetherockhey.github.io/apparent-trends/

Weekly run (Mondays), with FreeLLMAPI desktop app running on :31415:

    python tools/research.py     # free LLMs read the roundup pages -> data/trends.draft.json
    node tools/shots.cjs         # one example image per trend -> img/, data/shots.json
    python tools/build.py        # -> index.html, archive copy in data/weeks/

Then review `index.html` and push.
