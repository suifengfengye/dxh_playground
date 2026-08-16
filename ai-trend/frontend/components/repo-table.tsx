import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Repository } from "@/lib/types";

export function RepoTable({ repositories }: { repositories: Repository[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Watchlist</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b text-left text-mutedForeground">
                <th className="py-3 pr-4">仓库</th>
                <th className="py-3 pr-4">Language</th>
                <th className="py-3 pr-4">Stars</th>
                <th className="py-3 pr-4">Forks</th>
                <th className="py-3 pr-4">Subscribers</th>
                <th className="py-3 pr-4">Topics</th>
              </tr>
            </thead>
            <tbody>
              {repositories.map((repository) => (
                <tr className="border-b last:border-0" key={repository.id}>
                  <td className="py-3 pr-4">
                    <Link className="font-medium hover:underline" href={`/repos/${repository.id}`}>
                      {repository.full_name}
                    </Link>
                    <p className="mt-1 max-w-md text-xs text-mutedForeground">
                      {repository.description}
                    </p>
                  </td>
                  <td className="py-3 pr-4">{repository.language ?? "-"}</td>
                  <td className="py-3 pr-4">{repository.stars_current.toLocaleString()}</td>
                  <td className="py-3 pr-4">{repository.forks_current.toLocaleString()}</td>
                  <td className="py-3 pr-4">{repository.subscribers_current.toLocaleString()}</td>
                  <td className="py-3 pr-4">
                    <div className="flex flex-wrap gap-1">
                      {repository.topics.slice(0, 3).map((topic) => (
                        <Badge key={topic}>{topic}</Badge>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
