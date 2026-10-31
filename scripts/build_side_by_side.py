#!/usr/bin/env python3
"""Two cubes side by side in one page, each in its own area (own rotation, zoom, legend, VR button).
Each cube is embedded in the page (iframe srcdoc), so the page is one standalone file.

    python build_side_by_side.py <left cube.html> <right cube.html> <title> <out.html>
"""
import html
import pathlib
import sys

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --bg:#121317; --line:#2c2d33; }
  html,body { margin:0; height:100%; background:var(--bg); overflow:hidden; }
  #row { display:flex; height:100%; }
  iframe { flex:1; min-width:0; height:100%; border:0; border-right:1px solid var(--line); }
  iframe:last-child { border-right:0; }
  @media (max-width:900px){ #row { flex-direction:column; } iframe { border-right:0; border-bottom:1px solid var(--line); } }
</style>
</head>
<body>
<div id="row">
<iframe allow="xr-spatial-tracking; fullscreen" srcdoc="__LEFT__"></iframe>
<iframe allow="xr-spatial-tracking; fullscreen" srcdoc="__RIGHT__"></iframe>
</div>
</body>
</html>
"""


def main():
    left, right, title, out = sys.argv[1:5]
    s = PAGE.replace("__TITLE__", title)
    for key, f in (("__LEFT__", left), ("__RIGHT__", right)):
        s = s.replace(key, html.escape(pathlib.Path(f).read_text(encoding="utf-8"), quote=True))
    pathlib.Path(out).write_text(s, encoding="utf-8")
    print("saved", out)


if __name__ == "__main__":
    main()
