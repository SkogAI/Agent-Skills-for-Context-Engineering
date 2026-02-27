# Build Stress Test: Context-Aware Agent Harness

## What Was Built

A Python agent harness (`examples/context-harness/`) that implements filesystem-context patterns as working code. The harness wraps the Anthropic API with context management middleware:

- **Workspace manager**: Creates `scratch/`, `plans/`, `memory/`, `agents/` directories. File existence = state.
- **Scratch pad / observation masking**: Tool outputs > 2000 chars offloaded to `scratch/` files. Returns summary + file reference. Agent uses `read_file` with line ranges to retrieve specific sections.
- **Plan persistence**: Plans written to `plans/current.md`, re-read at the start of each turn. Survives workspace restarts.
- **Dynamic skill loading**: Scans YAML frontmatter at init (cheap — names + descriptions only). Keyword matches against task description. Loads full skill content only for top matches.
- **Context budget**: Tracks estimated token usage. Triggers compaction at 80% utilization. Default budget: 25k tokens.
- **Compaction**: Saves full history to scratch, asks a smaller model to summarize, reinitializes with summary.
- **Sub-agent workspace isolation**: Each sub-agent gets its own Workspace with independent scratch/plans/memory.
- **Architectural reduction**: 3 tools total (read_file, write_file, search_files). Not 17.

**Files**: `harness.py` (330 lines), `run.py` (demo), `test_harness.py` (45 tests, all passing), `pyproject.toml`.

## Skills Loaded and Used

| Skill | Loaded | Actually Used | Impact |
|-------|--------|---------------|--------|
| filesystem-context | Full read | **Heavy** — directly guided workspace layout, scratch pad, plan persistence, sub-agent isolation | High: most actionable skill in the collection |
| project-development | Full read | **Medium** — "manual prototype first" methodology, filesystem-as-state-machine pattern | Medium: good process guidance, less code-specific |
| tool-design | Full read | **Medium** — architectural reduction principle (17→3 tools), consolidation principle | Medium: the reduction insight was the takeaway |
| context-optimization | Full read | **Medium** — budget management, compaction trigger at 80%, observation masking | Medium: validated the budget approach |

## Where Skills Helped

### 1. Observation Masking Is the Killer Pattern

Budget simulation with real skill files:

| Approach | Budget Used | Remaining |
|----------|-------------|-----------|
| With masking (scratch pad) | 29% (7,373 tokens) | 17,627 tokens |
| Without masking (raw output) | 172% (43,069 tokens) | Budget blown |

**Masking saved 35,696 tokens** — a 5x reduction. The scratch pad pattern alone determines whether a 25k budget task succeeds or fails. This is the collection's most validated claim, now with concrete numbers.

### 2. Progressive Disclosure Works

Skill catalog (13 names + descriptions) costs **4% of budget** (1,119 tokens). Two fully loaded skills cost **~18% combined**. This confirms the design: names are cheap, full content is expensive, load selectively.

### 3. Architectural Reduction Was Immediately Useful

Started thinking about 5-7 tools (read, write, search, list, execute, mkdir, delete). The tool-design skill's consolidation principle compressed this to 3. Tests confirm 3 tools cover every use case the harness needs. The `search_files` tool + line-range reads on `read_file` replace what would otherwise be 4-5 separate tools.

### 4. Filesystem as State Machine Simplified Everything

The project-development pattern (file existence gates execution) eliminated the need for any state tracking code. Plan exists? Load it. Scratch file exists? It's been computed. Agent workspace exists? Agent has run. Zero state management code beyond the filesystem.

## Where Skills Were Silent

### 1. The Agent Loop Itself

**Biggest gap in the collection.** No skill covers: turn management, tool call parsing, response routing, termination conditions, or the API interaction layer. Every agent harness needs this, and the builder is on their own.

The collection covers what to put IN the context but not how to MANAGE the conversation loop that fills and drains it.

### 2. Compaction Bootstrapping

Skills say "summarize and reinitialize." But the compaction call itself needs a model call, which has its own context constraints. What model to use for compaction? What to include in the summary prompt? How to validate the summary didn't lose critical state? These are left as exercises.

### 3. Token Estimation

Budget tracking requires token estimation. The skills discuss budgets in tokens but provide no guidance on estimation. The harness uses chars/4 (rough approximation). In practice, token counts vary significantly between English text, code, JSON, and markdown. The collection should acknowledge this gap or provide estimation guidance.

### 4. Skill Matching Implementation

Skills say "load dynamically based on relevance" but don't discuss HOW to match. The harness uses keyword overlap on descriptions — crude but functional. Better approaches (TF-IDF, embedding similarity, explicit trigger patterns) aren't mentioned. The activation triggers in the frontmatter descriptions are the closest guidance, but they're written for human interpretation, not programmatic matching.

