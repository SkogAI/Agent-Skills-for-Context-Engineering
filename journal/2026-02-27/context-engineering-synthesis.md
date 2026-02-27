# Context Engineering — Personal Synthesis Reference

Dense lookup table distilled from 13 skills in the Agent Skills for Context Engineering collection. Not a tutorial. Collection's claims presented faithfully; conflicts with operating philosophy noted inline.

---

## 1. Principles

### The Subtractive Core

The only context that earns its tokens is the delta: `full_context_output - starved_context_output = delta`. Everything the model can infer is dead weight. Context engineering is deletion, not accumulation.

The collection agrees in spirit (progressive disclosure, just-in-time loading) but still defaults to additive framing — "load the right things" rather than "remove everything inferrable." The difference matters: additive asks "what should I include?", subtractive asks "what breaks if I remove this?"

### 25k Effective Limit

The collection's degradation thresholds (Claude Opus 4.5 onset at ~100K, severe at ~180K) describe theoretical capability, not working reality. For implementation-grade work — writing code, making decisions, tracking state — 25k tokens is the practical ceiling. The collection's 70-80% compaction trigger only makes sense if your denominator is ~30k (80% of 30k = 24k), not 200k.

The RULER data supports this indirectly: only 50% of models claiming 32K+ context actually maintain performance at 32K. Meaningful degradation begins at 8,000-16,000 tokens for many models. The advertised window is a marketing number.

### Context Distraction is Irreversible

You cannot tell an LLM to ignore what's in its context. "Don't think of a pink elephant." LLMs are additive by architecture — they cannot actively forget. The only mitigation is exclusion. The collection's context-degradation skill documents the mechanisms (poisoning, distraction, confusion) but understates the implication: a single distractor document causes step-function performance loss, not proportional. Prevention beats all forms of cure.

### Proximity Beats Position

The collection teaches lost-in-middle as a U-curve (beginning and end favored, middle suffers 10-40% recall loss) and attributes it to BOS attention sinks. The BOS explanation is post-hoc rationalization. Better operational model: the model attends in a sliding window of roughly +/-8k tokens from its current focus. "Keep related context together" is a more reliable rule than "put important things at the edges."

### Partitioning is Default, Not Nuclear Option

The collection frames context isolation (sub-agents with clean contexts) as the "most aggressive" strategy in its four-bucket model (Write, Select, Compress, Isolate). In practice, partitioning should be the default architecture, not the escalation path. Every task that can run in a separate context should. The cost is tokens (~15x baseline for multi-agent); the benefit is clean reasoning uncorrupted by irrelevant state.

### Tokens-per-Task, Not Tokens-per-Request

The compression skill gets this right: optimize total tokens to complete the task, not tokens per individual request. A 15x token multiplier from multi-agent is cheap if the task completes correctly on first attempt instead of requiring three retry cycles in a bloated single context.

---

## 2. Patterns

### L1/L2 Cache Architecture

Context window = L1 cache (hot, expensive, limited). Filesystem = L2 backing store (unlimited, cheap, higher latency). The collection's filesystem-context skill documents six patterns for this, but the unifying principle is: the context window holds pointers and working state; the filesystem holds everything else.

Scratch pad threshold: outputs above 2,000 tokens go to files. An 8,000-token web search result becomes ~100 tokens in context + file reference (80x active context reduction). The callable reference stays in context — that's the memory. Content is retrievable on demand.

### Three-Phase Workflow (Partitioning, Not Compression)

The collection presents this as a compression strategy. It's actually partitioning across time:

1. **Research phase**: architecture/docs in → single research document out
2. **Planning phase**: research document in → implementation spec out (5M token codebase → ~2,000 words of specification)
3. **Implementation phase**: execute against spec, not raw codebase

Each phase runs in a clean context. The previous phase's output is the only context the next phase inherits. This is the telephone game operating as designed.

### Telephone Game as Feature

The collection identifies "telephone game" as a problem — supervisor architectures initially performed 50% worse due to information loss across layers. Their fix: `forward_message` tool to bypass synthesis.

Alternative framing: the lossy compression between layers is a feature when you want strategic altitude. A sub-agent's 8,000-token analysis compressed to 200 tokens by the coordinator loses detail but gains abstraction. The coordinator doesn't need the detail — it needs the decision. The loss maintains the right level of zoom at each layer.

When it's a bug: when the coordinator needs to pass specific content to the user verbatim. Then `forward_message` is correct. The distinction is: synthesis layers should compress; passthrough layers should not.

