# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
        "name": "PropChart",
        "author":"dustractor@gmail.com",
        "blender":(2,80,0),
        "category": "System",
        "description":"Custom multi-object properties in the ui plus presets.",
        "location":"Viewport -> UI -> Chart",
        "warning":"",
        "wiki_url":"",
        "tracker_url":"https://github.com/dustractor/propchart",
        "version":(2,3)
}

from bpy.types import (
    Panel,Operator,bpy_prop_array,Object,Menu,PropertyGroup,WindowManager,
    AddonPreferences)
from bpy.utils import (
    register_class,unregister_class,preset_paths,user_resource)
from bpy.props import StringProperty,PointerProperty,EnumProperty
from pathlib import Path
from re import match
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from mathutils import Vector,Color,Euler,Quaternion
from shutil import copy2

def propexpr(obj,expr):
    if "." in expr:
        head,dot,rest = expr.partition(".")
        indexed = match(r"(\w*)\[(\d*)\]$",head)
        keyed = match(r"(\w*)\[[\"'](.*)[\"']\]$",head)
        if indexed:
            obj = getattr(
                obj,indexed.group(1)).__getitem__(int(indexed.group(2)))
        elif keyed:
            obj = getattr(obj,keyed.group(1)).get(keyed.group(2))
        else:
            obj = getattr(obj,head)
        return propexpr(obj,rest)
    return obj,expr

def _(c=None,r=[]):
    if c:
        r.append(c)
        return c
    return r


@_
class PROPCHART_OT_interpolate(Operator):
    bl_idname = "propchart.interpolate"
    bl_label = "Interpolate"
    bl_options = {"INTERNAL"}
    expr: StringProperty(default="")
    @classmethod
    def poll(self,context):
        return len(context.selected_objects) > 2
    def execute(self,context):
        expr = self.expr
        obs = list(context.selected_objects)
        tot = len(obs)-1
        inc = 1/tot
        first,last = obs[0],obs[-1]
        obj1,prop1 = propexpr(first,expr)
        obj2,prop2 = propexpr(last,expr)
        attr1 = getattr(obj1,prop1)
        attr2 = getattr(obj2,prop2)
        if isinstance(attr1,Vector):
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                attrx[:] = attr1.lerp(attr2,fac)
        elif isinstance(attr1,Euler):
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n + 1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                qa = attr1.to_quaternion()
                qb = attr2.to_quaternion()
                attrx[:] = qa.slerp(qb,fac).to_euler()
        elif isinstance(attr1,Quaternion):
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n + 1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                attrx[:] = attr1.slerp(attr2,fac)
        elif isinstance(attr1,Color):
            r1,g1,b1 = attr1
            r2,g2,b2 = attr2
            vec1 = Vector((r1,g1,b1))
            vec2 = Vector((r2,g2,b2))
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                attrx[:] = vec1.lerp(vec2,fac)
        elif isinstance(attr1,bpy_prop_array) and len(attr1)==4:
            r1,g1,b1,a1 = attr1
            r2,g2,b2,a2 = attr2
            vec1 = Vector((r1,g1,b1))
            vec2 = Vector((r2,g2,b2))
            avec1 = Vector((a1,a1,a1))
            avec2 = Vector((a2,a2,a2))
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                t = (*vec1.lerp(vec2,fac),avec1.lerp(avec2,fac)[0])
                attrx[:] = t
        elif type(attr1) == float:
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                v1 = Vector((attr1,)*3)
                v2 = Vector((attr2,)*3)
                objx,propx = propexpr(ob,expr)
                setattr(objx,propx,v1.lerp(v2,fac)[0])
        elif type(attr1) == Object:
            for n,ob in enumerate(obs):
                objx,propx = propexpr(ob,expr)
                setattr(objx,propx,attr1)
            print("I OBJECT")
        return {"FINISHED"}


@_
class PropChart(PropertyGroup):
    value: StringProperty(default="location,rotation_euler,scale",
                          name="Names of properties of selected objects",
                          description="Commas can be used to separate"
                                      " multiple datapath items.")



