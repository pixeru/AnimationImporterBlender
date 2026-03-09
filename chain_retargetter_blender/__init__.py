bl_info = {
    "name": "Chain Retargetter Blender",
    "author": "GitHub Copilot",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Chain Retarget",
    "description": "Detect common humanoid rigs and retarget selected actions through chain mapping.",
    "category": "Animation",
}

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup

from .detection import detect_rig
from .retarget import build_chain_mappings, gather_action_candidates, retarget_actions


class CRB_ActionItem(PropertyGroup):
    action_name: StringProperty(name="Action")
    selected: BoolProperty(name="Selected", default=False)


class CRB_ChainItem(PropertyGroup):
    chain_id: StringProperty(name="Chain ID")
    label: StringProperty(name="Label")
    source_bones: StringProperty(name="Source Bones")
    target_bones: StringProperty(name="Target Bones")
    enabled: BoolProperty(name="Enabled", default=True)


class CRB_Settings(PropertyGroup):
    source_armature: PointerProperty(name="Source", type=bpy.types.Object, poll=lambda self, obj: obj.type == "ARMATURE")
    target_armature: PointerProperty(name="Target", type=bpy.types.Object, poll=lambda self, obj: obj.type == "ARMATURE")

    source_profile_id: StringProperty(name="Source Profile")
    source_profile_label: StringProperty(name="Source Label", default="Unknown")
    source_profile_score: StringProperty(name="Source Score", default="0.0")
    source_profile_candidates: StringProperty(name="Source Candidates")

    target_profile_id: StringProperty(name="Target Profile")
    target_profile_label: StringProperty(name="Target Label", default="Unknown")
    target_profile_score: StringProperty(name="Target Score", default="0.0")
    target_profile_candidates: StringProperty(name="Target Candidates")

    actions: CollectionProperty(type=CRB_ActionItem)
    action_index: IntProperty(name="Action Index", default=0)

    chains: CollectionProperty(type=CRB_ChainItem)
    chain_index: IntProperty(name="Chain Index", default=0)

    copy_root_translation: BoolProperty(name="Copy Root Translation", default=True)
    scale_root_motion: BoolProperty(name="Scale Root Motion", default=True)
    frame_step: IntProperty(name="Frame Step", default=1, min=1, max=4)


class CRB_OT_detect_rig(Operator):
    bl_idname = "crb.detect_rig"
    bl_label = "Detect Rig"
    bl_description = "Identify the most likely rig profile and matching percentage"

    side: StringProperty(name="Side")

    def execute(self, context):
        settings = context.scene.crb_settings
        armature_obj = settings.source_armature if self.side == "SOURCE" else settings.target_armature
        if not armature_obj:
            self.report({"ERROR"}, "Select an armature first")
            return {"CANCELLED"}

        best, candidates = detect_rig(armature_obj)
        summary = ", ".join(f"{candidate.label}: {candidate.score:.1f}%" for candidate in candidates)

        if self.side == "SOURCE":
            settings.source_profile_id = best.profile_id
            settings.source_profile_label = best.label
            settings.source_profile_score = f"{best.score:.1f}"
            settings.source_profile_candidates = summary
        else:
            settings.target_profile_id = best.profile_id
            settings.target_profile_label = best.label
            settings.target_profile_score = f"{best.score:.1f}"
            settings.target_profile_candidates = summary

        self.report({"INFO"}, f"Detected {best.label} at {best.score:.1f}%")
        return {"FINISHED"}


class CRB_OT_refresh_actions(Operator):
    bl_idname = "crb.refresh_actions"
    bl_label = "Refresh Actions"
    bl_description = "Scan the source armature and collect matching actions"

    def execute(self, context):
        settings = context.scene.crb_settings
        if not settings.source_armature:
            self.report({"ERROR"}, "Select a source armature first")
            return {"CANCELLED"}

        settings.actions.clear()
        for action in gather_action_candidates(settings.source_armature):
            item = settings.actions.add()
            item.action_name = action.name
            item.selected = True

        self.report({"INFO"}, f"Loaded {len(settings.actions)} action(s)")
        return {"FINISHED"}


