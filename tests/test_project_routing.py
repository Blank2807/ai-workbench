import pytest
import sys
from modules.ide import tools


@pytest.mark.parametrize(
    ("indicator_file", "expected_types"),
    [
        ("requirements.txt", ["python"]),
        ("package.json", ["node"]),
        ("tsconfig.json", ["typescript"]),
        ("pom.xml", ["java_maven"]),
        ("build.gradle", ["java_gradle"]),
        ("composer.json", ["php"]),
        ("go.mod", ["go"]),
        ("Cargo.toml", ["rust"]),
        ("project.csproj", ["dotnet"]),
    ],
)
def test_detect_project_type(workspace, make_file, indicator_file, expected_types):
    make_file(indicator_file, "{}")

    result = tools.detect_project_type(".")

    assert result["success"] is True
    assert result["detected_project_types"] == expected_types


@pytest.mark.parametrize(
    ("indicator_file", "expected_command"),
    [
        ("requirements.txt", [sys.executable, "-m", "pytest", "-v"]),
        ("package.json", ["npm", "test"]),
        ("pom.xml", ["mvn", "test"]),
        ("build.gradle", ["gradle", "test"]),
        ("composer.json", ["vendor/bin/phpunit"]),
        ("go.mod", ["go", "test", "./..."]),
        ("Cargo.toml", ["cargo", "test"]),
        ("project.csproj", ["dotnet", "test"]),
    ],
)
def test_run_project_tests_routes_to_language_runner(
    workspace, make_file, monkeypatch, indicator_file, expected_command
):
    make_file(indicator_file, "{}")
    calls = {}

    def fake_run_command(command, timeout=60):
        calls["command"] = command
        calls["timeout"] = timeout
        return {
            "success": True,
            "status": "completed_successfully",
            "command": " ".join(command),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "ran": True,
            "completed": True,
        }

    monkeypatch.setattr(tools, "run_command", fake_run_command)

    result = tools.run_project_tests(".")

    assert result["success"] is True
    assert calls["command"] == expected_command


@pytest.mark.parametrize(
    ("indicator_file", "expected_command"),
    [
        ("requirements.txt", [sys.executable, "-m", "compileall", "."]),
        ("package.json", ["npm", "run", "build"]),
        ("pom.xml", ["mvn", "compile"]),
        ("build.gradle", ["gradle", "build"]),
        ("go.mod", ["go", "build", "./..."]),
        ("Cargo.toml", ["cargo", "build"]),
        ("project.csproj", ["dotnet", "build"]),
    ],
)
def test_run_project_build_routes_to_language_runner(
    workspace, make_file, monkeypatch, indicator_file, expected_command
):
    make_file(indicator_file, "{}")
    calls = {}

    def fake_run_command(command, timeout=60):
        calls["command"] = command
        calls["timeout"] = timeout
        return {
            "success": True,
            "status": "completed_successfully",
            "command": " ".join(command),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "ran": True,
            "completed": True,
        }

    monkeypatch.setattr(tools, "run_command", fake_run_command)

    result = tools.run_project_build(".")

    assert result["success"] is True
    assert calls["command"] == expected_command
