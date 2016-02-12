



def build_latex_doc(text, fontsize='11pt'):
    tex = r"""
\documentclass[preview, {fontsize}]{{standalone}}
\begin{{document}}
{text}%%\n
\newlength{{\lblwidth}}%%
\newlength{{\lblheight}}%%
\settowidth{{\lblwidth}}{{{text}}}%%
\settoheight{{\lblheight}}{{{text}}}%%
\typeout{{LABELWIDTH: \the\lblwidth}}%%
\typeout{{LABELHEIGHT: \the\lblheight}}%%
\end{{document}}
""".format(fontsize=fontsize, text=text)

def text_dimensions(text):
    pass
