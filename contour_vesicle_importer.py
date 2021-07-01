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
import numpy as np
import glob
import neuropil_tools
import cellblender


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
    filter_glob: StringProperty(default="*.ser", options={'HIDDEN'})
    filepath: StringProperty(subtype='FILE_PATH')

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
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Neuropil Tools"

    def draw(self, context):
        if context.scene != None:
            context.scene.contour_vesicle.draw_panel(context, panel=self)


#layout object lists
class NEUROPIL_UL_contour_ves_trace_draw_item(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
        global trace_filter_name
       
        trace_filter_name = self.filter_name
        self.use_filter_sort_alpha = True
        layout.label(text=item.name)


class NEUROPIL_UL_contour_ves_include_draw_item(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        scn = bpy.context.scene
        self.use_filter_sort_alpha = True    
        if item.imported == True:
            if item.vesicle_obj:
              layout.label(text=item.name, icon='GROUP_VERTEX')
            else:
              layout.label(text=item.name, icon='SORTSIZE')
        else:
            layout.label(text=item.name)


class ContourVesicleObjectProperty(bpy.types.PropertyGroup):
    vesicle_obj: BoolProperty(name="OBJ is Vesicle", default=False)

    # Set obj as active object with entire mesh unhidden and selected
    #   with Object Mode set
    def select_obj(self, context, obj):
        if context.active_object is not None:
          bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')


class ContourNameProperty(bpy.types.PropertyGroup):
    name: StringProperty(name= "Contour name", default ="")
   
    def init_contour(self,context,name):
        self.name = name


class IncludeNameProperty(bpy.types.PropertyGroup):
    name: StringProperty(name= "Include name", default ="")
    imported: BoolProperty(name = "Object Imported", default = False)
    vesicle_obj: BoolProperty(name="OBJ is Vesicle", default=False)
    filter_name: StringProperty(name="Read manually filtered names for Include", default= "")

    def init_include(self,context,name):
        self.name = name



class ContourVesicleSceneProperty(bpy.types.PropertyGroup):
    contour_list: CollectionProperty(
        type = ContourNameProperty, name = "Contour List")
    active_contour_index: IntProperty(name="Active Contour Index", default=0)
    include_list: CollectionProperty(
        type = IncludeNameProperty, name = "Include List")
    active_include_index: IntProperty(name="Active Include Index", default=0)
    filepath: StringProperty(name = "Remember Active Filepath", default= "")
    min_section: StringProperty(name="Minimum Reconstruct Section File", default= "")
    max_section: StringProperty(name="Maximum Reconstruct Section File", default= "")
    section_thickness: StringProperty(name="Maximum Reconstruct Section File", default= "0.05")
    vesicle_import: BoolProperty(name="Import Contours as Vesicles", default=False)
    

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
        ser_file = self.filepath
        ser_prefix = os.path.splitext(self.filepath)[0]

        first_re = re.compile('first3Dsection="(\d*)"')
        last_re = re.compile('last3Dsection="(\d*)"')
        default_thick_re = re.compile('defaultThickness="(.*)"')

        ser_data = open(ser_file, "r").read()
        self.section_thickness = default_thick_re.search(ser_data).group(1)

        trace_file_glob = sorted(glob.glob(ser_prefix + os.path.extsep + '[0-9]*'))
        pat = ser_prefix + '\\' + os.path.extsep + '[0-9]+'
        patc = re.compile(pat)
        trace_file_list = [patc.fullmatch(item).string for item in trace_file_glob if patc.fullmatch(item)]
        trace_num_list = sorted([int(os.path.splitext(fn)[1][1:]) for fn in trace_file_list])

        # create list of contiguous runs of section file numbers
        r_list = []
        cur_r = [0,1]
        r_next = trace_num_list[cur_r[0]]+1

        for i in range(1,len(trace_num_list)):
          if trace_num_list[i] == r_next:
            r_next += 1
            cur_r[1] += 1
            if i == len(trace_num_list)-1:
              r_list.append(cur_r)
          else:
            r_list.append(cur_r)
            cur_r = [i,1]
            r_next = trace_num_list[cur_r[0]]+1

        r_list = np.array(r_list)
        print('')
        print(trace_num_list)
        print('')
        print(r_list)
        print('')

        # set min and max section numbers of longest contiguous run found
        r_max = r_list[np.argmax(r_list[:, 1])]
        self.min_section = str(trace_num_list[r_max[0]])
        self.max_section = str(trace_num_list[r_max[0]+r_max[1]-1])

        contour_re = re.compile('Contour\ name=\"(.*?)\"')

        all_names = []
        for i in range(int(self.min_section), int(self.max_section)):
            trace_file_name = '%s%s%d' % (ser_prefix, os.path.extsep, i)
            print('Reading contour names in trace file: %s' % (trace_file_name))
#            all_names += contour_re.findall(open(ser_prefix[:-3] + str(i)).read())
            all_names += contour_re.findall(open(trace_file_name).read())
         # Now you would put each item in this python list into a Blender collection property
        contour_names = sorted(list(set(all_names)))

        for name in contour_names:
            self.add_contour(context, name,"contour")
        for item in self.contour_list:
            print(item)

    
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
                obj = bpy.context.scene.collection.children[0].objects[obj_name]
                obj.select = True
                context.view_layer.objects.active = obj
                m = obj.data
                context.scene.collection.children[0].objects.unlink(obj)
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
        bin_dir = os.path.join(os.path.dirname(__file__), 'bin')
        recon2obj_bin = os.path.join(bin_dir,'recon2obj')

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
                  recon2obj_cmd = recon2obj_bin + " -vesicles -object %s -section_thickness %s %s %s %s > %s" % (contour_name, self.section_thickness, ser_file_basename, self.min_section, self.max_section, obj_file)
                  print("Importing as Vesicles: %s" % (recon2obj_cmd))
                else:
                  self.include_list[contour_name].vesicle_obj = False
                  obj_file = ser_dir + '/' + contour_name + '_contours.obj'
                  recon2obj_cmd = recon2obj_bin + " -object %s -section_thickness %s %s %s %s > %s" % (contour_name, self.section_thickness, ser_file_basename, self.min_section, self.max_section, obj_file)
                  print("Importing as Contours: %s" % (recon2obj_cmd))
                subprocess.check_output([recon2obj_cmd],shell=True)
            #import obj
                bpy.ops.import_scene.obj(filepath=obj_file, axis_forward='Y', axis_up="Z")
                self.include_list[contour_name].imported = True


    #Draw panel
    def draw_panel(self, context, panel):
        layout = panel.layout
        row = layout.row()
        row.label(text='Import Reconstruct Series:', icon='MOD_ARRAY')
        row = layout.row(align=True)
        row.prop(self, "filepath", text='')
        row.operator('contour_vesicle.impser', icon='FILEBROWSER', text='')

        row = layout.row()
        row.label(text = 'section thickness: ' + self.section_thickness)
        row.label(text = 'min section #: ' + self.min_section)
        row.label(text = 'max section #: ' + self.max_section)

        row = layout.row()
        row.label(text="Series Contour List:", icon='CURVE_DATA')
        row.label(text="Import Include List:", icon='SORTSIZE')
        row = layout.row()
        col = row.column()
        col.template_list("NEUROPIL_UL_contour_ves_trace_draw_item","contours_in_ser_file",
                          bpy.context.scene.contour_vesicle, "contour_list",
                          self, "active_contour_index",
                          rows=2)
        col = row.column(align=True)
        col.operator("contour_vesicle.include_contour", icon='FORWARD', text='')
        col.operator("contour_vesicle.include_filtered_contour", icon='EXPORT', text='')
        col.operator("contour_vesicle.remove_contour_all", icon='X', text='')

        col = row.column()
        col.template_list("NEUROPIL_UL_contour_ves_include_draw_item","included_in_ser_file",
                          bpy.context.scene.contour_vesicle, "include_list",
                          self, "active_include_index",
                          rows=2)
        col = row.column(align=True)
        col.operator("contour_vesicle.remove_contour", icon='REMOVE', text='')
        col.operator("contour_vesicle.import_selected_contour", icon='CURVE_DATA', text='')
        col.operator("contour_vesicle.import_all_contours", icon='ARMATURE_DATA', text='')

        row = layout.row()
        row.prop(self,"vesicle_import",text="Import as Vesicles")
        row = layout.row()


classes = ( 
            NEUROPIL_OT_impser,
            NEUROPIL_OT_include_contour,
            NEUROPIL_OT_include_filtered_contour,
            NEUROPIL_OT_remove_contour,
            NEUROPIL_OT_remove_contour_all,
            NEUROPIL_OT_import_all_contours,
            NEUROPIL_OT_import_selected_contour,
            NEUROPIL_PT_ContourVesicleImporter,
            NEUROPIL_UL_contour_ves_trace_draw_item,
            NEUROPIL_UL_contour_ves_include_draw_item,
            ContourVesicleObjectProperty,
            ContourNameProperty,
            IncludeNameProperty,
            ContourVesicleSceneProperty,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

