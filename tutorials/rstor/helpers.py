from pathlib import Path
import json

import sysconfig
extension_suffix = sysconfig.get_config_var('EXT_SUFFIX')
pydist, pyver, os_so = extension_suffix.split('-')
os,soext = os_so.split('.')

# from et_rstor import *

_write = True

pickled =  Path(__file__).parent / 'heading_numbers.json'

def process(doc):
    doc.verbose = True
    if _write:
        doc.write(Path.home() / 'workspace/et-micc2/tutorials/')
    else:
        print(f'$$$$$$\n{doc}\n$$$$$$')

    with pickled.open(mode='w') as f:
        json.dump(doc.heading_numbers,f)


workspace = Path() / '../tutorials-workspace-tmp'
snippets = Path(__file__).parent / 'snippets'
