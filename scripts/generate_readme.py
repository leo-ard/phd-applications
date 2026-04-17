#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml", "jinja2"]
# ///
"""Generate README.md from _data/directory.yml using a Jinja2 template."""

import re
import yaml
import jinja2
from pathlib import Path


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text


def domain(url):
    """Extract domain from a URL."""
    return url.split("//")[1].split("/")[0]


def is_sequence_not_string(value):
    return isinstance(value, (list, tuple))


def main():
    repo = Path(__file__).parent.parent

    with open(repo / "_config.yml") as f:
        config = yaml.safe_load(f)

    with open(repo / "_data" / "directory.yml") as f:
        data = yaml.safe_load(f)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(repo / "scripts"),
        keep_trailing_newline=True,
    )
    env.filters["slugify"] = slugify
    env.filters["domain"] = domain
    env.tests["sequence_not_string"] = is_sequence_not_string

    template = env.get_template("readme.md.j2")
    readme = template.render(config=config, data=data)
    # Normalize whitespace: collapse 3+ newlines to 2, strip leading/trailing
    readme = re.sub(r"\n{3,}", "\n\n", readme).strip() + "\n"

    out = repo / "README.md"
    out.write_text(readme)
    print(f"Generated {out} ({len(readme)} bytes)")


if __name__ == "__main__":
    main()
