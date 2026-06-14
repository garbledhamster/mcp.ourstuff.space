# Ourstuff Local AI Brain

Domain language for the Local AI Brain installer and project-local memory system.

## Language

**Local AI Brain**:
A portable, project-scoped memory and context system for agent work. It keeps useful project history, decisions, proofs, and related lookup data close to the project that produced it.
_Avoid_: ailocalbrain, localai brain, AI local brain

**Install Container**:
The `localaibrain` directory at an installed project root that contains Local AI Brain-owned package files, runtime state, MCP files, plans, and similar support artifacts. It is a coherent Local AI Brain workspace, not a sealed box.
_Avoid_: localai brain folder, scattered install files

**Commander**:
The root-level `localaibrain.py` script used to deploy, run, roll back, and maintain an installed Local AI Brain.
_Avoid_: installer, wrapper script

**Brain UI**:
The human maintenance surface for inspecting, correcting, and organizing Local AI Brain memories and support data without requiring direct knowledge of the underlying storage structure.
_Avoid_: manual database editing, hidden internals

**Brain Memory**:
A durable Local AI Brain record stored in the project brain database. Brain Memory is the canonical project history that agents query before planning or acting.
_Avoid_: loose note, flat-file memory

**Brain Artifact**:
A readable file produced or retained by Local AI Brain to support inspection, import, export, or review. Brain Artifacts are useful context, but they are not the canonical memory store.
_Avoid_: source of truth, primary memory

**Brain Issue**:
A project-management work item stored in Local AI Brain for agent planning, assignment, status, and future handoff. Brain Issues may sync with external issue trackers, but the project brain can own the working state.
_Avoid_: Git-only issue, loose todo

**Brain Review**:
A Local AI Brain workflow item that records an agent proposal awaiting human or orchestrator approval, rejection, or revision. Brain Reviews make pending decisions visible in the commander and UI.
_Avoid_: hidden approval, chat-only decision

**Agent Workspace**:
The self-contained Local AI Brain environment that gives local agent models shared project memory, issue context, artifacts, and maintenance commands without requiring extra infrastructure.
_Avoid_: external project-management stack, cloud dependency

**PM User**:
A non-technical or semi-technical project owner who can use Local AI Brain through the commander, UI, and agent instructions without needing to understand the internal implementation.
_Avoid_: developer, operator
