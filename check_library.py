import argparse
import copy
import json
import math
import os
import sys
import time
from subprocess import Popen
import socket
from contextlib import closing
from tdw.librarian import ModelLibrarian
from tdw.output_data import OutputData, Bounds
from tdw.release.build import Build
from tdw.tdw_utils import TDWUtils

sys.path.append('/home/comsee/postdoc/tdw/Python')
from tdw.controller import Controller
from tdw.backend.platforms import SYSTEM_TO_UNITY
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

parser = argparse.ArgumentParser()
parser.add_argument("--library", type=str, default="library2/")
parser.add_argument("--begin", type=int, default=0)
parser.add_argument("--end", type=int, default=2000)
parser.add_argument("--delete", type=int, default=0)
args = parser.parse_args()


def find_free_port():
    """
    Returns a free port as a string.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return int(s.getsockname()[1])

def run(begin=0, end=2000):
    # Launch the controller.
    # c = Controller()
    port = find_free_port()
    Popen([str(Build.BUILD_PATH.resolve()), "-port " + str(port), "-force-glcore42"])
    c = Controller(check_version=False, port=port, launch_build=False)

    # camera = ThirdPersonCamera(position={"x": 0, "y": 0.5, "z": -1}, avatar_id="a")
    # c.add_ons.extend([camera])
    lib_path=args.library+"toys.json"
    c.communicate(TDWUtils.create_avatar(avatar_type="A_Img_Caps", avatar_id="a",
                                           position={"x": 0, "y": 0.5, "z": -1}))

    lib = ModelLibrarian(library=lib_path)
    # command = [{"$type": "create_empty_environment"},{"$type": "simulate_physics","value": False},{"$type": "set_aperture", "aperture": 20}]
    command = [TDWUtils.create_empty_room(15, 15),{"$type": "simulate_physics","value": False},{"$type": "set_aperture", "aperture": 20}]
    command.append({"$type": "set_screen_size", "width": 128, "height": 128})
    c.communicate(command)

    command = []
    i=0
    js = json.load(open(lib_path))
    js_copy = copy.deepcopy(js)


    for r in lib.records:
        # if os.path.isdir(args.library + r.wcategory + "/" + r.name):
        #     continue

        i+=1
        id = c.get_unique_id()
        if i < begin or i > end or r.name == "":
            continue
        if i%50 == 0:
            print(i)
        # if r.name not in ["chicken_021", "keyboard_027", "pig_000", "frog_01"]:
        #     continue
        #chicken_021, keyboard_027, pig_000, frog_019
        t = time.time()
        # command.append(c.get_add_object(r.name, object_id=id, library=lib_path, position={"x": 0, "y":0.5, "z":0},scale_factor=0.15*0.2))
        command.append({"$type": "add_object",
            "name": r.name,
            "url": r.get_url(),
            "scale_factor": 0.2,
            "position": {"x": 0, "y":0.5, "z":0},
            "rotation": {"x": 0, "y": 0, "z": 0},
            "category": r.wcategory,
            "id": id})
        command.append({"$type": "send_bounds", "ids": [id], "frequency": "always"})
        c.communicate(command)

        right = -100
        left = -100
        bottom = -100
        top = -100
        front = -100
        back = -100
        for _ in range(10):
            resp = c.communicate([{"$type": "rotate_object_by", "angle": 36, "axis": "yaw", "id": id}])
            for j in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[j])
                if r_id == "boun":
                    b = Bounds(resp[j])
                    bottom = max(bottom, abs(0.5-b.get_bottom(0)[1]))
                    top = max(top, abs(b.get_top(0)[1]-0.5))
                    right = max(right, math.sqrt(math.pow(b.get_right(0)[2],2)+math.pow(b.get_right(0)[0],2)))
                    left = max(left, math.sqrt(math.pow(b.get_left(0)[2],2)+math.pow(b.get_left(0)[0],2)))
                    front = max(front, math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(b.get_front(0)[0],2)))
                    back = max(back, math.sqrt(math.pow(b.get_back(0)[2],2)+math.pow(b.get_back(0)[0],2)))

        #0.15
        # print("------")
        delay = time.time() - t
        # limit = 0.35
        limit = 0.3
        # scale_factor = min(1, limit/bottom, limit/top, limit/right, limit/left, limit/front, limit/back)
        scale_factor = min(limit/bottom, limit/top, limit/right, limit/left, limit/front, limit/back)
        js_copy["records"][r.name]["scale_factor"] = 0.2*scale_factor#js_copy["records"][r.name]["scale_factor"]*0.2

        if delay > 0.5 and args.delete == 1:
            del js_copy["records"][r.name]
            print(r.name, "delay", delay)
        # if r.wcategory == "drum":
        #     del js_copy["records"][r.name]

        command = [{"$type": "destroy_object", "id": id}]

    c.communicate({"$type": "terminate"})
    if "piano_007" in js_copy["records"]:
        del js_copy["records"]["piano_007"]
    if "train_003" in js_copy["records"]:
        del js_copy["records"]["train_003"]


    # del js_copy["records"]["truck_022"]

    with open(lib_path, 'w') as f:
        json.dump(js_copy, f)

run(begin=args.begin,end=args.end)
