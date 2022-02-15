import argparse
import sys

from tdw.librarian import ModelLibrarian

sys.path.append('/home/comsee/postdoc/tdw/Python')
from tdw.controller import Controller
from tdw.backend.platforms import SYSTEM_TO_UNITY
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a local asset bundle and load it into TDW.
"""

class LocalObject:
    @staticmethod
    def run():
        # Launch the controller.
        c = Controller()
        camera = ThirdPersonCamera(position={"x": 0, "y": 0, "z": -1.6}, avatar_id="a")
        images_path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
        print(f"Images will be saved to: {images_path}")
        capture = ImageCapture(avatar_ids=["a"], path=images_path)
        c.add_ons.extend([camera, capture])
        lib_path="library/toys.json"
        lib = ModelLibrarian(library=lib_path)
        command = [{"$type": "create_empty_environment"}, {"$type": "set_target_framerate", "framerate": 10}]
        c.communicate(command)

        for r in lib.records:
            id = c.get_unique_id()
            c.communicate([c.get_add_object(r.name, object_id=id, library=lib_path)])
            for i in range(10):
                c.communicate([{"$type": "rotate_object_by", "angle": 36, "axis": "yaw", "id": id}])
            c.communicate({"$type": "destroy_object", "id": id})

        c.communicate({"$type": "terminate"})


LocalObject.run()
