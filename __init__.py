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
from bpy_extras.io_utils import ImportHelper


# Needed for Blender Addon System
bl_info = {
    "name": "Neuropil Tools",
    "author": "Cailey Bromer, Tom Bartol",
    "version": (1, 2, 0),
    "blender": (2, 93, 0),
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
    imp.reload(io_import_multiple_objs)
    imp.reload(processor_tool)
    imp.reload(contour_vesicle_importer)
    imp.reload(spine_head_analyzer)
    imp.reload(connectivity_tool)


else:
    print("Importing Neuropil Tools")
    from . import \
        io_import_multiple_objs, \
        processor_tool, \
        contour_vesicle_importer, \
	spine_head_analyzer, \
        connectivity_tool



import bpy


def npt_register():
    io_import_multiple_objs.register()
    processor_tool.register()
    contour_vesicle_importer.register()
    spine_head_analyzer.register()
    connectivity_tool.register()


def npt_unregister():
    connectivity_tool.unregister()
    spine_head_analyzer.unregister()
    contour_vesicle_importer.unregister()
    processor_tool.unregister()
    io_import_multiple_objs.unregister()


# Enable the Addon
def register():

    # register all of the components of the Addon
    npt_register()

    # Extend the metadata of bpy.types.Object with our Processor Tool metadata
    bpy.types.Object.processor = bpy.props.PointerProperty(
        type=processor_tool.ProcessorToolObjectProperty)

   # Extend the metadata of bpy.types.Object with our Jaccard Tool metadata
    #bpy.types.Object.jaccard_obj = bpy.props.PointerProperty(
    #    type=jaccard_tool.JaccardToolObjectProperty)

    # Extend the metadata of bpy.types.Object with our spine head metadata
    bpy.types.Object.spine_head_ana = bpy.props.PointerProperty(
        type=spine_head_analyzer.SpineHeadAnalyzerObjectProperty)

    # Extend the metadata of bpy.types.Object with our connectivity metadata
    bpy.types.Object.connectivity = bpy.props.PointerProperty(
        type=connectivity_tool.ConnectivityToolObjectProperty)

    # Extend the metadata of bpy.types.Scene with our Processor Tool metadata
    bpy.types.Scene.test_tool = bpy.props.PointerProperty(
        type=processor_tool.ProcessorToolSceneProperty)

    # Extend the metadata of bpy.types.Scene with our Contour/Vesicle metadata
    bpy.types.Scene.contour_vesicle = bpy.props.PointerProperty(
        type=contour_vesicle_importer.ContourVesicleSceneProperty)

    # Extend the metadata of bpy.types.Scene with our Volumetric Analysis metadata
    bpy.types.Scene.volume_analyzer = bpy.props.PointerProperty(
        type=spine_head_analyzer.SpineHeadAnalyzerSceneProperty)

    print("Neuropil Tools registered")

 

# Disable the Addon
def unregister():
    # unregister all of the components of the Addon
    npt_unregister()

    #bpy.types.INFO_MT_file_import.remove(menu_func_import)
    print("Neuropil Tools unregistered")

#def register():
#    bpy.utils.register_class(ImportMultipleObjs)
    

#def unregister():
#    bpy.utils.unregister_class(ImportMultipleObjs)
    

#if __name__ == "__main__":
#    register()



