"""
Demo: Use the context-aware harness to analyze the skill collection.

This exercises multiple patterns simultaneously:
- Dynamic skill loading (skills matched to the analysis task)
- Scratch pad (skill files are large → offloaded)
- Plan persistence (multi-step analysis → plan written to filesystem)
- Context budget (13 skills × ~300 lines each would blow the budget)
- Observation masking (read_file outputs masked when large)

Usage:
    cd examples/context-harness
    export ANTHROPIC_API_KEY=sk-...
    python run.py

    # Or with custom settings:
    python run.py --budget 20000 --model claude-haiku-4-5-20251001 --turns 10
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harness import ContextHarness


def main():
    parser = argparse.ArgumentParser(description="Context harness demo")
    parser.add_argument(
        "--budget", type=int, default=25_000,
        help="Context budget in tokens (default: 25000)",
    )
    parser.add_argument(
        "--model", type=str, default="claude-sonnet-4-20250514",
        help="Model to use",
    )
    parser.add_argument(
        "--turns", type=int, default=15,
        help="Max agent turns (default: 15)",
    )
    parser.add_argument(
        "--task", type=str, default=None,
        help="Custom task (default: skill collection analysis)",
    )
    parser.add_argument(
        "--workspace", type=str, default="./workspace",
        help="Workspace directory (default: ./workspace)",
    )
    args = parser.parse_args()

    # Paths
    here = Path(__file__).parent.resolve()
    repo_root = here.parent.parent
    skills_dir = repo_root / "skills"
    workspace = Path(args.workspace).resolve()

    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}", file=sys.stderr)
        sys.exit(1)

    # Default task: analyze the skill collection
    task = args.task or (
        "Analyze the skill collection in the skills/ directory. For each skill:\n"
        "1. Read the SKILL.md file\n"
        "2. Evaluate: Is the content actionable? Does it provide concrete guidance?\n"
        "3. Rate quality on a 1-5 scale\n"
        "4. Note any gaps or missing guidance\n\n"
        "Write your analysis plan to plans/current.md first.\n"
        "Write final results to scratch/skill_analysis.md.\n"
        "Be efficient — don't read entire files if a section sample suffices."
    )

    print(f"Workspace: {workspace}")
    print(f"Skills:    {skills_dir}")
    print(f"Budget:    {args.budget} tokens")
    print(f"Model:     {args.model}")
    print(f"Max turns: {args.turns}")
    print(f"Task:      {task[:80]}...")
    print("-" * 60)

    # Build and run
    harness = ContextHarness(
        workspace_path=workspace,
        skills_path=skills_dir,
        budget=args.budget,
        model=args.model,
        max_turns=args.turns,
        allowed_paths=[skills_dir, workspace],
    )

    result = harness.run(task)

    # Save trace
    trace_path = harness.save_trace()
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(result[:2000])
    if len(result) > 2000:
        print(f"\n... ({len(result)} chars total)")

    # Print trace summary
    print("\n" + "=" * 60)
    print("TRACE SUMMARY:")
    print("=" * 60)
    tool_calls = [e for e in harness.trace if e["event"] == "tool_call"]
    offloads = [e for e in harness.trace if e.get("was_offloaded")]
    skills_loaded = [e for e in harness.trace if e["event"] == "skill_loaded"]
    compactions = [e for e in harness.trace if e["event"] == "compaction_triggered"]

    print(f"Tool calls:     {len(tool_calls)}")
    print(f"Offloaded:      {len(offloads)} observations masked to scratch/")
    print(f"Skills loaded:  {len(skills_loaded)}")
    print(f"Compactions:    {len(compactions)}")
    print(f"Final budget:   {harness.budget.current}/{harness.budget.budget} tokens")
    print(f"Utilization:    {harness.budget.utilization:.0%}")
    print(f"Trace saved:    {trace_path}")

    # Tool call breakdown
    if tool_calls:
        print("\nTool usage breakdown:")
        counts: dict[str, int] = {}
        for tc in tool_calls:
            counts[tc["tool"]] = counts.get(tc["tool"], 0) + 1
        for tool, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  {tool}: {count}")


if __name__ == "__main__":
    main()
