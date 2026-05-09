#!/usr/bin/env python3

import sys
import re
import bibtexparser
import latexcodec
import codecs


def latex_to_unicode(s):
    s = codecs.decode(s, "ulatex")
    s = s.replace("{", "").replace("}", "")
    return s


def format_author(author):

    author = latex_to_unicode(author.strip())

    if "," in author:
        # "Last, First Middle"
        last, first = [x.strip() for x in author.split(",", 1)]
        first_parts = first.split()
    else:
        # "First Middle Last"
        parts = author.split()
        last = parts[-1]
        first_parts = parts[:-1]

    initials = " ".join(p[0] + "." for p in first_parts if p)

    return f"{last}, {initials}"


def format_authors(author_field):

    authors = [a.strip() for a in author_field.split(" and ")]

    return ", ".join(format_author(a) for a in authors)


def make_id(key):
    return re.sub(r"[^a-zA-Z0-9\-]", "", key.lower())


def generate_html(entry):

    key = entry["ID"]

    authors = format_authors(entry.get("author", ""))

    title = latex_to_unicode(entry.get("title", ""))

    venue = (
        latex_to_unicode(entry.get("journal", ""))
        or latex_to_unicode(entry.get("booktitle", ""))
    )

    year = entry.get("year", "")

    link = entry.get("pdf") or entry.get("url") or ""

    span_id = make_id(key)
    pre_id = f"pre-{span_id}"

    citation = f"{authors}. {title} <i>{venue}, {year}</i>."

    if link:
        link_html = f'<span><a href="{link}">pdf</a></span>'
    else:
        link_html = "<span>(link coming later)</span>"

    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = [entry]
    raw_bibtex = bibtexparser.dumps(db).strip()

    html = f"""
<li>
<div class="publicationEntry">
<span id="{span_id}">{citation}</span>

{link_html}
<div onClick="toggle('{pre_id}')" class="bibtexToggle">BibTeX</div>

</div>
<div><pre id="{pre_id}" class="bibtexDisplay">
{raw_bibtex}
</pre></div>
</li>
""".strip()

    return html


def main():

    if len(sys.argv) != 3:
        print("Usage: python bib_to_html.py file.bib bibtex_key")
        sys.exit(1)

    bibfile = sys.argv[1]
    key = sys.argv[2]

    with open(bibfile) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    entries = {entry["ID"]: entry for entry in bib_database.entries}

    if key not in entries:
        print(f"Error: key '{key}' not found")
        sys.exit(1)

    print(generate_html(entries[key]))


if __name__ == "__main__":
    main()