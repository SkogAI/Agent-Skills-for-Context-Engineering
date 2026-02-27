# Researcher Methodology Analysis

**Date**: 2026-02-27
**Scope**: `researcher/llm-as-a-judge.md` (362 lines), `researcher/example_output.md` (75 lines)
**Method**: Apply the collection's own evaluation + advanced-evaluation skills to the curation methodology itself.

---

## 1. Methodology Summary

The researcher pipeline is an LLM-as-a-Judge system for curating source content into skills. Two-phase evaluation:

1. **Gatekeeper Triage**: 4 binary gates (G1-G4), any failure = reject
2. **Dimensional Scoring**: 4 weighted dimensions (D1-D4), 3-point scale (0/1/2), max score 2.0

Decision thresholds: APPROVE >= 1.4, HUMAN_REVIEW 0.9-1.4, REJECT < 0.9. Four override rules handle edge cases.

Output is structured JSON with chain-of-thought reasoning, skill extraction, and human review notes.

---

## 2. Internal Contradiction in Gate Logic

**Critical finding**: The methodology contradicts itself on gate strictness.

- Line 28: "Apply 4 binary gates. **Failure more than 2** = immediate REJECT"
- Line 64: "Hard stops. Failure on **ANY** gate = immediate REJECT"
- Lines 73-77: Each individual gate failure triggers REJECT independently

The header (line 28) says you can fail 2 gates and still proceed. The body (line 64 and decision logic) says any single failure is fatal. These are mutually exclusive. An LLM judge receiving this prompt would have to resolve the contradiction itself, introducing inconsistency across evaluations depending on which instruction it weights higher.

**Verdict**: The body's "any gate = reject" is clearly the intended behavior based on the worked examples. Line 28 is a stale edit that was never cleaned up.

---

## 3. The 4 Gates — Are They Sound?

### Gate Design Quality

| Gate | What it tests | Well-defined? | Failure mode |
|------|--------------|---------------|-------------|
| G1: Mechanism Specificity | Does source define a specific pattern? | Good — clear PASS/FAIL examples | May reject high-level architectural insights that are valuable but not mechanism-specific |
| G2: Implementable Artifacts | Does source contain code/schemas/templates? | Good — concrete criteria | Biases toward written artifacts; rejects talks, oral presentations, design discussions |
| G3: Beyond Basics | Is it advanced? | **Weakest gate** — "advanced" is subjective | An LLM's idea of "basic" shifts with its training distribution; not stable across model versions |
| G4: Source Verifiability | Is author credible? | **Structurally biased** — see Section 4 | Rejects valid technical content from anonymous or independent contributors |

G3 is the weakest gate because "beyond basics" has no anchor point. What counts as "basic RAG" to Claude Opus 4.5 may be "advanced" to a less capable model. The gate provides examples ("post-retrieval processing, agent state management, tool interface design") but these are topics, not difficulty levels. A basic introduction to post-retrieval processing would pass G3 by topic alone.

G2 is biased toward textual artifacts. The example_output.md evaluation of the Netflix talk notes the speaker "lacks actual code snippets, prompt templates, or document schemas" and scores D1=1 partly for this reason. But the three-phase methodology described is arguably more valuable than any single code snippet. G2 forces the pipeline to undervalue architectural wisdom delivered verbally.

### Do Existing Skills Pass Their Own Gates?

Running the 13 skills through the gates *as if they were source content*:

**context-fundamentals** — would FAIL G3. It is explicitly foundational content covering "context anatomy," "attention mechanics," "progressive disclosure." These are the basics that G3 says to reject. The skill exists *because* it needs to exist as a foundation, but the methodology's gates would reject the source material that teaches it.

**context-degradation** — PASS all gates. Specific mechanisms (lost-in-middle, poisoning, distraction, clash, confusion), empirical data (RULER benchmark), counterintuitive findings.

**bdi-mental-states** — PASS all gates easily. Dense with RDF/Turtle schemas, SPARQL queries, Python code, Prolog rules. This is the most artifact-rich skill in the collection.

**memory-systems** — PASS all gates. Benchmark data, framework comparisons, code snippets. Strong on G2 and G3.

