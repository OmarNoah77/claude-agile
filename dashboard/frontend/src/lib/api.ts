import type { ProjectState, PipelineState, ChatMessage } from "./types";

const BASE = "";

async function request<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export function fetchState(): Promise<ProjectState> {
  return request<ProjectState>("/api/state");
}

export function fetchPipeline(): Promise<PipelineState> {
  return request<PipelineState>("/api/pipeline");
}

export function fetchChatHistory(
  limit = 40
): Promise<{ messages: ChatMessage[] }> {
  return request<{ messages: ChatMessage[] }>(
    `/api/chat/history?limit=${limit}`
  );
}

export function sendChatMessage(
  message: string
): Promise<{ ok: boolean; id: string }> {
  return request<{ ok: boolean; id: string }>("/api/chat/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
}

export function switchModule(
  module: string
): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>("/api/modules/active", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ module }),
  });
}

export function createModule(
  workspace: string,
  module: string
): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(`/api/workspaces/${workspace}/modules`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ module }),
  });
}