### Dynamic Context Discovery

The collection's filesystem-context skill identifies this as the answer to "niche buried information" — agents that know how to find context rather than having it pre-loaded. Models are specifically trained for filesystem traversal (ls, glob, grep, read_file with ranges).

Key claim: filesystem search often outperforms semantic search for technical content. This aligns. Semantic search works for fuzzy "find me something about X"; filesystem search works for "find the function that handles Y" — and agent work is overwhelmingly the latter.

Limitation: requires frontier models. Less capable models don't recognize when they need more information.

### Architectural Reduction

The collection's strongest empirical pattern. Vercel d0: 17 specialized tools → 2 primitives (bash + SQL). Results: 80% → 100% success rate, 274s → 77s execution time. The file system agent pattern: standard Unix utilities replace custom exploration tools.

The underlying principle: tool descriptions are prompt engineering. Every tool in context shapes the model's behavior space. Fewer tools = cleaner reasoning = better outcomes. The collection recommends 10-20 tools as a guideline; the Vercel data suggests even that may be too many.

### Prompt-Native Endpoint

Goal state: zero explicit tool calls. Agent uses plain text intents like a human user. "When to use it" is 70% of tool design — if the activation trigger is well-specified, the model selects correctly. If no error messages need to exist, the tool surface is right-sized.

The collection's tool-design skill asks the right question: "Are your tools enabling new capabilities, or constraining reasoning the model could handle on its own?" The Bitter Lesson applies: structures added for current limitations become constraints as models improve. Build minimal architectures.

### Observation Masking

Replace verbose tool outputs with compact references once their immediate purpose is served. 60-80% reduction target. Decision rules from the collection:

- **Never mask**: current task critical, most recent turn, active reasoning
- **Consider masking**: 3+ turns ago, verbose but extractable, purpose-served
- **Always mask**: repeated outputs, boilerplate, already-summarized

Always keep a unique callable reference when masking. The reference is the memory.

### Memory System Progression

The collection's data on memory frameworks:

| Need | Solution | Evidence |
|---|---|---|
| Prototype / most agents | Filesystem (JSON + timestamps) | Letta filesystem: 74% LoCoMo |
| Multi-tenant / scale | Mem0 or vector store | Mem0: 68.5% LoCoMo |
| Temporal reasoning | Zep/Graphiti | 18.5% accuracy improvement, 90% latency reduction |
| Multi-hop reasoning | Cognee | Outperforms all on HotPotQA |
| Full agent self-management | Letta or Cognee | — |

The surprise: Letta's plain filesystem operations beat Mem0's specialized tools on LoCoMo (74% vs 68.5%). Tool complexity matters less than reliable retrieval. Most teams reach for frameworks too early.

Active forgetting via pruning is the core memory strategy. "Invalidate but don't discard" — git handles temporal queries.

---

## 3. Numbers

### Context & Degradation

| Metric | Value |
|---|---|
| Practical effective limit | ~25k tokens |
| Degradation onset (many models) | 8,000-16,000 tokens |
| Models passing RULER at claimed 32K+ | 50% |
| Lost-in-middle recall penalty | 10-40% |
| Tool outputs as % of context | 83.9% |
| Attention cost scaling | n² per n tokens |
| Single distractor impact | Step-function (not proportional) |

### Compression

| Metric | Value |
|---|---|
| Anchored iterative quality | 3.70/5.0 (best) |
| Artifact trail (all methods) | 2.2-2.5/5.0 (weakest dimension) |
| Structured vs opaque compression | 0.7% more tokens buys 0.35 quality points |
| 5M token codebase → spec | ~2,000 words |
| Compaction target | 50-70% reduction, <5% quality loss |
| Compaction trigger | 70-80% utilization (of effective limit) |

### Multi-Agent & Tools

| Metric | Value |
|---|---|
| Multi-agent token multiplier | ~15x baseline |
| BrowseComp variance explained | 95% by 3 factors |
| — Token usage | 80% of variance |
| — Tool call count | ~10% |
| — Model choice | ~5% |
| Supervisor telephone game loss | 50% worse initially |
| Model upgrade vs token doubling | Model upgrade wins |
| Vercel reduction | 17→2 tools, 80%→100%, 274s→77s |
| Tool description optimization | 40% task time reduction |

### Evaluation

| Metric | Value |
|---|---|
| CoT reliability gain (justification before score) | 15-25% |
| Rubric variance reduction | 40-60% |
| Likert scale recommendation | 1-5 (standard) |
| Position bias mitigation | Always swap, majority vote |