**context-compression** — PASS, but G3 is marginal. Summarization strategies are well-known; the skill's value is in collecting them, not in novelty.

**evaluation** — PASS. Meta-skill about building test frameworks. Code examples and rubric patterns.

**advanced-evaluation** — PASS easily. The most methodologically rigorous skill. Detailed prompt templates, bias mitigation protocols, decision trees.

**Summary**: At least 1 of 13 skills (context-fundamentals) is sourced from material that would fail the methodology's own gates. Several others (context-compression, context-optimization) are borderline on G3. The methodology has a blind spot for foundational content that is essential but not "advanced."

---

## 4. Reputation Bias Baked Into G4

The methodology's bias avoidance section says:
> "Do NOT overweight author reputation over empirical evidence"

But G4's PASS criteria explicitly names organizations:
> "peer-reviewed papers, production engineering blogs from **AI labs (Anthropic, Google, Vercel, etc.)**, recognized practitioners with public code contributions"

And G4's FAIL criteria says:
> "Anonymous source, unverifiable credentials, obvious marketing/vendor content"

This is reputation bias encoded as a structural gate. An anonymous blog post with working code, benchmarks, and novel insights would FAIL G4 regardless of technical quality. Meanwhile, a shallow Anthropic blog post passes G4 on name alone before any content evaluation.

The example evaluations reinforce this: Example A passes G4 with "Anthropic engineering blog - top-tier AI lab." Example B fails G4 with "Anonymous author, no credentials provided." The system is trained to treat provenance as a proxy for quality.

**The real irony**: The override rules (O3, O4) can force HUMAN_REVIEW for breakthrough content with weak evidence, but G4 will reject that content before it ever reaches scoring. A genuine breakthrough from an anonymous source never gets evaluated.

**Counterpoint**: G4 has a defensible rationale — in a curated collection, traceability matters. But the gate should be "source is identifiable and claims are verifiable" rather than "source has institutional backing." These are different standards.

---

## 5. Dimensional Scoring — Self-Evaluation

### Rubric Design Quality (by advanced-evaluation's own standards)

**What it gets right:**
- 3-point scale (0/1/2): The advanced-evaluation skill recommends "1-3 scales: Binary with neutral option, lowest cognitive load." Match.
- Chain-of-thought before scoring: The methodology requires "Provide reasoning BEFORE each score." The advanced-evaluation skill says this improves reliability by 15-25%. Match.
- Weighted dimensions with explicit calculation: Transparent and reproducible. Good.
- Override rules: Handles edge cases where total score is misleading. Smart design.
- Structured JSON output: Forces consistency. Good.

**What it gets wrong (by its own standards):**

1. **No position bias mitigation**: The advanced-evaluation skill says "Always swap positions in pairwise comparison — Single-pass comparison is corrupted by position bias." The methodology uses direct scoring only, never pairwise. When evaluating a batch of sources, evaluation order creates position bias — the first source establishes the judge's calibration anchor.

2. **Overloaded criteria in D1**: D1 is "Technical Depth **& Actionability**." The advanced-evaluation skill's anti-patterns section warns: "Criteria measuring multiple things are unreliable. One criterion = one measurable aspect." A deeply technical paper with no actionable guidance scores differently than a shallow-but-practical tutorial, yet both are measured on D1. These should be separate dimensions.

3. **No multi-judge setup**: The advanced-evaluation skill recommends "Panel of LLMs (PoLL): Use multiple models as judges, aggregate votes — Reduces individual model bias." The methodology uses a single LLM judge with no validation against human ratings.

4. **Confidence is categorical, not calibrated**: The output schema uses "high | medium | low" for confidence. The advanced-evaluation skill emphasizes numeric confidence calibrated to evidence strength. Categorical confidence loses information.

5. **No edge case guidance in rubric levels**: Each dimension has 3 levels (0/1/2) with descriptions, but no edge case guidance. The advanced-evaluation skill lists "Edge cases: Guidance for ambiguous situations" as a required rubric component. What score does content get that has excellent code but the code is in an obscure language? What about content with strong evidence from a non-CE domain?

### Weight Distribution

