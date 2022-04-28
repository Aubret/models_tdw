import argparse
import os
from json import loads
from pathlib import Path
from subprocess import call

from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.librarian import ModelLibrarian, ModelRecord

#Delete things before regeneration

# src = Path().home().joinpath("postdoc/datasets/toys4k_fbx/").resolve()
parser = argparse.ArgumentParser()
parser.add_argument("--directory", type=str, default="../datasets/toys4K_obj_all/")
parser.add_argument("--dest", type=str, default="library2/")
parser.add_argument("--vhacd", type=int, default=4000) #precision of vahcd mesh decomposition, 800 000 the original default
args = parser.parse_args()

src = Path().resolve().joinpath(args.directory).resolve()
dest = Path().resolve().joinpath(args.dest)
file_type="obj"
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
        record.scale_factor = 0.1 if file_type == "fbx" else 0.2
        for platform in record.urls:
            dest_url = dest.joinpath(record.wnid + "/" + record.name + "/" + platform)
            url="file:///" + str(dest_url.resolve()).replace("\\", "/")
            record.urls[platform] = url
        lib.add_or_update_record(record, overwrite=True, write=False)
        # Write to disk.
        lib.write(pretty=False)

a = AssetBundleCreator(display=":1")

create_library()
# lib = ModelLibrarian(str(library_path.resolve()))
# for record in lib.records:
#     a.move_files_to_unity_project(None, model_path=src.joinpath(f"{record.name}."+file_type), sub_directory=f"models/{record.name}")
# a.create_many_asset_bundles(str(library_path.resolve()), vhacd_resolution=args.vhacd, cleanup=False)

# models_dir = a.get_resources_directory().joinpath("models")
# for ext in [".obj", ".fbx"]:
#     for f in models_dir.rglob(f"*{ext}"):
#         if f.stem.endswith("_colliders"):
#             continue
#         colliders_path = f.parent.joinpath(f"{f.stem}_colliders.obj")
#         # Don't regenerate a colliders file if one already exists.
#         if colliders_path.exists():
#             continue
#         # Don't recreate models that already have prefabs.
#         prefab_path = self.get_resources_directory().joinpath(f"prefab/{f.stem}.prefab")
#         if prefab_path.exists():
#             continue
#         # Create the colliders.
#         wrl_path = self.obj_to_wrl(f, vhacd_resolution=vhacd_resolution)
#         # Move the collider .obj to the correct directory.
#         wrl_to_obj_path = self.wrl_to_obj(wrl_path, f.stem)
#         distutils.file_util.move_file(str(wrl_to_obj_path.resolve()), str(colliders_path.resolve()))
#         # Remove the .wrl file.
#         wrl_path.unlink()

# Create the asset bundles.
record_call = a.get_base_unity_call()
record_call.extend(["-executeMethod",
                    "AssetBundleCreator.CreateManyAssetBundles",
                    "-library=" + str(library_path.resolve()),
                    "-internal_materials"])
call(record_call)

# if cleanup:
#     self.cleanup()


with open(str(library_path.resolve()),"r") as f:
    text = list(f.read())
for i in range(len(text)):
    if text[i] == ",":
        if text[i + 1] != " " and text[i + 1] != "\"":
            text[i] = "."
fixed_text = "".join(text)
with open(str(library_path.resolve()), 'w') as f:
    f.write(fixed_text)
#
# files_in_directory = os.listdir("./")
# mtls = [file for file in files_in_directory if file.endswith(".mtl")]
# for file in mtls:
#     os.remove(str(Path().resolve().joinpath(file)))

