import { RepoTable } from "@/components/repo-table";
import { getWatchlist } from "@/lib/api";

export default async function WatchlistPage() {
  const repositories = await getWatchlist().catch(() => []);

  return (
    <main className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Watchlist</h1>
        <p className="mt-2 text-mutedForeground">当前已经加入观察名单的 GitHub 仓库。</p>
      </div>
      <RepoTable repositories={repositories} />
    </main>
  );
}