### Memory

| System | LoCoMo | Latency |
|---|---|---|
| Letta (filesystem) | 74.0% | — |
| Mem0 | 68.5% | — |
| Zep (temporal KG) | — | 2.58s (90% reduction) |

---

## 4. Disagreements

### "Primary reason for multi-agent is context isolation"

The collection's project-development skill states this directly. Context isolation is the primary *mechanism*, but the primary *reason* is that different subtasks need different cognitive modes. A research agent and an implementation agent aren't just isolated — they think differently. Role anthropomorphization is the point, not the antipattern. Context isolation is how you achieve it, not why.

The collection's own data partially undermines its claim: swarm architectures (where agents have distinct roles) slightly outperform supervisors. If isolation alone mattered, supervisor delegation would be equivalent. The role differentiation adds value beyond what isolation explains.

### Lost-in-Middle Explanation

The collection attributes it to BOS attention sinks and presents the U-curve as settled science. The attention-sink mechanism is a plausible post-hoc explanation, but the operational implication is different from what the collection suggests. "Put important things at beginning and end" (position-based) is less reliable than "keep related context in proximity" (locality-based). The +/-8k sliding attention model predicts real behavior better.

### Degradation Thresholds

The collection presents model-specific thresholds (Claude Opus 4.5: onset ~100K, severe ~180K). These are benchmark numbers, not implementation numbers. The gap between "can retrieve a needle from a haystack at 100K" and "can write correct code with 100K of mixed context" is enormous. The 25k practical limit reflects the latter, not the former.

### Tool Reduction as Universal Solution

The collection presents Vercel's 17→2 reduction as a general pattern. The collection itself notes the caveat (reduction works when data is well-documented; fails when data is messy or safety constraints apply) but buries it. In practice, many domains have messy data and real safety constraints. The principle (fewer tools = cleaner reasoning) is sound; the specific extreme (2 tools) is domain-contingent.

### Compression Artifact Trail

The collection reports artifact trail integrity at 2.2-2.5/5.0 across all methods — the weakest dimension — but doesn't flag the architectural implication: any compression strategy that doesn't explicitly persist file paths, branch names, and artifact references will silently lose them. This isn't a quality tradeoff, it's a structural gap that needs explicit mitigation (dedicated artifact tracking sections in summaries).

---

## 5. Gaps

### Cost Modeling for Context Strategies

The collection provides the formula `items × tokens_per_item × price_per_token + 20-30% buffer` for pipelines but has no cost model for the architectural decisions it recommends. Multi-agent at 15x baseline — when is that cheaper than debugging a bloated single-agent? At what task failure rate does the 15x multiplier pay for itself? No framework for this.

### Degradation Detection at Runtime

The collection documents degradation patterns extensively but provides no runtime detection strategy. How does an agent know it's in a degraded state? The compression skill mentions probe-based evaluation (recall, artifact, continuation, decision probes) but only as post-hoc evaluation, not as inline health checks.

### Context Window Composition

The collection says tool outputs consume 83.9% of context in typical trajectories, but provides no breakdown of optimal allocation. How much should go to system prompt? Tool definitions? Message history? Working state? The allocation strategy is left to intuition.

### Incremental Context Management

The collection's compression strategies are batch operations (trigger at threshold, compress everything). No coverage of incremental strategies — managing context token-by-token as it grows, rather than in crisis-triggered compressions. The sliding window strategy is mentioned but not developed.

### Evaluation of Context Engineering Itself

The evaluation skills cover evaluating agent outputs and behaviors, but not evaluating context engineering decisions. How do you measure whether a context optimization actually improved downstream task quality? The 95% BrowseComp finding (tokens explain 80% of variance) is the closest the collection gets, but it applies to exploration tasks. For execution tasks, the collection claims decision quality matters more — and provides no evaluation framework for that.

### Cross-Session State Management

The memory-systems skill covers frameworks for persistent memory, but the gap between "filesystem as RAM" (within a session) and "persistent knowledge graph" (across sessions) is underexplored. What's the minimal viable cross-session state? When does a `.md` file with timestamps stop being enough?

### Model-Specific Context Strategies

The degradation skill provides per-model thresholds, but no model-specific optimization strategies. If Claude handles 100K before degradation onset and GPT degrades at 64K, the context strategy should differ — but the collection treats all models identically in its recommendations.

---

*Synthesized from 13 skills across 5 plugin bundles. Collection maintains additive framing; this reference applies subtractive lens. Both perspectives preserved intentionally.*
