#! /usr/bin/env python

from solid2 import *
from solid2.extensions.greedy_scad_interface import *

rotation_speed = CustomizerSliderVariable("rotation_speed", 1.0)

set_global_viewport_translation([4, 3, 15])
set_global_viewport_rotation([60, 0, rotation_speed * get_animation_time() * 360])
set_global_viewport_distance(100)

c = cube(get_animation_time() * 10)

scad_render_to_file(c)

