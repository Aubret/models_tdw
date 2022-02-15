import bpy
import os


basedir = bpy.path.abspath('//')
dir_dest = "toys4K_fbx_all/"

def save_object(objet, category_dir):
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
            target_file=os.path.join(basedir, dir_dest + objet + '.fbx')
            bpy.ops.export_scene.fbx(filepath=target_file, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS")

        # deselect the object and move on to another if any more are left
        ob.select_set(False)

def export_all_to_fbx():
    for category in os.listdir(os.path.join(basedir, "toys4k_blend_files/")):
        category_dir = os.path.join(basedir, "toys4k_blend_files/" + category + "/")
        i=0
        for objet in os.listdir(category_dir):
            if objet != "octopus_004":
                save_object(objet, category_dir)
            i=i+1

