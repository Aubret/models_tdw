import argparse
from threading import Thread
from time import sleep, time

import bpy
import os

basedir = "/home/comsee/postdoc/datasets"
# dir_dest = "toys4k_blend_baked_files/"
# dir_src = "toys4k_blend_files/"
dir_src = "test_blend/"
dir_dest = "test_blend/"

import sys
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

save_path = argv[0]
type = argv[1]

# bpy.ops.wm.open_mainfile(filepath=category_dir + "/"+ objet + "/" + objet + ".blend")


def lightpack_unwrap():
    max_poly = 50000
    i=0
    while len(bpy.context.view_layer.objects[0].data.polygons) > max_poly+2000 and i < 4:
        i+=1
        bpy.ops.object.modifier_add(type='DECIMATE')
        # bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        # bpy.context.object.modifiers["Decimate"].delimit = {'UV'}
        # bpy.context.object.modifiers["Decimate"].angle_limit = 0.20944
        bpy.context.object.modifiers["Decimate"].ratio = max_poly/len(bpy.context.view_layer.objects[0].data.polygons)
        try:
            bpy.ops.object.modifier_apply(modifier="Decimate")
        except:
            bpy.ops.wm.quit_blender()
            return -1

    if len(bpy.context.view_layer.objects[0].data.polygons) > max_poly+2000:
        bpy.ops.wm.quit_blender()
        return -1

    if type == "lightmap3":
        bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True,
                                   lightmap_margin=0.03, lightmap_quality=12)
        return 1
    if type == "lightmap4":
        bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True,
                                   lightmap_margin=0.1, lightmap_quality=12)
        return 1

    if type != "lightmap2":
        bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True,
                                   lightmap_margin=0.05, lightmap_quality=12)
    if type == "lightmap2" or (type == "all" and len(bpy.context.active_object.data.uv_layers[0].data) > 10000):
        bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True,
                               lightmap_margin=0.3, lightmap_quality=12)

    # if len(bpy.context.active_object.data.uv_layers[0].data) > 200000:
    #     return 0
    return 1

def check_overlaps(active_object, index = None):
    done = True
    if index is not None:
        active_object.data.uv_layers.active = active_object.data.uv_layers[0]
    # print(bpy.context.area.type)
    # bpy.context.area.type = 'UV'
    # bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_overlap()
    bpy.ops.object.editmode_toggle()

    num_overlaps = len([i for i in bpy.context.active_object.data.uv_layers.active.data if i.select])
    # print([i for i in bpy.context.active_object.data.uv_layers[0].data if i.select])
    if num_overlaps > len(bpy.context.view_layer.objects[0].data.polygons)/3:
        print("Finally not, there is too much overlapping", num_overlaps)
        done = False
    return done

