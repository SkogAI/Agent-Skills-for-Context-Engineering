# CLAUDE.md — Agent Guide for This Repository

This file provides context for AI assistants (Claude Code, Cursor, Codex, etc.) working in this codebase.

## Project Overview

**Agent Skills for Context Engineering** is an open-source collection of 13 agent skills and 5 example projects focused on context engineering — the discipline of managing LLM context windows to maximize agent effectiveness. Skills are platform-agnostic markdown documents with optional code examples. The repository also serves as a **Claude Code Plugin Marketplace**.

**License**: MIT
**Primary language**: Markdown (skills), TypeScript and Python (examples)
**Maintainer**: Muratcan Koylan

## Repository Structure

```
├── SKILL.md                         # Root skill metadata (collection-level)
├── README.md                        # Project overview, installation, usage
├── CONTRIBUTING.md                  # Contribution guidelines
├── .claude-plugin/marketplace.json  # Claude Code plugin marketplace config
│
├── skills/                          # 13 foundational skills (pure markdown)
│   ├── context-fundamentals/        #   Context anatomy, attention mechanics
│   ├── context-degradation/         #   Lost-in-middle, context poisoning
│   ├── context-compression/         #   Summarization strategies
│   ├── context-optimization/        #   Compaction, masking, caching
│   ├── multi-agent-patterns/        #   Supervisor, peer-to-peer, hierarchical
│   ├── memory-systems/              #   Short/long-term, graph-based memory
│   ├── tool-design/                 #   Tool consolidation, error handling
│   ├── filesystem-context/          #   File-based context management
│   ├── hosted-agents/               #   Sandboxed VMs, pre-built images
│   ├── evaluation/                  #   Multi-dimensional evaluation
│   ├── advanced-evaluation/         #   LLM-as-Judge, bias mitigation
│   ├── project-development/         #   Pipeline architecture, task-model fit
│   └── bdi-mental-states/           #   BDI cognitive modeling
│
├── examples/                        # Complete system demonstrations
│   ├── digital-brain-skill/         #   Personal OS (Claude Code skill)
│   ├── llm-as-judge-skills/         #   TypeScript evaluation tools (19 tests)
│   ├── book-sft-pipeline/           #   Model training pipeline
│   ├── x-to-book-system/            #   Multi-agent content synthesis
│   └── interleaved_thinking/        #   Reasoning trace optimizer (Python)
│
├── template/SKILL.md                # Canonical template for new skills
├── docs/                            # Research and reference documents
└── researcher/                      # Evaluation methodology & outputs
```

## Skill Structure Convention

Every skill follows this structure:

```
skill-name/
├── SKILL.md              # Required: instructions + YAML frontmatter
├── references/            # Optional: detailed reference materials
│   └── *.md
└── scripts/               # Optional: example implementations
    └── *.py or *.ts
```

All SKILL.md files must include YAML frontmatter:

```yaml
---
name: skill-name
description: Description with activation triggers and context
---
```

## Key Rules and Conventions

### Skill Authoring

- **SKILL.md must stay under 500 lines** for optimal context loading performance
- Move detailed reference material to `references/` subdirectory
- Write in **third person** (skills are injected into system prompts)
  - Good: "Processes Excel files and generates reports"
  - Bad: "I can help you process Excel files"
- Challenge every paragraph: "Does Claude really need this? Does it justify its token cost?"
- Skills are **platform-agnostic** — avoid vendor-specific implementations
- Use pseudocode over language-specific implementations in skill content
- Use **lowercase-with-hyphens** for skill directory names
- Each skill has a single focus; split if it grows too large

### Progressive Disclosure

The codebase follows a strict progressive disclosure pattern:
1. At startup, agents load only skill names and descriptions (from frontmatter)
2. Full skill content loads only when activated for a relevant task
3. References load only when deeper detail is needed

### Documentation Style

