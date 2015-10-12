import os
import re

from runipy.notebook_runner import NotebookRunner
from IPython.nbformat import NotebookNode

"""
Pre-process .doc files to execute code, insert stdout
and re-generate figures from code.
"""
adocs = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".adoc"):
             adocs.append( os.path.join(root, file) )
             
             
REGEXES = [
    re.compile(r'^\[[^]]*?python[^]]*?\]\n----\n(?P<code>.*?)\n----$', re.MULTILINE | re.DOTALL),
#    re.compile('^\[[.*python.*]\]\n----(?P<code>.*)----'),
#    re.compile('^\[[.*python.*]\]\n(?P<code>.*)\n\n'),
]             

# Create a kernel runner
runner = NotebookRunner(None)
             
# Iterate list of documents; searching for code blocks and snippets
# using [source,python,  (exec,stdout)
for file in adocs:

    blocks = []
    print(file)
    with open(file, 'r') as f:
        txt = f.read()

    matches = []
    # Match regex to find code blocks; build match objects
    for rx in REGEXES:
        for mo in rx.finditer(txt):
            cell = NotebookNode(
                cell_type='code',
                input=mo.group('code'),
                metadata={},
                span=mo.span(),
            )
            blocks.append(cell)
            try:
                runner.run_cell(cell)
            except:
                pass
            for out in cell.outputs:
                print(">>> %s" % cell.input)
                if hasattr(out, 'text'):
                    print(out.text)

    
    

        

