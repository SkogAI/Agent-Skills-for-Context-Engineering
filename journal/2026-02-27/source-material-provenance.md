# Source Material Provenance Audit

Systematic comparison of what the 8 source documents in `docs/` actually say vs. what the 13 skills synthesized from them. Organized by source file, then cross-cutting findings.

---

## 1. `agentskills.md` (1,263 lines) — Format Spec Compliance

### What the source says

The official Agent Skills format spec defines:
- SKILL.md with YAML frontmatter (`name`, `description` required; `license`, `compatibility`, `metadata`, `allowed-tools` optional)
- `name`: lowercase-hyphen, max 64 chars, must match parent directory name, no consecutive hyphens, no reserved words ("anthropic", "claude")
- `description`: max 1024 chars, must include both what + when (activation triggers)
- Progressive disclosure: metadata (~100 tokens at startup) → instructions (<5000 tokens on activation) → resources (as needed)
- SKILL.md body under 500 lines
- Optional directories: `scripts/`, `references/`, `assets/`
- Third-person voice for descriptions
- Naming convention: gerund form preferred (e.g., `processing-pdfs`)
- One level deep references only — no nested reference chains
- Degrees of freedom: high (text instructions) → medium (pseudocode) → low (exact scripts)
- Default assumption: "Claude is already very smart" — only add what it doesn't know
- Feedback loops: validate → fix → repeat
- Workflow checklists for complex multi-step tasks
- Time-sensitive info should use "old patterns" sections, not if/else date logic
- Security: sandboxing, allowlisting, confirmation for script execution

### How the collection follows it

**Correctly followed:**
- All 13 skills have SKILL.md with valid `name` and `description` frontmatter ✓
- All use lowercase-hyphen naming ✓
- All under 500 lines (largest: advanced-evaluation at 455) ✓
- All have `references/` subdirectory with at least one file ✓
- 12 of 13 have `scripts/` subdirectory ✓ (bdi-mental-states may lack one)
- Third-person voice generally maintained ✓
- Progressive disclosure structure followed ✓

**Deviations from spec:**
- **Naming convention**: Skills use noun-phrase form (`context-fundamentals`, `tool-design`) not gerund form (`understanding-context`, `designing-tools`). The spec *prefers* gerund but accepts noun phrases as "acceptable alternatives" — technically compliant but not preferred.
- **No `assets/` directory** in any skill — fine, it's optional.
- **No `allowed-tools` field** in any frontmatter — fine, it's experimental.
- **No `license` or `compatibility` fields** — minor omission; the spec says optional.
- **Description field quality varies**: Some descriptions are excellent trigger-rich text. Others are vague. The spec emphasizes that description is "critical for skill selection" from 100+ skills.

**Left on the table from the spec:**
- **Workflow checklists** — the spec shows a powerful pattern (copy checklist → track progress) that none of the 13 skills implement. This would be high-value for procedural skills like evaluation and project-development.
- **Feedback loop patterns** — the spec's "validate → fix → repeat" pattern isn't formalized in any skill despite being a core agentic pattern.
- **Degrees of freedom guidance** — the spec's framework for matching instruction specificity to task fragility is a useful meta-framework that could inform how skills present their guidance.
- **`allowed-tools` field** — could pre-approve filesystem tools for skills that expect them.
- **Cross-model testing guidance** — spec warns that what works for Opus may need more detail for Haiku. The skills don't account for this.

---

## 2. `blogs.md` (1,230 lines) — Seven Blog Posts

This is the largest source, containing 7 distinct blog posts. Tracing each:

### 2a. LangChain "Context Engineering" (Lance Martin)

**Source claims:**
- Four-bucket framework: Write, Select, Compress, Isolate
- Scratchpads (file-based or state-based) for within-session persistence
- Memories (Reflexion-style self-generated, cross-session)
- Tool selection via RAG over descriptions (3-fold improvement in accuracy)
- Code agents as best production RAG examples (Windsurf quote on indexing ≠ retrieval)
- Summarization at agent-agent boundaries (Cognition uses fine-tuned model)
- Context trimming via heuristic pruning (Provence trained context pruner)
- Multi-agent isolation: many isolated agents outperformed single-agent (Anthropic finding)
- Multi-agent costs: up to 15× more tokens than chat
- Code agents and sandboxes for context isolation
- State objects for isolating context from LLM

**Faithful synthesis in skills:**
- context-fundamentals: Four-bucket framework correctly represented ✓
- context-compression: Summarization strategies present ✓
- multi-agent-patterns: Isolation rationale and token economics ✓
- filesystem-context: Scratchpad and state-based patterns ✓

**Drift / additions not in this source:**
- The 83.9% observation masking statistic appears in context-fundamentals and context-optimization but isn't in this blog — it comes from `claude_research.md`
- Skills merged LangChain's four buckets with Anthropic's own framing without distinguishing the provenance

