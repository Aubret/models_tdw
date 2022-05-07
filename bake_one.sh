#!/bin/bash

location="/home/comsee/postdoc/datasets/test_blend3"
blender_location="/home/comsee/postdoc/datasets/blender-2.90.0-linux64/blender"
$blender_location $location"/"$1"/"$1"_"$2"/"$1"_"$2".blend" --python ./bake.py -- $location"/"$1"/"$1"_"$2 $3

