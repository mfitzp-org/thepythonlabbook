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

ansi_escape = re.compile(r'\x1b[^m]*m')
STDOUT_DELIMITER = '\n....'
             
REGEXES = [
    # Standard code blocks
    re.compile(r'^\[(?P<config>[^]]*?python[^]]*?)\]\n----\n(?P<code>.*?)\n----$', re.MULTILINE | re.DOTALL),
    # Invisible code blocks (for figure generation)
    re.compile(r'^\[(?P<config>[^]]*?python[^]]*?)\]\n////\n(?P<code>.*?)\n////$', re.MULTILINE | re.DOTALL),

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

    changes = False
    offset = 0
    # Match regex to find code blocks; build match objects
    for rx in REGEXES:
        for mo in rx.finditer(txt):
            changes = True
            cell = NotebookNode(
                cell_type='code',
                input=mo.group('code'),
                metadata={},
                #span=mo.span(),
            )
            blocks.append(cell)
            try:
                runner.run_cell(cell)
                
            except Exception as e:
                pass
                
            if 'stdout' in mo.group('config'):
                stdout = []
                for out in cell.outputs:
                    if hasattr(out, 'text'):
                        stdout.append( out.text )
                        
                output = '\n'.join(stdout)
                
            elif 'stderr' in mo.group('config'):
                stderr = []
                for out in cell.outputs:
                    if hasattr(out, 'traceback'):
                        stderr.append( ansi_escape.sub('', '\n'.join(out.traceback)))
                
                output = '\n'.join(stderr)
                
            else:
                continue # Next block
            
            
            # We want to output the relevant result, whether
            # stdout or stderr. Output is to the subsequent 
            # '....' delimited block (pre).
            
            start, end = mo.span()
            start, end = start+offset, end+offset
            
            if txt[end:end+len(STDOUT_DELIMITER)] == STDOUT_DELIMITER:
                outstart = end+len(STDOUT_DELIMITER)
                outend = txt[end+len(STDOUT_DELIMITER):].index(STDOUT_DELIMITER)+outstart
                
                txt = txt[:outstart+1] + output + txt[outend:]
                
                offset += len(output) +1 # \n

    # If we matched anything we need to rewrite
    if changes:
        with open(file, 'w') as f:
            f.write(txt)
        
    
    

        


