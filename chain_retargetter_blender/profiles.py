from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence


@dataclass(frozen=True)
class ChainDefinition:
    id: str
    label: str
    canonical_bones: Sequence[str]
    required: bool = True


@dataclass(frozen=True)
class RigProfile:
    id: str
    label: str
    aliases: Dict[str, Sequence[str]]
    required_bones: Sequence[str]
    optional_bones: Sequence[str]
    chains: Sequence[ChainDefinition]


COMMON_CHAINS: List[ChainDefinition] = [
    ChainDefinition("root", "Root", ("root", "pelvis", "hips"), required=False),
    ChainDefinition("spine", "Spine", ("pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck", "head")),
    ChainDefinition("left_arm", "Left Arm", ("clavicle_l", "upperarm_l", "lowerarm_l", "hand_l")),
    ChainDefinition("right_arm", "Right Arm", ("clavicle_r", "upperarm_r", "lowerarm_r", "hand_r")),
    ChainDefinition("left_leg", "Left Leg", ("pelvis", "thigh_l", "calf_l", "foot_l", "ball_l")),
    ChainDefinition("right_leg", "Right Leg", ("pelvis", "thigh_r", "calf_r", "foot_r", "ball_r")),
]


PROFILES: List[RigProfile] = [
    RigProfile(
        id="ue5_manny",
        label="UE5 Manny/Quinn",
        aliases={
            "root": ("root",),
            "pelvis": ("pelvis",),
            "spine_01": ("spine_01",),
            "spine_02": ("spine_02",),
            "spine_03": ("spine_03",),
            "spine_04": ("spine_04",),
            "spine_05": ("spine_05",),
            "neck": ("neck_01", "neck"),
            "head": ("head",),
            "clavicle_l": ("clavicle_l",),
            "upperarm_l": ("upperarm_l",),
            "lowerarm_l": ("lowerarm_l",),
            "hand_l": ("hand_l",),
            "clavicle_r": ("clavicle_r",),
            "upperarm_r": ("upperarm_r",),
            "lowerarm_r": ("lowerarm_r",),
            "hand_r": ("hand_r",),
            "thigh_l": ("thigh_l",),
            "calf_l": ("calf_l",),
            "foot_l": ("foot_l",),
            "ball_l": ("ball_l",),
            "thigh_r": ("thigh_r",),
            "calf_r": ("calf_r",),
            "foot_r": ("foot_r",),
            "ball_r": ("ball_r",),
        },
        required_bones=(
            "pelvis",
            "spine_01",
            "spine_02",
            "clavicle_l",
            "upperarm_l",
            "lowerarm_l",
            "thigh_l",
            "calf_l",
            "foot_l",
        ),
        optional_bones=("root", "spine_03", "spine_04", "spine_05", "neck", "head", "hand_l", "hand_r", "ball_l", "ball_r"),
        chains=COMMON_CHAINS,
    ),
    RigProfile(
        id="ue4_mannequin",
        label="UE4 Mannequin",
        aliases={
            "root": ("root",),
            "pelvis": ("pelvis",),
            "spine_01": ("spine_01",),
            "spine_02": ("spine_02",),
            "spine_03": ("spine_03",),
            "neck": ("neck_01", "neck"),
            "head": ("head",),
            "clavicle_l": ("clavicle_l",),
            "upperarm_l": ("upperarm_l",),
            "lowerarm_l": ("lowerarm_l",),
            "hand_l": ("hand_l",),
            "clavicle_r": ("clavicle_r",),
            "upperarm_r": ("upperarm_r",),
            "lowerarm_r": ("lowerarm_r",),
            "hand_r": ("hand_r",),
            "thigh_l": ("thigh_l",),
            "calf_l": ("calf_l",),
            "foot_l": ("foot_l",),
            "ball_l": ("ball_l",),
            "thigh_r": ("thigh_r",),
            "calf_r": ("calf_r",),
            "foot_r": ("foot_r",),
            "ball_r": ("ball_r",),
        },
        required_bones=(
            "pelvis",
            "spine_01",
            "spine_02",
            "spine_03",
            "clavicle_l",
            "upperarm_l",
            "lowerarm_l",
            "thigh_l",
            "calf_l",
            "foot_l",
        ),
        optional_bones=("root", "neck", "head", "hand_l", "hand_r", "ball_l", "ball_r"),
        chains=COMMON_CHAINS,
    ),
    RigProfile(
        id="mixamo",
        label="Mixamo",
        aliases={
            "hips": ("Hips", "mixamorig:Hips"),
            "pelvis": ("Hips", "mixamorig:Hips"),
            "spine_01": ("Spine", "mixamorig:Spine"),
            "spine_02": ("Spine1", "mixamorig:Spine1"),
            "spine_03": ("Spine2", "mixamorig:Spine2"),
            "neck": ("Neck", "mixamorig:Neck"),
            "head": ("Head", "mixamorig:Head"),
            "clavicle_l": ("LeftShoulder", "mixamorig:LeftShoulder"),
            "upperarm_l": ("LeftArm", "mixamorig:LeftArm"),
            "lowerarm_l": ("LeftForeArm", "mixamorig:LeftForeArm"),
            "hand_l": ("LeftHand", "mixamorig:LeftHand"),
            "clavicle_r": ("RightShoulder", "mixamorig:RightShoulder"),
            "upperarm_r": ("RightArm", "mixamorig:RightArm"),
            "lowerarm_r": ("RightForeArm", "mixamorig:RightForeArm"),
            "hand_r": ("RightHand", "mixamorig:RightHand"),
            "thigh_l": ("LeftUpLeg", "mixamorig:LeftUpLeg"),
            "calf_l": ("LeftLeg", "mixamorig:LeftLeg"),
            "foot_l": ("LeftFoot", "mixamorig:LeftFoot"),
            "ball_l": ("LeftToeBase", "mixamorig:LeftToeBase"),
            "thigh_r": ("RightUpLeg", "mixamorig:RightUpLeg"),
            "calf_r": ("RightLeg", "mixamorig:RightLeg"),
            "foot_r": ("RightFoot", "mixamorig:RightFoot"),
            "ball_r": ("RightToeBase", "mixamorig:RightToeBase"),
        },
        required_bones=(
            "pelvis",
            "spine_01",
            "spine_02",
            "neck",
            "head",
            "upperarm_l",
            "lowerarm_l",
            "hand_l",
            "thigh_l",
            "calf_l",
            "foot_l",
        ),
        optional_bones=("spine_03", "clavicle_l", "clavicle_r", "ball_l", "ball_r"),
        chains=COMMON_CHAINS,
    ),
    RigProfile(
        id="generic_humanoid",
        label="Generic Humanoid",
        aliases={
            "root": ("root", "Root", "Armature"),
            "hips": ("hips", "Hips", "pelvis", "Pelvis"),
            "pelvis": ("pelvis", "Pelvis", "hips", "Hips"),
            "spine_01": ("spine", "Spine", "spine_01", "Spine1"),
            "spine_02": ("spine_02", "Spine2", "chest", "Chest"),
            "spine_03": ("spine_03", "upperchest", "UpperChest"),
            "neck": ("neck", "Neck"),
            "head": ("head", "Head"),
            "clavicle_l": ("clavicle_l", "leftshoulder", "LeftShoulder", "shoulder_l"),
            "upperarm_l": ("upperarm_l", "LeftArm", "arm_l", "upper_arm.L", "upperarm.L"),
            "lowerarm_l": ("lowerarm_l", "LeftForeArm", "forearm_l", "lower_arm.L", "lowerarm.L"),
            "hand_l": ("hand_l", "LeftHand", "hand.L"),
            "clavicle_r": ("clavicle_r", "rightshoulder", "RightShoulder", "shoulder_r"),
            "upperarm_r": ("upperarm_r", "RightArm", "arm_r", "upper_arm.R", "upperarm.R"),
            "lowerarm_r": ("lowerarm_r", "RightForeArm", "forearm_r", "lower_arm.R", "lowerarm.R"),
            "hand_r": ("hand_r", "RightHand", "hand.R"),
            "thigh_l": ("thigh_l", "LeftUpLeg", "upleg_l", "thigh.L"),
            "calf_l": ("calf_l", "LeftLeg", "leg_l", "shin.L", "calf.L"),
            "foot_l": ("foot_l", "LeftFoot", "foot.L"),
            "ball_l": ("ball_l", "LeftToeBase", "toe.L"),
            "thigh_r": ("thigh_r", "RightUpLeg", "upleg_r", "thigh.R"),
            "calf_r": ("calf_r", "RightLeg", "leg_r", "shin.R", "calf.R"),
            "foot_r": ("foot_r", "RightFoot", "foot.R"),
            "ball_r": ("ball_r", "RightToeBase", "toe.R"),
        },
        required_bones=("pelvis", "spine_01", "upperarm_l", "lowerarm_l", "thigh_l", "calf_l", "foot_l"),
        optional_bones=("root", "spine_02", "spine_03", "neck", "head", "hand_l", "hand_r", "ball_l", "ball_r"),
        chains=COMMON_CHAINS,
    ),
]


def normalize_bone_name(name: str) -> str:
    return name.casefold().replace(" ", "").replace("-", "").replace("_", "").replace(".", "").replace(":", "")


def profile_by_id(profile_id: str) -> Optional[RigProfile]:
    for profile in PROFILES:
        if profile.id == profile_id:
            return profile
    return None


def alias_variants(values: Iterable[str]) -> List[str]:
    return [normalize_bone_name(value) for value in values]
