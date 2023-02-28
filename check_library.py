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


def str2table(v):
    return v.split(',')

parser = argparse.ArgumentParser()
parser.add_argument("--library", type=str, default="library2/")
parser.add_argument("--begin", type=int, default=0)
parser.add_argument("--end", type=int, default=2000)
parser.add_argument("--delete", type=int, default=0)
parser.add_argument("--not_include", type=int, default=0)
parser.add_argument("--disabled", type=int, default=0)
parser.add_argument("--name", type=str2table, default="")
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


    # camera = ThirdPersonCamera(position={"x": 0, "y": 0.5, "z": -1}, avatar_id="a")
    # c.add_ons.extend([camera])
    lib_path=args.library+"toys.json"


    command = []
    i=0
    js = json.load(open(lib_path))
    js_copy = copy.deepcopy(js)
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

    port = find_free_port()
    Popen([str(Build.BUILD_PATH.resolve()), "-port " + str(port), "-force-glcore42"])
    c = Controller(check_version=False, port=port, launch_build=False)
    c.communicate(TDWUtils.create_avatar(avatar_type="A_Img_Caps", avatar_id="a",
                                           position={"x": 0, "y": 0.5, "z": -1.5}))

    lib = ModelLibrarian(library=lib_path)
    # command = [{"$type": "create_empty_environment"},{"$type": "simulate_physics","value": False},{"$type": "set_aperture", "aperture": 20}]
    command = [TDWUtils.create_empty_room(15, 15),{"$type": "simulate_physics","value": False},{"$type": "set_aperture", "aperture": 20}]
    command.append({"$type": "set_screen_size", "width": 128, "height": 128})
    c.communicate(command)

    for r in lib.records:
    # for r in [lib.get_record("stove_000")]:
        # if os.path.isdir(args.library + r.wcategory + "/" + r.name):
        #     continue
        # print(r.name)
        i+=1
        id = c.get_unique_id()
        if i < begin or i > end or r.name == "":
            continue
        if args.not_include and r.name not in excluded:
            continue
        if args.name[0] != "" and r.name not in args.name:
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
            "position": {"x": 0, "y": 1, "z":0},
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
        diag, diag1, diag2, diag3, diag4, diag5, diag6, diag7 = -100, -100, -100, -100,-100, -100, -100, -100
        for _ in range(20):
            resp = c.communicate([{"$type": "rotate_object_by", "angle": 360//20, "axis": "yaw", "id": id}])
            # time.sleep(0.5)
            for _ in range(20):
                resp = c.communicate([{"$type": "rotate_object_by", "angle": 360 // 20, "axis": "pitch", "id": id}])
                for j in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[j])
                    if r_id == "boun":
                        b = Bounds(resp[j])
                        bottom = max(bottom, abs(1-b.get_bottom(0)[1]))
                        top = max(top, abs(b.get_top(0)[1]-1))
                        right = max(right, math.sqrt(math.pow(b.get_right(0)[2],2)+math.pow(1-b.get_right(0)[1],2)+math.pow(b.get_right(0)[0],2)))
                        left = max(left, math.sqrt(math.pow(b.get_left(0)[2],2)+math.pow(1-b.get_left(0)[1],2)+math.pow(b.get_left(0)[0],2)))
                        front = max(front, math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(1-b.get_front(0)[1],2)+math.pow(b.get_front(0)[0],2)))
                        back = max(back, math.sqrt(math.pow(b.get_back(0)[2],2)+math.pow(1-b.get_back(0)[1],2)+math.pow(b.get_back(0)[0],2)))
                        diag = max(diag, math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(b.get_top(0)[1]-1,2)+math.pow(b.get_right(0)[0],2)))
                        diag1 = max(diag1, math.sqrt(math.pow(b.get_back(0)[2],2)+math.pow(b.get_top(0)[1]-1,2)+math.pow(b.get_right(0)[0],2)))
                        diag2 = max(diag2, math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(b.get_bottom(0)[1]-1,2)+math.pow(b.get_right(0)[0],2)))
                        diag3 = max(diag3, math.sqrt(math.pow(b.get_back(0)[2],2)+math.pow(b.get_bottom(0)[1]-1,2)+math.pow(b.get_right(0)[0],2)))
                        diag4 = max(diag4, math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(b.get_top(0)[1]-1,2)+math.pow(b.get_left(0)[0],2)))
                        diag5 = max(diag5, math.sqrt(math.pow(b.get_back(0)[2],2)+math.pow(b.get_top(0)[1]-1,2)+math.pow(b.get_left(0)[0],2)))
                        diag6 = max(diag6, math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(b.get_bottom(0)[1]-1,2)+math.pow(b.get_left(0)[0],2)))
                        diag7 = max(diag7, math.sqrt(math.pow(b.get_back(0)[2],2)+math.pow(b.get_bottom(0)[1]-1,2)+math.pow(b.get_left(0)[0],2)))
                        # print("------")
                        # print(b.get_front(0))
                        # print(b.get_left(0))
                        # print(b.get_top(0))
                        # input()
                        # print(b.get_front(0)[0],b.get_top(0)[1], b.get_right(0)[2])


        #0.15
        # print("------")
        delay = time.time() - t
        # limit = 0.35
        limit = 0.3
        # scale_factor = min(1, limit/bottom, limit/top, limit/right, limit/left, limit/front, limit/back)
        diag = max(diag,diag1, diag2, diag3, diag4, diag5, diag6, diag7)
        scale_factor = min(limit/bottom, limit/top, limit/right, limit/left, limit/front, limit/back, limit/diag)
        js_copy["records"][r.name]["scale_factor"] = 0.2*scale_factor#js_copy["records"][r.name]["scale_factor"]*0.2
        if delay > 0.5 and args.delete == 1:
            del js_copy["records"][r.name]
            print(r.name, "delay", delay)
        # if r.wcategory == "drum":
        #     del js_copy["records"][r.name]

        command = [{"$type": "destroy_object", "id": id}]
    # print("here2", js_copy["records"]["stove_000"]["scale_factor"] )

    c.communicate({"$type": "terminate"})
    if "piano_007" in js_copy["records"]:
        del js_copy["records"]["piano_007"]
    if "train_003" in js_copy["records"]:
        del js_copy["records"]["train_003"]
    if "train_023" in js_copy["records"]:
        del js_copy["records"]["train_023"]
    if "" in js_copy["records"]:
        print("found")
        del js_copy["records"][""]
    if " " in js_copy["records"]:
        print("found2")
        del js_copy["records"][" "]
    # js = json.load(open(lib_path))
    # js_copy = copy.deepcopy(js)
    if args.library == "library_tex/":
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

    with open(lib_path, 'w') as f:
        json.dump(js_copy, f)

run(begin=args.begin,end=args.end)
