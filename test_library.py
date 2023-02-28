import argparse
import os
import socket
import sys
import time
from contextlib import closing
from subprocess import Popen

from tdw.add_ons.embodied_avatar import EmbodiedAvatar
from tdw.add_ons.floorplan import Floorplan
from tdw.librarian import ModelLibrarian
from tdw.output_data import OutputData, Images
from tdw.release.build import Build
from tdw.tdw_utils import TDWUtils

sys.path.append('/home/comsee/postdoc/tdw/Python')
from tdw.controller import Controller
from tdw.backend.platforms import SYSTEM_TO_UNITY
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


if os.environ["LOCAL_BUNDLES"]:
    TDWUtils.set_default_libraries(model_library=os.environ["LOCAL_BUNDLES"] + "/local_asset_bundles/models.json",
                                   scene_library=os.environ["LOCAL_BUNDLES"] + "/local_asset_bundles/scenes.json",
                                   material_library=os.environ["LOCAL_BUNDLES"] + "/local_asset_bundles/materials.json")

def str2table(v):
    return v.split(',')

parser = argparse.ArgumentParser()
parser.add_argument("--library", type=str, default="library2/toys.json")
parser.add_argument("--store", type=str, default="untextured_toys")
parser.add_argument("--begin", type=int, default=0)
parser.add_argument("--end", type=int, default=2000)
parser.add_argument("--not_include", type=int, default=0)
parser.add_argument("--name", type=str2table, default="")
args = parser.parse_args()

def find_free_port():
    """
    Returns a free port as a string.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return int(s.getsockname()[1])

def save_image(resp, name, path):
    for i in range(len(resp) - 1):
        r_id = OutputData.get_data_type_id(resp[i])
        if r_id == "imag":
            images = Images(resp[i])
            a = images.get_avatar_id()
            output_dir = path.joinpath(a)
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
                # Save images.
            TDWUtils.save_images(images=images,
                                 output_directory=str(output_dir.resolve()),
                                 filename=name)

def run(begin=0, end=2000):
    # Launch the controller.
    # c = Controller()
    port = find_free_port()
    Popen([str(Build.BUILD_PATH.resolve()), "-port " + str(port), "-force-glcore42"])
    c = Controller(check_version=False, port=port, launch_build=False)
    floorplan = Floorplan()
    floorplan.init_scene(scene="1a", layout=0)
    c.add_ons.extend([floorplan])
    c.communicate([])
    # c.communicate(TDWUtils.create_avatar(avatar_type="A_Img_Caps", avatar_id="a",
    #                                        position={"x": -9.5, "y": 1, "z": 2.6}))
    c.add_ons.append(EmbodiedAvatar(avatar_id="a", position={"x": -9.5, "y": 1, "z": 2.6},
                                         scale_factor={"x": 1, "y": 0, "z": 0.7}))
    c.communicate([])

    images_path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath(args.store+"_"+str(begin)+"_"+str(end))

    # camera = ThirdPersonCamera(position={"x": -9.5, "y": 1, "z": 2.6}, avatar_id="a")
    # print(f"Images will be saved to: {images_path}")
    # c.add_ons.extend([camera])
    # capture = ImageCapture(avatar_ids=["a"], path=images_path)

    # lib_path="test_library/toys.json"
    lib_path=args.library
    print("start library")
    lib = ModelLibrarian(library=lib_path)


    command=[]
    # command = [{"$type": "create_empty_environment"},{"$type": "simulate_physics","value": False},{"$type": "set_aperture", "aperture": 20}]
    # command = [TDWUtils.create_empty_room(10, 10), {"$type": "set_target_framerate", "framerate": 10},{"$type": "set_aperture", "aperture": 20}]
    # command = [TDWUtils.create_empty_room(10, 10), {"$type": "set_target_framerate", "framerate": 10},{"$type": "set_aperture", "aperture": 20}]
    command.append({"$type": "set_screen_size", "width": 200, "height": 200})
    command.append({"$type": "set_aperture", "aperture": 20})
    # command.append({"$type": "adjust_point_lights_intensity_by", "intensity": 5})
    command.append({"$type": "adjust_directional_light_intensity_by", "intensity": 1})
    # command.append({"$type": "rotate_directional_light_by", "angle": 30, "axis": "yaw", "index": 0})
    # command.append({"$type": "set_directional_light_color", "color": {"r": 2.219607845, "g": 0.0156862754, "b": 0.6901961, "a": 1.0}, "index": 0})

    command.append({"$type": "set_render_quality", "render_quality": 2})
    c.communicate(command)
    command=[]
    # command.append({"$type": "set_img_pass_encoding",
    #              "value": self._png})
    # Get the pass masks.
    command.append({"$type": "set_pass_masks", "pass_masks": ["_img"], "avatar_id": "a"})
    # self.env.list_possible_names[i]
    # Begin by sending images for the next frame.
    command.append({"$type": "send_images","frequency": "always","ids": ["a"]})

    c.communicate(command)

    command = []
    i=0

    excluded = []
    if args.not_include:
        with open("not_include") as f:
            rl = f.readlines()
            for l in rl:
                cat = "".join(list(l)[:-5])
                name = "".join(list(l)[:-1])
                if cat == "":
                    continue
                excluded.append(name)
    print("start records")
    for r in lib.records:
        i+=1
        id = c.get_unique_id()
        if i < begin or i > end or r.name == "":
            continue
        if args.not_include and r.name not in excluded:
            continue
        if args.name[0] != "" and r.name not in args.name:
            continue

        # if r.name != "drum_008": continue
        # command.append(c.get_add_object(r.name, object_id=id, library=lib_path))
        command.append( {"$type": "add_object",
                "name": r.name,
                "url": r.get_url(),
                "scale_factor": r.scale_factor,
                # "position":{ "x":-9.5, "y": 0.9, "z":3.3},
                "position":{ "x":-9.5, "y": 0.4, "z":3.3},
                "id": id})
        # c.get_add_object(r.name, object_id=id, library=lib_path, position={ "x":-9.5, "y": 1, "z":3.6},scale_factor=0.2)
        resp = c.communicate(command)
        save_image(resp, r.name+"_1", images_path)
        for j in [1, 2, 3]:
            resp = c.communicate([{"$type": "rotate_object_by", "angle": 90*j, "axis": "yaw", "id": id}])
            save_image(resp, r.name+"_"+str(1+j), images_path)

        command = [{"$type": "destroy_object", "id": id}]

    c.communicate({"$type": "terminate"})

run(begin=args.begin, end=args.end)