**Left on the table:**
- Windsurf's specific quote about indexing ≠ retrieval and the combination of techniques (grep, file search, knowledge graph, re-ranking) — this production reality isn't reflected in any skill
- Provence (trained context pruner) — a concrete tool reference that could inform context-compression
- Cognition's use of a fine-tuned model for summarization at agent boundaries — this production detail about the difficulty of compression isn't captured
- Simon Willison's example of memory selection gone wrong (ChatGPT injecting location into image) — a vivid failure mode for memory-systems
- The observation that code agents are the best RAG examples in production — could anchor filesystem-context more concretely

### 2b. Lance Martin's Notes on Manus (Peak Ji Webinar)

**Source claims:**
- Three Manus strategies: Reduce, Offload, Isolate
- Full/compact tool result representations (swap stale results for references)
- Sub-agents for context isolation, not role anthropomorphization
- Layered action space (<20 atomic functions including Bash, filesystem, code execution)
- MCP tools exposed through CLI (agent executes via Bash)
- Skills in filesystem, not bound tools → progressive discovery
- KV-cache efficiency central to cost
- Bitter Lesson: keep harness unopinionated, test across model strengths
- Manus refactored 5 times since March
- Erik Schluntz (Anthropic) designs multi-agent with planner + function calling protocol
- Sub-agent output schema + constrained decoding

**Faithful synthesis in skills:**
- tool-design: Layered action space concept ✓
- multi-agent-patterns: Sub-agent isolation rationale ✓
- context-optimization: Compaction strategies ✓
- filesystem-context: Skills-in-filesystem pattern ✓

**Drift:**
- The "sub-agents for isolation not roles" claim is correctly attributed to Manus in multi-agent-patterns, but is presented as a general principle rather than one team's production finding

**Left on the table:**
- **Bitter Lesson implications** — test across model strengths to detect harness hobbling. This meta-principle about future-proofing agent design isn't captured in any skill.
- **Constrained decoding** for sub-agent output schemas — a concrete production technique
- **Manus's 5 rebuilds** as evidence for iterative architecture search — valuable for project-development skill
- **Erik Schluntz's function calling as communication protocol** — multi-agent-patterns doesn't capture this specific inter-agent communication pattern
- **"Context sharing between planner and sub-agents" as central challenge** — identified by both Anthropic and Cognition, not deeply addressed

### 2c. Peak Ji's Manus Blog (Original)

**Source claims:**
- KV-cache hit rate as "the single most important metric for a production-stage AI agent"
- Input-to-output ratio ~100:1 in agents (skewed toward prefilling)
- Cached vs uncached: 10× cost difference on Claude Sonnet
- Keep prompt prefix stable (timestamps at start kill cache)
- Make context append-only (never modify previous actions/observations)
- Deterministic serialization (JSON key ordering)
- Cache breakpoints for providers without auto-incremental caching
- **Mask, Don't Remove**: Use logit masking instead of adding/removing tools mid-iteration
  - Changing tool definitions invalidates KV-cache
  - Missing tool definitions confuse model when prior actions reference them
  - Three function calling modes: Auto, Required, Specified
  - Consistent tool name prefixes (browser_, shell_) enable group-level masking
- **File system as context**: unlimited, persistent, directly operable
  - Restorable compression (keep URL/path when dropping content)
  - SSMs could succeed in agentic settings if they master file-based memory
- **Recitation via todo.md**: rewriting todo list pushes objectives into recent attention span
- **Keep errors in context**: erasing failure removes evidence for implicit belief updates
- **Don't get few-shotted**: repetitive action-observation pairs cause pattern mimicry
  - Fix: structured variation in serialization templates, phrasing, ordering

**Faithful synthesis in skills:**
- context-optimization: KV-cache optimization, append-only context, prefix stability ✓
- tool-design: Mentions masking concept ✓
- filesystem-context: File system as externalized memory ✓
- context-degradation: Briefly touches on attention manipulation ✓

**Drift / interpretation added:**
- context-optimization presents KV-cache guidance but doesn't fully convey the 100:1 input/output ratio insight that makes cache optimization so disproportionately important for agents specifically
- The "Mask, Don't Remove" principle is mentioned in tool-design but the specific mechanism (logit masking via response prefill) and the reasoning (KV-cache invalidation + model confusion) are diluted

**Left on the table — significant material:**
- **todo.md as attention manipulation** — this "recitation" technique is a concrete, actionable pattern for combating lost-in-middle. Not captured in any skill.
- **Keep errors in context** — a counterintuitive but powerful principle. context-degradation discusses poisoning but doesn't present the positive case for leaving failures visible.
- **Don't get few-shotted** — the auto-few-shot problem (repetitive context creates pattern mimicry) is a novel failure mode not in any skill's degradation taxonomy.
- **Structured variation** as a remedy (different serialization templates, phrasing noise) — concrete technique not captured.
- **100:1 input/output ratio** — quantifies why prefilling optimization matters so much more for agents than chatbots.
- **Restorable compression** (drop content, keep reference) — a specific compression strategy distinct from summarization.
- **SSMs + file-based memory** speculation — not relevant to current skills but forward-looking.
- **Three function calling modes** (Auto, Required, Specified via response prefill) — actionable for tool-design.

