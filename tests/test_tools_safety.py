from modules.ide import tools


def test_set_workspace_rejects_empty_path(workspace):
    result = tools.set_workspace("")

    assert result["success"] is False
    assert result["error_code"] == "MISSING_PATH"


def test_create_file_rejects_escape(workspace):
    result = tools.create_file("../escape.py", "print('nope')")

    assert result["success"] is False
    assert result["error_code"] == "UNSAFE_PATH"


def test_open_file_detects_ambiguous_filename(workspace, make_file):
    make_file("a/foo.py", "print('a')")
    make_file("b/foo.py", "print('b')")

    result = tools.open_file("foo.py")

    assert result["success"] is False
    assert result["error_code"] == "AMBIGUOUS_FILE"
    assert sorted(result["possible_matches"]) == ["a/foo.py", "b/foo.py"]


def test_replace_text_returns_text_not_found(workspace, make_file):
    make_file("script.py", "print('hello')")

    result = tools.replace_text("script.py", "missing", "x")

    assert result["success"] is False
    assert result["error_code"] == "TEXT_NOT_FOUND"


def test_update_file_creates_backup_before_overwrite(workspace, make_file):
    file_path = make_file("app.py", "print('old')")

    result = tools.update_file("app.py", "print('new')")

    assert result["success"] is True
    assert result["backup_path"] == "app.py.bak"
    assert file_path.read_text(encoding="utf-8") == "print('new')"
    assert (workspace / "app.py.bak").read_text(encoding="utf-8") == "print('old')"


def test_run_file_rejects_unsupported_extension(workspace, make_file):
    make_file("notes.txt", "not executable")

    result = tools.run_file("notes.txt")

    assert result["success"] is False
    assert result["error_code"] == "UNSUPPORTED_FILE_RUN"


def test_run_file_uses_tsx_for_typescript_when_available(workspace, make_file, monkeypatch):
    make_file("src/main.ts", "console.log('hi')")
    calls = {}

    def fake_command_exists(command):
        return command == "tsx"

    def fake_run_command(command, timeout=60):
        calls["command"] = command
        calls["timeout"] = timeout
        return {
            "success": True,
            "status": "completed_successfully",
            "command": " ".join(command),
            "exit_code": 0,
            "stdout": "ok",
            "stderr": "",
            "ran": True,
            "completed": True,
        }

    monkeypatch.setattr(tools, "command_exists", fake_command_exists)
    monkeypatch.setattr(tools, "run_command", fake_run_command)

    result = tools.run_file("src/main.ts")

    assert result["success"] is True
    assert result["runner"] == "tsx"
    assert calls["command"] == ["tsx", "src/main.ts"]
    assert calls["timeout"] == 60
