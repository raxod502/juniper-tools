#!/usr/bin/env python3

import argparse
import datetime
import re
import sys

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
    for match in re.finditer(r"\S*\s*\S*", content):
        part = match.group(0)
        if len(line) + len(part) > 69:
            lines.append(line)
            line = ""
        if lines and not line:
            part = part.lstrip()
        line += part
    if line:
        lines.append(line)
    return "\n".join("   " + line for line in lines)


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
            idx < len(parts) - 1
            and (
                len(part) == 1
                and (re.match(r"[0-9]+\.", part[0]) or part[0] in SECTION_HEADERS)
                or re.match(r" *EMail:", parts[idx + 1][0])
            )
            and len(new_page) + 1 + len(parts[idx + 1]) > 58
        ):
            pages.append(page)
            page = part
        else:
            page = new_page
    if page:
        pages.append(page)
    return pages


def find_sections(pages):
    sections = {}
    for page_num, page in enumerate(pages, 1):
        for line in page:
            match = re.match(r"((?:[0-9]+\.)+) +(.+)", line)
            if match:
                sections[match.group(1)] = (page_num, match.group(2))
    return sections


def format_toc(pages, sections):
    for page in pages:
        for idx, line in enumerate(page):
            match = re.match(r" *((?:[0-9]+\.)+) ([^ ].*)$", line)
            if match:
                page_num, sec_name = sections[match.group(1)]
                if match.group(2) != sec_name:
                    raise ValueError(
                        f"mismatched name in TOC for section {repr(match.group(1))}"
                        f" (expected {repr(sec_name)}, got {repr(match.group(2))})"
                    )
                line = (" " * 3) + line + " "
                suffix = str(page_num)
                line += "." * (72 - len(line + suffix))
                line += suffix
                page[idx] = line


def substitute_expiry(pages):
    for page in pages:
        for idx, line in enumerate(page):
            match = re.fullmatch(r"Expires: \[DATE\] +(.+)", line)
            if match:
                expiry = (
                    datetime.date.today() + datetime.timedelta(days=185)
                ).strftime("%B %-d, %Y")
                lhs = f"Expires: {expiry}"
                rhs = match.group(1)
                padding = " " * (72 - len(lhs + rhs))
                page[idx] = lhs + padding + rhs


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
        if not re.match(r" *[0-9]+\.", line) and line not in SECTION_HEADERS:
            line = wrap_paragraph(line)
    if line:
        formatted_lines.extend(line.splitlines())
    else:
        formatted_lines.append(line)

pages = break_into_pages(formatted_lines)
format_toc(pages, find_sections(pages))
substitute_expiry(pages)
formatted_text = "\n\f\n".join("\n".join(page) for page in pages).strip() + "\n"

if args.write:
    with open(args.file, "w") as f:
        f.write(formatted_text)
else:
    print(formatted_text, end="")
