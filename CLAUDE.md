# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a creative writing project for a Chinese political black comedy novel "协商共和国" (Republic of Consensus) - a philosophical allegory about AI-era governance. The project explores themes of technology, authoritarianism, and democracy through satirical fiction set in a world divided by a "Civilizational Contest" between the American Consensus Republic (ACR) and the Confederacy of American Free States (CAFS). The ACR, a technologically advanced society, views itself as the vanguard of human evolution, while CAFS represents the "old civilization" being left behind.

## Key Documentation Files

### Essential Reading (Must Read First)
- **INSTRUCT.md** - Project constitution defining core identity, worldview, and creative philosophy
- **WORKFLOW.md** - Operational manual for human-AI collaborative writing workflow
- **OUTLINE.md** - Story structure and plot framework
- **STRUCTURE.md** - Project file organization and structure

### Supporting Documentation
- **README.md** - Project introduction and quick start guide
- **ROADMAP.md** - Creative progress and planning
- **resources/style.md** - Writing style guide
- **resources/quality_control.md** - Quality control handbook
- **worldbuilding/politics.md** - Political legacy and hidden forces
- **worldbuilding/timeline.md** - Historical timeline
- **worldbuilding/life.md** - Daily Life in 2038 details
- **worldbuilding/organization_acr.md** - Institutions and organizations of the ACR
- **worldbuilding/organization_cafs.md** - Institutions and organizations of the CAFS

## Project Structure

```
manuscript/               # Novel chapters organized by parts
├── 第一部分_协商共和国示范区/  # Part 1: Demonstration Zone
worldbuilding/           # World-building documents
├── core.md             # Core worldview settings
├── charactor.md        # Character bios and profiles
├── glosory.md          # Terminology glossary
├── politics.md         # Political legacy and hidden forces
├── timeline.md         # Historical timeline
├── life.md             # Life in 2038 details
├── organization_acr.md # Institutions and organizations of the ACR
└── organization_cafs.md # Institutions and organizations of the CAFS
prompts/                # AI writing prompts
├── 提示模板/            # Template prompts
├── 当前章节提示/        # Current chapter prompts
└── 已完成提示/          # Completed prompts
resources/              # Writing resources
├── style.md            # Style guidelines
├── quality_control.md  # Quality control checklist
└── memory.md          # Project memory archive
```

## Creative Workflow

This project follows a **human-led, AI-assisted** creative workflow:

1. **Human-Led Ideation** - Humans create plot structure and chapter outlines
2. **Human-Led Writing** - Humans write initial drafts independently
3. **AI-Assisted Review** - AI provides optimization suggestions based on style.md
4. **Human-Led Finalization** - Humans make final edits and decisions

**Important**: AI should never directly modify human-written content without explicit permission. AI's role is to provide suggestions, not to rewrite.

## Writing Style & Tone

- **Genre**: Political black comedy / AI governance allegory
- **Core Tone**: "Rational packaging of absurdity" - serious treatment of absurd situations
- **Approach**: "Sideways portrayal" not "direct explanation" - reveal the system through details
- **Humor**: Comes from forced combination of incompatible discourse systems
- **Language**: 
  - Official contexts: "正能量表达" (positive energy expression)
  - Private contexts: "语言污染" (language pollution)
  - AI feedback: Cold, objective but absurd content

## Quality Control

The project uses a three-tier quality control system:
- **L1**: Basic consistency (worldview, character, terminology)
- **L2**: Style and execution (tone, pacing, humor techniques)
- **L3**: Theme and artistry (depth, irony, philosophical resonance)

## Character Consistency

All characters must align with `worldbuilding/charactor.md` definitions:
- **Stephen Hubbard** - NVPD cybercrime chief, pragmatic but conflicted, caught between ACR's progress and CAFS's tradition.
- **Sarah Hubbard** - Represents old-world humanistic values, struggling to preserve memory in a new era.
- **David Hubbard** - Talented programmer whose software challenges the system's control.
- **Emily Hubbard** - Future-oriented, pragmatic daughter, a true believer in ACR's vision.
- **Sharon Williams** - Procedural bureaucrat, Stephen's main opponent, a staunch defender of ACR's purity.

## Worldbuilding Rules

- **RESTORE AI** - The governing AI system that evaluates "civilizational maladaptation"
- **ACR (American Consensus Republic)** - The technologically advanced society, viewing itself as the vanguard of human evolution.
- **CAFS (Confederacy of American Free States)** - The traditional society, representing the "old civilization" being left behind.
- **Consensus scoring systems** - Family Harmony Index (FUS), Social Harmony Index (SHI), and Civilizational Adaptability Index (CAI)
- All terminology must match `worldbuilding/glosory.md`

## Chapter Structure Requirements

Each chapter must include:
- **Opening hook** within first 300 words
- **Mid-chapter reversal** (acts 3-4)
- **2-3 foreshadowing elements**
- **Emotional pacing** (tension-relief-tension)
- **Clear scene transitions** 
- **Cliffhanger ending**

## AI Collaboration Modes

1. **Worldview Coach** - Pre-writing inspiration and world-consistent details
2. **Red Team Review** - Post-writing critical analysis and plot hole identification
3. **Quantitative QC** - Scoring-based quality assessment against quality_control.md

## Publication Format

This is a GitBook-based project (book.json configuration). The novel is structured for episodic publication with each chapter as a standalone unit while contributing to the overall narrative arc.

## Working with This Project

1. Always read INSTRUCT.md first to understand the creative philosophy
2. Reference WORKFLOW.md for collaboration protocols
3. Check worldbuilding/ files for consistency
4. Use resources/style.md for writing guidance
5. Apply resources/quality_control.md for reviews
6. Never make major plot or character changes without consulting core documentation