"""
Context-aware agent harness implementing filesystem-context patterns.

Patterns implemented (from the skill collection):
- Scratch pad: tool outputs > threshold offloaded to files
- Plan persistence: plans written to filesystem, re-read each turn
- Dynamic skill loading: skills loaded by keyword match on frontmatter
- Context budget: token tracking with compaction trigger
- Observation masking: large outputs replaced with summaries + file refs
- Sub-agent workspace isolation: each agent gets its own directory

Design follows:
- Architectural reduction (tool-design): 3 tools, not 17
- Filesystem as state machine (project-development): file existence = state
- 25k effective budget (context-optimization): anything beyond is unreliable
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import anthropic


# --- Workspace ---

class Workspace:
    """Filesystem workspace for agent state management.

    Layout:
        workspace/
            scratch/        # Tool output offloading
            plans/          # Persistent plans
            memory/         # Cross-session learnings
            agents/{name}/  # Sub-agent isolation
    """

    _counter = 0

    def __init__(self, root: Path):
        self.root = Path(root)
        for d in ("scratch", "plans", "memory"):
            (self.root / d).mkdir(parents=True, exist_ok=True)

    def scratch_path(self, label: str) -> Path:
        Workspace._counter += 1
        ts = int(time.time() * 1000)
        name = re.sub(r"[^a-z0-9_-]", "_", label.lower())
        return self.root / "scratch" / f"{name}_{ts}_{Workspace._counter}.txt"

    def plan_path(self) -> Path:
        return self.root / "plans" / "current.md"

    def agent_workspace(self, agent_name: str) -> "Workspace":
        agent_dir = self.root / "agents" / agent_name
        return Workspace(agent_dir)

    def read_plan(self) -> str | None:
        p = self.plan_path()
        return p.read_text() if p.exists() else None

    def write_plan(self, content: str) -> Path:
        p = self.plan_path()
        p.write_text(content)
        return p


# --- Skill Loader ---

class SkillLoader:
    """Dynamic skill loading from the collection.

    At init: scans frontmatter for name + description (cheap).
    On demand: loads full SKILL.md content (expensive, only when needed).

    This implements the progressive disclosure pattern:
    startup = names/descriptions only, activation = full content.
    """

    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
        self.index: list[dict[str, str]] = []
        self._build_index()

    def _build_index(self):
        for skill_md in sorted(self.skills_dir.glob("*/SKILL.md")):
            meta = self._parse_frontmatter(skill_md)
            if meta:
                meta["path"] = str(skill_md)
                meta["dir_name"] = skill_md.parent.name
                self.index.append(meta)

    @staticmethod
    def _parse_frontmatter(path: Path) -> dict[str, str] | None:
        text = path.read_text()
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not match:
            return None
        result = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                result[key.strip()] = val.strip()
        return result

    def catalog(self) -> str:
        """Return compact skill catalog for static context."""
        lines = ["Available skills (load when relevant):"]
        for s in self.index:
            lines.append(f"- {s['dir_name']}: {s.get('description', 'No description')}")
        return "\n".join(lines)

    def match(self, query: str, top_n: int = 3) -> list[dict[str, str]]:
        """Keyword match against skill descriptions. Simple but sufficient."""
        query_words = set(query.lower().split())
        scored = []
        for s in self.index:
            desc_words = set(s.get("description", "").lower().split())
            overlap = len(query_words & desc_words)
            if overlap > 0:
                scored.append((overlap, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:top_n]]

    def load(self, dir_name: str) -> str | None:
        """Load full skill content. The expensive operation."""
        path = self.skills_dir / dir_name / "SKILL.md"
        if path.exists():
            return path.read_text()
        return None


# --- Context Budget ---

class ContextBudget:
    """Token budget tracker with compaction trigger.

    Default budget: 25k tokens (the effective reliable limit,
    regardless of model's advertised window).

    Compaction triggers at 80% utilization.
    """

    def __init__(self, budget: int = 25_000):
        self.budget = budget
        self.current = 0
        self.history: list[dict[str, int]] = []

    def estimate_tokens(self, text: str) -> int:
        """Rough estimate: 1 token ~= 4 chars for English."""
        return len(text) // 4

    def track(self, role: str, content: str) -> int:
        tokens = self.estimate_tokens(content)
        self.current += tokens
        self.history.append({"role": role, "tokens": tokens, "total": self.current})
        return tokens

    @property
    def utilization(self) -> float:
        return self.current / self.budget if self.budget > 0 else 0.0

    @property
    def needs_compaction(self) -> bool:
        return self.utilization > 0.8

    @property
    def remaining(self) -> int:
        return max(0, self.budget - self.current)

    def reset(self, new_baseline: int = 0):
        self.current = new_baseline
        self.history.clear()


# --- Tool Handling ---

# Three tools. Following architectural reduction: if the model can
# compose these primitives to do anything, more tools just add noise.

TOOLS = [
    {
        "name": "read_file",
        "description": (
            "Read a file's contents. Use when you need to examine a file. "
            "Supports optional line range to read specific sections without "
            "loading the entire file. Returns the file content as text."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or workspace-relative file path",
                },
                "start_line": {
                    "type": "integer",
                    "description": "First line to read (1-indexed). Omit for full file.",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Last line to read (inclusive). Omit for full file.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write content to a file in the workspace. Creates parent "
            "directories if needed. Use for saving plans, notes, analysis "
            "results, or any persistent output."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Workspace-relative file path to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "search_files",
        "description": (
            "Search for a pattern across files. Returns matching lines with "
            "file paths and line numbers. Use for finding specific content, "
            "understanding code structure, or locating relevant files. "
            "Searches workspace by default; set path to search elsewhere."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for",
                },
                "path": {
                    "type": "string",
                    "description": "Directory to search. Defaults to workspace root.",
                },
                "glob": {
                    "type": "string",
                    "description": "File glob filter, e.g. '*.md' or '**/*.py'",
                },
            },
            "required": ["pattern"],
        },
    },
]


def execute_tool(
    name: str,
    inputs: dict[str, Any],
    workspace: Workspace,
    allowed_paths: list[Path] | None = None,
) -> str:
    """Execute a tool call and return the result string.

    Resolves paths relative to workspace root.
    Enforces path restrictions if allowed_paths is set.
    """
    if name == "read_file":
        path = _resolve_path(inputs["path"], workspace.root, allowed_paths)
        if not path.exists():
            return f"Error: File not found: {path}"
        text = path.read_text()
        start = inputs.get("start_line")
        end = inputs.get("end_line")
        if start or end:
            lines = text.splitlines()
            s = (start or 1) - 1
            e = end or len(lines)
            text = "\n".join(lines[s:e])
        return text

    elif name == "write_file":
        rel = inputs["path"]
        path = workspace.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(inputs["content"])
        return f"Written {len(inputs['content'])} chars to {rel}"

    elif name == "search_files":
        import subprocess

        search_path = inputs.get("path", str(workspace.root))
        search_path = str(_resolve_path(search_path, workspace.root, allowed_paths))
        cmd = ["grep", "-rn", inputs["pattern"], search_path]
        if inputs.get("glob"):
            cmd.extend(["--include", inputs["glob"]])
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            return result.stdout or "(no matches)"
        except subprocess.TimeoutExpired:
            return "Error: Search timed out after 10s"

    return f"Error: Unknown tool: {name}"


def _resolve_path(
    raw: str, workspace_root: Path, allowed: list[Path] | None
) -> Path:
    """Resolve a path, making it absolute if relative."""
    p = Path(raw)
    if not p.is_absolute():
        p = workspace_root / p
    p = p.resolve()
    if allowed:
        if not any(p == a or a in p.parents for a in allowed):
            raise PermissionError(f"Path {p} not in allowed paths")
    return p


# --- Observation Masking ---

SCRATCH_THRESHOLD = 2000  # chars; from filesystem-context skill guidance


def mask_observation(
    tool_name: str, output: str, workspace: Workspace
) -> str:
    """Scratch pad pattern: offload large tool outputs to files.

    Returns the output directly if under threshold.
    Otherwise writes to scratch/ and returns a summary + file reference.
    """
    if len(output) <= SCRATCH_THRESHOLD:
        return output

    path = workspace.scratch_path(tool_name)
    path.write_text(output)

    # Simple summary: first 300 chars + line count
    line_count = output.count("\n") + 1
    preview = output[:300].rstrip()
    return (
        f"[Output ({len(output)} chars, {line_count} lines) saved to "
        f"{path.relative_to(workspace.root)}]\n"
        f"Preview: {preview}...\n"
        f"Use read_file to examine specific sections."
    )


# --- Compaction ---

def compact_messages(
    messages: list[dict], workspace: Workspace, client: anthropic.Anthropic
) -> list[dict]:
    """Compaction: summarize conversation history when budget is hit.

    Saves full history to scratch/, then asks the model to produce
    a high-fidelity summary. Returns a new message list with the summary
    as a single user message.

    This is the most aggressive context optimization — loses detail
    but preserves the ability to continue the task.
    """
    # Save full history for recovery
    history_path = workspace.scratch_path("compacted_history")
    history_text = "\n\n".join(
        f"[{m['role']}]: {_extract_text(m)}" for m in messages
    )
    history_path.write_text(history_text)

    # Ask model for summary
    summary_prompt = (
        "Summarize this conversation history. Preserve:\n"
        "- Key decisions made\n"
        "- Current plan and progress\n"
        "- Important findings\n"
        "- What remains to be done\n"
        "Be concise but complete. This summary replaces the full history.\n\n"
        f"{history_text[:8000]}"  # Limit input to summary call
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": summary_prompt}],
    )
    summary = response.content[0].text

    return [
        {
            "role": "user",
            "content": (
                f"[Context compacted. Full history in {history_path.name}]\n\n"
                f"Summary of work so far:\n{summary}\n\n"
                "Continue from where we left off."
            ),
        }
    ]


def _extract_text(message: dict) -> str:
    """Pull text from a message, handling both string and block formats."""
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block["text"])
            elif hasattr(block, "text"):
                parts.append(block.text)
        return " ".join(parts)
    return str(content)


# --- The Harness ---

class ContextHarness:
    """Agent harness with filesystem-backed context management.

    Usage:
        harness = ContextHarness(
            workspace_path="./workspace",
            skills_path="../skills",
        )
        result = harness.run("Analyze the quality of each skill document")
    """

    def __init__(
        self,
        workspace_path: str | Path,
        skills_path: str | Path | None = None,
        budget: int = 25_000,
        model: str = "claude-sonnet-4-20250514",
        max_turns: int = 20,
        allowed_paths: list[str | Path] | None = None,
    ):
        self.workspace = Workspace(Path(workspace_path))
        self.skills = SkillLoader(Path(skills_path)) if skills_path else None
        self.budget = ContextBudget(budget)
        self.model = model
        self.max_turns = max_turns
        self.client = anthropic.Anthropic()
        self.messages: list[dict] = []
        self.allowed_paths = (
            [Path(p).resolve() for p in allowed_paths] if allowed_paths else None
        )

        # Trace log for stress-testing analysis
        self.trace: list[dict] = []

    def run(self, task: str) -> str:
        """Run an agent task with full context management.

        Returns the final assistant response text.
        """
        system_prompt = self._build_system_prompt(task)
        self.budget.track("system", system_prompt)

        # Initial user message with task + plan (if exists)
        user_msg = task
        existing_plan = self.workspace.read_plan()
        if existing_plan:
            user_msg += f"\n\n[Existing plan loaded from filesystem:]\n{existing_plan}"
        self.messages.append({"role": "user", "content": user_msg})
        self.budget.track("user", user_msg)

        self._log("init", task=task, budget=self.budget.current, skills_loaded=bool(self.skills))

        for turn in range(self.max_turns):
            # Check budget before each turn
            if self.budget.needs_compaction:
                self._log("compaction_triggered", utilization=self.budget.utilization)
                self.messages = compact_messages(
                    self.messages, self.workspace, self.client
                )
                self.budget.reset(self.budget.estimate_tokens(
                    self.messages[0]["content"]
                ))

            # Call the model
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=TOOLS,
                messages=self.messages,
            )
            self.budget.track("assistant", str(response.content))

            # Process response
            assistant_msg = {"role": "assistant", "content": response.content}
            self.messages.append(assistant_msg)

            # Check for end turn (no tool use)
            if response.stop_reason == "end_turn":
                final_text = _extract_text(assistant_msg)
                self._log("complete", turns=turn + 1, final_budget=self.budget.current)
                return final_text

            # Handle tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    self._log("tool_call", tool=block.name, inputs=block.input)

                    raw_output = execute_tool(
                        block.name, block.input, self.workspace, self.allowed_paths
                    )
                    masked_output = mask_observation(
                        block.name, raw_output, self.workspace
                    )
                    self.budget.track("tool_result", masked_output)

                    self._log(
                        "tool_result",
                        tool=block.name,
                        raw_len=len(raw_output),
                        masked_len=len(masked_output),
                        was_offloaded=len(raw_output) > SCRATCH_THRESHOLD,
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": masked_output,
                    })

            if tool_results:
                self.messages.append({"role": "user", "content": tool_results})

        # Max turns reached
        self._log("max_turns", turns=self.max_turns)
        return "[Max turns reached]"

    def _build_system_prompt(self, task: str) -> str:
        """Build system prompt with dynamic skill loading."""
        parts = [
            "You are a context-aware agent. Your workspace is a filesystem.",
            "Write plans to plans/current.md. Write analysis to scratch/.",
            "Be thorough but concise. Prefer reading specific file sections over full files.",
            "",
        ]

        # Dynamic skill loading: match skills to task, load top matches
        if self.skills:
            parts.append(self.skills.catalog())
            parts.append("")

            matched = self.skills.match(task, top_n=2)
            for skill_meta in matched:
                content = self.skills.load(skill_meta["dir_name"])
                if content:
                    # Only load first 200 lines (skill guidance: keep under 500)
                    lines = content.splitlines()[:200]
                    parts.append(f"## Loaded Skill: {skill_meta['dir_name']}")
                    parts.append("\n".join(lines))
                    parts.append("")
                    self._log(
                        "skill_loaded",
                        skill=skill_meta["dir_name"],
                        lines=len(lines),
                        tokens=self.budget.estimate_tokens("\n".join(lines)),
                    )

        # Budget awareness in prompt
        parts.append(
            f"\nContext budget: {self.budget.remaining} tokens remaining. "
            f"Be efficient with tool calls."
        )

        return "\n".join(parts)

    def _log(self, event: str, **data):
        entry = {"event": event, "time": time.time(), **data}
        self.trace.append(entry)

    def save_trace(self, path: str | Path | None = None) -> Path:
        """Save execution trace for analysis."""
        if path is None:
            path = self.workspace.root / "trace.json"
        else:
            path = Path(path)
        path.write_text(json.dumps(self.trace, indent=2, default=str))
        return path
