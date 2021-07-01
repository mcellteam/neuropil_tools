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


#Define Operators

contour_filter_pattern = ''

def filter_items_by_pattern(self, context, data, propname):

  helper_funcs = bpy.types.UI_UL_list
  
  items = getattr(data, propname)

  flt_flags = []
  flt_neworder = []

  filt_pat = self.filter_name
  if filt_pat:
    # convert filter patterns to formal regex
    filt_pat = self.filter_name
    filt_regex = filt_pat.replace('#','[0-9]')
    filt_regex = filt_regex.replace('*','.*')
  
    filt_recomp = re.compile(filt_regex)
          
    flt_flags = [ self.bitflag_filter_item*((filt_recomp.fullmatch(item.name)!=None)) for item in items ]
  else:
    flt_flags = [self.bitflag_filter_item]*len(items)

  flt_neworder = helper_funcs.sort_items_by_name(items, 'name')

  return flt_flags, flt_neworder


class NEUROPIL_OT_impser(bpy.types.Operator, ImportHelper):
    """Import from RECONSTRUCT Series file format (.ser)"""
    bl_idname = "processor_tool.impser"
    bl_label = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_description = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'}            

    filename_ext = ".ser"
    filter_glob: StringProperty(default="*.ser", options={'HIDDEN'})
    filepath: StringProperty(subtype='FILE_PATH')

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

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        context.scene.test_tool.generate_mesh_object(context)
        context.scene.test_tool.fix_mesh(context,"all")
        return {'FINISHED'}


class NEUROPIL_OT_tile_one_mesh(bpy.types.Operator):
    bl_idname = "processor_tool.generate_mesh_object_single"
    bl_label = "Interpolate and Generate Meshes from Selected Contour"    
    bl_description = "Interpolate and Generate Meshes from Selected Contour"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.generate_mesh_object_single(context)
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


class NEUROPIL_OT_select_obj(bpy.types.Operator):
    bl_idname = "processor_tool.select_obj"
    bl_label = "Select Faces of OBJ"
    bl_description = "Select Faces of OBJ"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.select_obj(context,'spine')
        return {'FINISHED'}


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
    bl_label = "Smooth Single Object Selected in Object List"
    bl_description = "Smooth Single Object Selected in Object List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.select_obj(context,'spine')
        context.active_object.processor.smooth(context)
        return {'FINISHED'}


class NEUROPIL_OT_smooth_all(bpy.types.Operator):
    bl_idname = "processor_tool.smooth_all"
    bl_label = "Smooth All non-Contact Objects in Object List"
    bl_description = "Smooth All non-Contact Objects in Object List"
    bl_options = {'REGISTER', 'UNDO'}
  
    def execute(self, context):
        context.scene.test_tool.smooth_all(context)
        return {'FINISHED'}


class NEUROPIL_OT_tag_contact_single(bpy.types.Operator):
    bl_idname = "processor_tool.tag_contact_single"
    bl_label = "Tag Contact Regions On Single Object Selected in Object List"
    bl_description = "Tag Contact Regions On Single Object Selected in Object List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.tag_contacts(context,"single")
        return {'FINISHED'}


class NEUROPIL_OT_tag_contacts(bpy.types.Operator):
    bl_idname = "processor_tool.tag_contacts"
    bl_label = "Tag Contact Regions On All Objects in Object List"
    bl_description = "Tag Contact Regions On All Objects in Object List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.tag_contacts(context,"all")
        return {'FINISHED'}


class NEUROPIL_OT_merge_objs(bpy.types.Operator):
    bl_idname = "processor_tool.merge_objs"
    bl_label = "Merge Objects"
    bl_description = "Merge Objects"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        context.scene.test_tool.merge_objs(context)
        return {'FINISHED'}


class NEUROPIL_OT_gamer_coarse_dense(bpy.types.Operator):
    bl_idname = "npt_gamer.coarse_dense"
    bl_label = "Coarse Dense"
    bl_description = "Decimate selected dense areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        gamer_version = context.scene.gamer.gamer_version[1]
        if gamer_version == '2':
          bpy.ops.gamer.coarse_dense()
        else:
          context.scene.gamer.mesh_improve_panel.coarse_dense(context)
        return {'FINISHED'}