def run():
    # if os.path.exists(save_path+"/"+os.path.basename(save_path)+".obj"):
        # return


    if os.path.basename(save_path) == "dragon_042":
        bpy.ops.wm.quit_blender()
        return

    C = bpy.context
    scene = C.scene
    for ob in scene.objects:
        if ob.type == 'MESH':
            ob.select_set(True)
            C.view_layer.objects.active = ob
        else:
            ob.select_set(False)

    active_object = bpy.context.active_object
    # need_new_unwrap = len(active_object.data.uv_layers) != 1 or len(C.view_layer.objects[0].data.polygons) > 3000 #or (len(C.view_layer.objects[0].data.polygons) > 3000 and len(C.view_layer.objects[0].data.polygons) < 20000)
    #or len(active_object.data.uv_layers[0].data) > 3000  #
    # len(active_object.data.uv_layers) != 1 or len(C.view_layer.objects[0].data.polygons) > 3000
    #print("ok", len(active_object.data.uv_layers[0].data))
    #bpy.ops.mesh.select_all(action='SELECT')
    #bpy.ops.uv.select_overlap(extend=False)
    #print(len(active_object.data.uv_layers[0].data))
    max_poly = 300000
    i=0
    while len(C.view_layer.objects[0].data.polygons) > max_poly+2000 and i < 4:
        i+=1
        print("too many polys", len(C.view_layer.objects[0].data.polygons))
        try:
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = max_poly/len(C.view_layer.objects[0].data.polygons)
            bpy.ops.object.modifier_apply(modifier="Decimate")
        except:
            bpy.ops.wm.quit_blender()
            return

    if len(C.view_layer.objects[0].data.polygons) > max_poly+2000:
        bpy.ops.wm.quit_blender()
        return

    os.makedirs(save_path+"/Textures", exist_ok=True)
    #No need for baking
    nodes = False
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.bl_label not in ["Principled BSDF", "Material Output"]:
                    nodes = True

    if type != "none" and bpy.context.object.active_material and bpy.context.object.active_material.use_nodes and nodes:
        metal = 0
        for m in bpy.data.materials:
            if m.node_tree is not None and "Principled BSDF" in m.node_tree.nodes:
                metal = max(metal, m.node_tree.nodes["Principled BSDF"].inputs[4].default_value)
                m.node_tree.nodes["Principled BSDF"].inputs[4].default_value = 0

        bpy.context.scene.BakeLabProps.metalic = metal


        bpy.context.scene.BakeLabProps.save_or_pack = 'SAVE'
        bpy.context.scene.BakeLabProps.save_path = save_path
        bpy.context.scene.BakeLabProps.compute_device = 'GPU'
        bpy.context.scene.BakeLabProps.create_folder = False


        # bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True, lightmap_margin=0.1)
        # bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True, lightmap_margin=0.2, lightmap_quality=48)
        # make_new_uv = True
        t = time()
        #bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True, lightmap_margin=0.1, lightmap_quality=12
                               # , uvmap_options_individual="IF_MISSING")
                               #, uvmap_options_individual="CREATE_NEW" if need_new_unwrap else "IF_MISSING")
                               # , uvmap_options_individual="CREATE_NEW")
        # # bpy.ops.bakelab.unwrap(unwrap_method='smart_uv', unwrap_mode='INDIVIDUAL', make_single_user_view=True)
        done = (type == "keep")
        if type == "keep" and len(active_object.data.uv_layers) != 1:
            bpy.ops.wm.quit_blender()
            return
        if type == "all" and len(active_object.data.uv_layers) == 1 and len(bpy.data.materials) < 2:
            print("keep previous")
            done = check_overlaps(active_object, 0)

        if not done and (type == "all" or type =="unwrap"):#and len(bpy.data.materials) < 1:
            # bpy.ops.mesh.uv_texture_remove()
            bpy.ops.bakelab.unwrap(unwrap_method='unwrap', unwrap_mode='INDIVIDUAL', make_single_user_view=True)
            done = True

            if len(bpy.context.active_object.data.uv_layers) > 0 and len(bpy.context.active_object.data.uv_layers[-1].data) > 1500000:
                print("Too many uvs for this object", len(bpy.context.active_object.data.uv_layers[-1].data))
                done = False

            if done and type == "all":
                done = check_overlaps(active_object, None)

        # if not done and len(active_object.data.uv_layers) == 2:
        #     print("keep previous")
        #     done = check_overlaps(active_object, 0)
            # bpy.ops.uv.select_all()


        if not done and (type == "all" or type == "lightmap1" or type == "lightmap2"  or type == "lightmap3" or type == "lightmap4"):
            print("try lightmap")
            err = lightpack_unwrap()
            if not err:
                bpy.ops.wm.quit_blender()
                return

        print("unwrap time and number uvs", time()-t, len(bpy.context.active_object.data.uv_layers[0].data))

        # img_size = 2048
        # img_size = 512
        # img_size = 4096
        img_size = 1024
        float_depth = False
        bpy.ops.bakelab.newmapitem(type='Diffuse', width=img_size, height=img_size, float_depth=float_depth)
        bpy.ops.bakelab.newmapitem(type='Normal', width=img_size, height=img_size, float_depth=float_depth)
        # bpy.ops.bakelab.newmapitem(type='UV', width=img_size, height=img_size, float_depth=float_depth)
        bpy.ops.bakelab.newmapitem(type='Glossy', width=img_size, height=img_size, float_depth=float_depth)
        bpy.ops.bakelab.newmapitem(type='Roughness', width=img_size, height=img_size, float_depth=float_depth)
        bpy.ops.bakelab.newmapitem(type='Emission', width=img_size, height=img_size, float_depth=float_depth)

        bpy.ops.bakelab.bake()
    else:
        # bpy.ops.file.make_paths_relative()
        # bpy.ops.file.unpack_all(method='USE_LOCAL')
        # os.rename(save_path+"/textures", save_path+"/Textures")
        path = save_path
        path_s = path.split("/")[-1]
        bpy.ops.export_scene.obj(filepath=path+"/"+path_s+".obj", use_selection=True)
        bpy.ops.wm.quit_blender()

