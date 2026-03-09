from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor
from typing import Dict, Iterable, List, Sequence, Tuple

import bpy
from mathutils import Quaternion, Vector

from .detection import resolve_profile_bones
from .profiles import ChainDefinition, profile_by_id


@dataclass
class ChainMapping:
    id: str
    label: str
    source_bones: List[str]
    target_bones: List[str]


def build_chain_mappings(source_obj, target_obj, source_profile_id: str, target_profile_id: str) -> List[ChainMapping]:
    source_profile = profile_by_id(source_profile_id)
    target_profile = profile_by_id(target_profile_id)
    if not source_profile or not target_profile:
        return []

    source_resolved = resolve_profile_bones(source_obj, source_profile_id)
    target_resolved = resolve_profile_bones(target_obj, target_profile_id)

    mappings: List[ChainMapping] = []
    for source_chain, target_chain in zip(source_profile.chains, target_profile.chains):
        source_chain_bones = _resolve_chain_bones(source_chain, source_resolved)
        target_chain_bones = _resolve_chain_bones(target_chain, target_resolved)
        if not source_chain_bones and not target_chain_bones:
            continue
        mappings.append(
            ChainMapping(
                id=source_chain.id,
                label=source_chain.label,
                source_bones=source_chain_bones,
                target_bones=target_chain_bones,
            )
        )
    return mappings


def _resolve_chain_bones(chain: ChainDefinition, resolved_bones: Dict[str, str]) -> List[str]:
    result: List[str] = []
    for canonical_bone in chain.canonical_bones:
        bone_name = resolved_bones.get(canonical_bone)
        if bone_name and bone_name not in result:
            result.append(bone_name)
    return result


def pair_chain_bones(source_bones: Sequence[str], target_bones: Sequence[str]) -> List[Tuple[str, str]]:
    if not source_bones or not target_bones:
        return []
    if len(source_bones) == 1:
        return [(source_bones[0], target_bone) for target_bone in target_bones]

    pairs: List[Tuple[str, str]] = []
    target_count = len(target_bones)
    source_count = len(source_bones)
    for index, target_bone in enumerate(target_bones):
        factor = 0.0 if target_count == 1 else index / (target_count - 1)
        source_index = min(source_count - 1, round(factor * (source_count - 1)))
        pairs.append((source_bones[source_index], target_bone))
    return pairs


def gather_action_candidates(source_obj) -> List[bpy.types.Action]:
    candidates: Dict[str, bpy.types.Action] = {}
    source_bone_names = {bone.name for bone in source_obj.data.bones}

    if source_obj.animation_data and source_obj.animation_data.action:
        action = source_obj.animation_data.action
        candidates[action.name] = action

    for action in bpy.data.actions:
        if _action_matches_armature(action, source_bone_names):
            candidates[action.name] = action

    return sorted(candidates.values(), key=lambda item: item.name.casefold())


def _action_matches_armature(action: bpy.types.Action, source_bone_names: Iterable[str]) -> bool:
    for fcurve in action.fcurves:
        data_path = fcurve.data_path
        if "pose.bones[\"" not in data_path:
            continue
        bone_name = data_path.split('pose.bones["', 1)[1].split('"]', 1)[0]
        if bone_name in source_bone_names:
            return True
    return False


def estimate_height_ratio(source_obj, target_obj) -> float:
    source_height = _estimate_rest_height(source_obj)
    target_height = _estimate_rest_height(target_obj)
    if source_height <= 1e-5 or target_height <= 1e-5:
        return 1.0
    return target_height / source_height


def _estimate_rest_height(armature_obj) -> float:
    points = [bone.head_local.z for bone in armature_obj.data.bones]
    points.extend(bone.tail_local.z for bone in armature_obj.data.bones)
    if not points:
        return 1.0
    return max(points) - min(points)


def _bone_rest_offset(source_pbone, target_pbone) -> Quaternion:
    source_rest = source_pbone.bone.matrix_local.to_quaternion()
    target_rest = target_pbone.bone.matrix_local.to_quaternion()
    return target_rest @ source_rest.inverted()


