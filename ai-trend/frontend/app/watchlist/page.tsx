"use client";

import { useEffect, useState } from "react";

import { RepoTable } from "@/components/repo-table";
import { getWatchlist } from "@/lib/api";
import type { Repository } from "@/lib/types";

export default function WatchlistPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [listError, setListError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadWatchlist() {
      try {
        const data = await getWatchlist();
        if (!cancelled) {
          setRepositories(data);
          setListError(null);
        }
      } catch {
        if (!cancelled) {
          setListError("Watchlist 加载失败，请稍后重试");
        }
      }
    }

    loadWatchlist();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Watchlist</h1>
        <p className="mt-2 text-mutedForeground">当前已经加入观察名单的 GitHub 仓库。</p>
      </div>
      {listError ? <p className="text-sm text-destructive">{listError}</p> : null}
      <RepoTable repositories={repositories} />
    </main>
  );
}
