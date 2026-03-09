# Chain Retargetter Blender

Chain Retargetter Blender is a Blender add-on focused on animation retargeting through bone chains.

The current focus is humanoid retargeting, where common body regions can be mapped and transferred in a controlled, chain-based workflow.

The goal of the project is to make retargeting easier and more controllable by letting animators map and transfer motion chain by chain instead of forcing a full-rig solve or a tedious bone-by-bone workflow.

## Core Idea

Most retargeting workflows sit at one of two extremes:

- transfer everything at once and hope the rigs are similar enough
- manually adjust individual bones when they are not

This project is built around a middle-ground approach.

Instead of treating the rig as a single black box, the add-on should allow animation to be mapped and transferred one bone chain at a time, such as:

- spine
- neck and head
- arms
- hands
- legs
- feet

This chain-based workflow should provide much more control over how motion is interpreted between source and target humanoid rigs, especially when they do not share the same:

- proportions
- hierarchy
- naming conventions
- rest pose assumptions

## Project Vision

The add-on is intended to help bridge the gap between automation and manual control.

The near-term scope is humanoid retargeting, but the longer-term direction is to extend the system toward more general rig retargeting so users can define custom chains for non-humanoid setups as well.

With a chain-focused retargeting workflow, the user should be able to:

- define corresponding source and target chains
- tune how translation and rotation are transferred per chain
- handle rigs with different proportions more predictably
- isolate and fix problem areas without reworking the entire retarget
- build a retarget setup that is easier to understand and debug

## Why Chain Retargeting

Animation problems usually do not affect every part of a character equally. A spine may need one strategy, arms another, and legs another again. Treating retargeting as a set of chain-level problems makes that complexity manageable.

This approach should make it easier to preserve intent in the original motion while adapting it to rigs that differ structurally from the source.

## Planned Direction

While the implementation is still being defined, the add-on is expected to focus on:

- humanoid chain mapping tools
- retarget transfer controls per chain
- workflows for rigs with non-matching proportions or hierarchy
- future support for general rigs through user-defined custom chains
- practical usability inside Blender for iterative animation work

## Status

Functional Blender addon MVP.

## Current Addon

The repository now includes a Blender addon in [chain_retargetter_blender](/e:/PC/Desktop/ChainRetargetterBlender/chain_retargetter_blender) that provides a first pass at an Unreal-style chain retargeting workflow:

- detects likely humanoid rig profiles with a percentage score
- supports built-in profile heuristics for Mixamo, UE4 Mannequin, UE5 Manny/Quinn, and a generic humanoid fallback
- auto-builds source and target chain mappings for root, spine, arms, and legs
- scans and lists source actions so multiple animations can be selected and retargeted in one pass
- bakes retargeted animation onto the target armature as new Blender actions

## Install

1. Zip the [chain_retargetter_blender](/e:/PC/Desktop/ChainRetargetterBlender/chain_retargetter_blender) folder.
2. In Blender, open Edit > Preferences > Add-ons > Install.
3. Select the zip file and enable `Chain Retargetter Blender`.

## Workflow

1. Open the `Chain Retarget` panel in the 3D View sidebar.
2. Set the source armature and the target armature.
3. Run `Detect Source Rig` and `Detect Target Rig`.
4. Review the best-match profile and percentage for each rig.
5. Run `Refresh Source Actions` to load animations that belong to the source armature.
6. Leave enabled the actions you want to transfer.
7. Run `Auto Build Chain Map` and review the generated chains.
8. Adjust bake options and run `Retarget Selected Actions`.

## Notes

- This is a practical MVP, not a full clone of Unreal Engine's IK Retargeter.
- The current transfer uses chain-driven local rotation baking plus optional root translation scaling.
- The detection system is heuristic and works best on standard humanoid naming conventions.
- Finger chains, IK goals, twist bones, and pose correction layers are not yet implemented.