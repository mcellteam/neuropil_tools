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

"""
This file contains the classes for Diameter Tool.

"""

# stuff to call Volrover individual executables
import sys
import subprocess
import os
import re
#import numpy

# blender imports
import bpy
# IMPORT SWIG MODULE(s)
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, \
    IntVectorProperty, PointerProperty, StringProperty
import mathutils

from bpy_extras.io_utils import ImportHelper


# python imports

import re
from  re import compile
import numpy as np
import neuropil_tools
import cellblender

# register and unregister are required for Blender Addons
# We use per module class registration/unregistration


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

#Define operators

trace_filter_name = ""

class NEUROPIL_OT_impser(bpy.types.Operator, ImportHelper):
    """Import from RECONSTRUCT Series file format (.ser)"""
    bl_idname = "contour_vesicle.impser"
    bl_label = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_description = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'}            

    filename_ext = ".ser"
    filter_glob = StringProperty(default="*.ser", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):  
        context.scene.contour_vesicle.read_contour_list(context,self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}       


class NEUROPIL_OT_include_contour(bpy.types.Operator):
    bl_idname = "contour_vesicle.include_contour"
    bl_label = "Add Selected Contour to Include List"    
    bl_description = "Add Selected Contour to Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.contour_vesicle.include_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_include_filtered_contour(bpy.types.Operator):
    bl_idname = "contour_vesicle.include_filtered_contour"
    bl_label = "Add All Filtered Contours to Include List"    
    bl_description = "Add All Filtered Contours to Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.contour_vesicle.include_filtered_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_remove_contour(bpy.types.Operator):
    bl_idname = "contour_vesicle.remove_contour"
    bl_label = "Remove Selected Contour and Mesh from Include List"
    bl_description = "Remove Selected Contour and Mesh from Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.contour_vesicle.remove_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_remove_contour_all(bpy.types.Operator):
    bl_idname = "contour_vesicle.remove_contour_all"
    bl_label = "Clear All Contours from Contour List"
    bl_description = "Clear All Contours from Contour List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.contour_vesicle.remove_contour_all(context)
        return {'FINISHED'}


class NEUROPIL_OT_import_all_contours(bpy.types.Operator):
    bl_idname = "contour_vesicle.import_all_contours"
    bl_label = "Import Contour Objects for All Included Contours"    
    bl_description = "Import Contour Objects for All Included Contours"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.contour_vesicle.import_contours(context, contour_name = None)
        return {'FINISHED'}


class NEUROPIL_OT_import_selected_contour(bpy.types.Operator):
    bl_idname = "contour_vesicle.import_selected_contour"
    bl_label = "Import Contour Object for Selected Contour"    
    bl_description = "Import Contour Object for Selected Contour"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        contour_name = context.scene.contour_vesicle.get_active_include(context)
        if contour_name:
          context.scene.contour_vesicle.import_contours(context, contour_name = contour_name)
        return {'FINISHED'}


class NEUROPIL_PT_ContourVesicleImporter(bpy.types.Panel):
    bl_label = "Contour/Vesicle Importer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Neuropil Tools"

    def draw(self, context):
        if context.scene != None:
            context.scene.contour_vesicle.draw_panel(context, panel=self)


