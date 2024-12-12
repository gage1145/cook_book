\ProvidesClass{cookbook}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass{article}

\RequirePackage{enumitem}
\RequirePackage{fancyhdr}
\RequirePackage{multicol}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{caption}
\RequirePackage{float}
\RequirePackage[
    papersize={5.5in,8.5in},
    margin=0.75in,
    top=0.75in,
    bottom=0.75in,
    twoside
]{geometry}


\newif\if@mainmatter{}\@mainmattertrue{}

\setlength{\headheight}{14.0pt}

\raggedcolumns{}
\setlength{\multicolsep}{0pt}
\setlength{\columnseprule}{1pt}

\makeatletter

% Decide if you want numbered sections or not.
\setcounter{secnumdepth}{0}

% Used for the headnote and in \showit
% If the text is small it is placed on one line;
% otherwise it is put into a raggedright paragraph.
\long\def\testoneline#1{%
  \sbox\@tempboxa{#1}%
  \ifdim\wd\@tempboxa<0.75 \linewidth{}
        \begingroup
            \itshape{}
            #1\par
        \endgroup
  \else
    \parbox{0.75\linewidth}{\raggedright\itshape#1}
    \par
  \fi
}

%% temporary titles
% command to provide stretchy vertical space in proportion
\newcommand\nbvspace[1][3]{\vspace*{\stretch{#1}}}

% allow some slack to avoid under/overfull boxes
% \newcommand\nbstretchyspace{\spaceskip0.5em plus 0.25em minus 0.25em}
% To improve spacing on title pages
\newcommand{\nbtitlestretch}{\spaceskip0.6em}

% Borrowed from book.cls
\newcommand\frontmatter{%
    \cleardoublepage{}
  \@mainmatterfalse{}
  \pagenumbering{roman}
}
\newcommand\mainmatter{%
    \cleardoublepage{}
  \@mainmattertrue{}
  \pagenumbering{arabic}
}
\makeatother

% Vary the colors at will
% \dishother colors
\definecolor{vegcolor}{rgb}{0,0.4,0.2}
\definecolor{frzcolor}{rgb}{0,0,1}
\definecolor{makeaheadcolor}{rgb}{0.5,0.5,0.5}

% \dishtype colors
\definecolor{breadcolor}    {rgb}{0.5, 0.1, 0.2}
\definecolor{appcolor}      {rgb}{0.2, 0.05, 0.5}
\definecolor{saucecolor}    {rgb}{0.2, 0.5, 0.1}
\definecolor{preservecolor} {rgb}{0.0, 0.2, 0.4}
\definecolor{picklecolor}   {rgb}{0.0, 0.5, 0.1}
\definecolor{breakfastcolor}{rgb}{0.4, 0.2, 0.1}
\definecolor{sidecolor}     {rgb}{0.2, 0.5, 0.5}
\definecolor{soupcolor}     {rgb}{0, 0.05, 0.4}
\definecolor{maincolor}     {rgb}{0.5, 0.0, 0.05}
\definecolor{dessertcolor}  {rgb}{0.5, 0.2, 0.1}
\definecolor{methodcolor}   {rgb}{0.7, 0, 0}

%% Thanks to alephzero for the excellent start:
\newcommand{\recipe}[3][]{
    \newpage
    \thispagestyle{fancy}
    \lhead{}
    \chead{}
    \rhead{}
    \lfoot{}
    \rfoot{}
    \subsection[#2]{\Large#2 $-$ \large#3}
    \if###1##
    \else
        \begin{center}
            \testoneline{#1}
        \end{center}
    \fi
}

% Recipe header commands
\newcommand{\serves}[1]{\chead{Serves #1}}
\newcommand{\dishtype}[1]{\rhead{#1}}
\newcommand{\dishother}[1]{\lhead{#1}}

% dishother inputs
\newcommand{\vegetarian}{\large\color{vegcolor}\textbf{Vegetarian}}
\newcommand{\freeze}{\large\color{frzcolor}\textbf{Freeze}}
\newcommand{\makeahead}{\large\color{makeaheadcolor}\textbf{Make ahead}}

% dishtype inputs
\newcommand{\bread}{\large\color{breadcolor}\textbf{Bread}}
\newcommand{\apps}{\large\color{appcolor}\textbf{Appetizer}}
\newcommand{\sauce}{\large\color{saucecolor}\textbf{Sauce}}
\newcommand{\preserve}{\large\color{preservecolor}\textbf{Preserve}}
\newcommand{\pickle}{\large\color{picklecolor}\textbf{Pickle}}
\newcommand{\breakfast}{\large\color{breakfastcolor}\textbf{Breakfast}}
\newcommand{\side}{\large\color{sidecolor}\textbf{Side}}
\newcommand{\soup}{\large\color{soupcolor}\textbf{Soup}}
\newcommand{\main}{\large\color{maincolor}\textbf{Main}}
\newcommand{\dessert}{\large\color{dessertcolor}\textbf{Dessert}}

% Optional arguments for alternate names for these:
\newcommand{\preptime}[2][Prep time]{\lfoot{#1: #2}}
\newcommand{\cooktime}[2][Cook time]{\rfoot{#1: #2}}
\newcommand{\temp}[1]{$#1^\circ$F}

%% Optional argument is the width of the graphic, default = 1in
\newcommand{\showit}[3][1in]{
    \begin{figure}[H]
        \centering
        \includegraphics[width=#1]{#2}
        \caption*{\emph{#3}}
    \end{figure}

    % \begin{center}
    %     \bigskip
    %         \includegraphics[width=#1]{#2}
    %         \par
    %         \medskip
    %         \testoneline{#3}
    %         \par
    % \end{center}
}

%% Optional argument for a  heading within the ingredients section
\newcommand{\ingredients}[1][]{%
    \if###1##{
        \color{methodcolor}\Large\textbf{Ingredients}
    }
    \else
        \emph{\textbf{#1:}}
    \fi
}

\newcommand{\recipeSection}[2][]{
    \clearpage
    \begin{center}
        \hspace{0pt}\vfill
        \begin{minipage}{\textwidth}
            \centering
            \section[#2]{\fontsize{24.88pt}{24.88pt}\selectfont #2}
            \includegraphics[width=3in]{#1}
        \end{minipage}  
        \vfill\hspace{0pt}
    \end{center}
    \clearpage
}

%% Use \obeylines to minimize markup
\newenvironment{ingreds}{
    \parindent0pt
    \noindent
    \ingredients{}
    \par
    \smallskip
    \begin{multicols}{2}
    \leftskip1em
    \rightskip0pt plus 3em
    \parskip=0.25em
    \obeylines{}
    \everypar={\hangindent2em}
}{
    \end{multicols}
    \medskip
}

\newcounter{stepnum}

%% Optional argument for an italicized pre-step
%% Also use obeylines to minimize markup here as well
\newenvironment{method}[1][]{
    \setcounter{stepnum}{0}
    \noindent
    {\color{methodcolor}\Large\textbf{Instructions}}
    \par
    \smallskip
    \if#1
    \else
        \noindent
        \emph{#1}
        \par
    \fi
    \begingroup
    \parindent0pt
    \parskip0.25em
        \leftskip2em
    \everypar={\llap{\ensuremath{\stepcounter{stepnum}\hbox to2em{\thestepnum.\hfill}}}}
}{
    \par
    \endgroup
}

\newcommand{\submethod}[1]{
    \par
    \begingroup
    \medskip\leftskip-0.2em
    \everypar={}
    \textbf{#1}
    \par
    \endgroup
}

\AtBeginDocument{
  \pagestyle{plain}
}