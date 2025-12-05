from pathlib import Path
from types import SimpleNamespace

import pytest

from agentom.tools import common_tools as ct


def test_list_files_ignores_logs(tmp_path, monkeypatch):
    # Prepare a temporary workspace and point settings at it
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    monkeypatch.setattr(ct.settings, "WORKSPACE_DIR", workspace)

    # Create logs file and a normal input file
    logs_dir = workspace / "logs"
    logs_dir.mkdir()
    (logs_dir / "a.log").write_text("log contents")

    inputs_dir = workspace / "inputs"
    inputs_dir.mkdir()
    (inputs_dir / "b.txt").write_text("data contents")

    # Listing logs should be ignored (empty result)
    res = ct.list_files("logs")
    assert isinstance(res, dict)
    assert res.get("files") == ""

    # Listing inputs should return the file name
    res2 = ct.list_files("inputs")
    assert "b.txt" in res2.get("files")


def test_list_all_files_ignores_logs(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    monkeypatch.setattr(ct.settings, "WORKSPACE_DIR", workspace)

    # Create files under multiple directories
    (workspace / "logs").mkdir()
    (workspace / "logs" / "l1.log").write_text("log")

    (workspace / "inputs").mkdir()
    (workspace / "inputs" / "i1.txt").write_text("in")

    (workspace / "outputs").mkdir()
    (workspace / "outputs" / "o1.txt").write_text("out")

    results = ct.list_all_files()
    assert isinstance(results, dict)

    files_map = results.get("files")
    # logs folder should be absent
    assert all("logs" not in k for k in files_map.keys())

    # other folders should be present
    assert any("inputs" in k for k in files_map.keys())
    assert any("outputs" in k for k in files_map.keys())
