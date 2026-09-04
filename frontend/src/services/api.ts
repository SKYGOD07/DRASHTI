const API_BASE = "/api/v1";

export type Camera = {
  id: string;
  name: string;
  department: string;
  camera_type: string;
  lat: number;
  lon: number;
  status: "online" | "offline" | "degraded";
};

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return res.json();
}

export const api = {
  health: () => get<{ status: string; project: string }>("/health"),
  listCameras: () => get<Camera[]>("/cameras"),
};
