from pathlib import Path

import pytest

from modules.ide import tools


@pytest.fixture()
def workspace(tmp_path: Path):
    tools.WORKSPACE_STATE["workspace_root"] = tmp_path
    tools.WORKSPACE_STATE["active_file"] = None
    tools.WORKSPACE_STATE["active_folder"] = "."
    return tmp_path


@pytest.fixture()
def make_file(workspace):
    def _make_file(relative_path: str, content: str = "") -> Path:
        file_path = workspace / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _make_file