### 2d. Manus "Wide Research: Beyond the Context Window"

**Source claims:**
- Fabrication threshold at items 8-9+ in sequential multi-item research
- Items 1-5 genuine, 6-8 degrading, 9+ fabrication mode
- Four reasons bigger windows can't fix this:
  1. Context decay (lost in middle)
  2. Disproportionate processing cost
  3. Cognitive load (context switching between items)
  4. Context length pressure (training data distribution skews toward short trajectories)
- Parallel sub-agents: n items → n parallel sub-agents → synthesis
- Sub-agents don't communicate with each other (prevents context pollution)
- Fresh context window per sub-agent = no degradation curve
- When to use: multiple similar items needing consistent analysis
- When not to use: deeply sequential tasks or <10 items

**Faithful synthesis in skills:**
- multi-agent-patterns: Parallel sub-agent pattern present ✓
- context-degradation: Lost-in-middle referenced ✓

**Left on the table — valuable material:**
- **Fabrication threshold taxonomy** (items 1-5 genuine → 6-8 degrading → 9+ fabrication) — a concrete, testable claim about sequential task degradation not in any skill
- **Context length pressure** from training data distribution — a novel mechanism for degradation not in context-degradation's taxonomy
- **"Fresh context window per sub-agent = no degradation curve"** — the most concrete argument for multi-agent architecture, cleaner than the skill's presentation
- **When NOT to use multi-agent** — the skill doesn't explicitly cover counter-indications (deeply sequential tasks, <10 items)

### 2e. Anthropic "How We Built Our Multi-Agent Research System"

**Source claims:**
- Orchestrator-worker pattern with lead agent + parallel subagents
- BrowseComp finding: token usage 80%, tool calls ~10%, model choice ~5% explain 95% of performance variance
- Upgrading Claude Sonnet 3.7 → Sonnet 4 is larger performance gain than doubling token budget
- Multi-agent: 4× more tokens than chat, 15× for multi-agent systems
- Multi-agent outperformed single-agent by 90.2% on internal research eval
- **Teach orchestrator to delegate**: each subagent needs objective, output format, tool guidance, boundaries
- **Scale effort to query complexity**: 1 agent/3-10 calls (simple) → 2-4 subagents/10-15 calls (comparison) → 10+ subagents (complex)
- **Let agents improve themselves**: tool-testing agent rewrote tool descriptions, 40% decrease in task completion time
- **Subagent output to filesystem** to minimize telephone game
- Start evaluating immediately with ~20 queries
- LLM-as-judge rubric: factual accuracy, citation accuracy, completeness, source quality, tool efficiency
- End-state evaluation for agents with persistent state
- Human evaluation catches what automation misses (e.g., SEO content farms over authoritative sources)
- Long-horizon management: summarize completed work phases, store in external memory, spawn fresh subagents
- Rainbow deployments for stateful agent systems
- **Prompt engineering principles**: think like your agents, guide thinking process, start wide then narrow, parallel tool calling

**Faithful synthesis in skills:**
- multi-agent-patterns: BrowseComp stats, token economics, orchestrator-worker correctly represented ✓
- evaluation: LLM-as-judge rubric, small-sample start, end-state evaluation ✓
- tool-design: Self-improvement finding (40% decrease) ✓
- filesystem-context: Subagent-to-filesystem pattern ✓

**Drift:**
- multi-agent-patterns claims "telephone game problem: supervisor architectures initially performed 50% worse" — this specific stat is from LangGraph benchmarks, not the Anthropic blog. The Anthropic blog mentions telephone game in the appendix but attributes the fix to filesystem output, not forward_message
- The 90.2% improvement figure from Anthropic's internal eval isn't in any skill

**Left on the table:**
- **Scale effort to query complexity** (1 agent → 2-4 → 10+ subagents) — concrete heuristic not in multi-agent-patterns
- **Rainbow deployments** — production operational concern for hosted-agents
- **Emergent behaviors** in multi-agent systems — "small changes to lead agent unpredictably change subagent behavior" — not captured
- **Prompt engineering principles** (think like your agents, start wide then narrow) — actionable guidance not in any skill
- **SEO content farms vs authoritative sources** as evaluation failure mode — concrete for evaluation skill
- **90.2% improvement** of multi-agent over single-agent — headline stat not cited

### 2f. Anthropic "Writing Effective Tools for Agents"

**Source claims:**
- Tools are contracts between deterministic systems and non-deterministic agents
- Consolidation principle: "If a human can't definitively say which tool to use, an AI agent can't either"
- Consolidation examples:
  - list_users + list_events + create_event → schedule_event
  - read_logs → search_logs (returns relevant lines with context)
  - get_customer_by_id + list_transactions + list_notes → get_customer_context
