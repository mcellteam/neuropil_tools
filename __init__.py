# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import os
import sys

# Needed for Blender Addon System
bl_info = {
    "name": "Neuropil Tools",
    "author": "Cailey Bromer, Tom Bartol",
    "version": (1, 0, 0),
    "blender": (2, 66, 1),
    "api": 55057,
    "location": "View3D > Tools > Neuropil Tools Panel",
    "description": "Modeling Tools for Brain Neuropil",
    "warning": "",
    "wiki_url": "http://www.mcell.org",
    "tracker_url": "https://github.com/mcellteam/neuropil_tools/issues",
    "category": "Cell Modeling"
}


# To support reregistration of Addon properly, try to access a package var,
# and if it's there, reload everything
# and if not, then do initial import
if "bpy" in locals():
    print("Reloading Neuropil Tools")
    import imp
    imp.reload(spine_head_analyzer)
    imp.reload(connectivity_tool)
else:
    print("Importing Neuropil Tools")
    from . import \
        spine_head_analyzer, \
        connectivity_tool


import bpy

# Enable the Addon
def register():

    # register all of the components of the Addon
    bpy.utils.register_module(__name__)

    # Extend the metadata of bpy.types.Object with our spine head metadata
    bpy.types.Object.spine_head_ana = bpy.props.PointerProperty(
        type=spine_head_analyzer.SpineHeadAnalyzerObjectProperty)

    # Extend the metadata of bpy.types.Object with our connectivity metadata
    bpy.types.Object.connectivity = bpy.props.PointerProperty(
        type=connectivity_tool.ConnectivityToolObjectProperty)

    print("Neuropil Tools registered")



# Disable the Addon
def unregister():
    # unregister all of the components of the Addon
    bpy.utils.unregister_module(__name__)
    print("Neuropil Tools unregistered")


