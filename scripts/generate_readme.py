#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml"]
# ///
"""Generate README.md from _data/directory.yml."""

import re
import yaml
from pathlib import Path


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text


def _format_deadline(deadline):
    """Format a deadline value (string or list) for README. Returns (prefix, lines)."""
    if not deadline:
        return "❔", []
    if isinstance(deadline, str):
        return deadline, []
    # List of items — return as bullet points
    bullets = []
    for item in deadline:
        if isinstance(item, dict):
            text = item["text"]
            if item.get("url"):
                text += f" — see [{item['url'].split('//')[1].split('/')[0]}]({item['url']})"
            bullets.append(text)
        else:
            bullets.append(str(item))
    return None, bullets


def generate_readme(data, config):
    lines = []
    lines.append(f"# {config['title']}")
    lines.append("")
    lines.append("> **Note:** This file is auto-generated from")
    lines.append("> [`_data/directory.yml`](_data/directory.yml). To make changes,")
    lines.append("> edit the YAML and run `python scripts/generate_readme.py`.")
    lines.append("> See [CONTRIBUTING.md](CONTRIBUTING.md) for details.")
    lines.append("")
    lines.append(config["description"])
    lines.append("")
    page_url = f"https://bodzioney.github.io{config['baseurl']}/"
    lines.append(f"**[Browse the directory online]({page_url})**")
    lines.append("")
    credit_links = ", ".join(
        f"[{c['text']}]({c['url']})" for c in config["credits"]
    )
    lines.append(f"Inspired by and sourced from {credit_links}.")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("")
    for country in data:
        slug = slugify(country["name"])
        lines.append(f"- [{country['name']}](#{slug})")
    lines.append("")

    for country in data:
        lines.append(f"## {country['name']}")
        lines.append("")

        for uni in country.get("universities", []):
            # University heading
            if uni.get("url"):
                lines.append(f"### [{uni['name']}]({uni['url']})")
            else:
                lines.append(f"### {uni['name']}")
            lines.append("")

            # Deadline
            deadline = uni.get("deadline")
            deadline_url = uni.get("deadline_url")
            dl_text, dl_bullets = _format_deadline(deadline)

            if dl_bullets:
                # Multi-item deadline as bullet list
                if deadline_url:
                    lines.append(f"[Application deadline]({deadline_url}):")
                else:
                    lines.append("Application deadline:")
                lines.append("")
                for bullet in dl_bullets:
                    lines.append(f"- {bullet}")
                lines.append("")
            else:
                if deadline_url:
                    lines.append(f"[Application deadline]({deadline_url}): {dl_text}")
                else:
                    lines.append(f"Application deadline: {dl_text}")
                lines.append("")

            # Professors
            for prof in uni.get("professors", []):
                # Name and links
                link_parts = []
                if prof.get("homepage"):
                    link_parts.append(f"[Homepage]({prof['homepage']})")
                if prof.get("scholar"):
                    link_parts.append(f"[Scholar]({prof['scholar']})")
                if prof.get("orcid"):
                    link_parts.append(f"[ORCID]({prof['orcid']})")

                if link_parts:
                    links = " · ".join(link_parts)
                    lines.append(f"**{prof['name']}** — {links}")
                else:
                    lines.append(f"**{prof['name']}**")
                lines.append("")

                # Research
                research = prof.get("research")
                if research:
                    lines.append(f"- Research: {research}")
                else:
                    lines.append("- Research:❔")
                lines.append("")

                # Taking students
                ts = prof.get("taking_students")
                if ts == "yes":
                    lines.append("- Taking students: ✅")
                elif ts == "no":
                    lines.append("- Taking students: ❌")
                else:
                    lines.append("- Taking students:❔")
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    repo = Path(__file__).parent.parent

    with open(repo / "_config.yml") as f:
        config = yaml.safe_load(f)

    with open(repo / "_data" / "directory.yml") as f:
        data = yaml.safe_load(f)

    readme = generate_readme(data, config)
    out = repo / "README.md"
    out.write_text(readme)
    print(f"Generated {out} ({len(readme)} bytes)")


if __name__ == "__main__":
    main()