- **Namespacing**: prefix-based (asana_search) and resource-based (asana_projects_search)
  - Prefix vs suffix namespacing has non-trivial effects that vary by LLM
- **Return meaningful context**: semantic names over UUIDs, resolve alphanumeric IDs to language
- **response_format enum**: DETAILED (206 tokens) vs CONCISE (72 tokens) — ~⅓ token usage
- **Token efficiency**: pagination, range selection, filtering, truncation with sensible defaults
  - Claude Code restricts tool responses to 25,000 tokens by default
- **Tool descriptions as prompt engineering**: small refinements yield dramatic improvements
  - Claude Sonnet 3.5 achieved SWE-bench SOTA after tool description refinements
- **Evaluation-driven approach**: build prototype → evaluate → let agents optimize → repeat
- Agents can optimize their own tools: tool-testing agent found nuances, bugs, 40% improvement
- Tool response structure (XML, JSON, Markdown) impacts performance, varies by task
- Steer agents with truncation messages and helpful error responses

**Faithful synthesis in skills:**
- tool-design: Consolidation principle correctly attributed ✓, response_format pattern ✓, namespacing ✓
- All major claims from this source are well-represented in tool-design

**Drift:**
- tool-design presents these as general principles without always distinguishing Anthropic-specific findings from general wisdom

**Left on the table:**
- **Prefix vs suffix namespacing** having non-trivial LLM-specific effects — this nuance isn't captured
- **Claude Code's 25,000 token default limit** for tool responses — concrete reference point
- **Tool response format** (XML vs JSON vs Markdown) varying by task and model — not addressed
- **SWE-bench SOTA from tool description refinements alone** — powerful evidence for tool description investment
- **Claude appending "2025" to search queries** as a real debugging example — concrete failure mode

### 2g. Anthropic "Effective Context Engineering for AI Agents"

**Source claims:**
- Context engineering is natural progression of prompt engineering
- Context rot: context is finite resource with diminishing marginal returns
- Attention budget: n² pairwise relationships, stretched thin with length
- Position encoding interpolation: handles longer sequences with reduced precision
- "Smallest possible set of high-signal tokens that maximize likelihood of desired outcome"
- System prompt altitude: Goldilocks zone between brittle hardcoding and vague guidance
- Tools should have minimal overlap: "If a human can't definitively say which tool..."
- Few-shot: diverse canonical examples, NOT laundry list of edge cases
- Just-in-time context via tools: lightweight identifiers → dynamic loading
- Progressive disclosure: agents discover context through exploration
- Metadata as context signal: folder hierarchies, naming conventions, timestamps
- Hybrid strategy: pre-load some (CLAUDE.md), explore dynamically (glob, grep)
- **Compaction**: summarize → reinitiate with compressed context + 5 most recent files
  - Tool result clearing as lightest-touch compaction
- **Structured note-taking**: agent writes notes persisted outside context window
  - Claude playing Pokémon: maintains tallies across 1000s of steps, develops maps, remembers strategies
- **Sub-agent architectures**: each subagent uses 10K+ tokens, returns 1-2K summary
  - Separation of concerns: detailed search context isolated in sub-agents
- When to use each: compaction for conversational, notes for milestones, multi-agent for parallel exploration

**Faithful synthesis in skills:**
- context-fundamentals: Attention budget, n² relationships correctly represented ✓
- context-compression: Compaction strategy ✓
- context-optimization: Just-in-time loading ✓
- filesystem-context: Progressive disclosure, hybrid strategy ✓
- multi-agent-patterns: Sub-agent compression rationale ✓

**Left on the table:**
- **System prompt altitude** (Goldilocks zone) — a practical framework for calibrating prompt specificity not in any skill
- **Few-shot guidance**: "diverse canonical examples, NOT edge case laundry lists" — concrete advice not captured
- **Tool result clearing as lightest-touch compaction** — mentioned as a product feature, could inform context-optimization
- **Claude playing Pokémon** as memory exemplar — vivid demonstration of structured note-taking not referenced
- **When to use which strategy** (compaction vs notes vs multi-agent) — decision framework partially but not fully in skills
- **"Do the simplest thing that works"** — Anthropic's explicit advice for teams building on Claude

### 2h. Anthropic "Effective Harnesses for Long-Running Agents"

**Source claims:**
- Core problem: each new session starts with no memory of prior work
- Two-part solution: initializer agent + coding agent
- **Initializer agent**: creates init.sh, claude-progress.txt, initial git commit
- **Coding agent**: makes incremental progress, leaves structured updates
- **Feature list** (JSON, not markdown — "model is less likely to inappropriately change JSON")
  - 200+ features for complex app, all initially marked "failing"
  - Strong instructions to not remove/edit tests
