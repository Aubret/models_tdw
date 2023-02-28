import argparse
import copy
import json
import os
from pathlib import Path
from tdw.librarian import ModelLibrarian, ModelRecord

def str2table(v):
    return v.split(',')

parser = argparse.ArgumentParser()
parser.add_argument("--directory", type=str, default="../datasets/toys4K_obj_all/")
parser.add_argument("--dest", type=str, default="library2/")
parser.add_argument("--vhacd", type=int, default=10000) #precision of vahcd mesh decomposition, 800 000 the original default
parser.add_argument("--name", type=str2table, default="")
args = parser.parse_args()

src = Path().resolve().joinpath(args.directory).resolve()
dest = Path().resolve().joinpath(args.dest)
file_type="obj"
library_path = dest.joinpath("toys.json")
if not os.path.exists(dest):
    os.mkdir(args.dest)

def create_library(library_path, src) :
    # ModelLibrarian.create_library(description="Toys model librarian", path=str(Path().home().joinpath("postdoc/datasets/toys4k_lib/toys.json")))
    ModelLibrarian.create_library(description="Toys model librarian", path=str(library_path))
    lib = ModelLibrarian(str(library_path.resolve()))
    for f in src.rglob("*."+file_type):
        # if f.name < "chair_144" and f.name > "cupcake_026":
        #     continue

        record = ModelRecord()
        record.name = "".join(list(str(f.name))[:-4])
        if record.name == "":
            pass
        record.wcategory = "".join(list(str(f.name))[:-8])
        record.wnid = record.wcategory
        record.scale_factor = 0.1 if file_type == "fbx" else 0.2
        for platform in record.urls:
            dest_url = dest.joinpath(record.wnid + "/" + record.name + "/" + platform)
            url="file:///" + str(dest_url.resolve()).replace("\\", "/")
            record.urls[platform] = url
        lib.add_or_update_record(record, overwrite=True, write=False)
        # Write to disk.
        lib.write(pretty=False)

def fix_json(library_path):
    with open(str(library_path.resolve()), "r") as f:
        text = list(f.read())
    for i in range(len(text)):
        if text[i] == ",":
            if text[i + 1] != " " and text[i + 1] != "\"":
                text[i] = "."
    fixed_text = "".join(text)
    with open(str(library_path.resolve()), 'w') as f:
        f.write(fixed_text)


create_library(library_path,src)
fix_json(library_path)

js = json.load(open(library_path))
js_copy = copy.deepcopy(js)
to_remove = []
with open("disabled") as f:
    rl = f.readlines()
    for l in rl:
        cat = "".join(list(l)[:-5])
        name = "".join(list(l)[:-1])
        if cat == "":
            continue
        to_remove.append(name)
for name in to_remove:
    if name in js_copy["records"]:
        del js_copy["records"][name]

with open(library_path, 'w') as f:
    json.dump(js_copy, f)
