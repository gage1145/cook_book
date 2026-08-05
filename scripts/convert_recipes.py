#!/usr/bin/env python3
"""One-time migration: convert latex_src/recipes/*.tex into recipes/<category>/*.qmd.

Reads the section layout (and thus each recipe's category) from
latex_src/cook_book.tex, then parses each recipe file's LaTeX using the
grammar defined in latex_src/cookbook.cls.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEX_SRC = ROOT / "latex_src"
COOKBOOK_TEX = LATEX_SRC / "cook_book.tex"
RECIPES_TEX_DIR = LATEX_SRC / "recipes"
RECIPES_OUT_DIR = ROOT / "recipes"

# ---------------------------------------------------------------------------
# Category metadata: LaTeX color-key -> (display label)
# Keeps the same key names as \definecolor{...color} in cookbook.cls so the
# badge CSS classes (task 5) line up with what this script emits.
# ---------------------------------------------------------------------------
DISH_TYPE_LABELS = {
    "bread": "Bread",
    "apps": "Appetizer",
    "sauce": "Sauce",
    "preserve": "Preserve",
    "pickle": "Pickle",
    "breakfast": "Breakfast",
    "side": "Side",
    "soup": "Soup",
    "main": "Main",
    "dessert": "Dessert",
}
DISH_OTHER_LABELS = {
    "vegetarian": "Vegetarian",
    "freeze": "Freeze",
    "makeahead": "Make Ahead",
}

UNICODE_FRACTIONS = {
    (1, 2): "½", (1, 3): "⅓", (2, 3): "⅔", (1, 4): "¼", (3, 4): "¾",
    (1, 5): "⅕", (2, 5): "⅖", (3, 5): "⅗", (4, 5): "⅘",
    (1, 6): "⅙", (5, 6): "⅚", (1, 8): "⅛", (3, 8): "⅜", (5, 8): "⅝", (7, 8): "⅞",
}

ACCENTS = {
    "'": {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú", "y": "ý",
          "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú"},
    "`": {"a": "à", "e": "è", "i": "ì", "o": "ò", "u": "ù"},
    "^": {"a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û"},
    '"': {"a": "ä", "e": "ë", "i": "ï", "o": "ö", "u": "ü"},
    "~": {"a": "ã", "n": "ñ", "o": "õ"},
    "c": {"c": "ç", "C": "Ç"},
}


def strip_comment_lines(text):
    """Drop whole lines that are LaTeX comments (no inline trailing comments exist)."""
    return "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("%")
    )


def normalize_text(s):
    if s is None:
        return None

    FRAC_MODIFIERS = {None: "", "~": "~", "\\sim": "~", "\\geq": "≥", "\\leq": "≤"}

    def frac_sub(m):
        mod, num, den = m.group(1), int(m.group(2)), int(m.group(3))
        frac = UNICODE_FRACTIONS.get((num, den), f"{num}/{den}")
        return FRAC_MODIFIERS.get(mod, "") + frac

    s = re.sub(r"\$(~|\\sim|\\geq|\\leq)?\\frac\{(\d+)\}\{(\d+)\}\$", frac_sub, s)
    s = re.sub(r"\\temp\{([^}]*)\}", r"\1°F", s)
    s = re.sub(r"\\textsuperscript\{\\textregistered\}", "®", s)
    s = re.sub(r"\\textregistered\{?\}?", "®", s)
    s = re.sub(r"\\texttrademark\{?\}?", "™", s)
    s = re.sub(r"\$\\times\$", "×", s)
    s = re.sub(r"\$\\sim\$", "~", s)
    s = re.sub(r"\$\\geq\$", "≥", s)
    s = re.sub(r"\$\\leq\$", "≤", s)
    s = re.sub(r"\$>\$", ">", s)
    s = re.sub(r"\$<\$", "<", s)
    s = re.sub(r"\\ldots\{?\}?", "…", s)
    s = re.sub(r"\\emph\{([^{}]*)\}", r"*\1*", s)
    s = re.sub(r"\\linebreak\{?\}?", " ", s)

    def accent_sub(m):
        mark, letter = m.group(1), m.group(2)
        return ACCENTS.get(mark, {}).get(letter, letter)

    s = re.sub(r"\\(['`^\"~]|c)\{?([a-zA-Z])\}?", accent_sub, s)

    s = s.replace(r"\&", "&").replace(r"\%", "%").replace(r"\_", "_")
    s = s.replace(r"\@", "")  # LaTeX end-of-sentence marker, no textual meaning
    s = re.sub(r"--", "–", s)
    s = re.sub(r"''", "″", s)
    s = re.sub(r"\\ ", " ", s)  # stray LaTeX control space
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s


def strip_trailing_par(line):
    return re.sub(r"\\par\s*$", "", line).strip()


def slugify(text):
    s = normalize_text(text).lower()
    s = s.replace("&", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ---------------------------------------------------------------------------
# Section layout (category + order) from cook_book.tex
# ---------------------------------------------------------------------------
SECTION_RE = re.compile(r"\\recipeSection\[(?P<image>[^\]]+)\]\{(?P<title>[^}]+)\}")
INPUT_RE = re.compile(r"\\input\{recipes/(?P<name>[^}]+)\.tex\}")


def parse_sections():
    text = strip_comment_lines(COOKBOOK_TEX.read_text(encoding="utf-8"))
    matches = list(SECTION_RE.finditer(text))
    sections = []
    name_to_section = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end]
        names = INPUT_RE.findall(chunk)
        title = normalize_text(m.group("title"))
        slug = slugify(title)
        section = {"slug": slug, "title": title, "image": m.group("image"), "recipes": names}
        sections.append(section)
        for name in names:
            name_to_section[name] = section
    return sections, name_to_section


# ---------------------------------------------------------------------------
# Balanced-brace/bracket argument parsing.
# Regexes like \{(?P<v>[^}]*)\} break on arguments containing nested macros
# such as \preptime{2$\frac{1}{2}$ hours} or \recipe[...]{Spaghetti \emph{with} Meatballs}{...},
# so command arguments are extracted with explicit brace/bracket matching instead.
# ---------------------------------------------------------------------------
def _match_balanced(text, pos, open_ch, close_ch):
    assert text[pos] == open_ch
    depth = 0
    i = pos
    while i < len(text):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return text[pos + 1:i], i + 1
        i += 1
    raise ValueError(f"Unbalanced {open_ch!r} starting at {pos} in: {text[pos:pos+60]!r}")


def find_command(text, name, optional=False, num_braces=1):
    """Find \\name, then parse an optional [..] and num_braces {..} groups.

    Returns (optional_content_or_None, [brace_contents...]) or None if the
    command isn't found or its arguments are absent.
    """
    m = re.search(r"\\" + re.escape(name) + r"(?![a-zA-Z])", text)
    if not m:
        return None
    pos = m.end()
    opt = None
    if optional and pos < len(text) and text[pos] == "[":
        opt, pos = _match_balanced(text, pos, "[", "]")
    braces = []
    for _ in range(num_braces):
        while pos < len(text) and text[pos] in " \t\n":
            pos += 1
        if pos >= len(text) or text[pos] != "{":
            break
        content, pos = _match_balanced(text, pos, "{", "}")
        braces.append(content)
    return opt, braces


INGREDS_RE = re.compile(r"\\begin\{ingreds\}(?P<body>.*?)\\end\{ingreds\}", re.DOTALL)
METHOD_BODY_RE = re.compile(r"\\begin\{method\}(?P<rest>.*?)\\end\{method\}", re.DOTALL)
INGREDIENTS_HEADING_RE = re.compile(r"^\\ingredients(?:\[(?P<heading>[^\]]*)\])?\s*$")
SUBMETHOD_RE = re.compile(r"^\\submethod\{(?P<heading>[^}]*)\}\s*$")


def parse_ingredient_groups(body):
    groups = []
    heading, items = None, []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = INGREDIENTS_HEADING_RE.match(line)
        if m:
            if items or heading is not None:
                groups.append((heading, items))
            heading, items = m.group("heading"), []
            continue
        if line.startswith("\\columnbreak") or line.startswith("\\smallbreak"):
            continue
        items.append(normalize_text(strip_trailing_par(line)))
    if items or heading is not None:
        groups.append((heading, items))
    return [(normalize_text(h) if h else None, i) for h, i in groups if i]


def parse_method_groups(body):
    groups = []
    heading, steps = None, []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = SUBMETHOD_RE.match(line)
        if m:
            if steps or heading is not None:
                groups.append((heading, steps))
            heading, steps = m.group("heading"), []
            continue
        # A line can contain more than one step separated by a mid-line \par,
        # not just a trailing one (e.g. "...cool.\par Repeat with the...\par").
        for chunk in re.split(r"\\par\b", line):
            step = normalize_text(chunk.strip())
            if step:
                steps.append(step)
    if steps or heading is not None:
        groups.append((heading, steps))
    return [(normalize_text(h) if h else None, s) for h, s in groups if s]


def parse_recipe(tex_path):
    raw = strip_comment_lines(tex_path.read_text(encoding="utf-8"))

    recipe_args = find_command(raw, "recipe", optional=True, num_braces=2)
    if not recipe_args or len(recipe_args[1]) < 2:
        raise ValueError(f"No \\recipe{{}} found in {tex_path}")
    desc, (title, author) = recipe_args

    serves_args = find_command(raw, "serves", num_braces=1)
    preptime_args = find_command(raw, "preptime", optional=True, num_braces=1)
    cooktime_args = find_command(raw, "cooktime", optional=True, num_braces=1)
    dishtype_args = find_command(raw, "dishtype", num_braces=1)
    dishother_args = find_command(raw, "dishother", num_braces=1)
    showit_args = find_command(raw, "showit", optional=True, num_braces=2)

    ingreds_m = INGREDS_RE.search(raw)
    method_m = METHOD_BODY_RE.search(raw)
    prestep = None
    method_body = ""
    if method_m:
        rest = method_m.group("rest")
        if rest.lstrip().startswith("["):
            lead_ws = len(rest) - len(rest.lstrip())
            prestep, after_pos = _match_balanced(rest, lead_ws, "[", "]")
            method_body = rest[after_pos:]
        else:
            method_body = rest

    if not dishtype_args:
        print(f"  WARNING: {tex_path.name} missing \\dishtype")
    if not ingreds_m:
        print(f"  WARNING: {tex_path.name} missing ingreds block")
    if not method_m:
        print(f"  WARNING: {tex_path.name} missing method block")

    dish_type = dishtype_args[1][0].lstrip("\\") if dishtype_args and dishtype_args[1] else None
    dish_other = dishother_args[1][0].lstrip("\\") if dishother_args and dishother_args[1] else None
    if dish_other == "":
        dish_other = None

    return {
        "title": normalize_text(title),
        "author": normalize_text(author),
        "description": normalize_text(desc),
        "serves": normalize_text(serves_args[1][0]) if serves_args and serves_args[1] else None,
        "preptime_label": normalize_text(preptime_args[0]) if preptime_args and preptime_args[0] else "Prep time",
        "preptime": normalize_text(preptime_args[1][0]) if preptime_args and preptime_args[1] else None,
        "cooktime_label": normalize_text(cooktime_args[0]) if cooktime_args and cooktime_args[0] else "Cook time",
        "cooktime": normalize_text(cooktime_args[1][0]) if cooktime_args and cooktime_args[1] else None,
        "dish_type": dish_type,
        "dish_other": dish_other,
        "ingredient_groups": parse_ingredient_groups(ingreds_m.group("body")) if ingreds_m else [],
        "prestep": normalize_text(prestep),
        "method_groups": parse_method_groups(method_body),
        "showit": {
            "width": (showit_args[0] or "1in") if showit_args else "1in",
            "image": showit_args[1][0].strip(),
            "caption": normalize_text(showit_args[1][1]),
        } if showit_args and len(showit_args[1]) >= 2 else None,
    }


# ---------------------------------------------------------------------------
# .qmd rendering
# ---------------------------------------------------------------------------
def yaml_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def render_qmd(recipe, section):
    categories = []
    badges = []
    if recipe["dish_type"]:
        label = DISH_TYPE_LABELS.get(recipe["dish_type"], recipe["dish_type"].title())
        categories.append(label)
        badges.append((label, recipe["dish_type"]))
    if recipe["dish_other"]:
        label = DISH_OTHER_LABELS.get(recipe["dish_other"], recipe["dish_other"].title())
        categories.append(label)
        badges.append((label, recipe["dish_other"]))

    image = f"/{recipe['showit']['image']}" if recipe["showit"] else f"/{section['image']}"

    lines = ["---"]
    lines.append(f'title: "{yaml_escape(recipe["title"])}"')
    lines.append(f'author: "{yaml_escape(recipe["author"])}"')
    if recipe["description"]:
        lines.append(f'description: "{yaml_escape(recipe["description"])}"')
    if categories:
        cat_list = ", ".join(f'"{yaml_escape(c)}"' for c in categories)
        lines.append(f"categories: [{cat_list}]")
    lines.append(f'image: "{image}"')
    lines.append("---")
    lines.append("")

    # Meta block
    lines.append('::: {.recipe-meta}')
    meta_lines = []
    if recipe["serves"]:
        meta_lines.append(f'**Serves:** {recipe["serves"]}')
    if recipe["preptime"]:
        meta_lines.append(f'**{recipe["preptime_label"]}:** {recipe["preptime"]}')
    if recipe["cooktime"]:
        meta_lines.append(f'**{recipe["cooktime_label"]}:** {recipe["cooktime"]}')
    for i, meta_line in enumerate(meta_lines):
        suffix = "\\" if i < len(meta_lines) - 1 else ""
        lines.append(meta_line + suffix)
    if badges:
        lines.append("")
        lines.append(" ".join(f'[{label}]{{.badge .badge-{slug}}}' for label, slug in badges))
    lines.append(":::")
    lines.append("")

    if recipe["description"]:
        lines.append(f'*{recipe["description"]}*')
        lines.append("")

    # Ingredients
    lines.append("## Ingredients")
    lines.append("")
    groups = recipe["ingredient_groups"]
    if len(groups) == 1 and groups[0][0] is None:
        for item in groups[0][1]:
            lines.append(f"- {item}")
        lines.append("")
    else:
        for heading, items in groups:
            if heading:
                lines.append(f"### {heading}")
                lines.append("")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    # Instructions
    lines.append("## Instructions")
    lines.append("")
    if recipe["prestep"]:
        lines.append(f'*{recipe["prestep"]}*')
        lines.append("")
    step_num = 1
    for heading, steps in recipe["method_groups"]:
        if heading:
            lines.append(f"### {heading}")
            lines.append("")
        for i, step in enumerate(steps):
            lines.append(f"{step_num}. {step}")
            step_num += 1
        lines.append("")

    # Inline image
    if recipe["showit"]:
        lines.append(f'![{recipe["showit"]["caption"]}](/{recipe["showit"]["image"]}){{width="{recipe["showit"]["width"]}"}}')
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    sections, name_to_section = parse_sections()
    RECIPES_OUT_DIR.mkdir(exist_ok=True)

    tex_files = sorted(RECIPES_TEX_DIR.glob("*.tex"))
    written = 0
    for tex_path in tex_files:
        name = tex_path.stem
        section = name_to_section.get(name)
        if section is None:
            print(f"  WARNING: {tex_path.name} not referenced in cook_book.tex, skipping")
            continue
        recipe = parse_recipe(tex_path)
        qmd = render_qmd(recipe, section)
        out_dir = RECIPES_OUT_DIR / section["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name}.qmd"
        out_path.write_text(qmd, encoding="utf-8")
        written += 1

    print(f"\nWrote {written} of {len(tex_files)} recipe files across {len(sections)} sections.")


if __name__ == "__main__":
    main()