class NEUROPIL_OT_gamer_coarse_flat(bpy.types.Operator):
    bl_idname = "npt_gamer.coarse_flat"
    bl_label = "Coarse Flat"
    bl_description = "Decimate selected flat areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        gamer_version = context.scene.gamer.gamer_version[1]
        if gamer_version == '2':
          bpy.ops.gamer.coarse_flat()
        else:
          context.scene.gamer.mesh_improve_panel.coarse_flat(context)
        return {'FINISHED'}


class NEUROPIL_OT_gamer_smooth(bpy.types.Operator):
    bl_idname = "npt_gamer.smooth"
    bl_label = "Smooth"
    bl_description = "Smooth selected vertices of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        gamer_version = context.scene.gamer.gamer_version[1]
        if gamer_version == '2':
          bpy.ops.gamer.smooth()
        else:
          context.scene.gamer.mesh_improve_panel.smooth(context)
        return {'FINISHED'}

 
class NEUROPIL_OT_gamer_normal_smooth(bpy.types.Operator):
    bl_idname = "npt_gamer.normal_smooth"
    bl_label = "Normal Smooth"
    bl_description = "Smooth faces normals of selected faces of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        gamer_version = context.scene.gamer.gamer_version[1]
        if gamer_version == '2':
          bpy.ops.gamer.normal_smooth()
        else:
          context.scene.gamer.mesh_improve_panel.normal_smooth(context)
        return {'FINISHED'}


#layout object lists
class NEUROPIL_UL_trace_draw_item(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index, flt_flags):
       
        self.use_filter_sort_alpha = True
        layout.label(text=item.name)


    def filter_items(self, context, data, propname):
      global contour_filter_pattern

      flt_flags, flt_neworder = filter_items_by_pattern(self,context,data,propname)
      contour_filter_pattern = self.filter_name

      return flt_flags, flt_neworder



class NEUROPIL_UL_include_draw_item(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index, flt_flags):
        scn = bpy.context.scene
        self.use_filter_sort_alpha = True    
        #if item.non_manifold == True:
     #    layout.label(text=item.name, icon='ERROR')
        if item.multi_component == True:
            layout.label(text=item.name, icon='SEQ_SEQUENCER')
        elif item.genus_issue == True:
            layout.label(text=item.name, icon = "MESH_TORUS")
        elif item.generated == True:
            layout.label(text=item.name, icon='MESH_ICOSPHERE')
        else:
            layout.label(text=item.name)


    def filter_items(self, context, data, propname):
      flt_flags, flt_neworder = filter_items_by_pattern(self,context,data,propname)
      return flt_flags, flt_neworder



class NEUROPIL_UL_contact_pattern_draw_item(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
       
        self.use_filter_sort_alpha = True
        layout.label(text=item.name)



class NEUROPIL_UL_obj_draw_item(bpy.types.UIList):

    use_base_name_filter: BoolProperty(name = "Filter Object List by Base Names", default = False)
  
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index, flt_flags):

        self.use_filter_show = True
        match_text = '    [ '
        for contact_pattern in item.processor.contact_pattern_match_list:
            match_text += contact_pattern.name + ' '
        match_text += ']'

        if item.processor.multi_synaptic == True:
            layout.label(text=item.name + match_text, icon = "MANIPUL")
        elif item.processor.newton == True:
            layout.label(text=item.name + match_text, icon='FILE_TICK')
        elif item.processor.smoothed == True:
            layout.label(text=item.name + match_text, icon='MOD_SMOOTH')
        else:
            layout.label(text=item.name + match_text)


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


class NEUROPIL_PT_processor_tool(bpy.types.Panel):
    bl_label = "3DEM Processor Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Neuropil Tools"

    def draw(self, context):
        if context.scene != None:
            context.scene.test_tool.draw_panel(context, panel=self)


