import { useEffect, useState } from "react";
import "./App.css";

import apiClient from "./services/apiClient";
import { getGitStatus } from "./services/gitApi";
import { runTests } from "./services/ideApi";
import {
  getWorkspaceContext,
  listWorkspaceFiles,
  readWorkspaceFile,
} from "./services/workspaceApi";

function App() {
  const [health, setHealth] = useState(null);
  const [gitStatus, setGitStatus] = useState(null);
  const [testResult, setTestResult] = useState(null);

  const [workspaceContext, setWorkspaceContext] = useState(null);
  const [workspaceFiles, setWorkspaceFiles] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);

  const [loadingHealth, setLoadingHealth] = useState(false);
  const [loadingGit, setLoadingGit] = useState(false);
  const [loadingTests, setLoadingTests] = useState(false);
  const [loadingWorkspace, setLoadingWorkspace] = useState(false);
  const [loadingFile, setLoadingFile] = useState(false);

  const [error, setError] = useState("");

  async function checkHealth() {
    try {
      setLoadingHealth(true);
      setError("");

      const response = await apiClient.get("/health");
      setHealth(response.data);
    } catch (err) {
      setError(
        "FastAPI backend is not reachable. Make sure it is running on http://127.0.0.1:8000"
      );
    } finally {
      setLoadingHealth(false);
    }
  }

  async function loadGitStatus() {
    try {
      setLoadingGit(true);
      setError("");

      const data = await getGitStatus();
      setGitStatus(data);
    } catch (err) {
      setError("Unable to load Git status.");
    } finally {
      setLoadingGit(false);
    }
  }

  async function handleRunTests() {
    try {
      setLoadingTests(true);
      setError("");

      const data = await runTests();
      setTestResult(data);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setTestResult(detail || null);
      setError("Tests failed or could not be completed.");
    } finally {
      setLoadingTests(false);
    }
  }

  async function loadWorkspace() {
    try {
      setLoadingWorkspace(true);
      setError("");

      const context = await getWorkspaceContext();
      const files = await listWorkspaceFiles(".");

      setWorkspaceContext(context);
      setWorkspaceFiles(files);
    } catch (err) {
      setError("Unable to load workspace files.");
    } finally {
      setLoadingWorkspace(false);
    }
  }

  async function handleReadFile(path) {
    try {
      setLoadingFile(true);
      setError("");

      const data = await readWorkspaceFile(path, 20000);

      setSelectedFile(path);
      setFileContent(data);
    } catch (err) {
      setError(`Unable to read file: ${path}`);
    } finally {
      setLoadingFile(false);
    }
  }

  useEffect(() => {
    checkHealth();
    loadGitStatus();
    loadWorkspace();
  }, []);

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">AI Workbench</p>
          <h1>Developer Control Center</h1>
          <p className="subtitle">
            FastAPI backend connected with Git, GitHub, workspace tools, and IDE
            execution APIs.
          </p>
        </div>

        <button className="primary-button" onClick={checkHealth}>
          {loadingHealth ? "Checking..." : "Check API Health"}
        </button>
      </header>

      {error && <div className="alert">{error}</div>}

      <section className="grid">
        <div className="card">
          <div className="card-header">
            <h2>API Health</h2>
            <span className={health?.success ? "badge success" : "badge muted"}>
              {health?.success ? "Online" : "Unknown"}
            </span>
          </div>

          <p className="card-text">
            {health?.status
              ? `Backend status: ${health.status}`
              : "Health status not loaded yet."}
          </p>
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Git Status</h2>
            <button className="secondary-button" onClick={loadGitStatus}>
              {loadingGit ? "Loading..." : "Refresh"}
            </button>
          </div>

          {gitStatus ? (
            <>
              <p className="card-text">{gitStatus.summary}</p>

              <div className="metric-row">
                <span>Changed files</span>
                <strong>{gitStatus.changed_file_count}</strong>
              </div>

              {gitStatus.changed_files?.length > 0 && (
                <ul className="file-list">
                  {gitStatus.changed_files.map((file, index) => (
                    <li key={`${file.path}-${index}`}>
                      <span className="status-code">{file.status_code}</span>
                      <span>{file.path}</span>
                    </li>
                  ))}
                </ul>
              )}
            </>
          ) : (
            <p className="card-text">Git status not loaded yet.</p>
          )}
        </div>

        <div className="card wide">
          <div className="card-header">
            <h2>Workspace Files</h2>
            <button className="secondary-button" onClick={loadWorkspace}>
              {loadingWorkspace ? "Loading..." : "Refresh Files"}
            </button>
          </div>

          {workspaceContext && (
            <p className="card-text">
              Workspace: <code>{workspaceContext.workspace_root}</code>
            </p>
          )}

          {workspaceFiles?.files?.length > 0 ? (
            <div className="workspace-layout">
              <div className="workspace-file-list">
                {workspaceFiles.files.slice(0, 80).map((file) => (
                  <button
                    key={file}
                    className={`file-button ${
                      selectedFile === file ? "active" : ""
                    }`}
                    onClick={() => handleReadFile(file)}
                  >
                    {file}
                  </button>
                ))}
              </div>

              <div className="file-preview">
                <div className="file-preview-header">
                  <strong>{selectedFile || "No file selected"}</strong>
                  {loadingFile && <span>Loading...</span>}
                </div>

                <pre>
                  {fileContent?.content ||
                    "Select a file to preview its content."}
                </pre>
              </div>
            </div>
          ) : (
            <p className="card-text">No workspace files loaded yet.</p>
          )}
        </div>

        <div className="card wide">
          <div className="card-header">
            <h2>Project Tests</h2>
            <button className="primary-button" onClick={handleRunTests}>
              {loadingTests ? "Running Tests..." : "Run Tests"}
            </button>
          </div>

          {testResult ? (
            <>
              <p className="card-text">{testResult.summary}</p>

              <div className="test-summary">
                <div>
                  <span>Status</span>
                  <strong
                    className={
                      testResult.success ? "text-success" : "text-danger"
                    }
                  >
                    {testResult.status}
                  </strong>
                </div>

                <div>
                  <span>Passed</span>
                  <strong>{testResult.passed_count ?? 0}</strong>
                </div>

                <div>
                  <span>Failed</span>
                  <strong>{testResult.failed_count ?? 0}</strong>
                </div>
              </div>

              <details className="raw-output">
                <summary>View raw test output</summary>
                <pre>
                  {testResult.raw?.stdout ||
                    testResult.raw?.stderr ||
                    "No raw output."}
                </pre>
              </details>
            </>
          ) : (
            <p className="card-text">
              Click "Run Tests" to execute backend tests using the FastAPI IDE
              API.
            </p>
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
