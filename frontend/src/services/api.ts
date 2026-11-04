import { SystemStatus, GeneratedFile } from '../types/agent';

const API_BASE = 'http://localhost:8000/api';

export async function fetchHealth(): Promise<SystemStatus> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return await res.json();
  } catch {
    return {
      status: 'offline',
      service: 'AgentForge',
      version: '0.1.0',
      ollama: { online: false, base_url: 'http://localhost:11434', available_models: [] }
    };
  }
}

export async function startProjectRun(
  prompt: string,
  model: string
): Promise<{ project_id: string; stream_url: string }> {
  const res = await fetch(`${API_BASE}/agent/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, model })
  });
  if (!res.ok) throw new Error('Failed to start agent execution run');
  return await res.json();
}

export async function fetchWorkspaceFiles(projectId: string): Promise<GeneratedFile[]> {
  try {
    const res = await fetch(`${API_BASE}/agent/workspace/${projectId}`);
    const data = await res.json();
    return data.files || [];
  } catch {
    return [];
  }
}

export async function fetchProjectState(projectId: string) {
  try {
    const res = await fetch(`${API_BASE}/agent/state/${projectId}`);
    return await res.json();
  } catch {
    return null;
  }
}
