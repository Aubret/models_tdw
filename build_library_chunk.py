import argparse
import os
from json import loads
from pathlib import Path
from subprocess import call

from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.librarian import ModelLibrarian, ModelRecord

#Delete things before regeneration
def str2table(v):
    return v.split(',')
# src = Path().home().joinpath("postdoc/datasets/toys4k_fbx/").resolve()
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



def create_library() :
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

def fix_json():
    with open(str(library_path.resolve()), "r") as f:
        text = list(f.read())
    for i in range(len(text)):
        if text[i] == ",":
            if text[i + 1] != " " and text[i + 1] != "\"":
                text[i] = "."
    fixed_text = "".join(text)
    with open(str(library_path.resolve()), 'w') as f:
        f.write(fixed_text)


a = AssetBundleCreator(display=":1")

# if args.name == "":
create_library()
lib = ModelLibrarian(str(library_path.resolve()))

# if args.name == "":
i=0
for record in lib.records:
    if ( args.name[0] != "" or record.name not in args.name ) and os.path.isdir(args.dest+record.wcategory+"/"+record.name):
        continue
    i=i+1
    a.move_files_to_unity_project(None, model_path=src.joinpath(f"{record.wcategory}/{record.name}/{record.name}.{file_type}"), sub_directory=f"models/{record.name}")
    if i%50 == 0:
        a.create_many_asset_bundles(str(library_path.resolve()), vhacd_resolution=args.vhacd, cleanup=True)
        fix_json()
a.create_many_asset_bundles(str(library_path.resolve()), vhacd_resolution=args.vhacd, cleanup=True)
fix_json()


files_in_directory = os.listdir("./")
mtls = [file for file in files_in_directory if file.endswith(".mtl")]
for file in mtls:
    os.remove(str(Path().resolve().joinpath(file)))

