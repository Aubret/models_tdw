import argparse

import bpy
import os
#bpy.path.abspath('//')
basedir = "../datasets"
dir_dest = "toys4K_obj_all/"

def save_object(objet, category_dir):
    target_file = os.path.join(basedir, dir_dest + objet + '.obj')
    if os.path.isfile(target_file):
        return
    bpy.ops.wm.open_mainfile(filepath=category_dir + objet + "/" + objet + ".blend")
    # deselect all objects
    C = bpy.context
    bpy.ops.object.select_all(action='DESELECT')
    scene = C.scene
    for ob in scene.objects:


        C.view_layer.objects.active = ob
        # C.view_layer.objects.active = ob
        ob.select_set(True)
        ob.scale = (0.5, 0.5, 0.5)
        # make sure that we only export meshes
        if ob.type == 'MESH':
            # bpy.ops.export_scene.fbx(filepath=target_file, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS")
            bpy.ops.export_scene.obj(filepath=target_file, use_selection=True)

        # deselect the object and move on to another if any more are left
        ob.select_set(False)

# print(str(os.path.join(basedir, dir_dest + "obj" + '.fbx')))
# def export_all_to_fbx():
for category in os.listdir(os.path.join(basedir, "toys4k_blend_files/")):
    category_dir = os.path.join(basedir, "toys4k_blend_files/" + category + "/")
    # category_dir = os.path.join(basedir, "toys4k_blend_files/apple/")
    i=0
    for objet in os.listdir(category_dir):
        if objet != "octopus_004" and objet != "truck_022":
            try:
                save_object(objet, category_dir)
            except:
                print("Not working "+objet)
        i=i+1