- Be direct and precise
- Use technical terminology appropriately
- Include specific, actionable guidance — not vague recommendations
- Provide concrete examples with input/output pairs
- Point out complexity and trade-offs
- Metadata footer at the end of each SKILL.md: Created, Last Updated, Author, Version

## Example Projects

### TypeScript (llm-as-judge-skills)

- **Runtime**: Node.js >= 18
- **Module system**: ESM (`"type": "module"`)
- **Dependencies**: AI SDK 4.0, Zod, dotenv
- **Testing**: Vitest (19 passing tests)
- **Linting**: ESLint 9 + typescript-eslint
- **Formatting**: Prettier 3.4
- **Type checking**: `tsc --noEmit` (strict mode)

```bash
cd examples/llm-as-judge-skills
npm install
npm run test          # Run tests
npm run lint          # Lint
npm run format        # Format
npm run typecheck     # Type check
npm run build         # Compile to dist/
```

### Python (interleaved_thinking)

- **Runtime**: Python >= 3.10
- **Build system**: setuptools via pyproject.toml
- **Dependencies**: anthropic, pydantic, rich, python-dotenv
- **Testing**: pytest with pytest-asyncio (`asyncio_mode = "auto"`)
- **Linting**: Ruff (line-length=100, rules: E, F, I, N, W)

```bash
cd examples/interleaved_thinking
pip install -e ".[dev]"
pytest                # Run tests
ruff check .          # Lint
```

## Claude Code Plugin Marketplace

The `.claude-plugin/marketplace.json` file defines 5 plugin bundles grouping the 13 skills:

| Plugin | Skills |
|--------|--------|
| `context-engineering-fundamentals` | context-fundamentals, context-degradation, context-compression, context-optimization |
| `agent-architecture` | multi-agent-patterns, memory-systems, tool-design, filesystem-context, hosted-agents |
| `agent-evaluation` | evaluation, advanced-evaluation |
| `agent-development` | project-development |
| `cognitive-architecture` | bdi-mental-states |

All plugins use `"strict": false` to allow dynamic skill discovery.

## Contributing Workflow

1. Fork the repository
2. Create a feature branch
3. Follow the template in `template/SKILL.md` for new skills
4. Keep SKILL.md files under 500 lines
5. Update root `README.md` to include any new skills
6. Ensure content is platform-agnostic
7. Submit a pull request with a clear description

When adding a new skill:
- Use `template/SKILL.md` as the starting point
- Include YAML frontmatter with `name` and `description`
- Add the skill to the appropriate category in `README.md`
- Register it in `.claude-plugin/marketplace.json` under the appropriate plugin
- Update `SKILL.md` (root) references section

## Git Conventions

- Default branch: `main`
- Commit style: conventional-ish — use descriptive messages (e.g., `feat: add hosted-agents skill`, `fix typos`)
- PRs welcome from forks; community contributions are actively merged

## Files to Never Commit

Refer to `.gitignore` — notably:
- `Private/` — private folder, never push to public repo
- `dashboard/` — separate private repo
- `.env` files, credentials, secrets
- IDE-specific folders (`.vscode/`, `.idea/`, `.cursor/`)
- Python build artifacts (`__pycache__/`, `*.egg-info/`, `dist/`)
- Node build artifacts (`node_modules/`, `dist/` within examples)

## Common Tasks

### Adding a new skill

1. Copy `template/SKILL.md` to `skills/<new-skill-name>/SKILL.md`
2. Fill in frontmatter and sections
3. Add to `README.md` skills table
4. Add to `.claude-plugin/marketplace.json` under the appropriate plugin
5. Add to `SKILL.md` (root) references list

### Running example project tests

```bash
# TypeScript example
cd examples/llm-as-judge-skills && npm install && npm test

# Python example
cd examples/interleaved_thinking && pip install -e ".[dev]" && pytest
```

### Validating skill format

Check that every skill directory contains a `SKILL.md` with valid YAML frontmatter (`name` and `description` fields) and is under 500 lines.