### 5. Concurrent Tool Execution

The Anthropic API supports multiple `tool_use` blocks per response. The skills don't discuss handling parallel tool calls — do you mask all results independently? Track their combined budget impact? This matters for efficiency.

### 6. Error Recovery in Agent Loops

Tool-design mentions "error messages that enable recovery" but this is tool-level, not harness-level. What does the harness do when a tool fails? Retry? Report to the agent? Abort? The gap between "tools should have good errors" and "the harness should handle failure gracefully" is unaddressed.

## Where Skills Were Misleading or Imprecise

### 1. "2000 token" Threshold Ambiguity

Filesystem-context says threshold should be "2000 tokens" for the scratch pad. But implementations naturally work in characters, and the skill conflates chars and tokens. The 4x difference means a "2000 token" threshold is actually ~8000 chars. The harness uses 2000 chars (matching the code example, not the prose).

### 2. Compaction Quality Claims Without Evidence

Context-optimization states "50-70% token reduction with less than 5% quality degradation." This is stated as fact with no citation or conditions. In practice, compaction quality depends entirely on task type, summary prompt quality, and what information is critical. Stating these numbers without qualification is misleading.

### 3. "Semantic + Filesystem Search Work Well Together"

Asserted in filesystem-context without any guidance on how to combine them. What triggers semantic vs. filesystem search? How do you merge results? This is a claim, not guidance.

## Gaps Identified

### Missing Skill: Agent Loop Design

The collection needs a skill covering:
- Turn management (when to stop, how to detect completion)
- Tool call routing and parallel execution
- API interaction patterns (streaming vs. batch, retries)
- Response parsing (text blocks vs. tool_use blocks)
- Conversation state management

This is the "plumbing" skill that everything else depends on.

### Missing Skill: Token Economics

The collection needs a skill or section covering:
- Token estimation techniques (chars/4 for English, tiktoken for precision)
- Cost modeling (input vs. output pricing, cached vs. uncached)
- Budget allocation strategies (how much for system prompt vs. tools vs. messages)
- The gap between advertised context window and effective context

### Weak Area: Implementation Specificity in filesystem-context

The skill gives good patterns but its code examples are pseudocode that doesn't run. The `handle_tool_output` example is illustrative but misses: file naming collisions, cleanup of stale scratch files, concurrent access, and the actual summary generation (just `extract_summary(output, max_tokens=200)` with no implementation).

### Weak Area: Cross-Skill Integration Guidance

The skills reference each other (filesystem-context → context-optimization → multi-agent-patterns) but don't explain how patterns compose in practice. The harness uses masking (filesystem-context) + budget tracking (context-optimization) + reduced tools (tool-design) simultaneously. There's no skill that says "here's how these three patterns interact."

## Verdict: Did the Collection Help?

**Yes, meaningfully — during design. Less so during implementation.**

- **Design phase**: The skills provided a clear architectural vocabulary. "Scratch pad," "observation masking," "plan persistence," "dynamic loading," "architectural reduction" — each pattern became a concrete component in the harness. Without the skills, I would have built SOMETHING, but the result would be less coherent. The skills compressed the design space.

- **Implementation phase**: The skills ran out of gas. Writing the actual Python code — the agent loop, tool execution, path resolution, API interaction — required knowledge the skills don't provide. This is expected (they're architecture skills, not implementation guides) but worth noting. The gap between "here's the pattern" and "here's working code" is where most of the build time went.

- **Token overhead**: Loading 4 skills into the system prompt consumed ~23% of a 25k budget. This is non-trivial. For a tightly-budgeted agent, you can afford 2-3 loaded skills, not 13. The progressive disclosure pattern (catalog in static, full content on demand) is essential, not optional.

- **Net assessment**: The collection made the build **faster** (clear patterns to follow) and **better** (coherent architecture instead of ad-hoc). The token overhead of loading skills is real but manageable with selective loading. The biggest risk is loading too many skills and leaving insufficient budget for the actual task.

## Numbers Summary

| Metric | Value |
|--------|-------|
| Harness size | 330 lines Python |
| Tools | 3 (read_file, write_file, search_files) |
| Tests | 45 (all passing) |
| Skills loaded during design | 4 |
| Token cost of skill catalog | 4% of 25k budget |
| Token cost of 2 loaded skills | 18% of 25k budget |
| Observation masking savings | 5x (35,696 tokens saved on 13-skill analysis) |
| Compaction trigger | 80% utilization |
| Skills exercised | filesystem-context, context-optimization, tool-design, project-development |
| Skills silent | agent loop, token economics, error recovery, cross-pattern integration |

---

**Built**: 2026-02-27
**Session**: Build stress-test (handover-4)
**Harness location**: `examples/context-harness/`