| Dimension | Weight | Assessment |
|-----------|--------|------------|
| D1: Technical Depth & Actionability | 35% | Appropriate as primary driver. Consistent with "implementable engineering primitives" mission. |
| D2: CE Relevance | 30% | Appropriate. Ensures domain focus. |
| D3: Evidence & Rigor | 20% | **Too low**. The collection includes model-specific benchmark tables (context-degradation) and framework comparison data (memory-systems) that are presented as authoritative. With only 20% weight on evidence, weakly-evidenced content can score high enough to APPROVE (e.g., D1=2, D2=2, D3=0, D4=2 = 1.7 — APPROVE despite zero evidence). |
| D4: Novelty & Insight | 15% | Reasonable floor. Override O4 (novelty=2 forces HUMAN_REVIEW) partially compensates. |

The override rules partially fix the evidence problem: O1 and O2 auto-reject on zero scores, but there's no O-rule for D3=0. Content with no evidence whatsoever can still be APPROVED if it scores 2 on the other three dimensions (weighted total = 1.7). This is a design gap.

---

## 6. The Example Output — Does It Follow the Rubric?

The `example_output.md` evaluates a Netflix engineering talk. Quality assessment:

**What it does well:**
- Detailed gate evidence with specific quotes from the source
- Reasoning precedes scores (chain-of-thought)
- Override O3 correctly triggered (D3=1 with total >= 1.4)
- Human review notes are actionable (5 specific recommendations)
- Skill extraction maps to CE taxonomy categories
- Honest about limitations: "lacks actual code snippets, prompt templates, or document schemas"

**What it reveals:**
- G2 passed despite the evaluator noting "no code snippets" — the judgment was that "methodology structure is specific enough to implement." This shows G2 is more flexible in practice than in definition. The gate says "Contains at least one of: code snippets, JSON/XML schemas, prompt templates with structure, architectural diagrams, API contracts, configuration examples." A methodology description is none of those listed artifact types, yet it passed.
- The evaluation is thorough (~75 lines) for a single source. At this depth, evaluating the sources for 13 skills would produce massive documentation. Yet the repository has only this one example. Either: (a) evaluations were done but not preserved, (b) evaluations were done more lightly than this example suggests, or (c) the methodology was retroactively created after skills were already written.

**The 1-evaluation problem**: A methodology that claims to curate content through rigorous evaluation but shows only 1 worked example across 13 skills raises questions about actual adoption. The `researcher/` directory contains 2 files. If the pipeline had been actively used, we'd expect a directory of evaluation outputs.

---

## 7. Meta-Evaluation: The Methodology Against Its Own Collection

### Applying the evaluation skill's standards

The evaluation skill says:
- "Multi-dimensional rubrics capture various quality aspects" — ✓ methodology has 4 dimensions
- "Evaluate outcomes, not specific execution paths" — ✗ the gates evaluate *characteristics* of source content, not outcomes (does the resulting skill actually help agents?)
- "Cover complexity levels from simple to complex" — ✗ no stratification by source type; a YouTube talk and an arXiv paper use the same rubric
- "Test with realistic context sizes" — N/A
- "Supplement LLM evaluation with human review" — ✓ HUMAN_REVIEW verdict exists, though the override structure is the only trigger

### Applying the advanced-evaluation skill's standards

The advanced-evaluation skill identifies these anti-patterns:
- "Scoring without justification" — ✓ methodology avoids this
- "Single-pass pairwise comparison" — ✗ methodology doesn't use pairwise at all; when choosing between competing source materials for the same skill topic, direct scoring alone can't reliably pick the better one
- "Overloaded criteria" — ✗ D1 measures two things (see Section 5)
- "Missing edge case guidance" — ✗ no edge cases in dimension descriptions
- "Ignoring confidence calibration" — ✗ categorical only

**Score**: If I apply the methodology's own scoring to itself as a piece of content:
- G1: PASS — defines specific evaluation mechanism
- G2: PASS — JSON schema, worked examples, scoring formulas
- G3: PASS — beyond basic evaluation concepts
- G4: PASS — identifiable repository and author
- D1 (Technical Depth): 2 — complete, implementable evaluation system
- D2 (CE Relevance): 1 — it's meta-evaluation, not directly CE
- D3 (Evidence): 1 — claims about rubric effectiveness are unvalidated; no data on inter-rater reliability, accuracy, or false positive/negative rates
- D4 (Novelty): 1 — competent synthesis of known evaluation patterns, not novel

