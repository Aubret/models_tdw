import argparse
import os
from json import loads
from pathlib import Path
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.librarian import ModelLibrarian, ModelRecord

#Delete things before regeneration

# src = Path().home().joinpath("postdoc/datasets/toys4k_fbx/").resolve()
parser = argparse.ArgumentParser()
parser.add_argument("--fbx_directory", type=str, default="toys4K_fbx_one/")
parser.add_argument("--dest", type=str, default="library/")
parser.add_argument("--vhacd", type=int, default=800000) #precision of vahcd mesh decomposition
args = parser.parse_args()

src = Path().resolve().joinpath(args.fbx_directory).resolve()
dest = Path().resolve().joinpath(args.dest)
file_type="fbx"
library_path = dest.joinpath("toys.json")

def create_library() :
    # ModelLibrarian.create_library(description="Toys model librarian", path=str(Path().home().joinpath("postdoc/datasets/toys4k_lib/toys.json")))
    ModelLibrarian.create_library(description="Toys model librarian", path=str(library_path))
    lib = ModelLibrarian(str(library_path.resolve()))
    for f in src.rglob("*."+file_type):
        record = ModelRecord()
        record.name = "".join(list(str(f.name))[:-4])
        record.wcategory = "".join(list(str(f.name))[:-8])
        record.wnid = record.wcategory
        record.scale_factor = 0.1
        for platform in record.urls:
            dest_url = dest.joinpath(record.wnid + "/" + record.name + "/" + platform)
            url="file:///" + str(dest_url.resolve()).replace("\\", "/")
            record.urls[platform] = url
        lib.add_or_update_record(record, overwrite=True, write=False)
        # Write to disk.
        lib.write(pretty=False)

a = AssetBundleCreator(display=":1")

create_library()
lib = ModelLibrarian(str(library_path.resolve()))
for record in lib.records:
    a.move_files_to_unity_project(None, model_path=src.joinpath(f"{record.name}."+file_type), sub_directory=f"models/{record.name}")
a.create_many_asset_bundles(str(library_path.resolve()), vhacd_resolution=args.vhacd, cleanup=True)


with open(str(library_path.resolve()),"r") as f:
    text = list(f.read())
for i in range(len(text)):
    if text[i] == ",":
        if text[i + 1] != " " and text[i + 1] != "\"":
            text[i] = "."
fixed_text = "".join(text)
with open(str(library_path.resolve()), 'w') as f:
    f.write(fixed_text)

files_in_directory = os.listdir("./")
mtls = [file for file in files_in_directory if file.endswith(".mtl")]
for file in mtls:
    os.remove(str(Path().resolve().joinpath(file)))

