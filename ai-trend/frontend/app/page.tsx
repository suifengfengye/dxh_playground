"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { AddRepoForm } from "@/components/add-repo-form";
import { RepoTable } from "@/components/repo-table";
import { TrendCard } from "@/components/trend-card";
import { Button } from "@/components/ui/button";
import { getWatchlist } from "@/lib/api";
import type { Repository } from "@/lib/types";

export default function HomePage() {
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
          setListError("Watchlist 加载失败，请刷新页面重试");
        }
      }
    }

    loadWatchlist();

    return () => {
      cancelled = true;
    };
  }, []);

  function handleAddSuccess(repository: Repository) {
    setRepositories((current) => {
      const next = current.filter((item) => item.id !== repository.id);
      return [repository, ...next];
    });
    setListError(null);
  }

  return (
    <main className="space-y-8">
      <section className="flex items-start justify-between gap-6">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-mutedForeground">
            AI Trend MVP
          </p>
          <h1 className="mt-2 text-4xl font-bold tracking-tight">Watchlist + 爆发预警</h1>
          <p className="mt-3 max-w-2xl text-mutedForeground">
            手动输入 GitHub 仓库地址，保存仓库快照，后续即可按天采集并展示 stars、forks、
            subscribers 趋势。
          </p>
        </div>
        <Button variant="outline">
          <Link href="/watchlist">查看 Watchlist</Link>
        </Button>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <TrendCard title="已关注仓库" value={String(repositories.length)} helper="MVP 阶段建议维护 20-50 个仓库" />
        <TrendCard title="核心指标" value="Stars / Forks / Subscribers" helper="每日采集后即可生成折线图和增量统计" />
        {/* <TrendCard title="下一步" value="Breakout Score" helper="后续按 7d/30d 增长率补充预警逻辑" /> */}
      </section>

      <AddRepoForm onSuccess={handleAddSuccess} />
      {listError ? <p className="text-sm text-destructive">{listError}</p> : null}
      <RepoTable repositories={repositories} />
    </main>
  );
}
