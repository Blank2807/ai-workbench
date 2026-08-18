from typing import Any, Dict, List


IDE_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "name": "get_workspace_context",
        "description": "Get current workspace root, active file, and active folder.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "set_workspace",
        "description": "Set/open a workspace folder using an explicit folder path.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative folder path to use as workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "select_workspace_folder",
        "description": "Open a folder picker dialog and set the selected folder as the workspace.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "open_file",
        "description": "Open a file and set it as the active file. This does not visually open an editor; it sets IDE context.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path or filename, for example tools.py, src/app.tsx, Program.cs.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "open_folder",
        "description": "Open a folder inside the current workspace and set it as the active folder.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative folder path inside the workspace. Use '.' for workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "clear_active_context",
        "description": "Clear active file and active folder context.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_files",
        "description": "List all files inside the workspace, active folder, or a specific folder.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to list. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_code_files",
        "description": "List supported code/text files with detected language information.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to scan. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read a code/text file. Supports exact relative paths and filename-only recursive lookup.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path or filename. If empty, use active file.",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return from the file.",
                },
            },
            "required": ["path", "max_chars"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_active_file",
        "description": "Read the currently active file.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return from the active file.",
                }
            },
            "required": ["max_chars"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_folder",
        "description": "Read multiple code/text files from a folder with limits. Useful for folder-level understanding.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to read. Use '.' for active folder/workspace root.",
                },
                "max_files": {
                    "type": "integer",
                    "description": "Maximum number of files to read.",
                },
                "max_chars_per_file": {
                    "type": "integer",
                    "description": "Maximum characters to read per file.",
                },
            },
            "required": ["path", "max_files", "max_chars_per_file"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_text",
        "description": "Search for text across the workspace, active folder, or a specific folder/file.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for, for example auth, login, database, function name, class name, API route.",
                },
                "path": {
                    "type": "string",
                    "description": "Folder/file path to search in. Use '.' for active folder/workspace root.",
                },
                "max_matches": {
                    "type": "integer",
                    "description": "Maximum number of matches to return.",
                },
            },
            "required": ["query", "path", "max_matches"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_file_info",
        "description": "Return metadata for a file such as extension, language, size, and line count. If path is empty, use active file.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path, filename, or empty string for active file.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "summarize_folder",
        "description": "Summarize a folder by language, extension, and sample files.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path to summarize. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "detect_language_by_path",
        "description": "Detect programming language based on a file path or extension.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path, for example app.py, index.tsx, Program.cs, or query.sql.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "detect_project_type",
        "description": "Detect project type based on common project files like package.json, requirements.txt, pom.xml, .csproj, composer.json, go.mod, etc.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Project/folder path. Use '.' for active folder/workspace root.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "create_file",
    "description": "Create a new text/code file inside the workspace. Does not overwrite existing files.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path to create, for example src/utils.py.",
            },
            "content": {
                "type": "string",
                "description": "Full initial file content.",
            },
        },
        "required": ["path", "content"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "update_file",
    "description": "Overwrite an existing text/code file. Creates a backup before updating. Empty path means active file.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path or empty string for active file.",
            },
            "content": {
                "type": "string",
                "description": "Full replacement file content.",
            },
        },
        "required": ["path", "content"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "replace_text",
    "description": "Replace exact text inside an existing text/code file. Creates a backup before editing. Empty path means active file.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path or empty string for active file.",
            },
            "old_text": {
                "type": "string",
                "description": "Exact text to replace.",
            },
            "new_text": {
                "type": "string",
                "description": "Replacement text.",
            },
        },
        "required": ["path", "old_text", "new_text"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "run_file",
    "description": "Run the active file or a given file using safe language-specific execution. Supports direct run for Python, JavaScript, and PHP files.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path or empty string for active file.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
    },
},
{
    "type": "function",
    "name": "run_project_tests",
    "description": "Detect project type and run known safe test command, such as pytest, npm test, dotnet test, mvn test, go test, or cargo test.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project/folder path. Use '.' for current workspace/active folder.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
    },
    },
    {
    "type": "function",
    "name": "run_project_build",
    "description": "Detect project type and run known safe build/check command, such as compileall, npm run build, dotnet build, mvn compile, go build, or cargo build.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project/folder path. Use '.' for current workspace/active folder.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
        },
    },
    {
    "type": "function",
    "name": "run_static_analysis",
    "description": "Run safe static/code checks based on detected project type. Examples: compileall, ruff, bandit, npm lint/build, dotnet build, mvn compile.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Project/folder path. Use '.' for current workspace/active folder.",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
    },
},
]