def pattern_change_callback(self,context):
  self.pattern_change_callback(context)
  return


class ContourNameSceneProperty(bpy.types.PropertyGroup):
    name: StringProperty(name= "Contour name", default ="")
    
    def init_contour(self,context,name):
        self.name = name


class ContactPatternObjectProperty(bpy.types.PropertyGroup):
    name: StringProperty(name= "Contact Object Pattern", default ="")
    base_name_1_pattern: StringProperty("Base Name 1 Pattern", default = "")
    base_name_2_pattern: StringProperty("Base Name 2 Pattern", default = "")
    contact_name_pattern: StringProperty("Contact Name Pattern", default = "")
    base_name_1_regex: StringProperty("Base Name 1 Regex", default = "")
    base_name_2_regex: StringProperty("Base Name 2 Regex", default = "")
    contact_name_regex: StringProperty("Contact Name Regex", default = "")


class ContactPatternSceneProperty(bpy.types.PropertyGroup):
    name: StringProperty(name= "Contact Object Pattern", default ="")
    base_name_1_pattern: StringProperty("Base Name 1 Pattern", default = "", update=pattern_change_callback)          
    base_name_2_pattern: StringProperty("Base Name 2 Pattern", default = "", update=pattern_change_callback)          
    contact_name_pattern: StringProperty("Contact Name Pattern", default = "", update=pattern_change_callback)          
    base_name_1_regex: StringProperty("Base Name 1 Regex", default = "")
    base_name_2_regex: StringProperty("Base Name 2 Regex", default = "")
    contact_name_regex: StringProperty("Contact Name Regex", default = "")


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
        for obj in bpy.context.scene.collection.children[0].objects:
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
    name: StringProperty(name= "Include name", default ="")
    generated: BoolProperty(name = "Mesh Object Generated", default = False)
    multi_component: BoolProperty(name = "Multiple Components in Mesh", default = False)
    non_manifold: BoolProperty(name = "Non-manifold Mesh", default = False) 
    genus_issue: BoolProperty(name = "True if Genus > 0", default = False)         
    problem: BoolProperty(name = "Problem Tagging", default = False)
    
    def init_include(self,context,name):
        self.name = name



