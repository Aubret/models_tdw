import argparse
import copy
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--src", type=str, default="")
parser.add_argument("--dest", type=str, default="")
args = parser.parse_args()

src=args.src
if args.src == "":
    src = os.environ["TOY_TEX_LIBRARY_PATH"]

dest=args.dest
if args.src == "":
    dest = os.environ["TOY_TEX_LIBRARY_PATH"]



js = json.load(open(str(src)+"/toys.json"))
i= 0
js_copy = copy.deepcopy(js)
for key, val in js["records"].items():
    for platform in ["Linux", "Windows", "Darwin"]:
        new_url = dest + "/" + val["wnid"] + "/" + val["name"] +"/"+ platform
        js_copy["records"][key]["urls"][platform] = "file:///" + new_url

with open(src+"/toys.json", 'w') as f:
    json.dump(js_copy, f)
