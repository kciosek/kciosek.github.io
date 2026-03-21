#!/usr/bin/env python3

import sys
import re


def parse_bibtex_entries(text):
    entries = {}
    pattern = re.compile(r'@(\w+)\s*{\s*([^,]+),(.*?)\n}', re.S)

    for m in pattern.finditer(text):
        entry_type, key, body = m.groups()

        fields = dict(
            (k.lower(), v.strip())
            for k, v in re.findall(r'(\w+)\s*=\s*[{"]([^"}]+)[}"]', body)
        )

        entries[key.strip()] = {
            "type": entry_type,
            **fields,
            "raw": m.group(0)
        }

    return entries


def format_authors(author_string):
    authors = [a.strip() for a in author_string.split(" and ")]
    formatted = []

    for a in authors:

        if "," in a:
            # Format: Last, First Middle
            last, first = [x.strip() for x in a.split(",", 1)]
            initials = " ".join(p[0] + "." for p in first.split())
        else:
            # Format: First Middle Last
            parts = a.split()
            last = parts[-1]
            initials = " ".join(p[0] + "." for p in parts[:-1])

        formatted.append(f"{last}, {initials}")

    return ", ".join(formatted)


def make_id(key):
    return re.sub(r'[^a-zA-Z0-9\-]', '', key.lower())


def generate_html(entry, key):
    authors = format_authors(entry.get("author", ""))
    title = entry.get("title", "")
    venue = entry.get("journal") or entry.get("booktitle") or ""
    year = entry.get("year", "")

    link = entry.get("pdf") or entry.get("url") or ""

    span_id = make_id(key)
    pre_id = f"pre-{span_id}"

    citation = f"{authors}. {title} <i>{venue}, {year}</i>."

    if link:
        link_html = f'<span><a href="{link}">pdf</a></span>'
    else:
        link_html = "<span>(link coming later)</span>"

    html = f"""
<li>
<div class="publicationEntry">
<span id="{span_id}">{citation}</span>

{link_html}
<div onClick="toggle('{pre_id}')" class="bibtexToggle">BibTeX</div>

</div>
<div><pre id="{pre_id}" class="bibtexDisplay">
{entry["raw"]}
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

    with open(bibfile) as f:
        text = f.read()

    entries = parse_bibtex_entries(text)

    if key not in entries:
        print(f"Error: key '{key}' not found")
        sys.exit(1)

    print(generate_html(entries[key], key))


if __name__ == "__main__":
    main()