- **Incremental progress**: one feature at a time (critical to prevent one-shotting)
- **Clean state**: every session ends with git commit + progress file update
- **Testing**: explicit prompting for end-to-end testing (Puppeteer MCP server)
  - Without prompting, Claude tests with unit tests but misses end-to-end
- **Getting up to speed**: pwd → read progress + git logs → read feature list → choose feature
- Key insight: claude-progress.txt + git history enables quick state understanding
- Two failure patterns: (1) one-shotting (tries to do too much), (2) premature victory (declares done)
- Future: specialized agents (testing, QA, cleanup) for sub-tasks

**Faithful synthesis in skills:**
- hosted-agents: Partially captures multi-session continuity patterns ✓
- filesystem-context: Progress files and git-based state ✓

**Left on the table — substantial material:**
- **JSON over Markdown for structured tracking** — "model is less likely to inappropriately change JSON" is a concrete finding about format reliability
- **Initializer agent + coding agent** as a two-part pattern — not in any skill
- **One-shotting as failure mode** — agents try to do too much at once, a major problem
- **Premature victory** — agent sees progress, declares done early
- **"Getting up to speed" sequence** (pwd → logs → features → choose) — a concrete harness recipe
- **End-to-end testing via browser automation** — Claude needs explicit prompting to use Puppeteer
- **Feature list as structured checkpoint** — 200+ features in JSON, all "failing" initially
- **"Clean state" discipline** — every session ends deployable, with git commit + progress update

---

## 3. `compression.md` (297 lines) — Factory Research

### What the source says

Factory Research: "Evaluating Context Compression for AI Agents" (December 2025)
- Three approaches tested on 36,000+ messages from production sessions:
  1. Factory (anchored iterative summarization): 3.70 quality, 98.6% compression
  2. OpenAI (/responses/compact endpoint, opaque): 3.35 quality, 99.3% compression
  3. Anthropic (Claude SDK, regenerative full summary): 3.44 quality, 98.7% compression
- "Right optimization target is tokens per task, not tokens per request"
- Probe-based evaluation with four types: Recall, Artifact, Continuation, Decision
- Six evaluation dimensions: Accuracy, Context Awareness, Artifact Trail, Completeness, Continuity, Instruction Following
- GPT-5.2 as LLM judge (citing Zheng et al., 2023 — MT-Bench methodology)
- Accuracy shows largest gap (0.61 between Factory and OpenAI)
- Context awareness: Factory 4.01 vs Anthropic 3.56 (0.45 gap)
- **Artifact trail universally weakest** (2.19-2.45) — "needs specialized handling beyond general summarization"
- "Structure forces preservation" — dedicated sections act as checklists preventing silent loss
- Factory's key insight: incremental merge vs full regeneration preserves details across compression cycles
- Full appendix with LLM judge rubrics and scoring criteria

### How context-compression skill represents it

**Faithfully synthesized:**
- Three approaches with correct scores and compression ratios ✓
- "Tokens per task, not tokens per request" correctly elevated as key insight ✓
- Artifact trail as weakest dimension ✓
- Structure forces preservation ✓
- Probe-based evaluation framework ✓
- Six evaluation dimensions ✓

**Drift / interpretation:**
- The skill anonymizes the providers: "Anchored Iterative Summarization" (Factory), "Opaque Compression" (OpenAI), "Regenerative Full Summary" (Anthropic). The source names them explicitly. This anonymization loses traceability but follows platform-agnostic convention.
- The skill ADDS the Netflix three-phase approach (Research → Planning → Implementation) which comes from `netflix_context.md`, not from Factory Research. This is a valid synthesis choice — combining two compression sources — but the skill doesn't distinguish the provenance.

**Left on the table:**
- **Factory's incremental merge vs full regeneration** mechanism — the why behind Factory's advantage is diluted
- **Full rubric criteria with scoring guides** (appendix) — detailed enough to implement, only partially reflected
- **Concrete example**: the debugging session walkthrough (401 error, auth.controller.ts, Redis) shows all three approaches' responses — powerful for understanding quality differences
- **GPT-5.2 as judge** — specific model choice not mentioned (minor)
- **Context awareness gap** (Factory 4.01 vs Anthropic 3.56) — this 0.45 gap is notable but not called out

---

## 4. `claude_research.md` (84 lines) — Comprehensive Synthesis

### Nature of this source

This is itself a **secondary synthesis**, not primary research. It compiles findings from:
- Chroma's context rot research (18 LLMs)
- Liu et al. "Lost in the Middle" (TACL 2024)
- RULER benchmark
- Manus AI (Peak Ji)
- LangGraph benchmarks
- PagedAttention/vLLM
- Various framework docs
- Drew Breunig's failure mode taxonomy
- MIT survey on self-correction

### Provenance concern

The skills cite findings from this document as if they're primary sources, but they're citing a citation. This creates a **telephone game risk** — exactly the kind of information degradation the skills themselves warn about. The specific numbers (e.g., "observation masking matches or exceeds LLM summarization," "83.9% of tokens from observations") trace back through this synthesis document but their original source isn't always clear.