run()

# print(category_dir + "/"+ objet + "/" + objet + ".blend")
# override = bpy.context.copy()

# bpy.ops.wm.open_mainfile(filepath=category_dir + "/" + objet + "/" + objet + ".blend")
# bpy.context = context_override()
# for window in bpy.context.window_manager.windows:
#     screen = window.screen
#     for area in screen.areas:
#         if area.type == 'VIEW_3D':
#             override.update(window=window, screen=screen, area=area)
#             bpy.ops.screen.screen_full_area(override)
#             break
# bpy.context = override
# bpy.ops.object.select_all(action='DESELECT')


# bpy.context.space_data.shading.use_scene_world_render = False
# C.active_object = ob


# bpy.ops.bakelab.generate_mats()
# bpy.ops.bakelab.finish()



# for category in os.listdir(os.path.join(basedir, dir_src)):
#     category_dir = os.path.join(basedir, dir_src + category)# + "/")
#     if not os.path.isdir(category_dir):
#         continue
#     # category_dir = os.path.join(basedir, "toys4k_blend_files/apple/")
#     i=0
#     for objet in os.listdir(category_dir):
#         if objet != "octopus_004":
#             try:
#                 bake_object(objet, category_dir)
#                 # print(objet)
#             except Exception as e:
#                 print("Not working "+objet, str(e))
#         i=i+1


# bpy.ops.wm.quit_blender()
#     bpy.ops.object.select_all(action='DESELECT')
#     bpy.ops.object.make_single_user(object=True, obdata=True)
#     bpy.ops.object.select_all(action='DESELECT')
#     bpy.context.scene.BakeLabProps.apply_only_selected = True
#     bpy.context.scene.BakeLabProps.make_single_user = True


# bpy.ops.file.make_paths_relative()
# bpy.ops.file.unpack_all(method='USE_LOCAL')

# bpy.ops.bakelab.newmapitem(type='Environment')
# bpy.ops.export_scene.obj(filepath=target_file, use_selection=True)

# def threaded_function(bpy):
#     bpy = arg
#     i=0
# while len(bpy.context.scene.BakeLab_Data) == 0 and i < 5:
# i=0
# while i < 10 :
# # while bpy.context.scene.BakeLabProps.bake_state != "BAKED":
#     i=i+1
#     # print(i)
#     sleep(1)
# print("start already")
# bpy.ops.bakelab.generate_mats()
# bpy.ops.bakelab.finish()
# bpy.ops.export_scene.obj(filepath=os.path.join(basedir, dir_dest + objet), use_selection=True)

# bpy.ops.wm.save_as_mainfile(filepath=category_dir + "/"+ objet + "/" + objet + "2.blend")
# #
# thread = Thread(target = threaded_function, args = (bpy, ))
# thread.start()
# bpy.ops.bakelab.unwrap(unwrap_method='unwrap', unwrap_mode='IF_MISSING', default_uv_name="BakeUVMap",make_single_user_view=True)
# bpy.ops.bakelab.unwrap(unwrap_method='unwrap', unwrap_mode='ALL_TO_ONE', default_uv_name="BakeUVMap",make_single_user_view=True)
# bpy.ops.bakelab.unwrap(unwrap_method='unwrap', unwrap_mode='INDIVIDUAL', uvmap_options_individual='IF_MISSING',make_single_user_view=True)
# bpy.ops.bakelab.unwrap(unwrap_mode='INDIVIDUAL', make_single_user_view=True)
# bpy.ops.bakelab.unwrap(unwrap_method='lightmap_uv', unwrap_mode='INDIVIDUAL', default_uv_name="BakeUVMap",
#                        make_single_user_view=True, lightmap_quality=12, uvmap_options= 'CREATE_NEW')
# bpy.ops.bakelab.newmapitem(type='Combined', png_depth='16')

# bpy.ops.bakelab.newmapitem(type='AO') #CAn not export it to obj

# bpy.ops.bakelab.newmapitem(type='Albedo')
# bpy.ops.bakelab.newmapitem(type='Subsurface')
# bpy.ops.bakelab.newmapitem(type='Combined')
# bpy.ops.bakelab.newmapitem(type='Displacement')

# bpy.ops.bakelab.newmapitem(type='Transmission') #not working on cupcake
# bpy.ops.bakelab.newmapitem(type='Shadow')
# bpy.ops.object.select_all(action='DESELECT')