import apiClient from "./apiClient";

export async function getGitStatus(){
    const response = await apiClient.get("/api/git/status");
    return response.data;
}