def _rotation_from_source(source_pbone, target_pbone) -> Quaternion:
    source_rotation = source_pbone.matrix_basis.to_quaternion()
    return _bone_rest_offset(source_pbone, target_pbone) @ source_rotation


def _copy_root_translation(source_pbone, target_pbone, scale_ratio: float) -> Vector:
    source_location = source_pbone.matrix_basis.to_translation()
    target_rest = target_pbone.bone.matrix_local.to_translation()
    source_rest = source_pbone.bone.matrix_local.to_translation()
    rest_delta = target_rest - source_rest * scale_ratio
    return (source_location * scale_ratio) + rest_delta


def retarget_actions(scene, settings, mappings) -> List[str]:
    source_obj = settings.source_armature
    target_obj = settings.target_armature
    if not source_obj or not target_obj:
        return []

    selected_actions = [item.action_name for item in settings.actions if item.selected]
    if not selected_actions:
        return []

    original_frame = scene.frame_current
    scale_ratio = estimate_height_ratio(source_obj, target_obj) if settings.scale_root_motion else 1.0
    created_actions: List[str] = []

    source_pairs = _pair_lookup(mappings)
    root_targets = _root_targets(mappings)

    if not target_obj.animation_data:
        target_obj.animation_data_create()
    if not source_obj.animation_data:
        source_obj.animation_data_create()

    for action_name in selected_actions:
        source_action = bpy.data.actions.get(action_name)
        if not source_action:
            continue

        new_action = bpy.data.actions.new(name=f"{action_name}_to_{target_obj.name}")
        created_actions.append(new_action.name)
        source_obj.animation_data.action = source_action
        target_obj.animation_data.action = new_action

        frame_start = floor(source_action.frame_range[0])
        frame_end = ceil(source_action.frame_range[1])
        _clear_pose(target_obj)

        for frame in range(frame_start, frame_end + 1, max(1, settings.frame_step)):
            scene.frame_set(frame)
            for source_bone_name, target_bone_name in source_pairs:
                source_pbone = source_obj.pose.bones.get(source_bone_name)
                target_pbone = target_obj.pose.bones.get(target_bone_name)
                if not source_pbone or not target_pbone:
                    continue

                target_pbone.rotation_mode = "QUATERNION"
                target_pbone.rotation_quaternion = _rotation_from_source(source_pbone, target_pbone)
                target_pbone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

            if settings.copy_root_translation:
                for source_bone_name, target_bone_name in root_targets:
                    source_pbone = source_obj.pose.bones.get(source_bone_name)
                    target_pbone = target_obj.pose.bones.get(target_bone_name)
                    if not source_pbone or not target_pbone:
                        continue
                    target_pbone.location = _copy_root_translation(source_pbone, target_pbone, scale_ratio)
                    target_pbone.keyframe_insert(data_path="location", frame=frame)

        new_action.use_fake_user = True

    scene.frame_set(original_frame)
    return created_actions


def _pair_lookup(mappings) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for item in mappings:
        if not item.enabled or item.chain_id == "root":
            continue
        pairs.extend(pair_chain_bones(item.source_bones.split(","), item.target_bones.split(",")))
    return [(source, target) for source, target in pairs if source and target]


def _root_targets(mappings) -> List[Tuple[str, str]]:
    root_pairs: List[Tuple[str, str]] = []
    for item in mappings:
        if item.chain_id != "root" or not item.enabled:
            continue
        root_pairs.extend(pair_chain_bones(item.source_bones.split(","), item.target_bones.split(",")))
    return [(source, target) for source, target in root_pairs if source and target]


def _clear_pose(target_obj) -> None:
    for pose_bone in target_obj.pose.bones:
        pose_bone.location = (0.0, 0.0, 0.0)
        pose_bone.rotation_mode = "QUATERNION"
        pose_bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pose_bone.scale = (1.0, 1.0, 1.0)