class CRB_OT_build_chain_map(Operator):
    bl_idname = "crb.build_chain_map"
    bl_label = "Build Chain Map"
    bl_description = "Create automatic chain mappings between the detected source and target rigs"

    def execute(self, context):
        settings = context.scene.crb_settings
        if not settings.source_armature or not settings.target_armature:
            self.report({"ERROR"}, "Select both source and target armatures")
            return {"CANCELLED"}
        if not settings.source_profile_id or not settings.target_profile_id:
            self.report({"ERROR"}, "Detect both rigs first")
            return {"CANCELLED"}

        settings.chains.clear()
        for mapping in build_chain_mappings(
            settings.source_armature,
            settings.target_armature,
            settings.source_profile_id,
            settings.target_profile_id,
        ):
            item = settings.chains.add()
            item.chain_id = mapping.id
            item.label = mapping.label
            item.source_bones = ",".join(mapping.source_bones)
            item.target_bones = ",".join(mapping.target_bones)
            item.enabled = bool(mapping.source_bones and mapping.target_bones)

        self.report({"INFO"}, f"Built {len(settings.chains)} chain mapping(s)")
        return {"FINISHED"}


class CRB_OT_retarget_actions(Operator):
    bl_idname = "crb.retarget_actions"
    bl_label = "Retarget Selected Actions"
    bl_description = "Bake selected source actions onto the target armature"

    def execute(self, context):
        settings = context.scene.crb_settings
        if not settings.source_armature or not settings.target_armature:
            self.report({"ERROR"}, "Select both source and target armatures")
            return {"CANCELLED"}
        if not settings.chains:
            self.report({"ERROR"}, "Build the chain map first")
            return {"CANCELLED"}

        created_actions = retarget_actions(context.scene, settings, settings.chains)
        if not created_actions:
            self.report({"ERROR"}, "No actions were retargeted")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Created {len(created_actions)} retargeted action(s)")
        return {"FINISHED"}


class CRB_PT_panel(Panel):
    bl_label = "Chain Retarget"
    bl_idname = "CRB_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Chain Retarget"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.crb_settings

        source_box = layout.box()
        source_box.label(text="Source")
        source_box.prop(settings, "source_armature")
        source_box.operator("crb.detect_rig", text="Detect Source Rig").side = "SOURCE"
        source_box.label(text=f"Best Match: {settings.source_profile_label} ({settings.source_profile_score}%)")
        if settings.source_profile_candidates:
            source_box.label(text=settings.source_profile_candidates)

        target_box = layout.box()
        target_box.label(text="Target")
        target_box.prop(settings, "target_armature")
        target_box.operator("crb.detect_rig", text="Detect Target Rig").side = "TARGET"
        target_box.label(text=f"Best Match: {settings.target_profile_label} ({settings.target_profile_score}%)")
        if settings.target_profile_candidates:
            target_box.label(text=settings.target_profile_candidates)

        mapping_box = layout.box()
        mapping_box.label(text="Actions")
        mapping_box.operator("crb.refresh_actions", text="Refresh Source Actions")
        if not settings.actions:
            mapping_box.label(text="No actions loaded")
        for item in settings.actions:
            row = mapping_box.row(align=True)
            row.prop(item, "selected", text="")
            row.label(text=item.action_name)

        chain_box = layout.box()
        chain_box.label(text="Chain Map")
        chain_box.operator("crb.build_chain_map", text="Auto Build Chain Map")
        if not settings.chains:
            chain_box.label(text="No chains mapped yet")
        for item in settings.chains:
            row = chain_box.row(align=True)
            row.prop(item, "enabled", text="")
            split = row.split(factor=0.33)
            split.label(text=item.label)
            right = split.split(factor=0.5)
            right.label(text=item.source_bones or "Missing source")
            right.label(text=item.target_bones or "Missing target")

        options_box = layout.box()
        options_box.label(text="Bake Options")
        options_box.prop(settings, "copy_root_translation")
        options_box.prop(settings, "scale_root_motion")
        options_box.prop(settings, "frame_step")
        options_box.operator("crb.retarget_actions", text="Retarget Selected Actions")


CLASSES = (
    CRB_ActionItem,
    CRB_ChainItem,
    CRB_Settings,
    CRB_OT_detect_rig,
    CRB_OT_refresh_actions,
    CRB_OT_build_chain_map,
    CRB_OT_retarget_actions,
    CRB_PT_panel,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.crb_settings = PointerProperty(type=CRB_Settings)


def unregister():
    del bpy.types.Scene.crb_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()