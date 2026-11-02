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
@page { size: A4; margin: 24mm 22mm; @bottom-center { content: counter(page); font: 9pt "Times New Roman"; } }
body { font-family: "Times New Roman", Times, serif; font-size: 11pt; line-height: 1.35; color: #000; max-width: 100%; }
h1 { font-size: 17pt; text-align: center; line-height: 1.25; margin: 0 0 8pt; }
h1 + p { text-align: center; margin: 0 0 4pt; }
h1 + p + p { text-align: center; font-size: 9.5pt; margin: 0 0 16pt; }
h2 { font-size: 12.5pt; margin: 18pt 0 6pt; page-break-after: avoid; }
h3 { font-size: 11pt; font-style: italic; margin: 12pt 0 4pt; page-break-after: avoid; }
p { margin: 0 0 7pt; text-align: justify; hyphens: auto; }
h2#abstract + p { font-size: 10pt; margin: 0 14mm 6pt; }
ol, ul { margin: 0 0 7pt 18pt; padding: 0; } li { margin-bottom: 3pt; text-align: justify; }
table { border-collapse: collapse; font-size: 9pt; margin: 4pt auto 12pt; page-break-inside: avoid; }
th, td { padding: 2pt 6pt; text-align: left; vertical-align: top; }
thead tr { border-top: 1pt solid #000; border-bottom: 0.6pt solid #000; } tbody tr:last-child { border-bottom: 1pt solid #000; }
p.caption { font-size: 9.5pt; text-align: left; margin: 10pt 0 2pt; page-break-after: avoid; }
figure { margin: 10pt auto 12pt; text-align: center; page-break-inside: avoid; }
figure img { max-width: 72%; max-height: 82mm; } figure img[src*="figures/"] { max-width: 100%; max-height: 120mm; }
figcaption { font-size: 9.5pt; text-align: justify; margin-top: 4pt; }
h2#references + p, h2#references ~ p { font-size: 9.5pt; text-align: left; padding-left: 18pt; text-indent: -18pt; margin-bottom: 5pt; }
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
    page = f'<!doctype html><html><head><meta charset="utf-8"><title>paper</title><style>{CSS}</style></head><body>{html}</body></html>'
    (HERE / "paper.html").write_text(page)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir=/tmp/claude-chrome-pdf", f"--print-to-pdf={HERE / 'paper.pdf'}",
                    "--virtual-time-budget=10000", (HERE / "paper.html").as_uri()], check=True, capture_output=True)
    pdf = (HERE / "paper.pdf").read_bytes()
    assert b"TimesNewRoman" in pdf or b"Times New Roman" in pdf, "Times New Roman not embedded"
    print(HERE / "paper.pdf", len(pdf) // 1024, "KB, pages:", pdf.count(b"/Type /Page\n") + pdf.count(b"/Type /Page/") + pdf.count(b"/Type /Page>"))


if __name__ == "__main__":
    sys.exit(main())
