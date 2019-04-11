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
import shutil
import subprocess
import os
import re

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
import gamer

# register and unregister are required for Blender Addons
# We use per module class registration/unregistration


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


#Define Operators

class NEUROPIL_OT_impser(bpy.types.Operator, ImportHelper):
    """Import from RECONSTRUCT Series file format (.ser)"""
    bl_idname = "processor_tool.impser"
    bl_label = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_description = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'}            

    filename_ext = ".ser"
    filter_glob = StringProperty(default="*.ser", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):  
        context.scene.test_tool.generate_contour_list(context,self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}       


class NEUROPIL_OT_include_contour(bpy.types.Operator):
    bl_idname = "processor_tool.include_contour"
    bl_label = "Add Selected Contour to Include List"    
    bl_description = "Add Selected Contour to Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.include_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_include_filter_contour(bpy.types.Operator):
    bl_idname = "processor_tool.include_filter_contour"
    bl_label = "Add All Filtered Contours to Include List"    
    bl_description = "Add All Filtered Contours to Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.include_filter_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_remove_contour(bpy.types.Operator):
    bl_idname = "processor_tool.remove_contour"
    bl_label = "Remove Selected Contour and Mesh from Include List"
    bl_description = "Remove Selected Contour and Mesh from Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.remove_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_remove_contour_all(bpy.types.Operator):
    bl_idname = "processor_tool.remove_contour_all"
    bl_label = "Clear All Contours from Trace List"
    bl_description = "Clear All Contours from Trace List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.remove_contour_all(context)
        return {'FINISHED'}


class NEUROPIL_OT_remove_comp(bpy.types.Operator):
    bl_idname = "processor_tool.remove_components"
    bl_label = "Remove Multiple Components tag"    
    bl_description = "Remove Multiple Components tag"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.remove_components(context)
        return {'FINISHED'}   


class NEUROPIL_OT_tile_mesh(bpy.types.Operator):
    bl_idname = "processor_tool.generate_mesh_object"
    bl_label = "Interpolate and Generate Meshes from All Included Contours"    
    bl_description = "Interpolate and Generate Meshes from All Included Contours"    
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        context.scene.test_tool.generate_mesh_object(context)
        context.scene.test_tool.fix_mesh(context,"double")
        return {'FINISHED'}


class NEUROPIL_OT_tile_one_mesh(bpy.types.Operator):
    bl_idname = "processor_tool.generate_mesh_object_single"
    bl_label = "Interpolate and Generate Meshes from Selected Contour"    
    bl_description = "Interpolate and Generate Meshes from Selected Contour"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.scene.test_tool.generate_mesh_object_single(context)
        context.scene.test_tool.fix_mesh(context,"single")
        return {'FINISHED'}


class NEUROPIL_OT_fix_mesh(bpy.types.Operator):
    bl_idname = "processor_tool.fix_mesh"
    bl_label = "Fix Selected Mesh Object"
    bl_description = "Fix Selected Mesh Object"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.fix_mesh(context,"single")
        return {'FINISHED'}   


class NEUROPIL_OT_select_obje(bpy.types.Operator):
    bl_idname = "processor_tool.select_obje"
    bl_label = "Select Faces of OBJ"
    bl_description = "Select Faces of OBJ"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.select_obje(context,'spine')
        return {'FINISHED'}


#class NEUROPIL_OT_ImportMultipleObjs(bpy.types.Operator, ImportHelper):
#    """This appears in the tooltip of the operator and in the generated docs"""
#    bl_idname = "import_scene.multiple_objs"
#    bl_label = "Import multiple OBJ's"
#    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
#    filename_ext = ".obj"

#    filter_glob = StringProperty(
#            default="*.obj",
#            options={'HIDDEN'},
#            )

    #def execute(self, context):
    #    context.object.processor.multiple_objs(context)
    #    return {'FINISHED'}


class NEUROPIL_OT_add_contact_pattern(bpy.types.Operator):
    bl_idname = "processor_tool.add_contact_pattern"
    bl_label = "Define New Contact Pattern"
    bl_description = "Define New Contact Pattern"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.add_contact_pattern(context)
        return {'FINISHED'}


class NEUROPIL_OT_remove_contact_pattern(bpy.types.Operator):
    bl_idname = "processor_tool.remove_contact_pattern"
    bl_label = "Remove Contact Pattern"
    bl_description = "Remove Contact Pattern"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.remove_contact_pattern(context)
        return {'FINISHED'}


class NEUROPIL_OT_smooth(bpy.types.Operator):
    bl_idname = "processor_tool.smooth"
    bl_label = "Smooth Selected Object"
    bl_description = "Smooth Selected Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.select_obje(context,'spine')
        context.active_object.processor.smooth(context)
        return {'FINISHED'}


class NEUROPIL_OT_smooth_all(bpy.types.Operator):
    bl_idname = "processor_tool.smooth_all"
    bl_label = "Smooth All Objects"
    bl_description = "Smooth All Objects"
    bl_options = {'REGISTER', 'UNDO'}
  
    def execute(self, context):
        context.scene.test_tool.smooth_all(context)
        return {'FINISHED'}


class NEUROPIL_OT_tag_contacts(bpy.types.Operator):
    bl_idname = "processor_tool.tag_contacts"
    bl_label = "Tag Contact Region On All Objects"
    bl_description = "Tag Contact Region On All Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.tag_contacts(context,"double")
        return {'FINISHED'}


class NEUROPIL_OT_merge_objs(bpy.types.Operator):
    bl_idname = "processor_tool.merge_objs"
    bl_label = "Merge Objects"
    bl_description = "Merge Objects"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        context.scene.test_tool.merge_objs(context)
        return {'FINISHED'}


class NEUROPIL_OT_tag_contact_single(bpy.types.Operator):
    bl_idname = "processor_tool.tag_contact_single"
    bl_label = "Tag Contact Region On Selected Object"
    bl_description = "Tag Contact Region On Selected Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.tag_contacts(context,"single")
        return {'FINISHED'}


class GAMER_OT_coarse_dense(bpy.types.Operator):
    bl_idname = "gamer.coarse_dense"
    bl_label = "Coarse Dense"
    bl_description = "Decimate selected dense areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.coarse_dense(context)
        return {'FINISHED'}


class GAMER_OT_coarse_flat(bpy.types.Operator):
    bl_idname = "gamer.coarse_flat"
    bl_label = "Coarse Flat"
    bl_description = "Decimate selected flat areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.coarse_flat(context)
        return {'FINISHED'}


class GAMER_OT_smooth(bpy.types.Operator):
    bl_idname = "gamer.smooth"
    bl_label = "Smooth"
    bl_description = "Smooth selected vertices of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.smooth(context)
        return {'FINISHED'}

 
class GAMER_OT_normal_smooth(bpy.types.Operator):
    bl_idname = "gamer.normal_smooth"
    bl_label = "Normal Smooth"
    bl_description = "Smooth faces normals of selected faces of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.normal_smooth(context)
        return {'FINISHED'}


