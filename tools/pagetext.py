"""Print readable text of a URL (reuses research.py's HTML->text). Usage: python tools/pagetext.py <url> [maxchars]"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("r", pathlib.Path(__file__).with_name("research.py")); r = importlib.util.module_from_spec(spec)
sys.argv, url, n = [sys.argv[0]], sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 12000
spec.loader.exec_module(r)
t, em = r.fetch(url); print(t[:n]); print("EMBEDS", em)
