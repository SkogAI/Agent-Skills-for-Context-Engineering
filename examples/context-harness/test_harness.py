"""
Tests for the context harness — validates all filesystem-context patterns
without requiring API calls.

Tests exercise:
- Workspace creation and file layout
- Skill indexing and dynamic loading
- Keyword-based skill matching
- Context budget tracking and compaction triggers
- Observation masking (scratch pad pattern)
- Tool execution (read, write, search)
- Plan persistence
- Path resolution and safety
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from harness import (
    ContextBudget,
    SkillLoader,
    Workspace,
    execute_tool,
    mask_observation,
    SCRATCH_THRESHOLD,
    TOOLS,
)


@pytest.fixture
def tmp_workspace(tmp_path):
    return Workspace(tmp_path / "ws")


@pytest.fixture
def skills_dir():
    """Points to the real skills directory in the repo."""
    here = Path(__file__).parent.resolve()
    return here.parent.parent / "skills"


# --- Workspace Tests ---


class TestWorkspace:
    def test_creates_directory_structure(self, tmp_workspace):
        assert (tmp_workspace.root / "scratch").is_dir()
        assert (tmp_workspace.root / "plans").is_dir()
        assert (tmp_workspace.root / "memory").is_dir()

    def test_scratch_path_unique(self, tmp_workspace):
        p1 = tmp_workspace.scratch_path("test")
        p2 = tmp_workspace.scratch_path("test")
        # Paths should differ (timestamp-based)
        assert p1 != p2

    def test_scratch_path_sanitizes_name(self, tmp_workspace):
        p = tmp_workspace.scratch_path("My Tool/Output!")
        assert "my_tool_output_" in p.name

    def test_plan_persistence(self, tmp_workspace):
        assert tmp_workspace.read_plan() is None  # No plan yet

        tmp_workspace.write_plan("## Step 1\nDo the thing")
        plan = tmp_workspace.read_plan()
        assert "Step 1" in plan
        assert "Do the thing" in plan

    def test_plan_overwrite(self, tmp_workspace):
        tmp_workspace.write_plan("v1")
        tmp_workspace.write_plan("v2")
        assert tmp_workspace.read_plan() == "v2"

    def test_agent_workspace_isolation(self, tmp_workspace):
        agent_ws = tmp_workspace.agent_workspace("researcher")
        assert agent_ws.root == tmp_workspace.root / "agents" / "researcher"
        assert (agent_ws.root / "scratch").is_dir()

        # Write in agent workspace doesn't affect parent
        agent_ws.write_plan("agent plan")
        assert tmp_workspace.read_plan() is None
        assert agent_ws.read_plan() == "agent plan"


# --- Skill Loader Tests ---


class TestSkillLoader:
    def test_indexes_all_skills(self, skills_dir):
        loader = SkillLoader(skills_dir)
        assert len(loader.index) == 13

    def test_index_has_required_fields(self, skills_dir):
        loader = SkillLoader(skills_dir)
        for skill in loader.index:
            assert "name" in skill, f"Skill missing name: {skill}"
            assert "description" in skill, f"Skill missing description: {skill}"
            assert "dir_name" in skill
            assert "path" in skill

    def test_catalog_output(self, skills_dir):
        loader = SkillLoader(skills_dir)
        catalog = loader.catalog()
        assert "Available skills" in catalog
        assert "filesystem-context" in catalog
        assert "tool-design" in catalog

    def test_keyword_matching(self, skills_dir):
        loader = SkillLoader(skills_dir)

        # "optimize context" should match context-optimization
        matches = loader.match("optimize context reduce token costs")
        names = [m["dir_name"] for m in matches]
        assert "context-optimization" in names

        # "design tools" should match tool-design
        matches = loader.match("design agent tools create tool descriptions")
        names = [m["dir_name"] for m in matches]
        assert "tool-design" in names

    def test_match_returns_top_n(self, skills_dir):
        loader = SkillLoader(skills_dir)
        matches = loader.match("context optimization compression", top_n=2)
        assert len(matches) <= 2

    def test_no_match_returns_empty(self, skills_dir):
        loader = SkillLoader(skills_dir)
        matches = loader.match("xyzzy plugh nothing_matches_this")
        assert len(matches) == 0

    def test_load_full_skill(self, skills_dir):
        loader = SkillLoader(skills_dir)
        content = loader.load("filesystem-context")
        assert content is not None
        assert "Filesystem-Based Context Engineering" in content

    def test_load_nonexistent_returns_none(self, skills_dir):
        loader = SkillLoader(skills_dir)
        assert loader.load("nonexistent-skill") is None


# --- Context Budget Tests ---


class TestContextBudget:
    def test_initial_state(self):
        budget = ContextBudget(25000)
        assert budget.current == 0
        assert budget.utilization == 0.0
        assert not budget.needs_compaction
        assert budget.remaining == 25000

    def test_tracking(self):
        budget = ContextBudget(25000)
        tokens = budget.track("user", "Hello world")  # ~3 tokens
        assert tokens > 0
        assert budget.current == tokens

    def test_compaction_trigger(self):
        budget = ContextBudget(1000)
        # Push past 80% (800 tokens = 3200 chars)
        budget.track("user", "x" * 3600)
        assert budget.needs_compaction

    def test_no_compaction_under_threshold(self):
        budget = ContextBudget(1000)
        budget.track("user", "x" * 2000)  # 500 tokens = 50%
        assert not budget.needs_compaction

    def test_reset(self):
        budget = ContextBudget(25000)
        budget.track("user", "x" * 40000)
        budget.reset(100)
        assert budget.current == 100
        assert len(budget.history) == 0

    def test_remaining_calculation(self):
        budget = ContextBudget(1000)
        budget.track("user", "x" * 2000)  # 500 tokens
        assert budget.remaining == 500

    def test_remaining_never_negative(self):
        budget = ContextBudget(100)
        budget.track("user", "x" * 10000)  # Way over budget
        assert budget.remaining == 0


# --- Observation Masking Tests ---


class TestObservationMasking:
    def test_small_output_returned_directly(self, tmp_workspace):
        result = mask_observation("test", "small output", tmp_workspace)
        assert result == "small output"

    def test_large_output_offloaded(self, tmp_workspace):
        large = "x" * (SCRATCH_THRESHOLD + 100)
        result = mask_observation("big_tool", large, tmp_workspace)
        assert "[Output" in result
        assert "saved to scratch/" in result
        assert "read_file" in result

    def test_offloaded_file_exists(self, tmp_workspace):
        large = "line\n" * 1000
        mask_observation("test_tool", large, tmp_workspace)
        scratch_files = list((tmp_workspace.root / "scratch").glob("test_tool_*"))
        assert len(scratch_files) == 1
        assert scratch_files[0].read_text() == large

    def test_threshold_boundary(self, tmp_workspace):
        exact = "x" * SCRATCH_THRESHOLD
        result = mask_observation("test", exact, tmp_workspace)
        assert result == exact  # Exactly at threshold → not offloaded

        over = "x" * (SCRATCH_THRESHOLD + 1)
        result = mask_observation("test", over, tmp_workspace)
        assert "[Output" in result  # Over threshold → offloaded


# --- Tool Execution Tests ---


class TestToolExecution:
    def test_read_file(self, tmp_workspace):
        # Write a test file
        test_file = tmp_workspace.root / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")

        result = execute_tool("read_file", {"path": str(test_file)}, tmp_workspace)
        assert "line1" in result
        assert "line5" in result

    def test_read_file_with_range(self, tmp_workspace):
        test_file = tmp_workspace.root / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")

        result = execute_tool(
            "read_file",
            {"path": str(test_file), "start_line": 2, "end_line": 3},
            tmp_workspace,
        )
        assert "line2" in result
        assert "line3" in result
        assert "line1" not in result
        assert "line5" not in result

    def test_read_file_not_found(self, tmp_workspace):
        result = execute_tool(
            "read_file", {"path": "/nonexistent/file.txt"}, tmp_workspace
        )
        assert "Error" in result

    def test_read_file_relative_path(self, tmp_workspace):
        test_file = tmp_workspace.root / "data" / "test.txt"
        test_file.parent.mkdir()
        test_file.write_text("relative content")

        result = execute_tool(
            "read_file", {"path": "data/test.txt"}, tmp_workspace
        )
        assert "relative content" in result

    def test_write_file(self, tmp_workspace):
        result = execute_tool(
            "write_file",
            {"path": "output/result.md", "content": "# Analysis\nDone."},
            tmp_workspace,
        )
        assert "Written" in result
        written = (tmp_workspace.root / "output" / "result.md").read_text()
        assert "# Analysis" in written

    def test_write_file_creates_parents(self, tmp_workspace):
        execute_tool(
            "write_file",
            {"path": "deep/nested/dir/file.txt", "content": "hello"},
            tmp_workspace,
        )
        assert (tmp_workspace.root / "deep" / "nested" / "dir" / "file.txt").exists()

    def test_search_files(self, tmp_workspace):
        (tmp_workspace.root / "a.txt").write_text("hello world\nfoo bar")
        (tmp_workspace.root / "b.txt").write_text("goodbye world\nbaz")

        result = execute_tool(
            "search_files", {"pattern": "world"}, tmp_workspace
        )
        assert "hello world" in result
        assert "goodbye world" in result

    def test_search_with_glob(self, tmp_workspace):
        (tmp_workspace.root / "code.py").write_text("def main(): pass")
        (tmp_workspace.root / "notes.md").write_text("def is a keyword")

        result = execute_tool(
            "search_files", {"pattern": "def", "glob": "*.py"}, tmp_workspace
        )
        assert "code.py" in result

    def test_search_no_matches(self, tmp_workspace):
        (tmp_workspace.root / "a.txt").write_text("hello")
        result = execute_tool(
            "search_files", {"pattern": "nonexistent_pattern_xyz"}, tmp_workspace
        )
        assert "no matches" in result

    def test_unknown_tool(self, tmp_workspace):
        result = execute_tool("nonexistent_tool", {}, tmp_workspace)
        assert "Error" in result


# --- Tool Definition Tests ---


class TestToolDefinitions:
    """Validate tool definitions follow tool-design skill principles."""

    def test_tool_count(self):
        """Architectural reduction: should be minimal."""
        assert len(TOOLS) <= 5, "Too many tools — violates reduction principle"

    def test_all_tools_have_descriptions(self):
        for tool in TOOLS:
            assert "description" in tool
            assert len(tool["description"]) > 20, (
                f"Tool {tool['name']} has too-short description"
            )

    def test_descriptions_answer_when(self):
        """Tool-design skill: descriptions should answer 'when to use'."""
        for tool in TOOLS:
            desc = tool["description"].lower()
            assert any(
                keyword in desc
                for keyword in ["use when", "use for", "returns", "search", "read", "write"]
            ), f"Tool {tool['name']} description lacks usage guidance"

    def test_all_tools_have_schemas(self):
        for tool in TOOLS:
            assert "input_schema" in tool
            assert tool["input_schema"]["type"] == "object"

    def test_required_params_documented(self):
        for tool in TOOLS:
            required = tool["input_schema"].get("required", [])
            props = tool["input_schema"].get("properties", {})
            for param in required:
                assert param in props, (
                    f"Tool {tool['name']}: required param '{param}' not in properties"
                )
                assert "description" in props[param], (
                    f"Tool {tool['name']}: param '{param}' missing description"
                )


# --- Integration Tests ---


class TestIntegration:
    """Test patterns working together."""

    def test_skill_loading_then_reading(self, tmp_workspace, skills_dir):
        """Dynamic skill loading → tool execution chain."""
        loader = SkillLoader(skills_dir)
        matches = loader.match("filesystem context offload")
        assert len(matches) > 0

        skill_path = matches[0]["path"]
        result = execute_tool(
            "read_file", {"path": skill_path}, tmp_workspace
        )
        assert "Filesystem" in result or "filesystem" in result

    def test_large_skill_gets_masked(self, tmp_workspace, skills_dir):
        """Reading a full skill file should trigger masking."""
        loader = SkillLoader(skills_dir)
        content = loader.load("filesystem-context")
        assert content is not None
        assert len(content) > SCRATCH_THRESHOLD

        masked = mask_observation("skill_load", content, tmp_workspace)
        assert "[Output" in masked
        assert len(masked) < len(content)

    def test_budget_tracks_skill_loading(self, skills_dir):
        """Budget should account for dynamically loaded skills."""
        budget = ContextBudget(25000)
        loader = SkillLoader(skills_dir)

        # Track catalog (static context)
        catalog = loader.catalog()
        budget.track("system", catalog)
        after_catalog = budget.current

        # Track loaded skill (dynamic context)
        content = loader.load("filesystem-context")
        budget.track("system", content)
        after_skill = budget.current

        assert after_skill > after_catalog
        # A single skill shouldn't blow the budget
        assert budget.utilization < 0.5

    def test_plan_survives_workspace_reopen(self, tmp_path):
        """Plan persistence across workspace instances."""
        ws1 = Workspace(tmp_path / "shared_ws")
        ws1.write_plan("## Plan v1\n- Step 1: analyze\n- Step 2: report")

        # New workspace instance, same directory
        ws2 = Workspace(tmp_path / "shared_ws")
        plan = ws2.read_plan()
        assert "Plan v1" in plan
        assert "Step 2" in plan

    def test_full_budget_accounting(self, skills_dir):
        """Simulate a realistic session's token budget."""
        budget = ContextBudget(25000)

        # System prompt with catalog
        loader = SkillLoader(skills_dir)
        budget.track("system", loader.catalog())

        # Load 2 skills dynamically
        for name in ["filesystem-context", "tool-design"]:
            content = loader.load(name)
            budget.track("system", content)

        # Simulate 5 tool call results (some large, some small)
        for i in range(5):
            size = 500 if i % 2 == 0 else 3000
            budget.track("tool_result", "x" * size)

        # Should be under budget with room to spare
        print(f"Budget after sim: {budget.current}/{budget.budget} ({budget.utilization:.0%})")
        assert budget.utilization < 1.0