class ProcessorToolObjectProperty(bpy.types.PropertyGroup):
    n_components: IntProperty(name="Number of Components in Mesh", default=0)
    smoothed: BoolProperty(name="Smoothed Object", default=False)
    newton: BoolProperty(name = "New Object", default=False)
    multi_synaptic: BoolProperty(name = "Multiple Synapses", default = False)
    fix_all_fail: BoolProperty(name = "Failed to Fix Obj", default = False)
    contact_pattern_match_list: CollectionProperty(type = ContactPatternObjectProperty, name = "Contact Pattern Match List")


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
          

    def select_obj(self, context, obj):
        if context.active_object is not None:
          bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
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
        if not self.smoothed:
          """ Smooth using GAMer """
          print('Smoothing: %s' % (context.active_object.name))

          gamer_version = context.scene.gamer.gamer_version[1]
          if gamer_version == '2':
            # We have found GAMer version 2
            gamer_smiprops = context.scene.gamer.surfmesh_improvement_properties
            gamer_smiprops.dense_rate = 2.5
            gamer_smiprops.dense_iter = 1
            gamer_smiprops.smooth_iter = 10
            gamer_smiprops.preserve_ridges = True
          else:
            # We have found GAMer version 1
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
          bpy.ops.npt_gamer.smooth('INVOKE_DEFAULT')      
          bpy.ops.npt_gamer.coarse_dense('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.smooth('INVOKE_DEFAULT')      
          bpy.ops.npt_gamer.coarse_dense('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.smooth('INVOKE_DEFAULT')      
          bpy.ops.npt_gamer.coarse_dense('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.smooth('INVOKE_DEFAULT')      
          bpy.ops.npt_gamer.coarse_dense('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.smooth('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.normal_smooth('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.normal_smooth('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.normal_smooth('INVOKE_DEFAULT')
          bpy.ops.npt_gamer.normal_smooth('INVOKE_DEFAULT')
          self.smoothed = True
          obj = context.active_object
          obj.processor.update_contact_pattern_match_list(context, obj)
        else:
          print('Not smoothing object, already smoothed: %s' % (context.active_object.name))

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
        objs = scn.collection.children[0].objects

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
          bpy.context.view_layer.objects.active = b_obj
          b_obj.select_set(True)

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
            bpy.context.view_layer.objects.active = c_obj
            c_obj.select_set(True)
            c_obj_file_name = cwd + '/' + c_obj.name + ".obj"
            bpy.ops.export_scene.obj(filepath=c_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 

            tag_cmd = tag_bin + " %s %s > %s" % (b_obj_file_name, cwd + '/' + c_obj_name + ".obj", cwd + '/' + c_obj_name + "_regions.mdl")
            subprocess.check_output([tag_cmd],shell=True)
            append_cmd = append_bin + " %s %s > %s" % (b_mdl_file_name, cwd + '/' + c_obj_name + "_regions.mdl", b_mdl_with_tags_file_name)
            subprocess.check_output([append_cmd],shell=True)
            shutil.copyfile(b_mdl_with_tags_file_name, b_mdl_file_name)

          bpy.ops.object.select_all(action='DESELECT')
          b_obj.select_set(True)
          b_mesh = b_obj.data
          bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath=b_mdl_with_tags_file_name)
          bpy.data.meshes.remove(b_mesh)
          b_obj = scn.objects[b_obj_name]
          b_obj.processor.smoothed = True
          b_obj.processor.newton = True
          b_obj.processor.update_contact_pattern_match_list(context, b_obj)


class ProcessorToolSceneProperty(bpy.types.PropertyGroup):
    active_sp_index: IntProperty(name="Active Spine Object Index", default=0)
    active_c_index: IntProperty(name="Active Contact Object Index", default=0)
    contour_list: CollectionProperty(
        type = ContourNameSceneProperty, name = "Contour List")
    active_contour_index: IntProperty(name="Active Contour Index", default=0)
    include_list: CollectionProperty(
        type = IncludeNameSceneProperty, name = "Include List")
    active_include_index: IntProperty(name="Active Include Index", default=0)
    contact_pattern_list: CollectionProperty(type = ContactPatternSceneProperty, name = "Contact Pattern List")
    active_contact_pattern_index: IntProperty(name="Active Contact Pattern Index", default=0)
    new: BoolProperty(name = "Imported MDL Object", default = False)
    filepath: StringProperty(name = "RECONSTRUCT Series Filepath", default= "")
    min_section: StringProperty(name="Minimum Reconstruct Section File", default= "")
    max_section: StringProperty(name="Maximum Reconstruct Section File", default= "")
    section_thickness: StringProperty(name="Section Thickness", default= "0.05")
    min_sample_interval: FloatProperty(name="Minimum Sample Interval", description='Minimum interpolation interval in microns', default=0.01, precision=4)
    max_sample_interval: FloatProperty(name="Maximum Sample Interval", description='Maximum interpolation interval in microns', default=0.05, precision=4)
    filt: StringProperty(name = "Filter for Object list", default = "d[0-9][0-9]sp[0-9][0-9]")


    '''
    def pattern_change_callback(self,context):

        print('Called whole-scene-level pattern_change_callback')
        bn1_regex = self.base_name_1_pattern.replace('#','[0-9]')
        bn1_regex = bn1_regex.replace('*','.*')
        bn2_regex = self.base_name_2_pattern.replace('#','[0-9]')
        bn2_regex = bn2_regex.replace('*','.*')

        bn1_recomp = re.compile(bn1_regex)
        bn2_recomp = re.compile(bn2_regex)
        
        for obj in bpy.context.scene.collection.children[0].objects:
          if bn1_recomp.fullmatch(obj.name) or bn2_recomp.fullmatch(obj.name):
            obj.processor.name_match=True
          else:
            obj.processor.name_match=False
        return
    '''


    def add_contour(self,context,contour_name,mode):
        if mode == 'contour':
            new_contour=self.contour_list.add()
            new_contour.init_contour(context,contour_name)
        else:
            new_contour=self.include_list.add()
            new_contour.init_include(context,contour_name)
        return(new_contour)


    def generate_contour_list(self, context, filepath):

        # Begin by clearing the current contour list
        self.remove_contour_all(context)

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
      if contour_filter_pattern:
        # convert contour filter pattern to formal regex
        filt_pat = contour_filter_pattern
        filt_regex = filt_pat.replace('#','[0-9]')
        filt_regex = filt_regex.replace('*','.*')
    
        filt_recomp = re.compile(filt_regex)
        filt_contour_list = [ item for item in self.contour_list if filt_recomp.fullmatch(item.name) != None and item.name not in self.include_list ]
      else:
        filt_contour_list = [ item for item in self.contour_list if item.name not in self.include_list ]

      for item in filt_contour_list:
        self.add_contour(context, item.name, "include")

      return


    def include_contour(self, context):
        name = self.contour_list[self.active_contour_index].name
        if name not in self.include_list:
            self.add_contour(context, name, "include")
        return


    def remove_contour(self, context):
        #for name in self.contour_list:
        if (len(self.include_list) > 0):
            name = self.include_list[self.active_include_index].name
            ser_dir = os.path.split(self.filepath)[0]
            ser_file = os.path.split(self.filepath)[-1]

            ser_prefix = os.path.splitext(ser_file)[0]
            out_file = ser_dir + '/' + ser_prefix + "_output"


            #for item in self.include_list:
            #objs = bpy.context.scene.collection.children[0].objects
            #for obj in objs:
            if bpy.data.objects.get(name) is not None:
                bpy.ops.object.select_all(action='DESELECT')
                obj = bpy.context.scene.collection.children[0].objects[self.include_list[self.active_include_index].name]
                obj.select_set(True)
                context.view_layer.objects.active = obj
                m = obj.data
                context.scene.collection.children[0].objects.unlink(obj)
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(m)
                if os.path.exists(out_file + '/'+ name + '_tiles.rawc'):
                    os.remove(out_file + '/'+ name + '_tiles.rawc')
                if os. path.exists(out_file + '/'+ name + '.obj'):
                    os.remove(out_file + '/'+ name + '.obj')
            self.include_list.remove(self.active_include_index)
               
        return


    def remove_contour_all(self, context):

        self.contour_list.clear()
        self.active_contour_index = 0
               
        return


    def remove_components(self,context):
        scn = bpy.context.scene
        contour = self.include_list[self.active_include_index]
        contour_name = contour.name
        self.include_list[contour_name].multi_component == False


    def generate_mesh_object(self, context):
        #set variables
        scn = bpy.context.scene
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
        contour_names = '' 
        for item in self.include_list:
            if self.include_list[str(item.name)].generated == True:
              print('Not generating object, already generated: %s' % (str(item.name)))
              continue
            inc_contour = "-I " + str(item.name) + " "  
            contour_names += inc_contour        
        
        if contour_names != '':
          interpolate_cmd = interpolate_bin + " -i %s -f %s -o %s --min_section=%s --max_section=%s --section_thickness %s  --min_sample_interval %.4g --max_sample_interval %.4g --curvature_gain=1E2 --proximity_gain=3 --min_point_per_contour=4 --deviation_threshold=0.005 %s -w %s" % (ser_dir, ser_prefix, out_file, self.min_section, self.max_section, self.section_thickness, self.min_sample_interval, self.max_sample_interval, contour_names, interp_file)
          print('\nInterpolating Series: \n%s\n' % (interpolate_cmd))
          subprocess.check_output([interpolate_cmd],shell=True)

        #tile traces
        for item in self.include_list:
            if self.include_list[str(item.name)].generated == True:
              continue
            contour_name = str(item.name)
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
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    obj.processor.update_contact_pattern_match_list(context, obj)
                if item.multi_component == True:
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
        if contour.generated == True:
          print('Not generating object, already generated: %s' % (contour_name))
          return

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
                obj.select_set(True)
                context.view_layer.objects.active = obj
                obj.processor.update_contact_pattern_match_list(context, obj)

        if self.include_list[contour_name].multi_component == True:
            print("Multiple Components: %s" % (str(self.include_list[contour_name])))
        return


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
        #    obj= bpy.context.scene.collection.children[0].objects[contour_name] 
        #    obj.select_set(True)

        if mode == "single":
            contour = self.include_list[self.active_include_index]
            contour_name  = contour.name
            bpy.ops.object.select_all(action='DESELECT')
            obj = scn.objects[contour_name]
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj 
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
                context.scene.collection.children[0].objects.unlink(obj)
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
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj 
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
                #obj= bpy.context.scene.collection.children[0].objects[contour_name] 
                #print(obj.name)
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj 
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
                    context.scene.collection.children[0].objects.unlink(obj)
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
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj 
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


    def get_active_obj(self, context, mode):
        scn = bpy.context.scene

        if mode == 'spine':
            obj = scn.objects[self.active_sp_index]
            print(obj.name)
        else: 
            obj = scn.objects[self.active_c_index]
            print(obj.name)
           
        return(obj)


    def select_obj(self,context, mode):
        obj = self.get_active_obj(context, mode)
        obj.processor.select_obj(context, obj)


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
      for obj in bpy.context.scene.collection.children[0].objects:
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
        objs = scn.collection.children[0].objects

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


    def smooth_all(self,context):
      scn = bpy.context.scene
      contact_pattern_list = scn.test_tool.contact_pattern_list
      c_object_list = []
      for contact_pattern in contact_pattern_list:
        bn1_regex = contact_pattern.base_name_1_regex
        bn2_regex = contact_pattern.base_name_2_regex
        c_regex = contact_pattern.contact_name_regex
        full_regex = bn1_regex + c_regex + bn2_regex

        full_recomp = re.compile(full_regex)

        c_object_list.extend([obj.name for obj in scn.objects if full_recomp.fullmatch(obj.name)!= None])

      obj_name_list = sorted([obj.name for obj in scn.objects if obj.name not in c_object_list and obj.type == 'MESH'])

      for obj_name in obj_name_list:
        if (self.include_list[obj_name].multi_component == False) and (self.include_list[obj_name].non_manifold == False):
          obj = scn.objects[obj_name]
          obj.processor.select_obj(context, obj)
          obj.processor.smooth(context)


    def merge_objs(self,context):
        merge_obj = bpy.context.active_object
        name = merge_obj.name
        #bpy.ops.object.modifier_add(type = 'BOOLEAN')
        #bpy.data.objects[name].modifiers['Boolean'].operation = 'UNION'
        merge_obj_list = [obj.name for obj in self.include_list if re.match(name[:3], obj.name[:3]) != None and obj.name != name]
        for obj in merge_obj_list: 
           bpy.ops.object.modifier_add(type = 'BOOLEAN')
           bpy.data.objects[name].modifiers['Boolean'].operation = 'UNION'
           bpy.data.objects[name].modifiers['Boolean'].object = bpy.data.objects[obj]
           bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier='Boolean')
        merge_obj.processor.select_obj(context, merge_obj)
        #self.fix_mesh(merge_obj, 'single')
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
        row.operator('processor_tool.impser', icon='FILEBROWSER', text='')  
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
        col.template_list("NEUROPIL_UL_trace_draw_item","contours_in_ser_file",
                          self, "contour_list",
                          self, "active_contour_index",
                          rows=5)
        col = row.column(align=True)
        col.operator('processor_tool.include_contour', icon='FORWARD', text='') 
        col.operator('processor_tool.include_filter_contour', icon='ANIM', text='') 
        col.operator('processor_tool.remove_contour_all', icon='X', text='') 

        col = row.column()
        col.template_list("NEUROPIL_UL_include_draw_item","included_in_ser_file",
                          self, "include_list",
                          self, "active_include_index",
                          rows=5)
        col = row.column(align=True)
        col.operator('processor_tool.remove_contour', icon='REMOVE', text='')
        col.operator('processor_tool.generate_mesh_object_single', icon='MESH_ICOSPHERE', text='')
        col.operator('processor_tool.generate_mesh_object', icon='ARMATURE_DATA', text='')
        col.label(text='', icon='BLANK1')
        col.operator('processor_tool.fix_mesh', icon='MODIFIER', text='')
        col.operator('processor_tool.remove_components', icon='SEQ_SEQUENCER', text='')

        box1 = layout.box()

        box1 = layout.box()
        row = box1.row()
        row.label(text="Contact Object Pattern List:", icon='OVERLAY')
        row = box1.row()
        col = row.column()
        row.template_list("NEUROPIL_UL_contact_pattern_draw_item","contact_patterns",
                          self, "contact_pattern_list",
                          self, "active_contact_pattern_index",
                          rows=4) 
        col = row.column(align=True)
        col.operator('processor_tool.add_contact_pattern', icon='ADD', text='')
        col.operator('processor_tool.remove_contact_pattern', icon='REMOVE', text='')

        if self.contact_pattern_list:
          contact_pattern = self.contact_pattern_list[self.active_contact_pattern_index]
          contact_pattern.draw_props(box1)


        row = layout.row()
        row.label(text="Object List:", icon='MESH_ICOSPHERE')
        row = layout.row()
        col = row.column()
        row.template_list("NEUROPIL_UL_obj_draw_item","sp_objects_in_scene",
                          bpy.context.scene.collection.children[0], "objects",
                          self, "active_sp_index",
                          rows=4) 
        col = row.column(align=True)
        col.operator('processor_tool.smooth', icon='MOD_SMOOTH', text='')
        col.operator('processor_tool.smooth_all', icon='MOD_OCEAN', text='')
        col.label(text='', icon='BLANK1')
        col.operator('processor_tool.tag_contact_single', icon='PIVOT_MEDIAN', text='')
        col.operator('processor_tool.tag_contacts', icon='POSE_HLT', text='')

        row = layout.row()
        row.label(text= "Merge central object with associated objects: ")
        row = layout.row()
        row.operator("processor_tool.merge_objs", text="Merge Objects")


classes = ( 
            NEUROPIL_OT_impser,
            NEUROPIL_OT_include_contour,
            NEUROPIL_OT_include_filter_contour,
            NEUROPIL_OT_remove_contour,
            NEUROPIL_OT_remove_contour_all,
            NEUROPIL_OT_remove_comp,
            NEUROPIL_OT_tile_mesh,
            NEUROPIL_OT_tile_one_mesh,
            NEUROPIL_OT_fix_mesh,
            NEUROPIL_OT_select_obj,
            NEUROPIL_OT_add_contact_pattern,
            NEUROPIL_OT_remove_contact_pattern,
            NEUROPIL_OT_smooth,
            NEUROPIL_OT_smooth_all,
            NEUROPIL_OT_tag_contact_single,
            NEUROPIL_OT_tag_contacts,
            NEUROPIL_OT_merge_objs,
            NEUROPIL_OT_gamer_coarse_dense,
            NEUROPIL_OT_gamer_coarse_flat,
            NEUROPIL_OT_gamer_smooth,
            NEUROPIL_OT_gamer_normal_smooth,
            NEUROPIL_UL_trace_draw_item,
            NEUROPIL_UL_include_draw_item,
            NEUROPIL_UL_contact_pattern_draw_item,
            ContourNameSceneProperty,
            ContactPatternObjectProperty,
            ContactPatternSceneProperty,
            IncludeNameSceneProperty,
            ProcessorToolObjectProperty,
            ProcessorToolSceneProperty,
            NEUROPIL_UL_obj_draw_item,
            NEUROPIL_PT_processor_tool,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

