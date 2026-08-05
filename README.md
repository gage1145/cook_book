# The Family Cookbook

A Quarto website. The original LaTeX book (`latex_src/`) is archived and no longer the primary workflow.

## Recipe Organization
*   Recipes are saved as their own `.qmd` files.
*   Save each file in `recipes/<category>/`, where `<category>` is one of the existing folders (`breads-baked-goods`, `appetizers-snacks`, `sauces-jams-canned-goods`, `breakfast`, `side-dishes`, `soups`, `mains`, `desserts`) or a new one if it doesn't fit.
*   The `recipes.qmd` listing page picks up every `.qmd` under `recipes/` automatically — no need to register new recipes anywhere else.

### Example Recipe File
```markdown
---
title: "Apple Pie"
author: "Gran"
description: "A is for apple…America's first choice in pie."
categories: ["Dessert", "Vegetarian"]
image: "/images/dessert.png"
---

::: {.recipe-meta}
**Serves:** 8–10\
**Prep time:** 15 minutes\
**Cook time:** 1 hour

[Dessert]{.badge .badge-dessert} [Vegetarian]{.badge .badge-vegetarian}
:::

*A is for apple…America's first choice in pie.*

## Ingredients

### For 9″ pie

- ¾–1 cup sugar
- 1 tsp cinnamon or nutmeg
- 6–7 cups apples (sliced, pared)
- 1½ tbsp butter (melted)

### For 8″ pie

- ½–¾ cup sugar
- ¾ tsp cinnamon or nutmeg
- 4–5 cups apples (sliced, pared)
- 1 tbsp butter (melted)

## Instructions

*Preheat the oven to 425°F.*

1. Mix the sugar and cinnamon/nutmeg.
2. Mix lightly through the apples.
3. Heat up in pastry-lined pie pan.
4. Dot with butter.
5. Cover with top crust which has slits cut in it.
6. Seal and flute.
7. Cover edge with a strip of aluminum foil to prevent excessive browning.
8. Bake 50–60 minutes, or until crust is nicely browned and apples are cooked through (test with a fork).
9. Serve warm or cold with a heaping scoop of vanilla ice cream.
```

Notes:
*   `categories` drives both the badge colors and the filter list on the Recipes page. Available badge classes (`badge-<slug>`) are defined in `styles.css`: dish types (`bread`, `apps`, `sauce`, `preserve`, `pickle`, `breakfast`, `side`, `soup`, `main`, `dessert`) and dish traits (`vegetarian`, `freeze`, `makeahead`).
*   `image` is shown as the card thumbnail on the Recipes listing page; reuse one of the existing section images in `images/` unless the recipe has its own photo.
*   Ingredient/instruction subheadings (`### Heading`) are optional — omit them for a flat list.
*   Numbered instruction steps can use explicit start numbers (e.g. `4. ...`) to keep numbering continuous across subheadings.

## Rendering the site
```
quarto preview
```
or
```
quarto render
```

## Legacy LaTeX build
The original LaTeX sources are preserved under `latex_src/` for reference and can still be built into a PDF with a standard LaTeX toolchain (`latexmk latex_src/cook_book.tex`), but they are not kept in sync with `recipes/` going forward. `scripts/convert_recipes.py` was the one-time script used to migrate `latex_src/recipes/*.tex` into `recipes/*.qmd`.