#layout object lists
class Trace_UL_draw_item(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
       
        self.use_filter_sort_alpha = True
        layout.label(item.name)


class Include_UL_draw_item(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        scn = bpy.context.scene
        self.use_filter_sort_alpha = True    
        #if item.non_manifold == True:
     #    layout.label(item.name, icon='ERROR')
        if item.multi_component == True:
            layout.label(item.name, icon='NLA')
        elif item.genus_issue == True:
            layout.label(item.name, icon = "MESH_TORUS")
        elif item.generated == True:
            layout.label(item.name, icon='MESH_ICOSPHERE')
        else:
            layout.label(item.name)


class Contact_Pattern_UL_draw_item(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
       
        self.use_filter_sort_alpha = True
        layout.label(item.name)


class SCN_UL_obj_draw_item(bpy.types.UIList):

    use_base_name_filter = BoolProperty(name = "Filter Object List by Base Names", default = False)
  
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index, flt_flag):

        match_text = '    [ '
        for contact_pattern in item.processor.contact_pattern_match_list:
            match_text += contact_pattern.name + ' '
        match_text += ']'

        if item.processor.multi_synaptic == True:
            layout.label(item.name + match_text, icon = "MANIPUL")
        elif item.processor.newton == True:
            layout.label(item.name + match_text, icon='FILE_TICK')
        elif item.processor.smoothed == True:
            layout.label(item.name + match_text, icon='MOD_SMOOTH')
        else:
            layout.label(item.name + match_text)

    def draw_filter(self, context, layout):
        box1 = layout.box()
        row = box1.row()
        row.prop(self, 'use_base_name_filter', text='Use Base Name Filter')


    def filter_items(self, context, data, propname):
      helper_funcs = bpy.types.UI_UL_list
      
      objs = getattr(data, propname)

      scn_tt = bpy.context.scene.test_tool
      if scn_tt.contact_pattern_list:
        contact_pattern = scn_tt.contact_pattern_list[scn_tt.active_contact_pattern_index]
      else:
        contact_pattern = None
      
      flt_flags = []
      flt_neworder = []

      if self.use_base_name_filter and contact_pattern:
        bn1_regex = contact_pattern.base_name_1_regex
        bn2_regex = contact_pattern.base_name_2_regex
  
        bn1_recomp = re.compile(bn1_regex)
        bn2_recomp = re.compile(bn2_regex)
          
        flt_flags = [ self.bitflag_filter_item*((bn1_recomp.fullmatch(obj.name)!=None) or (bn2_recomp.fullmatch(obj.name)!=None)) for obj in objs ]
      else:
        flt_flags = [self.bitflag_filter_item]*len(objs)

      flt_neworder = helper_funcs.sort_items_by_name(objs, 'name')

      return flt_flags, flt_neworder


class SCN_TestTool(bpy.types.Panel):
    bl_label = "3DEM Processor Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Neuropil Tools"

    def draw(self, context):
        if context.scene != None:
            context.scene.test_tool.draw_panel(context, panel=self)


def pattern_change_callback(self,context):
  self.pattern_change_callback(context)
  return


class ContourNameSceneProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Contour name", default ="")
    
    def init_contour(self,context,name):
        self.name = name


class ContactPatternObjectProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Contact Object Pattern", default ="")
    base_name_1_pattern = StringProperty("Base Name 1 Pattern", default = "")
    base_name_2_pattern = StringProperty("Base Name 2 Pattern", default = "")
    contact_name_pattern = StringProperty("Contact Name Pattern", default = "")
    base_name_1_regex = StringProperty("Base Name 1 Regex", default = "")
    base_name_2_regex = StringProperty("Base Name 2 Regex", default = "")
    contact_name_regex = StringProperty("Contact Name Regex", default = "")


class ContactPatternSceneProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Contact Object Pattern", default ="")
    base_name_1_pattern = StringProperty("Base Name 1 Pattern", default = "", update=pattern_change_callback)          
    base_name_2_pattern = StringProperty("Base Name 2 Pattern", default = "", update=pattern_change_callback)          
    contact_name_pattern = StringProperty("Contact Name Pattern", default = "", update=pattern_change_callback)          
    base_name_1_regex = StringProperty("Base Name 1 Regex", default = "")
    base_name_2_regex = StringProperty("Base Name 2 Regex", default = "")
    contact_name_regex = StringProperty("Contact Name Regex", default = "")


    def pattern_change_callback(self,context):

        self.name = self.base_name_1_pattern + self.contact_name_pattern + self.base_name_2_pattern
        # FIXME:  Check for uniqueness of name here:

        # convert patterns to formal regex
        bn1_regex = self.base_name_1_pattern.replace('#','[0-9]')
        bn1_regex = bn1_regex.replace('*','.*')
        bn2_regex = self.base_name_2_pattern.replace('#','[0-9]')
        bn2_regex = bn2_regex.replace('*','.*')
        c_regex = self.contact_name_pattern.replace('#','[0-9]')
        c_regex = c_regex.replace('*','.*')

        self.base_name_1_regex = bn1_regex
        self.base_name_2_regex = bn2_regex
        self.contact_name_regex = c_regex

        # update (rebuild) match list for each object
        for obj in bpy.context.scene.objects:
           obj.processor.update_contact_pattern_match_list(context, obj)
        return


    def draw_props(self,layout):
        row = layout.row()
        row.label(text="Define Name Patterns for Tagging Contacts")  
        row = layout.row()
        row.label(text="(Use '#' to signify an integer,  '*' to signify a wildcard character)")  
        row = layout.row()
        row.prop(self, 'base_name_1_pattern', text='Base Name 1 Pattern')
        row = layout.row()
        row.prop(self, 'base_name_2_pattern', text='Base Name 2 Pattern')
        row = layout.row()
        row.prop(self, 'contact_name_pattern', text='Contact Name Pattern')
        row = layout.row()
        row.label(text='Contact Object Pattern:   ' + self.base_name_1_pattern + self.contact_name_pattern + self.base_name_2_pattern)




class IncludeNameSceneProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Include name", default ="")
    generated = BoolProperty(name = "Mesh Object Generated", default = False)
    multi_component = BoolProperty(name = "Multiple Components in Mesh", default = False)
    non_manifold = BoolProperty(name = "Non-manifold Mesh", default = False) 
    genus_issue = BoolProperty(name = "Genus > 0", default = False)         
    filter_name = StringProperty(name="Read manually filtered names for Include", default= "")
    spine_filter_name = StringProperty(name="Read manually filtered names for Include", default= "")
    problem = BoolProperty(name = "Problem Tagging", default = False)
    
    def init_include(self,context,name):
        self.name = name


class ProcessorToolObjectProperty(bpy.types.PropertyGroup):
    active_obj_region_index = IntProperty(name="Active OBJ Index", default=0)
    n_components = IntProperty(name="Number of Components in Mesh", default=0)
    smoothed = BoolProperty(name="Smoothed Object", default=False)
    newton = BoolProperty(name = "New Object", default=False)
    multi_synaptic = BoolProperty(name = "Multiple Synapses", default = False)
    fix_all_fail = BoolProperty(name = "Failed to Fix Obj", default = False)
    namestruct = StringProperty("Base and Meta Object Struct", default = "")
    contact_pattern_match_list = CollectionProperty(type = ContactPatternObjectProperty, name = "Contact Pattern Match List")


    def update_contact_pattern_match_list(self, context, obj):
      # Clear current match list
      self.contact_pattern_match_list.clear()

      # Rebuild match list
      contact_pattern_list = bpy.context.scene.test_tool.contact_pattern_list
      for contact_pattern in contact_pattern_list:
        bn1_regex = contact_pattern.base_name_1_regex
        bn2_regex = contact_pattern.base_name_2_regex

        bn1_recomp = re.compile(bn1_regex)
        bn2_recomp = re.compile(bn2_regex)

        if bn1_recomp.fullmatch(obj.name) or bn2_recomp.fullmatch(obj.name):
          new_match_pattern = self.contact_pattern_match_list.add()
          new_match_pattern.name = contact_pattern.name
          new_match_pattern.base_name_1_pattern = contact_pattern.base_name_1_pattern
          new_match_pattern.base_name_2_pattern = contact_pattern.base_name_2_pattern
          new_match_pattern.contact_name_pattern = contact_pattern.contact_name_pattern
          new_match_pattern.base_name_1_regex = contact_pattern.base_name_1_regex
          new_match_pattern.base_name_2_regex = contact_pattern.base_name_2_regex
          new_match_pattern.contact_name_regex = contact_pattern.contact_name_regex
        
      return
          

    def select_obje(self, context, obje):
        if context.active_object is not None:
          bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obje.select = True
        bpy.context.scene.objects.active = obje
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

    def set_n_components(self,context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.active_object
        mesh = obj.data

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Count total vertices and number of vertices contiguous with vertex 0
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh.vertices[0].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_linked()
        n_v_tot = len(mesh.vertices)
        n_v_sel = mesh.total_vert_sel
        bpy.ops.object.mode_set(mode='OBJECT')

        # Loop over disjoint components
        n_components = 1
        while (n_v_sel < n_v_tot):
            n_components += 1
            # make list of selected indices
            vl1 = [v.index for v in mesh.vertices if v.select == True]
            # make list of indices of remaining component(s)
            vl2 = [v.index for v in mesh.vertices if v.select == False]
            # Grow selection with vertices contiguous with first vertex of remainder
            mesh.vertices[vl2[0]].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked()

            # Count number of vertices now selected and loop again if necessary
            n_v_sel = mesh.total_vert_sel
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        self.n_components = n_components


    def smooth(self, context):
        """ Smooth using GAMer """
        print('Smoothing: %s' % (context.active_object.name))
        gamer_mip = context.scene.gamer.mesh_improve_panel
        gamer_mip.dense_rate = 2.5
        gamer_mip.dense_iter = 1
        gamer_mip.max_min_angle = 20.0
        gamer_mip.smooth_iter = 10
        gamer_mip.preserve_ridges = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.beautify_fill(angle_limit=1.57)
        bpy.ops.mesh.subdivide(number_cuts=2)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
#        bpy.ops.mesh.select_all(action='DESELECT')
#        bpy.ops.object.mode_set(mode='OBJECT')
        self.smoothed = True
        obj = context.active_object
        obj.processor.update_contact_pattern_match_list(context, obj)

        # ADD OBJ2MCELL
        return('FINISHED')


    # Export object in Wavefront OBJ file format
    def export_obj(self, context, obj, obj_file_name):

        m = obj.data
        obj_file =  open(obj_file_name, 'w')

        # Export vertices
        for v in m.vertices:
          obj_file.write('v %f %f %f\n' % (v.co.x, v.co.y, v.co.z))

#        obj_file.write('s off\n')
        # Export polygons
        for p in m.polygons:
          obj_file.write('f')
          for idx in p.vertices:
            obj_file.write(' %d' % (idx+1))
          obj_file.write('\n')
        obj_file.close()


    def tag_object(self, context, b_obj):
        """ Assign Contact metadata from Boolean intersection of Contact Object and Base Object """

        cwd = bpy.path.abspath(os.path.dirname(__file__))
        print('tag_object cwd: %s' % (cwd))
        bin_dir = os.path.join(os.path.dirname(__file__), 'bin') 
        tag_bin = os.path.join(bin_dir, 'obj_tag_region')
        append_bin = os.path.join(bin_dir, 'insert_mdl_region.py')

        scn = bpy.context.scene
        objs = scn.objects

        b_obj_name = b_obj.name
        print('Tagging Object: ' + b_obj_name)

        contact_pattern_match_list = self.contact_pattern_match_list
        c_objs = []
        for contact_pattern in contact_pattern_match_list:
          print('Contact Pattern: ' + contact_pattern.name)
          print('BN1 pat:' + contact_pattern.base_name_1_pattern)
          print('BN2 pat:' + contact_pattern.base_name_2_pattern)

          bn1_regex = contact_pattern.base_name_1_regex
          bn2_regex = contact_pattern.base_name_2_regex
          c_regex = contact_pattern.contact_name_regex

          bn1_recomp = re.compile(bn1_regex)
          bn2_recomp = re.compile(bn2_regex)
          c_recomp = re.compile(c_regex)

          print('BN1 regex: ' + bn1_regex)
          print('BN2 regex: ' + bn2_regex)

          if bn1_recomp.fullmatch(b_obj_name):
            c_obj_regex = b_obj_name + c_regex + bn2_regex
            c_obj_recomp = re.compile(c_obj_regex)
            c_objs.extend([ obj.name for obj in objs if c_obj_recomp.fullmatch(obj.name) ])

          if bn2_recomp.fullmatch(b_obj_name):
            c_obj_regex = bn1_regex + c_regex + b_obj_name
            c_obj_recomp = re.compile(c_obj_regex)
            c_objs.extend([ obj.name for obj in objs if c_obj_recomp.fullmatch(obj.name) ])
          print('Matching Contact Objects: ', c_objs)
 
        if len(c_objs) > 0:

          # unselect all objects 
          bpy.ops.object.select_all(action='DESELECT')
          # now select and export the base object:
          bpy.context.scene.objects.active = b_obj
          b_obj.select = True

          # Clear all existing regions from object
          print("Clearing all regions from object")
          bpy.ops.mcell.region_remove_all()

          b_obj_file_name = cwd + '/' + b_obj_name + ".obj"
          b_mdl_file_name = cwd + '/' + b_obj_name + ".mdl"
          b_mdl_with_tags_file_name = cwd + '/' + b_obj_name + "_tagged.mdl"

          # export b_obj as an OBJ file
          b_obj.processor.export_obj(context, b_obj, b_obj_file_name)

#          bpy.ops.export_scene.obj(filepath=b_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
          # export b_obj as an MDL file
          bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=b_mdl_file_name)

          for c_obj_name in c_objs:
            bpy.ops.object.select_all(action='DESELECT')
            c_obj = scn.objects[c_obj_name]
            bpy.context.scene.objects.active = c_obj
            c_obj.select = True
            c_obj_file_name = cwd + '/' + c_obj.name + ".obj"
            bpy.ops.export_scene.obj(filepath=c_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 

            tag_cmd = tag_bin + " %s %s > %s" % (b_obj_file_name, cwd + '/' + c_obj_name + ".obj", cwd + '/' + c_obj_name + "_regions.mdl")
            subprocess.check_output([tag_cmd],shell=True)
            append_cmd = append_bin + " %s %s > %s" % (b_mdl_file_name, cwd + '/' + c_obj_name + "_regions.mdl", b_mdl_with_tags_file_name)
            subprocess.check_output([append_cmd],shell=True)
            shutil.copyfile(b_mdl_with_tags_file_name, b_mdl_file_name)

          bpy.ops.object.select_all(action='DESELECT')
          b_obj.select = True
          b_mesh = b_obj.data
          bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath=b_mdl_with_tags_file_name)
          bpy.data.meshes.remove(b_mesh)
          b_obj = scn.objects[b_obj_name]
          b_obj.processor.smoothed = True
          b_obj.processor.newton = True
          b_obj.processor.update_contact_pattern_match_list(context, b_obj)


class ProcessorToolSceneProperty(bpy.types.PropertyGroup):
    active_sp_index = IntProperty(name="Active Spine Object Index", default=0)
    active_c_index = IntProperty(name="Active Contact Object Index", default=0)
    contour_list = CollectionProperty(
        type = ContourNameSceneProperty, name = "Contour List")
    active_contour_index = IntProperty(name="Active Contour Index", default=0)
    include_list = CollectionProperty(
        type = IncludeNameSceneProperty, name = "Include List")
    active_include_index = IntProperty(name="Active Include Index", default=0)
    contact_pattern_list = CollectionProperty(type = ContactPatternSceneProperty, name = "Contact Pattern List")
    active_contact_pattern_index = IntProperty(name="Active Contact Pattern Index", default=0)
    new = BoolProperty(name = "Imported MDL Object", default = False)
    filepath = StringProperty(name = "RECONSTRUCT Series Filepath", default= "")
    min_section = StringProperty(name="Minimum Reconstruct Section File", default= "")
    max_section = StringProperty(name="Maximum Reconstruct Section File", default= "")
    section_thickness = StringProperty(name="Section Thickness", default= "0.05")
    min_sample_interval = FloatProperty(name="Minimum Sample Interval", default=0.01)
    max_sample_interval = FloatProperty(name="Maximum Sample Interval", default=0.05)
    filt = StringProperty(name = "Filter for Object list", default = "d[0-9][0-9]sp[0-9][0-9]")


    '''
    def pattern_change_callback(self,context):

        print('Called whole-scene-level pattern_change_callback')
        bn1_regex = self.base_name_1_pattern.replace('#','[0-9]')
        bn1_regex = bn1_regex.replace('*','.*')
        bn2_regex = self.base_name_2_pattern.replace('#','[0-9]')
        bn2_regex = bn2_regex.replace('*','.*')

        bn1_recomp = re.compile(bn1_regex)
        bn2_recomp = re.compile(bn2_regex)
        
        for obj in bpy.context.scene.objects:
          if bn1_recomp.fullmatch(obj.name) or bn2_recomp.fullmatch(obj.name):
            obj.processor.name_match=True
          else:
            obj.processor.name_match=False
        return
    '''

    def spine_namestruct(self, context, spine_namestruct_name):
        self.spine_namestruct_name = spine_namestruct_name
        self.filt = self.spine_namestruct_name.replace('#','[0-9]')
        print("CHANGED NAME FILTER", self.filt)


    def PSD_namestruct(self, context, PSD_namestruct_name):
        self.PSD_namestruct_name = PSD_namestruct_name


    def central_namestruct(self, context, central_namestruct_name):
        self.central_namestruct_name = central_namestruct_name
       
       #for i in self.spine_namestruct:
        #   if i == 'X':
        #       i.= '[0-9]'

       # print(self.spine_namestruct_name)
       # print(spine_name)
        #print(type(self.spine_namestruct_name))
    
    
    def add_contour(self,context,contour_name,mode):
        if mode == 'contour':
            new_contour=self.contour_list.add()
            new_contour.init_contour(context,contour_name)
        else:
            new_contour=self.include_list.add()
            new_contour.init_include(context,contour_name)
        return(new_contour)


    def generate_contour_list(self, context, filepath):
        self.filepath = filepath
        ser_file = self.filepath
        ser_prefix = os.path.splitext(self.filepath)[0]

        print('SER filepath: ', filepath)
        print('SER prefix: ', ser_prefix)

        first_re = re.compile('first3Dsection="(\d*)"')
        last_re = re.compile('last3Dsection="(\d*)"')
        default_thick_re = re.compile('defaultThickness="(.*)"')

        ser_data = open(ser_file, "r").read()
#        self.min_section = first_re.search(ser_data).group(1)
#        self.min_section = str(int(self.min_section) +1)
#        self.max_section = last_re.search(ser_data).group(1)
#        self.max_section = str(int(self.max_section)- 1)
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
#        print('')
#        print(trace_num_list)
#        print('')
#        print(r_list)
#        print('')

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
#        for item in self.contour_list:
#            print(item)
        return(self.contour_list)
    
    
    #def get_active_contour(self, context,mode):
    #    scn = bpy.context.scene
    #    if mode == 'contour':
    #        contour = scn.test_tool[self.active_contour_index]
    #    else:
    #        contour = 


    def include_filter_contour(self,context):
#  FIXME:  add a proper regex trace filter method:
#        for item in self.contour_list:
#            if ((re.search(trace_filter_name, item.name)) or (re.search(trace_filter_name, item.name)))  and item.name not in self.include_list:
#                self.add_contour(context, item.name, "include")
        pass
        return(self.include_list)


    def include_contour(self, context):
        name = self.contour_list[self.active_contour_index].name
        if name not in self.include_list:
            self.add_contour(context, name, "include")
        return(self.include_list)


    def remove_contour(self, context):
        #for name in self.contour_list:
        if (len(self.include_list) > 0):
            name = self.include_list[self.active_include_index].name
            ser_dir = os.path.split(self.filepath)[0]
            ser_file = os.path.split(self.filepath)[-1]

            ser_prefix = os.path.splitext(ser_file)[0]
            out_file = ser_dir + '/' + ser_prefix + "_output"


            #for item in self.include_list:
            #objs = bpy.context.scene.objects
            #for obj in objs:
            if bpy.data.objects.get(name) is not None:
                bpy.ops.object.select_all(action='DESELECT')
                obj = bpy.context.scene.objects[self.include_list[self.active_include_index].name]
                obj.select = True
                context.scene.objects.active = obj
                m = obj.data
                context.scene.objects.unlink(obj)
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(m)
                if os.path.exists(out_file + '/'+ name + '_tiles.rawc'):
                    os.remove(out_file + '/'+ name + '_tiles.rawc')
                if os. path.exists(out_file + '/'+ name + '.obj'):
                    os.remove(out_file + '/'+ name + '.obj')
            self.include_list.remove(self.active_include_index)
               
        return(self.include_list)


    def remove_contour_all(self, context):
        #for name in self.contour_list:
        #name = self.include_list[self.active_include_index].name
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]

        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"

        self.contour_list.clear()
               
        return(self.contour_list)


    def remove_components(self,context):
        scn = bpy.context.scene
        contour = self.include_list[self.active_include_index]
        contour_name = contour.name
        self.include_list[contour_name].multi_component == False


    #def generate_mesh_object(self, context)
    #     for item in self.include_list:
    #         self.contourcontour.generate_mesh_object(context,trace) 


    def generate_mesh_object(self, context):
        #set variables
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]
        bin_dir = os.path.join(os.path.dirname(__file__), 'bin') 
        interpolate_bin = os.path.join(bin_dir, 'reconstruct_interpolate') 
        tile_bin = os.path.join(bin_dir, 'ContourTilerBin') 
        rawc2obj_bin = os.path.join(bin_dir, 'rawc2obj.py')

        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"
        if os.path.exists(out_file) == False:
            os.mkdir(out_file)
        interp_file = ser_prefix + "_interp" 
        
        #interpolate traces
        contour_name = " "
        for i in self.include_list: 
            contour = "-I " + str(i.name) + " "  
            contour_name += contour        
        
        interpolate_cmd = interpolate_bin + " -i %s -f %s -o %s --min_section=%s --max_section=%s --section_thickness %s  --min_sample_interval %.4g --max_sample_interval %.4g --curvature_gain=1E2 --proximity_gain=3 --min_point_per_contour=4 --deviation_threshold=0.005 %s -w %s" % (ser_dir, ser_prefix, out_file, self.min_section, self.max_section, self.section_thickness, self.min_sample_interval, self.max_sample_interval, contour_name, interp_file)
        print('\nInterpolating Series: \n%s\n' % (interpolate_cmd))
        subprocess.check_output([interpolate_cmd],shell=True)

        #tile traces
        for i in self.include_list:
            contour_name = str(i.name)
            print('\nGenerating Mesh for: %s\n' % (contour_name))
            if bpy.data.objects.get(contour_name) is None:
                tile_cmd = tile_bin + " -f ser -n %s -d %s -c %s -s  %s %s -z %s -C 0.001 -e 1e-15 -o raw -r %s" % (out_file, out_file, contour_name, self.min_section, self.max_section, self.section_thickness, interp_file)
                print('\nTiling Object: \n%s\n' % (tile_cmd))
                subprocess.check_output([tile_cmd],shell=True)
            #make obj
                rawc2obj_cmd = rawc2obj_bin + " %s > %s" % (out_file + '/'+ contour_name + '_tiles.rawc', out_file + '/'+  contour_name + ".obj")
                subprocess.check_output([rawc2obj_cmd],shell=True)
            #import obj
                bpy.ops.import_scene.obj(filepath=out_file + '/' + contour_name  + ".obj", axis_forward='Y', axis_up="Z")
                obj = bpy.data.objects.get(contour_name)
                if obj != None:
                    self.include_list[str(contour_name)].generated = True
                    obj.select = True
                    context.scene.objects.active = obj
                    obj.processor.update_contact_pattern_match_list(context, obj)
        #obj = bpy.context.scene.objects[contour_name]
         #   obj != None:
                if i.multi_component == True:
                    print("Multiple Components: %s" % (str(self.include_list[contour_name])))

  
    def generate_mesh_object_single(self,context): 
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]
        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"
        bin_dir = os.path.join(os.path.dirname(__file__), 'bin') 
        interpolate_bin = os.path.join(bin_dir, 'reconstruct_interpolate') 
        tile_bin = os.path.join(bin_dir, 'ContourTilerBin') 
        rawc2obj_bin = os.path.join(bin_dir, 'rawc2obj.py')

        if os.path.exists(out_file) == False:
            os.mkdir(out_file)
        interp_file = ser_prefix + "_interp" 
       
        contour = self.include_list[self.active_include_index]
        contour_name  = contour.name
        print(contour_name)
        obj = None
        interpolate_cmd = interpolate_bin + " -i %s -f %s -o %s --min_section=%s --max_section=%s --section_thickness %s --min_sample_interval %.4g --max_sample_interval %.4g --curvature_gain=1E2 --proximity_gain=3 --min_point_per_contour=4 --deviation_threshold=0.005 -I %s -w %s" % (ser_dir, ser_prefix, out_file, self.min_section, self.max_section, self.section_thickness, self.min_sample_interval, self.max_sample_interval, contour_name, interp_file)
        print('\nInterpolating Series: \n%s\n' % (interpolate_cmd))
        subprocess.check_output([interpolate_cmd],shell=True)

        if bpy.data.objects.get(contour_name) is None:
            tile_cmd = tile_bin + " -f ser -n %s -d %s -c %s -s  %s %s -z %s -C 0.001 -e 1e-15 -o raw -r %s" % (out_file, out_file, contour_name, self.min_section, self.max_section, self.section_thickness, interp_file)
            print('\nTiling Object: \n%s\n' % (tile_cmd))
            subprocess.check_output([tile_cmd],shell=True)
            #make obj
            rawc2obj_cmd = rawc2obj_bin + " %s > %s" % (out_file + '/'+ contour_name + '_tiles.rawc', out_file + '/'+  contour_name + ".obj")
            subprocess.check_output([rawc2obj_cmd],shell=True)
            #import obj
            bpy.ops.import_scene.obj(filepath=out_file + '/' + contour_name  + ".obj", axis_forward='Y', axis_up="Z")
            obj = bpy.data.objects.get(contour_name)
            if obj != None:
                self.include_list[str(contour_name)].generated = True
                obj.select = True
                context.scene.objects.active = obj
                obj.processor.update_contact_pattern_match_list(context, obj)
        '''
        else:
            obj = bpy.data.objects.get(contour_name)
            name = obj.name
            m = obj.data
            context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)
            bpy.data.meshes.remove(m)
            if os.path.isfile(out_file + '/'+ name + '_fix.rawc'):
                os.remove(out_file + '/'+ name + '_fix.rawc')
            if os.path.isfile(out_file + '/'+ name + '.obj'):
                os.remove(out_file + '/'+ name + '.obj')
            tile_cmd = tile_bin + " -f ser -n %s -d %s -c %s -s  %s %s -z .05 -C 0.001 -e 1e-15 -o raw -r %s" % (out_file, out_file, contour_name, self.min_section, self.max_section, interp_file)
            print('\nTiling Object: \n%s\n' % (tile_cmd))
            subprocess.check_output([tile_cmd],shell=True)
            #make obj
            rawc2obj_cmd = rawc2obj_bin + " %s > %s" % (out_file + '/'+ contour_name + '_tiles.rawc', out_file + '/'+  contour_name + ".obj")
            subprocess.check_output([rawc2obj_cmd],shell=True)
            #import obj
            bpy.ops.import_scene.obj(filepath=out_file + '/' + contour_name  + ".obj", axis_forward='Y', axis_up="Z")
        #obj = bpy.context.scene.objects[contour_name]
         #   obj != None:
            self.include_list[contour_name].generated = True
        '''

        if self.include_list[contour_name].multi_component == True:
            print("Multiple Components: %s" % (str(self.include_list[contour_name])))
        return (obj)


    def fix_mesh(self, context, mode):
        scn = bpy.context.scene         
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]
        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"
        bin_dir = os.path.join(os.path.dirname(__file__), 'bin') 
        rawc2obj_bin = os.path.join(bin_dir, 'rawc2obj.py')
        fix_all_bin = os.path.join(bin_dir, 'volFixAll')

        print("Fix Mesh Out_file:", out_file)

        if os.path.exists(out_file) == False:
            os.mkdir(out_file)

        #for i in self.include_list:
        #    #print(include_name)
        #    contour_name = str(i.name)
        #    bpy.ops.object.select_all(action='DESELECT')
        #    #obj = scn.objects.get(str(i.name))
        #    obj= bpy.context.scene.objects[contour_name] 
        #    obj.select = True

        if mode == "single":
            contour = self.include_list[self.active_include_index]
            contour_name  = contour.name
            bpy.ops.object.select_all(action='DESELECT')
            obj = scn.objects[contour_name]
            obj.select = True
            bpy.context.scene.objects.active = obj 
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.mcell.meshalyzer()
            mesh_props = bpy.context.scene.mcell.meshalyzer
            name = obj.name
            if mesh_props.components >1:           
                print('\nFound Multi-component Mesh: %s\n' % (obj.name))
                self.include_list[name].multi_component = True
            #if mesh_props.manifold == False:
            if mesh_props.genus  >= 1:           
                print('\nFound Genus > 0: %s\n' % (obj.name))
                self.include_list[name].genus_issue = True
            #if mesh_props.manifold == False:
            #    print('\nFound Non-manifold Mesh: %s\n' % (obj.name))
            #    self.include_list[name].non_manifold = True
            if ((mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals') and mesh_props.components == 1): 
                print('\nFixing Single Flawed Mesh: %s\n' % (contour_name))
                name = obj.name
                m = obj.data
                context.scene.objects.unlink(obj)
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(m)  

                #fix mesh
                fix_all_cmd = fix_all_bin + " %s %s" % (out_file + '/' + name + "_tiles.rawc", out_file + '/'+ name + "_fix.rawc")  
                subprocess.check_output([fix_all_cmd], shell=True)

                #make obj
                rawc2obj_cmd = rawc2obj_bin + " %s > %s" % (out_file + '/'+ name + '_fix.rawc', out_file + '/'+  name + ".obj")
                subprocess.check_output([rawc2obj_cmd],shell=True)

                #import obj
                bpy.ops.import_scene.obj(filepath=out_file + '/' + name  + ".obj", axis_forward='Y', axis_up="Z") 
                self.include_list[name].generated = True
                bpy.ops.object.select_all(action='DESELECT')
                obj = scn.objects[contour_name]
                obj.select = True
                bpy.context.scene.objects.active = obj 
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.mcell.meshalyzer()
                mesh_props = bpy.context.scene.mcell.meshalyzer
                if (mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals'):
                    print('\nMesh Still Flawed: %s\n' % (contour_name))
                    #self.include_list[name].non_manifold = True
                else:
                    print('\nMesh Successfully Fixed: %s\n' % (contour_name))
                    #self.include_list[name].non_manifold = False

            if os.path.isfile(out_file + '/'+ name + '_tiles.rawc'):
                os.remove(out_file + '/'+ name + '_tiles.rawc')
            if os.path.isfile(out_file + '/'+ name + '_fix.rawc'):
                os.remove(out_file + '/'+ name + '_fix.rawc')
            if os.path.isfile(out_file + '/'+ name + '.obj'):
                os.remove(out_file + '/'+ name + '.obj')
                      
        else: 
            for obj in scn.objects:
                #obj= bpy.context.scene.objects[contour_name] 
                #print(obj.name)
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True
                bpy.context.scene.objects.active = obj 
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.mcell.meshalyzer()
                mesh_props = bpy.context.scene.mcell.meshalyzer
                name = obj.name
                if mesh_props.components >1:
                    print('\nFound Multi-component Mesh: %s\n' % (obj.name))
                    self.include_list[name].multi_component = True
                if mesh_props.genus  >= 1:           
                    print('\nFound Genus > 0: %s\n' % (obj.name))
                    self.include_list[name].genus_issue = True
                if ((mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals') and mesh_props.components == 1): 
                    print('\nFound Flawed Mesh: %s\n' % (obj.name))
                    m = obj.data
                    context.scene.objects.unlink(obj)
                    bpy.data.objects.remove(obj)
                    bpy.data.meshes.remove(m)  

                    #fix mesh
                    fix_all_cmd = fix_all_bin + " %s %s" % (out_file + '/' + name + "_tiles.rawc", out_file + '/'+ name + "_fix.rawc")  
                    subprocess.check_output([fix_all_cmd], shell=True)

                    #make obj
                    rawc2obj_cmd = rawc2obj_bin + " %s > %s" % (out_file + '/'+ name + '_fix.rawc', out_file + '/'+  name + ".obj")
                    subprocess.check_output([rawc2obj_cmd],shell=True)

                    #import obj
                    bpy.ops.import_scene.obj(filepath=out_file + '/' + name  + ".obj", axis_forward='Y', axis_up="Z") 
                    self.include_list[name].generated = True
                    bpy.ops.object.select_all(action='DESELECT')
                    obj = scn.objects[name]
                    obj.select = True
                    bpy.context.scene.objects.active = obj 
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.ops.mcell.meshalyzer()
                    mesh_props = bpy.context.scene.mcell.meshalyzer
                    if (mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals'):
                        print('\nMesh Still Flawed: %s\n' % (name))
                        self.include_list[name].non_manifold = True
                    else:
                        print('\nMesh Successfully Fixed: %s\n' % (name))
                        self.include_list[name].non_manifold = False

                #do some clean up
                if os.path.isfile(out_file + '/'+ name + '_tiles.rawc'):
                    os.remove(out_file + '/'+ name + '_tiles.rawc')
                if os.path.isfile(out_file + '/'+ name + '_fix.rawc'):
                    os.remove(out_file + '/'+ name + '_fix.rawc')
                if os.path.isfile(out_file + '/'+ name + '.obj'):
                    os.remove(out_file + '/'+ name + '.obj')

        print("\nMulti-component meshes:\n")
        for item in self.include_list:
            if item.multi_component == True:
                print(item.name) 

        print("\nGenus > 0:\n")
        for item in self.include_list:
            if item.genus_issue == True:
                print(item.name) 

        #for i in range(int(self.min_section), int(self.max_section)+1):
        #    if os.path.isfile(out_file + '/'+ ser_prefix + '_interp.' + str(i)):
        #        os.remove(out_file + '/'+ ser_prefix + '_interp.' + str(i))
        #os.remove(out_file + '/_tiles.rawc')
        #os.remove(out_file + '/convert.sh')
        #os.remove(out_file + '/mesh.sh')
        #os.remove(out_file + '/mesh_and_convert.sh')
        #os.remove(out_file + '/'+ ser_prefix + '_interp.ser')
        #os.rmdir(out_file)


    def get_active_obje(self, context, mode):
        scn = bpy.context.scene

        if mode == 'spine':
            obje = scn.objects[self.active_sp_index]
            print(obje.name)
        else: 
            obje = scn.objects[self.active_c_index]
            print(obje.name)
           
        return(obje)


    def select_obje(self,context, mode):
        obje = self.get_active_obje(context, mode)
        obje.processor.select_obje(context, obje)


    def add_contact_pattern(self,context):
      new_contact_pattern = self.contact_pattern_list.add()
      self.active_contact_pattern_index = self.contact_pattern_list.find("")


    def remove_contact_pattern(self,context):
      if self.active_contact_pattern_index == 0:
        self.contact_pattern_list.remove(self.active_contact_pattern_index)
        self.active_contact_pattern_index = 0
      elif self.active_contact_pattern_index == (len(self.contact_pattern_list)-1):
        self.contact_pattern_list.remove(self.active_contact_pattern_index)
        self.active_contact_pattern_index = len(self.contact_pattern_list)-1

      # update (rebuild) match list for each object
      for obj in bpy.context.scene.objects:
         obj.processor.update_contact_pattern_match_list(context, obj)
      return


    def tag_contacts(self, context, mode):
        """ Assign Contact metadata from Boolean intersection of Contact Object and Base Object """

        # 1 - select cfa and do obj2mcell
        # 2 - regular expression match for names, assign to variables
        # 3 - mesh tag region
        # 4 - add option for one spine versus whole branch

        cwd = bpy.path.abspath(os.path.dirname(__file__))
        print('tag_contacts cwd: %s' % (cwd))

        # given a list of selected cfa's find all the unique sp's they match

        # for each sp associated with a group of cfa's
        
        # 5. for each cfa object:

        bin_dir = os.path.join(os.path.dirname(__file__), 'bin') 
        tag_bin = os.path.join(bin_dir, 'obj_tag_region')
        append_bin = os.path.join(bin_dir, 'insert_mdl_region.py')

        scn = bpy.context.scene
        objs = scn.objects

        print('Tag Objects Mode: ' + mode)
        
        if mode == 'single':
          b_obj = scn.objects[self.active_sp_index]

          b_obj.processor.tag_object(context, b_obj)
        else:
          b_objs = []
          for contact_pattern in self.contact_pattern_list:
            bn1_regex = contact_pattern.base_name_1_regex
            bn2_regex = contact_pattern.base_name_2_regex

            bn1_recomp = re.compile(bn1_regex)
            bn2_recomp = re.compile(bn2_regex)
 
            b_objs.extend([ obj.name for obj in objs if bn1_recomp.fullmatch(obj.name) or bn2_recomp.fullmatch(obj.name) ])
        
          b_objs = set(b_objs)
          for b_obj_name in b_objs:
            b_obj = scn.objects[b_obj_name]
            b_obj.processor.tag_object(context, b_obj)

        return

######## previous version of tagging code:
        obj1 = self.spine_namestruct_name
        obj2 = self.PSD_namestruct_name
        print(obj1,obj2)

        obje_list = [obje.name for obje in self.include_list if re.search(obj1, obje.name) != None]
        var_split_re = re.compile('#+|@+')

        num_re = re.compile('#')
        alpha_re = re.compile('@')
        star_re = re.compile('\*')

        base_pat_var = var_split_re.findall(self.spine_namestruct_name)
        base_pat_const = var_split_re.split(self.spine_namestruct_name)

        bpat = ''
        i=0
        for bvar in base_pat_var:
            bpat = bpat + base_pat_const[i] + '(' + bvar + ')'
            i += 1

        if len(base_pat_const) > len(base_pat_var):
            bpat = bpat + base_pat_const[i]

        print("THIS IS BPAT:", bpat)

        meta_pat_var = var_split_re.findall(self.PSD_namestruct_name)
        meta_pat_const = var_split_re.split(self.PSD_namestruct_name)

        mpat = ''
        i=0

        for mvar in meta_pat_var:
            mpat = mpat + meta_pat_const[i] + '(' + mvar + ')'
            i += 1

        if len(meta_pat_const) > len(meta_pat_var):
            mpat = mpat + meta_pat_const[i]

        base_pat_expr = num_re.sub('[0-9]',bpat)
        base_pat_expr = alpha_re.sub('[a-zA-Z]',base_pat_expr)
        base_pat_expr = star_re.sub('.*?',base_pat_expr)
        base_pat_re = re.compile(base_pat_expr)

        meta_pat_expr = num_re.sub('[0-9]',mpat)
        meta_pat_expr = alpha_re.sub('[a-zA-Z]',meta_pat_expr)
        meta_pat_expr = star_re.sub('.*?',meta_pat_expr)
        meta_pat_re = re.compile(meta_pat_expr)

        base_objs = [ obj.name for obj in objs if base_pat_re.fullmatch(obj.name) ]
        print("BASE OBJS:", base_objs)
        meta_objs = [ obj.name for obj in objs if meta_pat_re.fullmatch(obj.name) ]

        match_dict = {}
        
        for bobj in base_objs:
            bmtch = base_pat_re.fullmatch(bobj)
            bgrps = bmtch.groups()
            c_obj_list = []
            for mobj in meta_objs:
                mmtch = meta_pat_re.fullmatch(mobj)
                mgrps = mmtch.groups()
                if len(mgrps) != len(bgrps):
                    print('Oops! base and meta patterns have different number of matching groups')
                    break
                match_found = True
                for i in range(len(mgrps)):
                    if mgrps[i] != bgrps[i]:
                        match_found = False
                if match_found:
                    c_obj_list.append(mobj)
                match_dict[bobj]= c_obj_list
        print('MATCHDICT:', match_dict)

        if mode != "single":
            for key, value in match_dict.items():
                sp_obj_name = key
                #if sp_obj_re.fullmatch(mtch[1]):
                #sp_obj_name = item[1]
                #c_obj_name = item[0]
                #print("MTCH:  ", mtch)
                #if re.search(mtch[1], sp_obj_name):
                #    print ('FIND: ',mtch[1], mtch[0])
                #    c_obj_name = mtch[0]
                #else:
                #   print('FAILLLL')
                c_obj_list = value

                print('PRINT NAMES: ', sp_obj_name)
                sp_obj = scn.objects.get(sp_obj_name)
                sp_obj.processor.namestruct = self.spine_namestruct_name
    
            #print(type(sp_obj_name), type(c_obj_name))
                if (sp_obj != None) and (sp_obj.processor.smoothed == True) and (self.include_list[sp_obj.name].non_manifold == False):
            #INDENT THE FOLLOWING:    
                    sp_obj_file_name = cwd + '/' + sp_obj_name + ".obj"
                    sp_mdl_file_name = cwd + '/' + sp_obj_name + ".mdl"
                #sp_mdl_file_name_2 = cwd + '/' + sp_obj_name + "_2.mdl"
                    sp_mdl_with_tags_file_name = cwd + '/' + sp_obj_name + "_tagged_1.mdl"
                    '''sp_mdl_with_tags_file_name_2 = cwd + '/' + sp_obj_name + "_tagged_2.mdl"
                    sp_mdl_with_tags_file_name_3 = cwd + '/' + sp_obj_name + "_tagged_3.mdl"
                    sp_mdl_with_tags_file_name_4 = cwd + '/' + sp_obj_name + "_tagged_4.mdl"
                    sp_mdl_with_tags_file_obj = cwd + '/' + sp_obj_name + "_tagged.obj"
                    sp_mdl_with_tags_file_obj_2 = cwd + '/' + sp_obj_name + "_tagged_2.obj"
                    sp_mdl_with_tags_file_obj_3 = cwd + '/' + sp_obj_name + "_tagged_3.obj"'''

                    #c_obj_file_name = cwd + '/' + c_obj_name + ".obj"
                    '''c_obj_file_name_3 = cwd + '/' + c_obj_name + "_3.obj"
                    c_obj_file_name_4 = cwd + '/' + c_obj_name + "_4.obj"
                    c_mdl_tag_file_name= cwd + '/' + c_obj_name + "_regions.mdl"
                    c_mdl_tag_file_name_2 = cwd + '/' + c_obj_name + "_regions_2.mdl"
                    c_mdl_tag_file_name_3 = cwd + '/' + c_obj_name + "_regions_3.mdl"
                    c_mdl_tag_file_name_4 = cwd + '/' + c_obj_name + "_regions_4.mdl"'''
                
            # export smoothed blender object as an obj file to file name sp_obj_file_name
            # unselect all objects 
                    bpy.ops.object.select_all(action='DESELECT')
            # now select and export the "sp" object:
                    bpy.context.scene.objects.active = sp_obj
                    sp_obj.select = True
                    

                    #reg_list = sp_obj.mcell.regions.region_list
                    #if len(reg_list) <= 0:
                    bpy.ops.export_scene.obj(filepath=sp_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
            # export sp_obj as an MDL file
                    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_file_name)
                    bpy.ops.object.select_all(action='DESELECT')
                    i = 0
                    for item in c_obj_list:
                        c_obj_name = item
                        c_obj = scn.objects.get(c_obj_name)
                        c_obj.processor.namestruct = self.PSD_namestruct_name
                        print(c_obj_name)
                        print("found c object: " + c_obj.name) 
                        if i == 0 and c_obj != None:
                        # now select and export the "c" object:
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.context.scene.objects.active = c_obj
                            c_obj.select = True
                            bpy.ops.export_scene.obj(filepath=cwd + '/' + c_obj_name + ".obj", axis_forward='Y', axis_up="Z", use_selection=True,                                                                                                                                              use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
                            tag_cmd = tag_bin + " %s %s > %s" % (sp_obj_file_name, cwd + '/' + c_obj_name + ".obj", cwd + '/' + c_obj_name + "_regions.mdl")
                            subprocess.check_output([tag_cmd],shell=True)
                        #concat_cmd = "( head -n -2 %s ; cat %s ; echo '}' ) > %s" % (sp_mdl_file_name, c_mdl_tag_file_name, sp_mdl_with_tags_file_name)
                       # subprocess.check_output([concat_cmd],shell=True)
                            append_cmd = append_bin + " %s %s > %s" % (sp_mdl_file_name, cwd + '/' + c_obj_name + "_regions.mdl", sp_mdl_with_tags_file_name)
                            subprocess.check_output([append_cmd],shell=True)
                            bpy.ops.object.select_all(action='DESELECT')
                            sp_obj.select = True
                            bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_with_tags_file_name)
                            obje = scn.objects[sp_obj_name]
                            obje.processor.smoothed = True
                            obje.processor.newton = True
                        else:

                   #bpy.ops.export_scene.obj(filepath=sp_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
            # export sp_obj as an MDL file
                   #bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_file_name)
                   
                                #reg_list_2 = [region.name for region in reg_list]
                                #print(reg_list_2)
                                #length = []
                                #for item in reg_list_2:
                                #    item = item[:-1] 
                                #    print(item)
                                #    print(type(item))
                                #    print(bool(re.match(str(item),c_obj_name)))
                                #    if re.match(str(item), c_obj_name):
                                #        print('beetle')
                                #        length.append(item)
                                #        i = len(length)
                                #        print('len:',i)
                                #c_obj = scn.objects.get(c_obj_name)
                            #if c_obj != None:
                                    #i+=1
                    # now select and export the "c" object:
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.context.scene.objects.active = c_obj
                            c_obj.select = True
                               #bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=c_obj_name +".mdl")
                            bpy.ops.export_scene.obj(filepath=cwd + '/' + c_obj_name + ".obj", axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
                    
                            tag_cmd = tag_bin + " %s %s > %s" % (cwd + '/' + sp_obj_name + ".obj", cwd + '/' + c_obj_name + ".obj", cwd + '/' + c_obj_name + "_regions.mdl")
                            print("tag command:", tag_cmd) 
                            subprocess.check_output([tag_cmd],shell=True)

                                            #item2 = item[:-2]
                                #concat_cmd = "( head -n -2 %s ; cat %s ; echo '}' ) > %s" % (sp_obj_name + "_tagged_" + str(i) + ".mdl", c_obj_name + "_regions_" + str(i) + ".mdl", sp_obj_name + "_tagged_" + ".mdl") 
                                #subprocess.check_output([concat_cmd],shell=True)
                                            #print("i", i)
                            print('tag obj:',cwd + '/' + sp_obj_name + "_tagged_"+ str(i) + ".mdl")
                            append_cmd = append_bin + " %s %s > %s" % (cwd + '/' + sp_obj_name + "_tagged_"+ str(i) + ".mdl", cwd + '/' + c_obj_name + "_regions.mdl", cwd + '/' + sp_obj_name + "_tagged_"+ str(i+1) + ".mdl")
                            subprocess.check_output([append_cmd],shell=True)
                            bpy.ops.object.select_all(action='DESELECT')
                            sp_obj.select = True
                            bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath= cwd + '/' +sp_obj_name + "_tagged_"+ str(i+1)+ ".mdl")
                            obje = scn.objects[sp_obj_name]
                            obje.processor.smoothed = True
                            obje.processor.multi_synaptic = True
                                #obje.processor.newton = True
                        i += 1
                #regions = [item for item in reg_list]

            # export "c" object as an obj file to file name c_obj_file_name
            # unselect all objects 
                #bpy.ops.object.select_all(action='DESELECT')
                #c_obj_name = obje.replace('sp', 'c')

        else:  # tagging mode is 'single'
            contour = scn.objects[self.active_sp_index]
            print(contour)
            sp_obj_name  = contour.name
            sp_obj = scn.objects.get(sp_obj_name)
            sp_obj.processor.namestruct = self.spine_namestruct_name
            sp_obj_re = re.compile(sp_obj_name)

            bmtch = base_pat_re.fullmatch(sp_obj_name)
            #bgrps = bmtch.groups()

            #bpy.ops.object.select_all(action='DESELECT')
            # now select and export the "sp" object:
            #bpy.context.scene.objects.active = sp_obj
            #sp_obj.select = True
            reg_list = sp_obj.mcell.regions.region_list
            #bpy.ops.export_scene.obj(filepath = cwd + '/' + sp_obj_name + ".obj", axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
            # export sp_obj as an MDL file
            #bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=cwd + '/' + sp_obj_name + ".mdl")
            #bpy.ops.object.select_all(action='DESELECT')
 
            i = 0
            sp_obj_file_name = cwd + '/' + sp_obj_name + ".obj" 
            for key, value in match_dict.items():
                if sp_obj_re.fullmatch(key):
                    sp_obj_name = key
                    print("SP OBJ KEY", sp_obj_name)
                    c_obj_list = value
                    print("C_OBJ_LIST", c_obj_list)

                    print('PRINT NAMES: ', sp_obj_name)
                    sp_obj = scn.objects.get(sp_obj_name)
            #print(type(sp_obj_name), type(c_obj_name))
                    if (sp_obj != None) and (sp_obj.processor.smoothed == True) and (self.include_list[sp_obj.name].non_manifold == False):
            #INDENT THE FOLLOWING:    
                        sp_obj_file_name = cwd + '/' + sp_obj_name + ".obj"
                        sp_mdl_file_name = cwd + '/' + sp_obj_name + ".mdl"
                        #sp_mdl_file_name_2 = cwd + '/' + sp_obj_name + "_2.mdl"
                        sp_mdl_with_tags_file_name = cwd + '/' + sp_obj_name + "_tagged_1.mdl"
                        '''sp_mdl_with_tags_file_name_2 = cwd + '/' + sp_obj_name + "_tagged_2.mdl"
                        sp_mdl_with_tags_file_name_3 = cwd + '/' + sp_obj_name + "_tagged_3.mdl"
                        sp_mdl_with_tags_file_name_4 = cwd + '/' + sp_obj_name + "_tagged_4.mdl"
                        sp_mdl_with_tags_file_obj = cwd + '/' + sp_obj_name + "_tagged.obj"
                        sp_mdl_with_tags_file_obj_2 = cwd + '/' + sp_obj_name + "_tagged_2.obj"
                        sp_mdl_with_tags_file_obj_3 = cwd + '/' + sp_obj_name + "_tagged_3.obj"'''

                        #c_obj_file_name = cwd + '/' + c_obj_name + ".obj"
                        '''c_obj_file_name_2 = cwd + '/' + c_obj_name + "_2.obj"
                        c_obj_file_name_3 = cwd + '/' + c_obj_name + "_3.obj"
                        c_obj_file_name_4 = cwd + '/' + c_obj_name + "_4.obj"
                        c_mdl_tag_file_name= cwd + '/' + c_obj_name + "_regions.mdl"

                        c_mdl_tag_file_name_2 = cwd + '/' + c_obj_name + "_regions_2.mdl"
                        c_mdl_tag_file_name_3 = cwd + '/' + c_obj_name + "_regions_3.mdl"
                        c_mdl_tag_file_name_4 = cwd + '/' + c_obj_name + "_regions_4.mdl"'''
                
                        # export smoothed blender object as an obj file to file name sp_obj_file_name
                        # unselect all objects 
                        bpy.ops.object.select_all(action='DESELECT')
                        # now select and export the "sp" object:
                        bpy.context.scene.objects.active = sp_obj
                        sp_obj.select = True
                    

                    #reg_list = sp_obj.mcell.regions.region_list
                    #if len(reg_list) <= 0:
                        bpy.ops.export_scene.obj(filepath=sp_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
            # export sp_obj as an MDL file
                        bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_file_name)
                        bpy.ops.object.select_all(action='DESELECT')
                        i = 0
                        print("Length c ob list:",len(c_obj_list))
                        for item in c_obj_list:
                            print("i + C LIST", i, item)
                            c_obj_name = item
                            c_obj = scn.objects.get(c_obj_name)
                            c_obj.processor.namestruct = self.PSD_namestruct_name
                            print(c_obj_name)
                            print("found c object: " + c_obj.name) 
                            if i==0 and c_obj != None:
                        # now select and export the "c" object:
                                bpy.ops.object.select_all(action='DESELECT')
                                bpy.context.scene.objects.active = c_obj
                                c_obj.select = True
                                bpy.ops.export_scene.obj(filepath= cwd + '/' + c_obj_name + ".obj", axis_forward='Y', axis_up="Z", use_selection=True,                                                                                                                                              use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 

                                tag_cmd = tag_bin + " %s %s > %s" % (sp_obj_file_name, cwd + '/' + c_obj_name + ".obj", cwd + '/' + c_obj_name + "_regions.mdl")
                                subprocess.check_output([tag_cmd],shell=True)
                        #concat_cmd = "( head -n -2 %s ; cat %s ; echo '}' ) > %s" % (sp_mdl_file_name, c_mdl_tag_file_name, sp_mdl_with_tags_file_name)
                       # subprocess.check_output([concat_cmd],shell=True)
                                append_cmd = append_bin + " %s %s > %s" % (cwd + '/' + sp_obj_name + ".mdl", cwd + '/' + c_obj_name + "_regions.mdl", sp_mdl_with_tags_file_name)
                                subprocess.check_output([append_cmd],shell=True)
                                bpy.ops.object.select_all(action='DESELECT')
                                sp_obj.select = True
                                bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_with_tags_file_name)
                                obje = scn.objects[sp_obj_name]
                                obje.processor.smoothed = True
                                obje.processor.newton = True
                            else:
                                print(i)
                   #bpy.ops.export_scene.obj(filepath=sp_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
            # export sp_obj as an MDL file
                   #bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_file_name)
                   
                                #reg_list_2 = [region.name for region in reg_list]
                                #print(reg_list_2)
                                #length = []
                                #for item in reg_list_2:
                                #    item = item[:-1] 
                                #    print(item)
                                #    print(type(item))
                                #    print(bool(re.match(str(item),c_obj_name)))
                                #    if re.match(str(item), c_obj_name):
                                #        print('beetle')
                                #        length.append(item)
                                #        i = len(length)
                                #        print('len:',i)
                                #c_obj = scn.objects.get(c_obj_name)
                                #if c_obj != None:
                                    #i+=1
                    # now select and export the "c" object:
                                bpy.ops.object.select_all(action='DESELECT')
                                bpy.context.scene.objects.active = c_obj
                                c_obj.select = True
                               #bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=c_obj_name +".mdl")
                                bpy.ops.export_scene.obj(filepath=cwd + '/' + c_obj_name + ".obj", axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
                    
                                tag_cmd = tag_bin + " %s %s > %s" % (cwd + '/' + sp_obj_name + ".obj", cwd + '/' + c_obj_name + ".obj", cwd + '/' + c_obj_name + "_regions.mdl")
                                print("tag command:", tag_cmd) 
                                subprocess.check_output([tag_cmd],shell=True)

                                            #item2 = item[:-2]
                                #concat_cmd = "( head -n -2 %s ; cat %s ; echo '}' ) > %s" % (sp_obj_name + "_tagged_" + str(i) + ".mdl", c_obj_name + "_regions_" + str(i) + ".mdl", sp_obj_name + "_tagged_" + ".mdl") 
                                #subprocess.check_output([concat_cmd],shell=True)
                                            #print("i", i)
                                print('tag obj:',cwd + '/' + sp_obj_name + "_tagged_"+ str(i) + ".mdl")
                                append_cmd = append_bin + " %s %s > %s" % (cwd + '/' + sp_obj_name + "_tagged_"+ str(i) + ".mdl", cwd + '/' + c_obj_name + "_regions.mdl", cwd + '/' + sp_obj_name + "_tagged_"+ str(i+1) + ".mdl")
                                subprocess.check_output([append_cmd],shell=True)
                                bpy.ops.object.select_all(action='DESELECT')
                                sp_obj.select = True
                                bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath= cwd + '/' +sp_obj_name + "_tagged_"+ str(i+1)+ ".mdl")
                                obje = scn.objects[sp_obj_name]
                                obje.processor.smoothed = True
                                obje.processor.multi_synaptic = True
                            i += 1

                    else: 
                        obje = scn.objects[sp_obj_name]
                        self.include_list[obje.name].problem = True

                else: 
                    pass

            else: 
                obje = scn.objects[sp_obj_name]
                self.include_list[obje.name].problem = True
       

    def smooth_all(self,context):
#        spine_name = self.spine_namestruct_name.replace('#','*')
        num_re = re.compile('#')
        spine_name = num_re.sub('[0-9]',self.spine_namestruct_name)
        print('namestruct:  %s' % (self.spine_namestruct_name))
        print('spine_name:  %s' % (spine_name))
        scn = bpy.context.scene
        the_list = [obje for obje in scn.objects if re.search(spine_name, obje.name)!= None]
        for obje in the_list:
            if (self.include_list[obje.name].multi_component == False) and (self.include_list[obje.name].non_manifold == False) and(obje.processor.smoothed == False):
                obje.processor.select_obje(context, obje)
                obje.processor.smooth(context)


    def merge_objs(self,context):
        merge_obje = bpy.context.active_object
        name = merge_obje.name
        #bpy.ops.object.modifier_add(type = 'BOOLEAN')
        #bpy.data.objects[name].modifiers['Boolean'].operation = 'UNION'
        merge_obje_list = [obje.name for obje in self.include_list if re.match(name[:3], obje.name[:3]) != None and obje.name != name]
        for obje in merge_obje_list: 
           bpy.ops.object.modifier_add(type = 'BOOLEAN')
           bpy.data.objects[name].modifiers['Boolean'].operation = 'UNION'
           bpy.data.objects[name].modifiers['Boolean'].object = bpy.data.objects[obje]
           bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier='Boolean')
        merge_obje.processor.select_obje(context, merge_obje)
        #self.fix_mesh(merge_obje, 'single')
        bpy.ops.object.mode_set(mode='EDIT')       
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris(quad_method = 'BEAUTY', ngon_method='BEAUTY')


    #Draw panel
    def draw_panel(self, context, panel):
        layout = panel.layout
        row = layout.row()
        row.label(text='Import Reconstruct Series:', icon='MOD_ARRAY')
        row = layout.row(align=True)
        row.prop(self, "filepath", text='')
        row.operator('processor_tool.impser', icon='FILESEL', text='')  
        #row.operator("processor_tool.spine_namestruct", text = "Set Spine Name")
        row = layout.row()
        row.label(text = 'section thickness: ' + self.section_thickness) 
        row.label(text = 'min section #: ' + self.min_section) 
        row.label(text = 'max section #: ' + self.max_section) 
        row = layout.row()
        row.prop(self,'min_sample_interval',text='Min Sample Interval:')
        row.prop(self,'max_sample_interval',text='Max Sample Interval:')

        row = layout.row()
        row.label(text="Trace List:", icon='CURVE_DATA')
        row.label(text="Include List:", icon='MESH_ICOSPHERE')
        row = layout.row()
        col = row.column()
        col.template_list("Trace_UL_draw_item","contours_in_ser_file",
                          self, "contour_list",
                          self, "active_contour_index",
                          rows=5)
        col = row.column(align=True)
        col.operator('processor_tool.include_contour', icon='FORWARD', text='') 
        col.operator('processor_tool.include_filter_contour', icon='EXPORT', text='') 
        col.operator('processor_tool.remove_contour_all', icon='X', text='') 

        col = row.column()
        col.template_list("Include_UL_draw_item","included_in_ser_file",
                          self, "include_list",
                          self, "active_include_index",
                          rows=5)
        col = row.column(align=True)
        col.operator('processor_tool.remove_contour', icon='ZOOMOUT', text='')
        col.operator('processor_tool.generate_mesh_object_single', icon='MESH_ICOSPHERE', text='')
        col.operator('processor_tool.generate_mesh_object', icon='POSE_DATA', text='')
        col.label('', icon='BLANK1')
        col.operator('processor_tool.fix_mesh', icon='MODIFIER', text='')
        col.operator('processor_tool.remove_components', icon='SEQ_SEQUENCER', text='')

        box1 = layout.box()

        box1 = layout.box()
        row = box1.row()
        row.label(text="Contact Object Pattern List:", icon='HAND')
        row = box1.row()
        col = row.column()
        row.template_list("Contact_Pattern_UL_draw_item","contact_patterns",
                          self, "contact_pattern_list",
                          self, "active_contact_pattern_index",
                          rows=4) 
        col = row.column(align=True)
        col.operator('processor_tool.add_contact_pattern', icon='ZOOMIN', text='')
        col.operator('processor_tool.remove_contact_pattern', icon='ZOOMOUT', text='')

        if self.contact_pattern_list:
          contact_pattern = self.contact_pattern_list[self.active_contact_pattern_index]
          contact_pattern.draw_props(box1)


        row = layout.row()
        row.label(text="Object List:", icon='MESH_ICOSPHERE')
        row = layout.row()
        col = row.column()
        row.template_list("SCN_UL_obj_draw_item","sp_objects_in_scene",
                          bpy.context.scene, "objects",
                          self, "active_sp_index",
                          rows=4) 
        col = row.column(align=True)
        col.operator('processor_tool.smooth', icon='MOD_SMOOTH', text='')
        col.operator('processor_tool.smooth_all', icon='MOD_WAVE', text='')
        col.label('', icon='BLANK1')
        col.operator('processor_tool.tag_contact_single', icon='STYLUS_PRESSURE', text='')
        col.operator('processor_tool.tag_contacts', icon='POSE_HLT', text='')

        row = layout.row()
        row.label(text= "Merge central object with associated objects: ")
        row = layout.row()
        row.operator("processor_tool.merge_objs", text="Merge Objects")

