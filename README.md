# Diagram Skills

A collection of **agent skills** for producing software design diagrams as **PlantUML** code - sequence, class, use case, activity, state, component, deployment, ER and more.

Each skill teaches an AI coding agent (such as Claude Code) how to draw one kind of diagram the way a team would draw it by hand: read the real code, agree on conventions with the user first, write `.puml` files in a consistent house style, then lint and render them. The output is meant to go straight into design documents (SDS, technical specs) and be reviewed against the codebase.

## Why

Diagrams generated ad hoc by an agent tend to drift: every diagram uses different participant names, wording, numbering and error handling, and many don't match what the code actually does. These skills fix that by giving the agent:

- **A workflow** - settle conventions, trace the real code, write, number, lint, render, check.
- **A house style** - one look across all diagrams of the same kind, so they read as if drawn by one person.
- **Building blocks and templates** - ready-made PlantUML fragments for common patterns.
- **Scripts** - helpers that number steps and lint the style so mistakes are caught before rendering.

## Skills

| Skill | Diagram | Status |
|---|---|---|
| [`sequence-diagram`](sequence-diagram/SKILL.md) | Sequence diagrams for features / use cases, traced through every layer down to the database | Available |
| `class-diagram` | Classes, attributes, methods and relationships | Planned |
| `use-case-diagram` | Actors, use cases, include/extend | Planned |
| `activity-diagram` | Workflows and business processes | Planned |
| `state-diagram` | State machines for entities (orders, payments, ...) | Planned |
| `component-diagram` | Modules/services and their interfaces | Planned |
| `deployment-diagram` | Nodes, containers and infrastructure | Planned |
| `er-diagram` | Database entities and relationships | Planned |

## Repository layout

Every skill lives in its own folder and follows the same structure:

```
<skill-name>/
├── SKILL.md          # entry point: when to use the skill and the step-by-step workflow
├── assets/           # starter templates (.puml)
├── references/       # building blocks, patterns, style details loaded on demand
└── scripts/          # helpers (numbering, linting, ...)
```

`SKILL.md` starts with a YAML front matter (`name`, `description`). The description is what the agent uses to decide when to load the skill, so it lists the phrases that should trigger it.

## Installation

Copy (or symlink) the skill folders into a location your agent reads skills from.

**Claude Code - for all your projects:**

```bash
git clone <this-repo-url> diagram-skills
cp -r diagram-skills/sequence-diagram ~/.claude/skills/
```

**Claude Code - for a single project:**

```bash
mkdir -p .claude/skills
cp -r diagram-skills/sequence-diagram .claude/skills/
```

The skill is picked up automatically in the next session.

## Usage

Just ask for the diagram in plain language; the agent loads the matching skill on its own:

```
Draw sequence diagrams for the Create Order and Delete Order features.
Make sequence diagrams for the backlog items assigned to me.
Check and renumber the diagrams in docs/diagrams/sequence.
Vẽ sequence cho chức năng Login.
```

On the first run the agent asks about conventions (participant naming, stereotypes, actor roles, label language, file locations) and saves the answers to a conventions file next to the diagrams (e.g. `SEQUENCE_CONVENTIONS.md`), so later sessions and teammates reuse them instead of asking again.

## Requirements

- **Python 3** - to run the helper scripts, e.g.
  ```bash
  python sequence-diagram/scripts/number_steps.py docs/diagrams/*.puml
  ```
- **Java + PlantUML** (optional) - to check and render diagrams. If PlantUML isn't installed, the agent can download `plantuml.jar` into a temporary folder:
  ```bash
  java -jar plantuml.jar -charset UTF-8 -checkonly diagrams/*.puml
  java -jar plantuml.jar -tpng -o out diagrams/*.puml
  ```

## Adding a new skill

1. Create a folder named after the diagram type (`class-diagram`, `state-diagram`, ...).
2. Write `SKILL.md` with front matter and a workflow that:
   - asks the user to settle conventions before drawing, and records them in a conventions file;
   - derives the diagram from the real code rather than old docs;
   - defines a house style and how to verify it (lint, render, look at the output).
3. Add a starter template in `assets/`, patterns in `references/`, and any lint/format helpers in `scripts/`.
4. Add the skill to the table above.
