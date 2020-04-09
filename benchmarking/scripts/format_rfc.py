#!/usr/bin/env python3

import argparse
import re

SECTION_HEADERS = (
    "Abstract",
    "Status of This Memo",
    "Copyright Notice",
    "Table of Contents",
    "Acknowledgements",
    "Authors' Addresses",
)

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Filename of Internet-Draft to format")
parser.add_argument("-w", "--write", action="store_true", help="Write file in place")

args = parser.parse_args()

with open(args.file) as f:
    text = f.read()


def wrap_paragraph(content):
    lines = []
    line = ""
    for match in re.finditer(r"\s*\S*", content):
        part = match.group(0)
        if len(line) + len(part) > 70:
            lines.append(line)
            line = ""
        if not line:
            part = part.lstrip()
        line += part
    if line:
        lines.append(line)
    return "\n".join("  " + line for line in lines)


def break_into_pages(all_lines):
    parts = []
    part = []
    for line in all_lines:
        if line:
            part.append(line)
        else:
            if part:
                parts.append(part)
            part = []
    if part:
        parts.append(part)
    pages = []
    page = []
    for idx, part in enumerate(parts):
        new_page = list(page)
        if new_page:
            new_page.append("")
        new_page.extend(part)
        # Spill to next page if necessary, and avoid orphaned section
        # headers.
        if len(new_page) > 58 or (
            len(part) == 1
            and (re.match(r"[0-9]+\.", part[0]) or part[0] in SECTION_HEADERS)
            and len(new_page) + 1 + len(parts[idx + 1]) > 58
        ):
            pages.append(page)
            page = part
        else:
            page = new_page
    if page:
        pages.append(page)
    return pages


formatted_lines = []
state = "header"
for line in text.splitlines():
    if state == "header":
        if not line:
            state = "title"
        else:
            line = line.rjust(72)
    elif state == "title":
        if not line:
            state = "body"
        else:
            line = line.center(72)
    elif state == "body":
        if line == "-- Notes --":
            break
        if (
            not re.match(r" *[0-9]+\.", line)
            and not re.match(r" ", line)
            and line not in SECTION_HEADERS
        ):
            line = wrap_paragraph(line)
    if line:
        formatted_lines.extend(line.splitlines())
    else:
        formatted_lines.append(line)

pages = break_into_pages(formatted_lines)
formatted_text = "\n\f\n".join("\n".join(page) for page in pages).strip() + "\n"

if args.write:
    with open(args.file, "w") as f:
        f.write(formatted_text)
else:
    print(formatted_text, end="")
