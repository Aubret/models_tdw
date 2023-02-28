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

import numpy
from tdw.librarian import ModelLibrarian
from tdw.output_data import OutputData, Bounds
from tdw.release.build import Build
from tdw.tdw_utils import TDWUtils

sys.path.append('/home/comsee/postdoc/tdw/Python')
from tdw.controller import Controller



def str2table(v):
    return v.split(',')

parser = argparse.ArgumentParser()
parser.add_argument("--library", type=str, default="library2/")
parser.add_argument("--begin", type=int, default=0)
parser.add_argument("--end", type=int, default=2000)
parser.add_argument("--name", type=str2table, default="")

args = parser.parse_args()


def find_free_port():
    """
    Returns a free port as a string.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return int(s.getsockname()[1])

def get_elongation_axis(resp):
    for j in range(len(resp) - 1):
        r_id = OutputData.get_data_type_id(resp[j])
        if r_id == "boun":
            b = Bounds(resp[j])
            left = math.sqrt(math.pow(b.get_left(0)[2],2)+math.pow(1-b.get_left(0)[1],2)+math.pow(b.get_left(0)[0],2))
            front = math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(1-b.get_front(0)[1],2)+math.pow(b.get_front(0)[0],2))
    return left,front

def get_all_axis(resp):
    for j in range(len(resp) - 1):
        r_id = OutputData.get_data_type_id(resp[j])
        if r_id == "boun":
            b = Bounds(resp[j])
            left = math.sqrt(math.pow(b.get_left(0)[2],2)+math.pow(1-b.get_left(0)[1],2)+math.pow(b.get_left(0)[0],2))
            front = math.sqrt(math.pow(b.get_front(0)[2],2)+math.pow(1-b.get_front(0)[1],2)+math.pow(b.get_front(0)[0],2))
            back = math.sqrt(math.pow(b.get_back(0)[2],2)+math.pow(1-b.get_back(0)[1],2)+math.pow(b.get_back(0)[0],2))
            right = math.sqrt(math.pow(b.get_right(0)[2],2)+math.pow(1-b.get_right(0)[1],2)+math.pow(b.get_right(0)[0],2))
    return left,front,right,back

def run(begin=0, end=2000):
    # Launch the controller.
    lib_path=args.library+"toys.json"
    js = json.load(open(lib_path))
    js_copy = copy.deepcopy(js)
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
    i=0
    for r in lib.records:
        #chicken_021, keyboard_027, pig_000, frog_019

        # if r.wcategory in ["airplane","bunny","cat","chair","cow","crab","deer_moose","dinosaur","dog","dolphin",
        #                    "dragon","elephant","fan","fish","flower","fox","fridge"]
        #banana
        i += 1

        if i < begin or i > end or r.name == "":
            continue
        if i % 200 == 0:
            print(i)
        if args.name[0] != "" and r.name not in args.name:
            continue
        if r.wcategory in ["coin","ball","apple","cookie","cup","fries","mug","orange","pear","toaster"]:


            t = time.time()
            command=[]
            # command.append(c.get_add_object(r.name, object_id=id, library=lib_path, position={"x": 0, "y":0.5, "z":0},scale_factor=0.15*0.2))
            id = c.get_unique_id()
            command.append({"$type": "add_object",
                "name": r.name,
                "url": r.get_url(),
                "scale_factor": 0.2,
                "position": {"x": 0, "y": 1, "z":0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "category": r.wcategory,
                "id": id})
            command.append({"$type": "send_bounds", "ids": [id], "frequency": "always"})
            resp = c.communicate(command)
            # r0,r0f = get_elongation_axis(resp)
            # resp = c.communicate([{"$type": "rotate_object_by", "angle": 90, "axis": "yaw", "id": id}])
            # print(r0)
            # r90,r90f = get_elongation_axis(resp)
            # resp = c.communicate([{"$type": "rotate_object_by", "angle": 90, "axis": "yaw", "id": id}])
            # print(r90)
            # r180,r180f = get_elongation_axis(resp)
            # resp = c.communicate([{"$type": "rotate_object_by", "angle": 90, "axis": "yaw", "id": id}])
            # r270,r270f = get_elongation_axis(resp)
            # axis = numpy.argmax(numpy.array([r0+r0/10,r90,r180,r270]))
            # print([r0,r90,r180,r270])
            # print([r0f,r90f,r180f,r270f])
            # print(axis)


            left,front,right,back= get_all_axis(resp)
            axis = numpy.argmax(numpy.array([front,left]))
            # print(front+front/30,left,back-back/20,right-right/20)
            # print(axis)
            js_copy["records"][r.name]["canonical_rotation"] = {"x":0, "y":90, "z":0}
            c.communicate([{"$type": "destroy_object", "id": id}])

        else:
            js_copy["records"][r.name]["canonical_rotation"] = {"x":0, "y":0, "z":0}


    # print("here2", js_copy["records"]["stove_000"]["scale_factor"] )
    print("over")
    c.communicate({"$type": "terminate"})


    with open(lib_path, 'w') as f:
        json.dump(js_copy, f)

run(begin=args.begin,end=args.end)
