import os
import re
import sys

from runipy.notebook_runner import NotebookRunner
from IPython.nbformat import NotebookNode

filter_by = sys.argv[1:2]
if filter_by:
    filter_by = filter_by[0]

"""
Pre-process .doc files to execute code, insert stdout
and re-generate figures from code.
"""
adocs = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".adoc"):
            if not filter_by or filter_by in file:
                adocs.append( os.path.join(root, file) )

ansi_escape = re.compile(r'\x1b[^m]*m')
STDOUT_DELIMITER = '\n....'

REGEXES = [
    # Standard code blocks
    re.compile(r'^\[(?P<config>[^]]*?python[^]]*?)\]\n----\n(?P<code>.*?)\n----$', re.MULTILINE | re.DOTALL),
    # Invisible code blocks (for figure generation)
    re.compile(r'^////\npython\n(?P<code>.*?)\n////$', re.MULTILINE | re.DOTALL),

#    re.compile('^\[[.*python.*]\]\n----(?P<code>.*)----'),
#    re.compile('^\[[.*python.*]\]\n(?P<code>.*)\n\n'),
]

# Create a kernel runner
runner = NotebookRunner(None)

# Iterate list of documents; searching for code blocks and snippets
# using [source,python,  (exec,stdout)
for file in adocs:
    blocks = []
    
    # Make output folder for images
    folder = os.path.join('.','img',os.path.splitext(os.path.basename(file))[0])
    try:
        os.mkdir(folder)
    except OSError:
        pass
    
    with open(file, 'r') as f:
        txt = f.read()

    changes = 0
    offset = 0
    matches = []
    # Match regex to find code blocks; build match objects
    for rx in REGEXES:
        # We need to sort them into order (for comment-exec blocks to be performed in the correct order)
        for mo in rx.finditer(txt):
            matches.append( (mo.span(), mo) )

    if matches:

        matches.sort(key=lambda x: x[0][0])

        for (start, end), mo in matches:
            changes += 1
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

            output = []
            for out in cell.outputs:
                if hasattr(out, 'text'):
                    output.append( out.text )
                if hasattr(out, 'traceback'):
                    output.append( ansi_escape.sub('', '\n'.join(out.traceback)))

            if not output:
                continue

            # Join up then strip trailing newlines.
            output = '\n'.join(output)
            output = output.strip()

            # We want to output the relevant result, whether
            # stdout or stderr. Output is to the subsequent
            # '....' delimited block (pre).

            start, end = start+offset, end+offset

            # Only fill in blocks immediately followed by a container
            if output and txt[end:end+len(STDOUT_DELIMITER)] == STDOUT_DELIMITER:
                outstart = end+len(STDOUT_DELIMITER)
                outend = txt[end+len(STDOUT_DELIMITER):].index(STDOUT_DELIMITER)+outstart
                previous_len = len(txt)
                txt = txt[:outstart+1] + output + txt[outend:]
                offset += len(txt) - previous_len
            else:
                if output:
                    # If there is nowhere for the output to go; display
                    print("Unused output from:")
                    print(mo.group('code'))
                    print("-------------")
                    print(output)
                    print("-------------")

        # If we matched anything we need to rewrite
        if changes:
            with open(file, 'w') as f:
                f.write(txt)

    # Clean up empty folder
    if os.listdir(folder) == []:
        print("DELETING", folder)
        os.rmdir(folder)