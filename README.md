# models_tdw
Codes to export blender models to tdw: in particular https://github.com/rehg-lab/lowshot-shapebias/tree/main/toys4k

### Downloads
Download the toys4k dataset, a put it in toys4k_blend_files/

Download blender, version > 2.8

### Export to fbx
To export all fbx from toys4k dataset:
```
blender --python export_all_fbx.py --background
```
To export one fbx from each category of the toys4k dataset:
```
blender --python export_one_fbx.py --background
```

### Transfer fbx to tdw
You will need the Unity editor, as explained here: 

https://github.com/threedworld-mit/tdw/blob/master/Documentation/lessons/3d_models/custom_models.md


To build the library:
```
python3 build_library --fbx_directory test_toys4K_fbx --dest library/ --vhacd 4000
```

### Transfering the library to another computer

Copy and paste the library directory somewhere else. Update the paths of the models by running:
```
python3 update_url.py
```


### Test the library

```
python3 test_library.py
```

### TODO

- At least half of the objects do not export with textures in fbx.
- Check why json files from unity editor are badly formatted.