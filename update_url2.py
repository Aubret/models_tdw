import argparse
import copy
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--dest", type=str, default="")#models, materials
args = parser.parse_args()

jsons = ["hdri_skyboxes.json", "materials.json", "models.json", "scenes.json"]

for extension in jsons:
    current = os.environ["LOCAL_BUNDLES"]+"local_asset_bundles/" if args.dest == "" else args.dest
    # extension=args.type+".json"
    type = extension.split(".")[0]

    js = json.load(open(str(current)+extension))
    i= 0
    js_copy = copy.deepcopy(js)
    for key, val in js["records"].items():
        for platform in ["Linux", "Windows", "Darwin"]:
            new_url = current +type+"/" + val["name"]
            js_copy["records"][key]["urls"][platform] = "file:///" + new_url

    with open(current+extension, 'w') as f:
        json.dump(js_copy, f)
