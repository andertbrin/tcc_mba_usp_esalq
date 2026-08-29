# Force latexmk to use LuaLaTeX so fontspec works.
$pdflatex = 'lualatex %O %S';
# MiKTeX's lualatex (LuaHBTeX) rejects --max-print-line, which latexmk adds by default.
$max_print_line = '';
