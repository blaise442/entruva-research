"""Build the journal-format manuscript (manuscript.tex, manuscript.pdf) from paper.md.

paper.md stays the single source. This script rewrites its front matter, table
captions, figure captions and headings into pandoc markdown, lets pandoc write
LaTeX, and compiles it with pdflatex. Needs pandoc and a LaTeX install with
booktabs, longtable, caption, xurl and mathptmx.

    python paper/build_tex.py            single column, single spaced
    python paper/build_tex.py --review   double spaced with line numbers
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN_IN = ("Data and code availability", "Ethics", "Author contributions (CRediT)", "Conflict of interest", "Funding", "AI use")

HEADER = r"""
\usepackage{mathptmx}
\usepackage[scaled=0.9]{helvet}
\usepackage{microtype}
\usepackage{xurl}
\usepackage{etoolbox}
\usepackage[font=small,labelfont=bf,labelsep=period]{caption}
\AtBeginEnvironment{longtable}{\footnotesize}
\setlength{\LTcapwidth}{\textwidth}
\renewcommand{\arraystretch}{1.15}
\setlength{\tabcolsep}{4pt}
\setlength{\emergencystretch}{2em}
"""
REVIEW = r"""
\usepackage{setspace}
\usepackage{lineno}
\doublespacing
\linenumbers
"""


def front_matter(md: str) -> tuple[dict, str]:
    head, body = md.split("\n## 1. Introduction\n", 1)
    blocks = [b.strip() for b in head.split("\n\n") if b.strip()]
    title = blocks[0].lstrip("# ").strip()
    name, affiliation, contact = [line.strip() for line in blocks[1].splitlines()]
    version = blocks[2]
    abstract = blocks[blocks.index("## Abstract") + 1]
    keywords = next(b for b in blocks if b.startswith("Keywords:"))[len("Keywords:"):].strip()
    return {"title": title, "name": name, "affiliation": affiliation, "contact": contact,
            "version": version, "abstract": abstract, "keywords": keywords}, "## 1. Introduction\n" + body


def table_block(caption: str, table: str) -> str:
    """'Table N. caption' paragraph plus pipe table -> pandoc table with caption and proportional column widths."""
    rows = table.strip().splitlines()
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    header, body = cells[0], cells[2:]
    cap = 46 if len(header) <= 5 else 16  # many-column tables wrap their interval cells
    widths = [min(max(max(len(r[i]) for r in body), max(len(w) for w in header[i].split() or [""])), cap) + 2 for i in range(len(header))]
    sep = "|" + "|".join("-" * w for w in widths) + "|"
    return "\n".join([rows[0], sep] + rows[2:]) + f"\n\n: {caption}\n\n"


def to_pandoc(body: str) -> str:
    body = re.sub(r"^Table \d+\. (.+?)\n\n((?:\|.*\n)+)", lambda m: table_block(m.group(1), m.group(2)), body, flags=re.M)

    def figure(m):
        width = "100%" if m.group(2).startswith("figures/") else "62%"
        return f"![{m.group(1)}]({m.group(2)}){{width={width}}}"
    body = re.sub(r"!\[Figure \d+\. (.*?)\]\((.*?)\)", figure, body)
    body = re.sub(r"^## \d+\. (.+)$", r"# \1", body, flags=re.M)
    body = re.sub(r"^### \d+\.\d+ (.+)$", r"## \1", body, flags=re.M)
    body = re.sub(r"^## (Declarations|References)$", r"# \1 {-}", body, flags=re.M)
    for label in RUN_IN:
        body = body.replace(f"\n{label}. ", f"\n**{label}.** ")
    pre, refs = body.split("# References {-}\n", 1)
    hang = "\\begingroup\\small\\setlength{\\parindent}{-1.5em}\\setlength{\\leftskip}{1.5em}\\setlength{\\parskip}{3pt}"
    refs = f"\n\n```{{=latex}}\n{hang}\n```\n\n" + refs.strip() + "\n\n```{=latex}\n\\par\\endgroup\n```\n"
    return pre + "# References {-}\n" + refs


def main() -> int:
    review = "--review" in sys.argv
    meta, body = front_matter((HERE / "paper.md").read_text())
    emails = ", ".join(f"`{e.strip()}`" for e in meta["contact"].split(":", 1)[1].split(","))
    yaml = "\n".join([
        "---",
        f"title: |\n  {meta['title']}",
        f"author: |\n  {meta['name']}\\\n  {meta['affiliation']}\\\n  Correspondence: {emails}",
        f"thanks: |\n  {meta['version']}",
        "date: \"\"",
        f"abstract: |\n  {meta['abstract']}\n\n  \\medskip\\noindent\\textbf{{Keywords:}} {meta['keywords']}",
        "documentclass: article", "papersize: a4", "fontsize: 11pt", "geometry: margin=25mm",
        "numbersections: true", "colorlinks: false", "link-citations: false",
        "header-includes: |\n  ```{=latex}\n" + "\n".join("  " + line for line in (HEADER + (REVIEW if review else "")).strip().splitlines()) + "\n  ```",
        "---", "",
    ])
    src = HERE / "manuscript.pandoc.md"
    src.write_text(yaml + to_pandoc(body))
    tex = HERE / "manuscript.tex"
    subprocess.run(["pandoc", str(src), "-f", "markdown", "-t", "latex", "-s", "--columns=72", "-o", str(tex)], check=True, cwd=HERE)
    src.unlink()
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name], cwd=HERE, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-3000:]); return 1
    for ext in (".aux", ".log", ".out"):
        (HERE / f"manuscript{ext}").unlink(missing_ok=True)
    print(HERE / "manuscript.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