#layout object lists
class Contour_Ves_UL_draw_item(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
        global trace_filter_name
       
        trace_filter_name = self.filter_name
        self.use_filter_sort_alpha = True
        layout.label(item.name)


class Include_Ves_UL_draw_item(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        scn = bpy.context.scene
        self.use_filter_sort_alpha = True    
        if item.imported == True:
            if item.vesicle_obj:
              layout.label(item.name, icon='GROUP_VERTEX')
            else:
              layout.label(item.name, icon='COLLAPSEMENU')
        else:
            layout.label(item.name)


class ContourVesicleObjectProperty(bpy.types.PropertyGroup):
    vesicle_obj = BoolProperty(name="OBJ is Vesicle", default=False)

    # Set obj as active object with entire mesh unhidden and selected
    #   with Object Mode set
    def select_obj(self, context, obj):
        if context.active_object is not None:
          bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')


class ContourNameProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Contour name", default ="")
   
    def init_contour(self,context,name):
        self.name = name


class IncludeNameProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Include name", default ="")
    imported = BoolProperty(name = "Object Imported", default = False)
    vesicle_obj = BoolProperty(name="OBJ is Vesicle", default=False)
    filter_name = StringProperty(name="Read manually filtered names for Include", default= "")

    def init_include(self,context,name):
        self.name = name



class ContourVesicleSceneProperty(bpy.types.PropertyGroup):
    contour_list = CollectionProperty(
        type = ContourNameProperty, name = "Contour List")
    active_contour_index = IntProperty(name="Active Contour Index", default=0)
    include_list = CollectionProperty(
        type = IncludeNameProperty, name = "Include List")
    active_include_index = IntProperty(name="Active Include Index", default=0)
    filepath = StringProperty(name = "Remember Active Filepath", default= "")
    min_section = StringProperty(name="Minimum Reconstruct Section File", default= "")
    max_section = StringProperty(name="Maximum Reconstruct Section File", default= "")
    section_thickness = StringProperty(name="Maximum Reconstruct Section File", default= "0.05")
    vesicle_import = BoolProperty(name="Import Contours as Vesicles", default=False)
    

    def add_contour(self,context,contour_name,mode):
        if mode == 'contour':
            new_contour=self.contour_list.add()
            new_contour.init_contour(context,contour_name)
        else:
            new_contour=self.include_list.add()
            new_contour.init_include(context,contour_name)
        return(new_contour)


    def read_contour_list(self, context, filepath):
        self.filepath = filepath
        ser_prefix = self.filepath

        first_re = compile('first3Dsection="(\d*)"')
        last_re = compile('last3Dsection="(\d*)"')
        default_thick_re = compile('defaultThickness="(.*)"')

        ser_data = open(ser_prefix[:-4] + ".ser", "r").read()
        self.min_section = first_re.search(ser_data).group(1)
        self.min_section = str(int(self.min_section))
        self.max_section = last_re.search(ser_data).group(1)
        self.max_section = str(int(self.max_section))
        self.section_thickness = default_thick_re.search(ser_data).group(1)
        print("First Section:  %s" % (self.min_section))
        print("Last Section:  %s" % (self.max_section))
        print("Section Thickness:  %s" % (self.section_thickness))

        contour_re = compile('Contour\ name=\"(.*?)\"')

        all_names = []
        for i in range(int(self.min_section), int(self.max_section)+1):
            print(i)
            all_names += contour_re.findall(open(ser_prefix[:-3] + str(i)).read())
         # Now put each item in this python list into a Blender collection property
        contour_names = sorted(list(set(all_names))) 
       
        for name in contour_names:
            self.add_contour(context, name,"contour")
        for item in self.contour_list:
            print(item)
        return(self.contour_list)
    
    
    def include_filtered_contour(self,context):
        for item in self.contour_list:
            if ((re.search(trace_filter_name, item.name)) or (re.search(trace_filter_name, item.name)))  and item.name not in self.include_list:
                self.add_contour(context, item.name, "include")
        return(self.include_list)


    def include_contour(self, context):
        name = self.contour_list[self.active_contour_index].name
        if name not in self.include_list:
            self.add_contour(context, name, "include")
        return(self.include_list)


    def get_active_include(self, context):
        scn = bpy.context.scene

        if len(self.include_list):
          obj_name = self.include_list[self.active_include_index].name
        else:
          obj_name = None
           
        return(obj_name)


    def remove_contour(self, context):
        #for name in self.contour_list:
        if (len(self.include_list) > 0):
            if self.include_list[self.active_include_index].vesicle_obj:
              obj_name = self.include_list[self.active_include_index].name
            else:
              obj_name = self.include_list[self.active_include_index].name+'_contours'
            ser_dir = os.path.split(self.filepath)[0]
            ser_file = os.path.split(self.filepath)[-1]

            ser_prefix = os.path.splitext(ser_file)[0]
            out_file = ser_dir + '/' + ser_prefix + "_output"

            if bpy.data.objects.get(obj_name) is not None:
                bpy.ops.object.select_all(action='DESELECT')
                obj = bpy.context.scene.objects[obj_name]
                obj.select = True
                context.scene.objects.active = obj
                m = obj.data
                context.scene.objects.unlink(obj)
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(m)
                if os.path.exists(out_file + '/'+ obj_name + '_tiles.rawc'):
                    os.remove(out_file + '/'+ obj_name + '_tiles.rawc')
                if os. path.exists(out_file + '/'+ obj_name + '.obj'):
                    os.remove(out_file + '/'+ obj_name + '.obj')
            self.include_list.remove(self.active_include_index)
               
        return(self.include_list)


    def remove_contour_all(self, context):
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]

        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"

        self.contour_list.clear()
               
        return(self.contour_list)


    def import_contours(self, context, contour_name = None):
        #set variables
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]

        ser_prefix = os.path.splitext(ser_file)[0]
        ser_file_basename = ser_dir + '/' + ser_prefix
        
        if contour_name == None:
          import_list = [ i.name for i in self.include_list ]
        else:
          import_list = [ contour_name ]
       
        #import contours
        for contour_name in import_list:
            print('\nImporting Contours for: %s\n' % (contour_name))
            if self.vesicle_import:
                  check_obj_name = contour_name
            else: 
                  check_obj_name = contour_name + "_contours"
            if bpy.data.objects.get(check_obj_name) is None:
                if self.vesicle_import:
                  self.include_list[contour_name].vesicle_obj = True
                  obj_file = ser_dir + '/' + contour_name + '.obj'
                  recon2obj_cmd = "recon2obj -vesicles -object %s -section_thickness %s %s %s %s > %s" % (contour_name, self.section_thickness, ser_file_basename, self.min_section, self.max_section, obj_file)
                  print("Importing as Vesicles: %s" % (recon2obj_cmd))
                else:
                  self.include_list[contour_name].vesicle_obj = False
                  obj_file = ser_dir + '/' + contour_name + '_contours.obj'
                  recon2obj_cmd = "recon2obj -object %s -section_thickness %s %s %s %s > %s" % (contour_name, self.section_thickness, ser_file_basename, self.min_section, self.max_section, obj_file)
                  print("Importing as Contours: %s" % (recon2obj_cmd))
                subprocess.check_output([recon2obj_cmd],shell=True)
            #import obj
                bpy.ops.import_scene.obj(filepath=obj_file, axis_forward='Y', axis_up="Z")
                self.include_list[contour_name].imported = True


    #Draw panel
    def draw_panel(self, context, panel):
        layout = panel.layout
        row = layout.row()
        row.operator("contour_vesicle.impser", text="Import .ser file")  
        row = layout.row()
        row.label(text="Series Contour List:", icon='CURVE_DATA')
        row.label(text="Import Include List:", icon='COLLAPSEMENU')
        row = layout.row()
        row.template_list("Contour_Ves_UL_draw_item","contours_in_ser_file",
                          bpy.context.scene.contour_vesicle, "contour_list",
                          self, "active_contour_index",
                          rows=2)
        row.template_list("Include_Ves_UL_draw_item","included_in_ser_file",
                          bpy.context.scene.contour_vesicle, "include_list",
                          self, "active_include_index",
                          rows=2)
        row = layout.row()
        row.prop(self,"vesicle_import",text="Import as Vesicles")
        row = layout.row()
        row.operator("contour_vesicle.include_contour", text="Include Contour") 
        row.operator("contour_vesicle.remove_contour", text="Remove Contour")

        row = layout.row()
        row.operator("contour_vesicle.include_filtered_contour", text = "Include Current Filtered Contours") 
        row.operator("contour_vesicle.import_selected_contour", text="Import Selected Include Contour")

        row = layout.row()
        row.operator("contour_vesicle.remove_contour_all", text = "Clear Contour List") 
        row.operator("contour_vesicle.import_all_contours", text="Import All Included Contours")