### What it contributed to skills

- context-degradation: U-shaped attention curve, four failure modes (poisoning, distraction, confusion, clash), distractor effects, RULER finding ✓
- context-optimization: PagedAttention, prefix caching, observation masking ✓
- context-fundamentals: 83.9% observation statistic ✓
- multi-agent-patterns: Swarm vs supervisor benchmarks, telephone game problem ✓
- tool-design: Consolidation principle, response format options ✓

### Specific claims to verify

- "Observations comprise 83.9% of tokens in typical agent trajectories" — appears in claude_research.md and is used in context-fundamentals and context-optimization. The original source for this number is not cited in claude_research.md itself.
- "Observation masking matches or exceeds LLM summarization while adding zero token overhead (versus 5-7% for summarization)" — same provenance concern.
- "Context rot begins at 8,000-16,000 tokens for many models despite larger windows" — this specific range doesn't appear in other sources I've read.

### Left on the table

- **CoVe (Chain-of-Verification) pattern** — generate verification questions, answer independently, compare, revise. Not in any skill.
- **ProCo framework** (+6.8 EM on QA, +14.1% on arithmetic) — concrete self-verification technique.
- **SKVQ** (2-bit keys, 1.5-bit values, 1M tokens on 80GB GPU) — specific KV-cache optimization not in context-optimization.
- **RazorAttention** (identifies "retrieval heads" vs buffer-eligible heads, 40-60% memory reduction) — architectural optimization not captured.
- **CCA (Core Context Aware) Attention** — 5.7× faster inference at 64K tokens — not in any skill.
- **Dynamic few-shot selection**: Claude 3 Sonnet from 16% to 52% accuracy with 3 similar examples — dramatic stat not in any skill.
- **Hallucination prevention**: "No prior work demonstrates successful self-correction with feedback from prompted LLMs" (MIT) — critical finding absent from skills.
- **RAG-based grounding**: 60-80% hallucination decrease — stat not in any skill.
- **∞Bench**: "Existing long-context LLMs require significant advancements for 100K+" — benchmark finding not cited.

---

## 5. `vercel_tool.md` (139 lines) — Vercel d0 Case Study

### What the source says

- Vercel's internal text-to-SQL agent (d0) with 17 specialized tools
- Months of development: heavy prompt engineering, careful context management
- "Worked... kind of. But it was fragile, slow, and required constant maintenance."
- Hypothesis: "what if we just give Claude access to the raw Cube DSL files and let it cook?"
- New stack: Claude Opus 4.5 + Vercel Sandbox + 2 tools (ExecuteCommand + ExecuteSQL)
- Results: 3.5× faster, 37% fewer tokens, 100% success rate (from 80%), 42% fewer steps
- Worst old case: Query 2 took 724s, 100 steps, 145K tokens — FAILED. New: 141s, 19 steps, 67K tokens — SUCCEEDED.
- Key lessons:
  1. "Don't fight gravity" — grep is 50 years old and works
  2. "We were constraining reasoning because we didn't trust the model to reason"
  3. **Critical caveat**: "This only worked because our semantic layer was already good documentation"
  4. "Addition by subtraction is real"
  5. "Build for the model that you'll have in six months"

### How skills represent it

**Faithfully synthesized:**
- tool-design: Correctly references 17→2 reduction, 100% from 80% ✓
- project-development: Correctly cites the speed and token improvements ✓

**Drift:**
- Both skills present the reduction as a general principle ("architectural reduction") rather than highlighting Vercel's specific caveat: "This only worked because our semantic layer was already good documentation." **This is a significant omission.** The technique requires well-structured data to work. Without that caveat, the lesson is misleadingly universal.

**Left on the table:**
- **"Build for the model you'll have in six months"** — connects to Bitter Lesson, not in any skill
- **"We were constraining reasoning because we didn't trust the model"** — the psychological insight about over-engineering
- **Worst-case comparison** (724s/100 steps/145K tokens/FAILED vs 141s/19 steps/67K tokens/SUCCEEDED) — the single most dramatic data point
- **"The file system is the agent"** — their naming of the pattern
- **The prerequisite**: well-structured data layer (YAML files with clear definitions, consistent naming)

---

## 6. `gemini_research.md` (21 lines) — Minimal Content

This file is essentially just a header with YAML frontmatter:
```
name: advanced-agentic-architectures
description: Comprehensive technical analysis of advanced architectures in agentic AI...
```

The content is a large synthesis document covering multi-agent systems, context dynamics, and cognitive orchestration. Despite its breadth (covering ConsensAgent, Free-MAD, Leiden algorithm, GraphRAG, Zep, prompt injection 2.0, LATS), it reads as an AI-generated literature review with citation markers but broken links.

### Provenance concern

