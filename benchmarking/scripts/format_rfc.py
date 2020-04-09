#!/usr/bin/env python3

import argparse
import re

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


formatted_lines = []
state = "header"
for line in text.splitlines():
    if state == "header":
        if not line:
            state = "title"
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
            and line
            not in (
                "Abstract",
                "Status of This Memo",
                "Copyright Notice",
                "Table of Contents",
                "Acknowledgements",
                "Authors' Addresses",
            )
        ):
            line = wrap_paragraph(line)
    formatted_lines.append(line)

formatted_text = "".join(l + "\n" for l in formatted_lines)

if args.write:
    with open(args.file, "w") as f:
        f.write(formatted_text)
else:
    print(formatted_text, end="")
