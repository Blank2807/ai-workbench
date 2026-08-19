import apiClient from "./apiClient";

export async function runTests() {
    const response = await apiClient.post("/api/ide/run-tests", {
        path: "."
    });
    return response.data;
}
