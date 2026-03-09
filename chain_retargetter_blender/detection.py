from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from .profiles import PROFILES, RigProfile, alias_variants, normalize_bone_name, profile_by_id


@dataclass
class DetectionCandidate:
    profile_id: str
    label: str
    score: float
    matches: Dict[str, str]
    missing: List[str]


def _bone_lookup(armature_obj) -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for bone in armature_obj.data.bones:
        lookup[normalize_bone_name(bone.name)] = bone.name
    return lookup


def match_profile(armature_obj, profile: RigProfile) -> DetectionCandidate:
    lookup = _bone_lookup(armature_obj)
    matches: Dict[str, str] = {}
    missing: List[str] = []

    required_weight = 0.75
    optional_weight = 0.25
    total_required = max(1, len(profile.required_bones))
    total_optional = max(1, len(profile.optional_bones))

    required_hits = 0
    optional_hits = 0

    for canonical_name, aliases in profile.aliases.items():
        found_name = find_matching_bone_name(lookup, aliases)
        if found_name:
            matches[canonical_name] = found_name

    for canonical_name in profile.required_bones:
        if canonical_name in matches:
            required_hits += 1
        else:
            missing.append(canonical_name)

    for canonical_name in profile.optional_bones:
        if canonical_name in matches:
            optional_hits += 1

    score = (
        (required_hits / total_required) * required_weight
        + (optional_hits / total_optional) * optional_weight
    ) * 100.0

    return DetectionCandidate(
        profile_id=profile.id,
        label=profile.label,
        score=round(score, 1),
        matches=matches,
        missing=missing,
    )


def detect_rig(armature_obj) -> Tuple[DetectionCandidate, List[DetectionCandidate]]:
    candidates = [match_profile(armature_obj, profile) for profile in PROFILES]
    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    best = candidates[0]
    return best, candidates[:3]


def find_matching_bone_name(lookup: Dict[str, str], aliases: Sequence[str]) -> str:
    normalized_aliases = alias_variants(aliases)
    for alias in normalized_aliases:
        match = lookup.get(alias)
        if match:
            return match
    for alias in normalized_aliases:
        for normalized_name, original_name in lookup.items():
            if normalized_name.endswith(alias) or alias.endswith(normalized_name):
                return original_name
    return ""


def resolve_profile_bones(armature_obj, profile_id: str) -> Dict[str, str]:
    profile = profile_by_id(profile_id)
    if not profile:
        return {}
    lookup = _bone_lookup(armature_obj)
    result: Dict[str, str] = {}
    for canonical_name, aliases in profile.aliases.items():
        match = find_matching_bone_name(lookup, aliases)
        if match:
            result[canonical_name] = match
    return result