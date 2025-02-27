#! /usr/bin/env python

from solid2 import *
#we must import the greedy_scad_interface AFTER math because it overwrites sin, cos,....
from solid2.extensions.greedy_scad_interface import *

set_global_fn(32)
set_global_viewport_distance(abs(sin(get_animation_time() * 360)) * 10 + 5)
set_global_viewport_translation([0, -1, 0])
set_global_viewport_rotation([63, 0, get_animation_time() * 360])
set_global_viewport_fov(25)

def funny_cube():
    customized_color = CustomizerDropdownVariable(name = "cube_color",
                                                  default_value = "blue",
                                                  options = ["red", "green", "blue"],
                                                  label = "The color of the cube",
                                                  tab="Colors")

    customized_animation_factor = CustomizerSliderVariable(name = "anim_factor",
                                                           default_value = 1,
                                                           min_ = 1,
                                                           max_ = 10,
                                                           step = 0.5,
                                                           label = "Animation speed factor",
                                                           tab = "Animation")

    return color(customized_color) (
                cube(abs(sin(get_animation_time() * 360 * customized_animation_factor)), center=True)
           )

def funny_sphere():
    customized_color = ScadValue("cube_color")
    customized_animation_factor = ScadValue("anim_factor")

    return translate([0, -2, 0]) (
                color(customized_color) (
                    sphere(r = abs(sin(get_animation_time() * 360 * customized_animation_factor - 90)))
                )
           )

def do_nots():
    customized_color = ScadValue("cube_color")
    customized_animation_factor = ScadValue("anim_factor")

    #if customized_color == "blue":
    #    print("This causes a python runtime error!")

    #for i in range(customized_animation_factor):
    #    print("This causes a python runtime error!")

    #f = 1.0
    #f *= customized_animation_factor
    #for i in range(f):
    #    print("This causes a python runtime error! (and this is why it is called greedy)")

(funny_cube() + funny_sphere()).save_as_scad()
