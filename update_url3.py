import argparse
import copy
import json
import os
from pathlib import Path

def modify_canonical_rotation(target, source):
    js = json.load(open(source))
    js_copy_grey = copy.deepcopy(js)
    i= 0
    js_true = json.load(open(target))
    js_copy = copy.deepcopy(js_true)
    for key, val in js["records"].items():
        js_copy["records"][key]["canonical_rotation"] = js_copy_grey["records"][key]["canonical_rotation"]
    with open(target, 'w') as f:
        json.dump(js_copy, f)

modify_canonical_rotation(os.environ["TOY_UTEX_LIBRARY_PATH"] + "/toys.json","./toys_grey.json")
modify_canonical_rotation(os.environ["TOY_TEX_LIBRARY_PATH"] + "/toys.json","./toys_col.json")