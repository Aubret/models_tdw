# models_tdw
Codes to export blender models to tdw

###Downloads
Download the toys4k dataset, a put it in toys4k_blend_files/

Download blender, version > 2.8

###Export to fbx
To export all fbx from toys4k dataset:
```
blender --python export_all_fbx.py --background
```
To export one fbx from each category of the toys4k dataset:
```
blender --python export_one_fbx.py --background
```

###Transfer fbx to tdw

To build the library:
```
python3 build_library --fbx_directory test_toys4K_fbx --dest library/ --vhacd 4000
```

###Transfering the library to another computer

Copy and paste the library directory somewhere else. Update the paths of the models by running:
```
python3 update_url.py
```


###Test the library

```
python3 test_library.py
```