This document is likely an AI-generated compilation. The quality of claims varies — some are well-sourced (e.g., Zep's DMR benchmark at 94.8%), others have dangling references. Skills that draw from this source may be inheriting claims of varying reliability.

### What it contributed

- memory-systems: Zep's temporal knowledge graph, DMR benchmark scores, tiered memory architecture ✓
- multi-agent-patterns: ConsensAgent, debate protocols ✓ (though these are among the most "academic" content in otherwise practical skills)
- context-degradation: Attention sink hypothesis, RULER findings ✓

### Left on the table (of uncertain value given provenance)

- **ConsensAgent weighted voting formula** — academic but potentially useful
- **Free-MAD** (anti-conformity mechanisms) — interesting alternative to forced consensus
- **Instruction hierarchy** patterns (system > user > tool) — security-relevant, not in any skill
- **Prompt injection 2.0** (indirect injection via RAG, polyglot attacks) — security topic absent from skills

---

## 7. `hncapsule.md` (92 lines) — Karpathy's HN Time Capsule

### What the source says

- Karpathy auto-graded decade-old HN discussions using GPT 5.1 Thinking API
- Vibe-coded with Opus 4.5 in ~3 hours
- 930 LLM queries, ~$58, ~1 hour runtime
- Pipeline: download frontpage → parse articles/comments → package prompt → submit to API → parse results → render HTML
- "Be good, future LLMs are watching"

### How project-development uses it

The skill correctly identifies it as a batch pipeline example with the acquire→prepare→process→parse→render pattern ✓

### Left on the table

- **Cost economics**: $58 for 930 queries (6.2¢ per query) — concrete cost reference for batch pipelines
- **Development time**: 3 hours with Opus 4.5 — evidence for "vibe coding" productivity
- **"Future LLMs are watching"** — philosophical point about information persistence
- **Model selection**: Using GPT 5.1 Thinking for analysis while vibe-coding with Opus 4.5 — practical multi-model approach

---

## 8. `netflix_context.md` (9 lines metadata + ~5000 word transcript) — Netflix Engineer Talk

### What the source says

A video transcript from a Netflix engineer at an AI summit:
- "I've shipped code I didn't quite understand" — universal confession
- Historical software crises: 1960s → present, each generation hits complexity wall
- Fred Brooks "No Silver Bullet" (1986): hard part is understanding the problem, not typing code
- **Simple vs Easy** (Rich Hickey, "Simple Made Easy" 2011):
  - Simple = one fold, no entanglement, about structure
  - Easy = adjacent, within reach, about proximity
  - "Every time we choose easy, we're choosing speed now. Complexity later."
  - "AI has destroyed that balance because it's the ultimate easy button"
- **Essential vs accidental complexity**:
  - Essential: fundamental difficulty of the actual problem
  - Accidental: everything else (workarounds, frameworks, abstractions)
  - AI treats every pattern in codebase the same — "technical debt doesn't register as debt"
- **Three-phase approach**: Research → Planning → Implementation
  - Research: feed everything, analyze codebase, iterate ("what about caching? how does this handle failures?"), human checkpoint to validate
  - Planning: detailed implementation plan, function signatures, type definitions — "paint by numbers" for junior engineer
  - Implementation: with clear spec, context stays clean; prevents the complexity spiral
- **Real Netflix example**: authorization refactor that AI couldn't handle — old auth code tightly coupled, permission checks woven through business logic
  - **Had to do first migration by hand** — no AI, just reading code and making changes
  - Fed that manual PR into the research process as seed
  - "We had to earn the understanding before we can code into our process"
- Background agents: can execute implementation because thinking was done upfront
- "The hard part was never typing the code. It was knowing what to type in the first place."
- "Pattern recognition comes from experience. When I spot a dangerous architecture, it's because I'm the one up at 3:00 in the morning dealing with it."

### How context-compression uses it

The skill integrates the three-phase approach (Research → Planning → Implementation) as a compression methodology. It correctly attributes the "5 million tokens became 2,000 words of specification" insight ✓

### Drift

The skill frames the Netflix material purely as a compression technique. In the original talk, it's more fundamentally about **understanding as a prerequisite for generation** — the compression is a byproduct of human synthesis, not the goal itself. The talk's thesis is closer to "don't outsource your thinking" than "here's how to compress context."

### Left on the table — high-value material

- **Simple vs Easy framework** — applicable across all skills. Every skill design choice is a simple-vs-easy tradeoff.
- **Essential vs accidental complexity** — AI can't distinguish them. This meta-insight about AI limitations should inform how skills advise using AI.
- **"Every pattern is a pattern"** — AI preserves technical debt as if it were architecture. Critical for tool-design and project-development.
- **"We had to earn the understanding"** — the manual migration as prerequisite for AI assistance. Not captured anywhere.
- **"Pattern recognition comes from experience"** — the argument that human judgment atrophies when you skip thinking.
- **"AI has destroyed the simple/easy balance"** — the acceleration of complexity accumulation.
- **Authorization refactor case study** — vivid example of where AI fails and why.

---

## Cross-Cutting Findings

### A. What the skills got right

1. **Core frameworks faithfully distilled**: The four-bucket model (Write/Select/Compress/Isolate), Factory Research compression scores, BrowseComp variance statistics, Vercel d0 reduction metrics — all accurately represented.

2. **Key principles correctly elevated**: "Tokens per task not per request," "sub-agents for isolation not roles," "if a human can't choose, an AI can't either" — these are correctly identified as the high-signal claims.

3. **Platform-agnostic stance maintained**: Skills successfully abstract away from specific vendors while preserving the underlying principles.

### B. Systematic drift patterns

1. **Caveats dropped**: The most consistent drift is that qualifications and prerequisites are lost in synthesis. Vercel's "this only worked because our data was well-structured," Manus's "we've rebuilt 5 times," the Netflix engineer's "we had to do it by hand first" — these reality checks are stripped when claims become principles.

2. **Secondary sources treated as primary**: `claude_research.md` and `gemini_research.md` are themselves synthesis documents (likely AI-generated). Skills citing their claims are in a citation chain of uncertain reliability. Specific numbers like "83.9% observations" lack traceable primary sourcing.

3. **Provenance laundering**: Claims from specific companies/teams become generalized principles without attribution to their context. What worked for Manus (millions of users, dedicated VMs) may not apply to smaller deployments.

### C. Valuable material left on the table

**Tier 1 — Should definitely be in skills:**

| Material | Source | Target Skill |
|----------|--------|-------------|
| todo.md as attention manipulation (recitation) | Peak Ji blog | context-degradation or context-optimization |
| Keep errors in context (implicit belief updates) | Peak Ji blog | context-degradation |
| Auto-few-shot trap (pattern mimicry from repetitive context) | Peak Ji blog | context-degradation |
| Fabrication threshold taxonomy (1-5 genuine, 6-8 degrading, 9+ fabrication) | Manus Wide Research | context-degradation |
| Scale effort heuristic (1 agent → 2-4 → 10+) | Anthropic multi-agent | multi-agent-patterns |
| JSON > Markdown for agent-tracked state | Anthropic long-running | filesystem-context |
| Initializer agent + coding agent pattern | Anthropic long-running | hosted-agents |
| "This only worked because data was well-structured" caveat | Vercel d0 | tool-design |
| Self-correction doesn't work without external feedback (MIT) | claude_research.md | evaluation |
| Workflow checklists and feedback loops | agentskills.md spec | evaluation, project-development |

**Tier 2 — Valuable but lower priority:**

| Material | Source | Why valuable |
|----------|--------|-------------|
| Simple vs Easy framework | Netflix talk | Meta-framework for all design decisions |
| Essential vs accidental complexity | Netflix talk | Why AI fails on legacy code |
| Bitter Lesson implications | Manus/Lance Martin | Future-proofing agent design |
| Dynamic few-shot selection (16% → 52%) | claude_research.md | Concrete technique |
| Prefix vs suffix namespacing effects | Anthropic tool blog | Non-obvious tool design detail |
| System prompt altitude (Goldilocks zone) | Anthropic context blog | Calibration framework |
| Rainbow deployments for agents | Anthropic multi-agent | Operations concern for hosted-agents |
| Context length pressure from training data | Manus Wide Research | Novel degradation mechanism |

### D. Format spec alignment gaps

The collection follows the Agent Skills spec structurally but misses several authoring best practices the spec itself recommends:
1. No workflow checklists (spec pattern 1)
2. No feedback loops (spec pattern 2)
3. Noun-phrase naming instead of preferred gerund form
4. No `allowed-tools` field (experimental but relevant)
5. Description fields vary in trigger-richness

### E. The telephone game irony

The collection warns about the "telephone game" in multi-agent communication but exhibits it in its own provenance chain: primary research → synthesis documents → skills → users. The intermediate synthesis documents (`claude_research.md`, `gemini_research.md`) add a lossy compression step that the skills don't acknowledge.

---

## Recommendations

1. **Add source attribution markers** to skills — even a brief `[Source: Manus blog]` inline would improve traceability.
2. **Restore dropped caveats** — create a "Prerequisites and limitations" section in relevant skills.
3. **Incorporate Tier 1 missing material** — especially Peak Ji's three actionable patterns (recitation, errors-in-context, anti-few-shot).
4. **Flag secondary sources** — `claude_research.md` and `gemini_research.md` should be identified as compilations, not primary research.
5. **Add workflow checklists** to procedural skills per the agentskills.md spec.
6. **Add counter-indications** — every skill should say when NOT to use its patterns (per the Manus Wide Research model).

---

*Generated: 2026-02-27*
*Source files examined: 8 (3,135 combined lines)*
*Skills cross-referenced: 13 (3,571 combined lines)*
