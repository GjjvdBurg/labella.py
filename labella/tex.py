
import os
import shutil
import subprocess
import tempfile
import unicodedata

def uni2tex(text):
    # Courtesy of https://tex.stackexchange.com/q/23410
    accents = {
        0x0300: '`', 0x0301: "'", 0x0302: '^', 0x0308: '"',
        0x030B: 'H', 0x0303: '~', 0x0327: 'c', 0x0328: 'k',
        0x0304: '=', 0x0331: 'b', 0x0307: '.', 0x0323: 'd',
        0x030A: 'r', 0x0306: 'u', 0x030C: 'v',
        }
    out = ""
    txt = tuple(text)
    i = 0
    while i < len(txt):
        char = text[i]
        code = ord(char)

        # combining marks
        if unicodedata.category(char) in ("Mn", "Mc") and code in accents:
            out += "\\%s{%s}" % (accents[code], txt[i+1])
            i += 1
        # precomposed characters
        elif unicodedata.decomposition(char):
            base, acc = unicodedata.decomposition(char).split()
            acc = int(acc, 16)
            base = int(base, 16)
            if acc in accents:
                out += "\\%s{%s}" % (accents[acc], chr(base))
            else:
                out += char
        else:
            out += char
        i += 1
    return out

def get_latex_fontdoc(text, fontsize='11pt', preamble=''):
    tex = r"""\documentclass[preview, {fontsize}]{{standalone}}
{preamble}%
\begin{{document}}
{text}%
\newlength{{\lblwidth}}%
\newlength{{\lblheight}}%
\settowidth{{\lblwidth}}{{{text}}}%
\settoheight{{\lblheight}}{{{text}}}%
\typeout{{LABELWIDTH: \the\lblwidth}}%
\typeout{{LABELHEIGHT: \the\lblheight}}%
\end{{document}}
""".format(fontsize=fontsize, text=uni2tex(text), preamble=uni2tex(preamble))
    return tex

def compile_latex(fname, tmpdirname, silent=True):
    compiler = 'latexmk'
    compiler_args = ['--pdf', '--outdir=' + tmpdirname,
            '--interaction=nonstopmode', fname]
    command = [compiler] + compiler_args
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except (OSError, IOError) as e:
        raise(e)
    except subprocess.CalledProcessError as e:
        print(e.output.decode())
        raise(e)
    else:
        if not silent:
            print(output.decode())

def get_latex_dims(tex, silent=True):
    with tempfile.TemporaryDirectory() as tmpdirname:
        basename = 'labella_text'
        fname = os.path.join(tmpdirname, basename + '.tex')
        with open(fname, 'w') as fid:
            fid.write(tex)

        compile_latex(fname, tmpdirname, silent=silent)

        logname = os.path.join(tmpdirname, basename + '.log')
        with open(logname, 'r') as fid:
            lines = fid.readlines()

        line_width = next((l for l in lines if l.startswith('LABELWIDTH')),
                None)
        line_height = next((l for l in lines if l.startswith('LABELHEIGHT')),
                None)

        width = line_width.strip().split(':')[-1].strip().rstrip('pt')
        height = line_height.strip().split(':')[-1].strip().rstrip('pt')
    return float(width), float(height)

def build_latex_doc(tex, output_name=None, silent=True):
    with tempfile.TemporaryDirectory() as tmpdirname:
        basename = 'labella_text'
        fname = os.path.join(tmpdirname, basename + '.tex')
        with open(fname, 'w') as fid:
            fid.write(tex)

        compile_latex(fname, tmpdirname, silent=silent)

        pdfname = os.path.join(tmpdirname, basename + '.pdf')
        if output_name:
            shutil.copy2(pdfname, output_name)

def text_dimensions(text, fontsize='11pt', preamble='', silent=True):
    tex = get_latex_fontdoc(text, fontsize=fontsize, preamble=preamble)
    width, height = get_latex_dims(tex, silent=silent)
    return width, height
