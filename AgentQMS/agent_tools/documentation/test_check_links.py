#!/usr/bin/env python3
"""
Unit tests for check_links.py
Tests argument parsing behavior for --no-agentqms flag and link checking logic.
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the module under test
from check_links import check_links_in_directory, main, resolve_link


class TestCheckLinksArgumentParsing:
    """Test argument parsing behavior for --no-agentqms flag."""

    @patch("check_links.check_links_in_directory")
    @patch("AgentQMS.agent_tools.utils.paths.get_project_root")
    def test_default_includes_agentqms(self, mock_root, mock_check):
        """Test that AgentQMS is included by default (no flags)."""
        # Setup mocks
        project_root = Path("/fake/project")
        mock_root.return_value = project_root
        mock_check.return_value = (5, 20, [])  # checked_files, total_links, broken_links

        # Mock Path.exists() to return True for both directories
        with patch.object(Path, "exists", return_value=True):
            # Mock sys.argv to simulate no arguments
            with patch.object(sys, "argv", ["check_links.py"]):
                result = main()

        # Assert check_links_in_directory called twice (docs + AgentQMS)
        EXPECTED_CALL_COUNT = 2
        assert mock_check.call_count == EXPECTED_CALL_COUNT

        # Verify both directories were checked
        calls = mock_check.call_args_list
        assert calls[0][0][0] == project_root / "docs"  # First call: docs
        assert calls[1][0][0] == project_root / "AgentQMS"  # Second call: AgentQMS

        # Should return 0 (success, no broken links)
        assert result == 0

    @patch("check_links.check_links_in_directory")
    @patch("AgentQMS.agent_tools.utils.paths.get_project_root")
    def test_no_agentqms_excludes_directory(self, mock_root, mock_check):
        """Test that --no-agentqms excludes AgentQMS directory."""
        # Setup mocks
        project_root = Path("/fake/project")
        mock_root.return_value = project_root
        mock_check.return_value = (3, 15, [])

        # Mock Path.exists() to return True for both directories
        with patch.object(Path, "exists", return_value=True):
            # Mock sys.argv to simulate --no-agentqms flag
            with patch.object(sys, "argv", ["check_links.py", "--no-agentqms"]):
                result = main()

        # Assert check_links_in_directory called once (docs only)
        assert mock_check.call_count == 1

        # Verify only docs directory was checked
        calls = mock_check.call_args_list
        assert calls[0][0][0] == project_root / "docs"

        assert result == 0

    @patch("check_links.check_links_in_directory")
    @patch("AgentQMS.agent_tools.utils.paths.get_project_root")
    def test_json_output_with_default(self, mock_root, mock_check):
        """Test --json flag with default AgentQMS inclusion."""
        # Setup mocks
        project_root = Path("/fake/project")
        mock_root.return_value = project_root
        mock_check.return_value = (2, 10, [])

        # Mock Path.exists() to return True for both directories
        with patch.object(Path, "exists", return_value=True):
            # Mock sys.argv to simulate --json flag only
            with patch.object(sys, "argv", ["check_links.py", "--json"]):
                with patch("builtins.print") as mock_print:
                    result = main()

        # Should check both directories
        assert mock_check.call_count == EXPECTED_CALL_COUNT

        # Verify JSON output was printed
        assert mock_print.called
        printed_output = mock_print.call_args[0][0]
        assert '"checked_files"' in printed_output
        assert '"status": "pass"' in printed_output

        assert result == 0

    @patch("check_links.check_links_in_directory")
    @patch("AgentQMS.agent_tools.utils.paths.get_project_root")
    def test_json_output_with_no_agentqms(self, mock_root, mock_check):
        """Test --json with --no-agentqms excludes AgentQMS."""
        # Setup mocks
        project_root = Path("/fake/project")
        mock_root.return_value = project_root
        mock_check.return_value = (2, 10, [])

        # Mock Path.exists() to return True for both directories
        with patch.object(Path, "exists", return_value=True):
            # Mock sys.argv to simulate both flags
            with patch.object(sys, "argv", ["check_links.py", "--json", "--no-agentqms"]):
                with patch("builtins.print") as mock_print:
                    result = main()

        # Should check only docs directory
        assert mock_check.call_count == 1
        assert mock_check.call_args_list[0][0][0] == project_root / "docs"

        # Verify JSON output
        assert mock_print.called
        printed_output = mock_print.call_args[0][0]
        assert '"checked_files": 2' in printed_output

        assert result == 0

    @patch("check_links.check_links_in_directory")
    @patch("AgentQMS.agent_tools.utils.paths.get_project_root")
    def test_artifacts_only_with_default(self, mock_root, mock_check):
        """Test --artifacts-only with default AgentQMS inclusion."""
        # Setup mocks
        project_root = Path("/fake/project")
        mock_root.return_value = project_root
        mock_check.return_value = (1, 5, [])

        # Mock Path.exists() to return True for both directories
        with patch.object(Path, "exists", return_value=True):
            # Mock sys.argv
            with patch.object(sys, "argv", ["check_links.py", "--artifacts-only"]):
                result = main()

        # Should check both directories
        assert mock_check.call_count == EXPECTED_CALL_COUNT

        # Verify artifacts_only flag was passed
        for call_args in mock_check.call_args_list:
            assert call_args[0][2] is True  # check_artifacts_only parameter

        assert result == 0

    @patch("check_links.check_links_in_directory")
    @patch("AgentQMS.agent_tools.utils.paths.get_project_root")
    def test_broken_links_return_nonzero(self, mock_root, mock_check):
        """Test that broken links cause non-zero exit code."""
        # Setup mocks with broken links
        project_root = Path("/fake/project")
        mock_root.return_value = project_root
        broken_link = {
            "file": "test.md",
            "line": 10,
            "text": "Link",
            "url": "broken.md",
            "resolved": "docs/broken.md"
        }
        mock_check.return_value = (1, 5, [broken_link])

        # Mock Path.exists() to return True for both directories
        with patch.object(Path, "exists", return_value=True):
            # Mock sys.argv
            with patch.object(sys, "argv", ["check_links.py"]):
                result = main()

        # Should return 1 (failure)
        assert result == 1


class TestResolveLinkFunction:
    """Test the resolve_link helper function."""

    def test_external_urls_return_none(self):
        """Test that external URLs are skipped."""
        source = Path("/fake/docs/test.md")

        assert resolve_link(source, "http://example.com") is None
        assert resolve_link(source, "https://example.com") is None
        assert resolve_link(source, "mailto:test@example.com") is None

    def test_anchor_only_returns_none(self):
        """Test that anchor-only links are skipped."""
        source = Path("/fake/docs/test.md")

        assert resolve_link(source, "#section") is None
        assert resolve_link(source, "#") is None

    def test_removes_fragment(self):
        """Test that fragments are removed from link URLs."""
        source = Path("/fake/docs/test.md")

        result = resolve_link(source, "other.md#section")
        assert result is not None
        assert "#" not in str(result)

    def test_relative_path_resolution(self):
        """Test that relative paths are resolved correctly."""
        source = Path("/fake/docs/subdir/test.md")

        result = resolve_link(source, "../other.md")
        assert result is not None
        assert result.name == "other.md"


class TestCheckLinksInDirectory:
    """Test the check_links_in_directory function."""

    def test_skips_git_directory(self, tmp_path):
        """Test that .git directories are skipped."""
        # Create test structure
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "test.md").write_text("# Test")

        checked, total, broken = check_links_in_directory(tmp_path, tmp_path, False)

        # Should skip .git directory
        assert checked == 0

    def test_skips_node_modules(self, tmp_path):
        """Test that node_modules directories are skipped."""
        # Create test structure
        node_dir = tmp_path / "node_modules"
        node_dir.mkdir()
        (node_dir / "test.md").write_text("# Test")

        checked, total, broken = check_links_in_directory(tmp_path, tmp_path, False)

        # Should skip node_modules
        assert checked == 0

    def test_counts_markdown_files(self, tmp_path):
        """Test that markdown files are counted correctly."""
        # Create test files
        (tmp_path / "test1.md").write_text("# Test 1")
        (tmp_path / "test2.md").write_text("# Test 2")
        (tmp_path / "not_markdown.txt").write_text("Not markdown")

        checked, total, broken = check_links_in_directory(tmp_path, tmp_path, False)

        # Should count only .md files
        EXPECTED_MD_COUNT = 2
        assert checked == EXPECTED_MD_COUNT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