Weighted total: (2×0.35) + (1×0.30) + (1×0.20) + (1×0.15) = 0.70 + 0.30 + 0.20 + 0.15 = **1.35**

**Decision: HUMAN_REVIEW** (below 1.4 threshold). The methodology doesn't pass its own bar for APPROVE.

---

## 8. What the Methodology Reveals About Collection Quality Control

### The Good

1. **The rubric is thoughtful**. Four dimensions with explicit weights, override rules for edge cases, structured output. This is better than most open-source project curation processes.
2. **Chain-of-thought is enforced**. Requiring reasoning before scores is the single highest-impact evaluation technique.
3. **The skill extraction step is valuable**. Connecting evaluation directly to "what skill can we build from this" keeps curation focused on the collection's mission.
4. **The Netflix example is honest**. It correctly triggers HUMAN_REVIEW despite a passing score, and the human review notes are specific and actionable.

### The Concerning

1. **Evidence of actual use is thin**. One worked example across 13 skills. The methodology may be aspirational rather than operational.
2. **The gates create structural blind spots**. Foundational content (context-fundamentals) and verbal/architectural wisdom (talks without code artifacts) get filtered out by gates that were designed for blog posts and papers.
3. **G4 encodes the reputation bias it claims to avoid**. The fix is simple: change G4 to test verifiability of claims rather than prestige of source.
4. **No D3=0 override**. Evidence-free content can score APPROVE. This is a gap.
5. **The methodology doesn't evaluate itself**. No inter-rater reliability data, no calibration against human curation decisions, no measurement of false positive/negative rates.

### The Missing

1. **No provenance chain from source → skill**. The methodology evaluates sources but doesn't track which sources fed which skills. Without this, there's no way to audit whether the methodology was actually applied.
2. **No batch evaluation protocol**. When evaluating multiple sources for the same topic, there's no guidance on comparative evaluation. Which Netflix talk about context compression is better? The methodology can only rate them independently.
3. **No versioning protocol**. Skills get updated (memory-systems is on v3.0.0). When new sources emerge, there's no re-evaluation trigger or update protocol.

---

## 9. Recommendations

1. **Fix the gate contradiction** (line 28 vs line 64). Decide on one behavior and make it unambiguous.
2. **Split D1** into Technical Depth and Actionability as separate dimensions, or rename to just "Actionability" since that's the core mission.
3. **Add D3=0 override** (O5: D3=0 → Force REJECT). Evidence-free content should never APPROVE.
4. **Rework G4** to test "claims are verifiable" rather than "source is prestigious." Keep "identifiable source" but drop the organizational name-dropping.
5. **Add a G3 exception** for foundational/reference content that is intentionally basic. The collection needs foundation skills; the methodology should accommodate them.
6. **Preserve evaluation outputs** alongside skills. Each skill directory could include a `provenance/` folder with the evaluation(s) that informed it.
7. **Implement batch comparison** using the advanced-evaluation skill's pairwise protocol when multiple sources compete for the same skill topic.
8. **Calibrate against human decisions**. Pick 20 source materials, have both the LLM and a human curator evaluate them, measure agreement. This is the methodology's own recommendation (from the evaluation skill).

---

## 10. Bottom Line

The researcher methodology is a competent first-generation curation system with genuine strengths (chain-of-thought requirement, override rules, structured output) and structural weaknesses (gate contradictions, encoded reputation bias, missing evidence override, overloaded D1). It scores **1.35** by its own rubric — HUMAN_REVIEW, not APPROVE.

The most telling finding: there's only one worked example in the repository. A methodology that isn't demonstrably used is a spec, not a process. The path forward is to either (a) retroactively evaluate all source material and preserve the outputs, proving the methodology works, or (b) acknowledge the methodology as aspirational and use it going forward with the fixes above.

The methodology's heart is in the right place — "Implementable Engineering Primitives" is the right mission, and the dimensional scoring captures the right qualities. But it needs the same rigor it demands of its inputs.