@_
class PROPCHART_MT_preset_menu(Menu):
    bl_label = "propchart presets"
    preset_subdir = "propchart_strings"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


@_
class PROPCHART_OT_propchart_preset_add(AddPresetBase,Operator):
    bl_idname = "propchart.add_preset"
    bl_label = "add propchart preset"
    preset_menu = "PROPCHART_MT_preset_menu"
    preset_subdir = "propchart_strings"
    preset_defines = ["propchart = bpy.context.window_manager.propchart"]
    preset_values = ["propchart.value"]

@_
class PROPCHART_PT_presets(PresetPanel,Panel):
    bl_label = "PropChart Presets"
    preset_subdir = "propchart_strings"
    preset_operator = "script.execute_preset"
    preset_add_operator = "propchart.add_preset"


def interp_op(layout,expr):
    op = layout.row(align=True).operator(
        "propchart.interpolate",text=f"∀{expr}",icon="HANDLETYPE_AUTO_VEC")
    op.expr = expr
@_
class PROPCHART_PT_panel(Panel):
    bl_label = "PropChart"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Chart"
    def draw_header_preset(self,context):
        PROPCHART_PT_presets.draw_panel_header(self.layout)
    def draw(self,context):
        prefs = context.preferences.addons[__package__].preferences
        displaystyle = prefs.displaystyle
        propchart_string = context.window_manager.propchart.value
        propstrings = propchart_string.split(",")
        layout = self.layout
        box = layout.box()
        box.prop(context.window_manager.propchart,"value",
                 text="",icon="VIEW_ORTHO")
        box.label(text=propchart_string)
        row = layout.row(align=True)
        row.prop_enum(prefs,"displaystyle","LIST",
                      text="",icon="ALIGN_JUSTIFY")
        row.prop_enum(prefs,"displaystyle","LISTS",
                      text="",icon="LINENUMBERS_OFF")
        row.prop_enum(prefs,"displaystyle","CHART",
                      text="",icon="VIEW_ORTHO")
        if displaystyle == "LIST":
            col = layout.column(align=True)
            for ob in context.selected_objects:
                for expr in propstrings:
                    col.row(align=True).prop(*propexpr(ob,expr),text="")
            layout.separator()
            for expr in propstrings:
                interp_op(layout,expr)

        elif displaystyle == "LISTS":
            cols = {expr:layout.column(align=True) for expr in propstrings}
            for expr in propstrings:
                interp_op(cols[expr],expr)
            for ob in context.selected_objects:
                for expr in propstrings:
                    cols[expr].row(align=True).prop(*propexpr(ob,expr),text="")

        elif displaystyle == "CHART":
            row = layout.row(align=True)
            cols = {expr:row.column(align=True) for expr in propstrings}
            for expr in propstrings:
                interp_op(cols[expr],expr)
            for ob in context.selected_objects:
                for expr in propstrings:
                    cols[expr].row(align=True).prop(*propexpr(ob,expr),text="")
        else:
            print("display style:",displaystyle,"not implemented")
@_
class PropChartPrefs(AddonPreferences):
    bl_idname = __package__
    displaystyle: EnumProperty(
        items=((_.upper(),_,_.title()) for _ in "list lists chart".split()),
        default="LIST")
    def draw(self,context):
        self.layout.prop(self,"displaystyle")
        self.layout.label(text=self.displaystyle)

def deploy_presets():
    if not len(preset_paths("propchart_strings")):
        scriptsdir = Path(user_resource("SCRIPTS"))
        presetsdir = scriptsdir / "presets" / "propchart_strings"
        presetsdir.mkdir(parents=True,exist_ok=True)
        presetsdir = str(presetsdir)
        print(f"[{__package__}]deploying presets to {presetsdir}",end="...")
        builtin_presets = Path(__file__).parent / "presets"
        for presetfile in map(str,builtin_presets.iterdir()):
            copy2(presetfile,presetsdir)
        print("OK")

def register():
    deploy_presets()
    list(map(register_class,_()))
    WindowManager.propchart = PointerProperty(type=PropChart)

def unregister():
    del WindowManager.propchart
    list(map(unregister_class,_()))

