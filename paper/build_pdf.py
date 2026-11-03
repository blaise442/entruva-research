"""Build paper.pdf from paper.md with Chrome headless (no LaTeX on this machine).
Composite figures are assembled from the result PNGs into paper/figures/."""
import re
import subprocess
import sys
from pathlib import Path

import markdown
from PIL import Image

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FIGS = HERE / "figures"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
COMPOSITES = {
    "fig3_attacks.png": [[f"2026-10-28_S3_{a}.png" for a in ("error_suppression", "retry_diversification")],
                         [f"2026-10-28_S3_{a}.png" for a in ("call_shaping", "message_shaping")]],
    "fig4_registries.png": [["2026-10-29_erc8004_registrations_ethereum-mainnet.png", "2026-11-02_erc8004_registrations_base-mainnet.png"],
                            ["2026-11-02_erc8004_registrations_bnb-mainnet.png", "2026-10-27_erc8004_givers.png"]],
}
CSS = """
@page { size: A4; margin: 20mm 17mm 20mm 17mm; @bottom-center { content: counter(page); font: 8.5pt "STIXGeneral", "Times New Roman", serif; } }
html { -webkit-hyphens: auto; hyphens: auto; }
body { font-family: "STIXGeneral", "Times New Roman", Times, serif; font-size: 10pt; line-height: 1.22; color: #000; max-width: 100%; margin: 0; }
.front { column-span: all; margin: 0 0 10pt; }
h1 { font-size: 17pt; font-weight: bold; text-align: center; line-height: 1.2; margin: 0 8mm 8pt; }
h1 + p { text-align: center; font-size: 11pt; margin: 0 0 3pt; }
h1 + p + p { text-align: center; font-size: 8.5pt; margin: 0 12mm 12pt; }
.front h2 { font-size: 10pt; text-align: center; margin: 0 0 3pt; }
.front h2 + p { font-size: 9pt; line-height: 1.25; margin: 0 10mm 5pt; text-align: justify; }
.front p.keywords { font-size: 9pt; margin: 0 10mm 0; text-align: left; }
.cols { columns: 2; column-gap: 6mm; }
h2 { font-size: 11pt; margin: 12pt 0 4pt; break-after: avoid; }
h3 { font-size: 10pt; font-style: italic; font-weight: bold; margin: 9pt 0 3pt; break-after: avoid; }
p { margin: 0 0 5pt; text-align: justify; }
ol, ul { margin: 0 0 5pt 14pt; padding: 0; } li { margin-bottom: 2pt; text-align: justify; }
.tbl { column-span: all; margin: 6pt 0 8pt; }  /* break-inside on a spanner pushes the whole body to page 2 in Chrome */
p.caption { font-size: 9pt; text-align: left; margin: 0 0 2pt; break-after: avoid; }
table { border-collapse: collapse; font-size: 8.5pt; line-height: 1.2; margin: 0 auto; }
th, td { padding: 1.5pt 5pt; text-align: left; vertical-align: top; }
thead tr { border-top: 1pt solid #000; border-bottom: 0.5pt solid #000; } tbody tr:last-child { border-bottom: 1pt solid #000; }
figure { margin: 6pt 0 8pt; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 70mm; }
figure.wide { column-span: all; } figure.wide img { max-width: 92%; max-height: 105mm; }
figcaption { font-size: 9pt; text-align: justify; margin-top: 3pt; }
h2#references ~ p { font-size: 8.5pt; line-height: 1.2; text-align: left; padding-left: 12pt; text-indent: -12pt; margin-bottom: 3pt; }
h2#declarations ~ p { font-size: 9pt; }
a { color: #000; text-decoration: none; word-break: break-all; }
"""


def composite(name, grid):
    rows = [[Image.open(RESULTS / f).convert("RGB") for f in row] for row in grid]
    w = max(sum(i.width for i in r) for r in rows)
    h = sum(max(i.height for i in r) for r in rows)
    out = Image.new("RGB", (w, h), "white")
    y = 0
    for r in rows:
        x = 0
        for i in r:
            out.paste(i, (x, y)); x += i.width
        y += max(i.height for i in r)
    out.save(FIGS / name)


def main():
    FIGS.mkdir(exist_ok=True)
    for name, grid in COMPOSITES.items():
        composite(name, grid)
    md = (HERE / "paper.md").read_text()
    html = markdown.markdown(md, extensions=["tables", "toc"])
    html = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" /></p>',
                  lambda m: f'<figure><img src="{m.group(2)}"><figcaption>{m.group(1)}</figcaption></figure>', html)
    html = re.sub(r"<p>(Table \d+\. )", r'<p class="caption">\1', html)
    html = re.sub(r'(<p class="caption">.*?</p>\s*<table>.*?</table>)', r'<div class="tbl">\1</div>', html, flags=re.S)
    html = html.replace('<figure><img src="figures/', '<figure class="wide"><img src="figures/')
    html = re.sub(r"<p>(Keywords:)", r'<p class="keywords">\1', html)
    cut = html.index("</p>", html.index('<p class="keywords">')) + 4  # title, authors, abstract and keywords span the page
    html = f'<div class="cols"><div class="front">{html[:cut]}</div>{html[cut:]}</div>'  # front matter is a spanner so columns start on page 1
    page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>paper</title><style>{CSS}</style></head><body>{html}</body></html>'
    (HERE / "paper.html").write_text(page)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir=/tmp/claude-chrome-pdf", f"--print-to-pdf={HERE / 'paper.pdf'}",
                    "--virtual-time-budget=10000", (HERE / "paper.html").as_uri()], check=True, capture_output=True)
    pdf = (HERE / "paper.pdf").read_bytes()
    assert b"STIXGeneral" in pdf, "STIXGeneral not embedded"
    print(HERE / "paper.pdf", len(pdf) // 1024, "KB, pages:", pdf.count(b"/Type /Page\n") + pdf.count(b"/Type /Page/") + pdf.count(b"/Type /Page>"))


if __name__ == "__main__":
    sys.exit(main())
