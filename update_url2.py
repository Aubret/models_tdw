import argparse
import copy
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--type", type=str, default="scenes")#models, materials
args = parser.parse_args()


current = os.environ["LOCAL_BUNDLES"]+"local_asset_bundles/"
extension=args.type+".json"

js = json.load(open(str(current)+extension))
i= 0
js_copy = copy.deepcopy(js)
for key, val in js["records"].items():
    for platform in ["Linux", "Windows", "Darwin"]:
        new_url = current +args.type+"/" + val["name"]

with open(current+extension, 'w') as f:
    json.dump(js_copy, f)
