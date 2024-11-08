# The Family Cookbook

## Recipe Organization
*   Recipes should be saved as their own $\TeX$ files.
*   Save each file in the /recipes/ directory.

### Example Recipe File
``` LaTeX
% Apple Pie

% Required arguments are the recipe name and original author.
% Optionally include a brief description. 
\recipe[A is for apple; America's first choice in pie.]{Apple Pie}{Gran}

% Number of servings.
\serves{8--10}

% Prep and cook time.
\preptime{15 minutes}
\cooktime{1 hour}

% Optional functions for more description to include.
% See main tex file for available args.
\dishtype{\vegetarian}

% Ingredient section. \ingredients function is optional if subheadings are needed.
\begin{ingreds}
    \ingredients[For 9'' pie]
        $\frac{3}{4}$--1 cup sugar
        1 tsp cinnamon or nutmeg
        6--7 cups apples (sliced, pared)
        1$\frac{1}{2}$ tbsp butter (melted)
    \ingredients[For 8'' pie]
        $\frac{1}{2}$--$\frac{3}{4}$ cup sugar
        $\frac{3}{4}$ tsp cinnamon or nutmeg
        4--5 cups apples (sliced, pared)
        1 tbsp butter (melted)
\end{ingreds}

% Protocol section. Each step must be separated by a paragraph.
% This is done with \par or a double enter.
\begin{method}[Preheat the oven to \temp{425}.]
    Mix the sugar and cinnamon/nutmeg.\par
    Mix lightly through the apples.\par
    Heat up in pastry-lined pie pan.\par
    Dot with butter.\par
    Cover with top crust which has slits cut in it.\par
    Seal and flute.\par
    Cover edge with a strip of aluminum foil to prevend excessive browning.\par
    Bake 50--60 minutes, or until crust is nicely browned and apples are cooked through (test with a fork).\par
    Serve warm or cold with a heaping scoop of vanilla ice cream.    
\end{method}
```

## Adding recipes to the main document
Within the main body of the document, add the following line which will refer to the recipe file saved in the /recipes/ directory.
``` LaTeX
\input{recipes/apple_pie.tex}
```