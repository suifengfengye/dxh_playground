import { DailyMetric, Repository } from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export async function getWatchlist(): Promise<Repository[]> {
  const response = await fetch(`${API_BASE_URL}/watchlist`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch watchlist");
  }
  return response.json();
}

export async function addToWatchlist(repoUrl: string): Promise<Repository> {
  const response = await fetch(`${API_BASE_URL}/watchlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl })
  });
  if (!response.ok) {
    throw new Error("Failed to add repository");
  }
  return response.json();
}

export async function getRepository(repoId: string): Promise<Repository> {
  const response = await fetch(`${API_BASE_URL}/repos/${repoId}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch repository");
  }
  return response.json();
}

export async function getRepositoryMetrics(repoId: string): Promise<DailyMetric[]> {
  const response = await fetch(`${API_BASE_URL}/repos/${repoId}/metrics`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch metrics");
  }
  return response.json();
}
