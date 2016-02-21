
import errno
import os
import tempfile
import subprocess

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
    return tex

def compile_latex_doc(tex, silent=True):
    with tempfile.TemporaryDirectory() as tmpdirname:
        basename = 'labella_text'
        fname = os.path.join(tmpdirname, basename + '.tex')
        with open(fname, 'w') as fid:
            fid.write(tex)
        compiler = 'latexmk'
        compiler_args = ['--pdf', '--outdir=' + tmpdirname, 
                '--interaction=nonstopmode', fname]
        command = [compiler] + compiler_args
        try:
            output = subprocess.check_output(command, 
                    stderr=subprocess.STDOUT)
        except (OSError, IOError) as e:
            raise(e)
        except subprocess.CalledProcessError as e:
            print(e.output.decode())
            raise(e)
        else:
            if not silent:
                print(output.decode())
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

def text_dimensions(text, fontsize='11pt', silent=True):
    tex = build_latex_doc(text, fontsize=fontsize)
    width, height = compile_latex_doc(tex, silent=silent)
    return width, height
