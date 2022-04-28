#!/bin/bash

location="/home/comsee/postdoc/datasets/test_blend2"
blender_location="/home/comsee/postdoc/datasets/blender-2.90.0-linux64/blender"

for d in $location/*; do
  if [ -d "$d" ]; then
    for f in $d/*; do
      for f2 in $f/*.blend; do
          echo $f2
          if [ -d "$f/Textures" ]; then
              continue
          fi
          $blender_location $f2 --python ./bake.py -- $f all
      done
    done
  fi
done



