import apiClient from "./apiClient";

export async function getWorkspaceContext() {
  const response = await apiClient.get("/api/workspace/context");
  return response.data;
}

export async function listWorkspaceFiles(path = ".") {
  const response = await apiClient.post("/api/workspace/list-files", {
    path,
  });
  return response.data;
}

export async function readWorkspaceFile(path, max_chars = 20000) {
  const response = await apiClient.post("/api/workspace/read-file", {
    path,
    max_chars,
  });
  return response.data;
}
