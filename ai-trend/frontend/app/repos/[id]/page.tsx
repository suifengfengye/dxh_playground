import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getRepository, getRepositoryMetrics } from "@/lib/api";

export default async function RepoDetailPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const repository = await getRepository(id);
  const metrics = await getRepositoryMetrics(id).catch(() => []);

  return (
    <main className="space-y-6">
      <section className="space-y-2">
        <h1 className="text-3xl font-bold">{repository.full_name}</h1>
        <p className="text-mutedForeground">{repository.description}</p>
        <div className="flex flex-wrap gap-2">
          {repository.topics.map((topic) => (
            <Badge key={topic}>{topic}</Badge>
          ))}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader><CardTitle>Stars</CardTitle></CardHeader><CardContent>{repository.stars_current.toLocaleString()}</CardContent></Card>
        <Card><CardHeader><CardTitle>Forks</CardTitle></CardHeader><CardContent>{repository.forks_current.toLocaleString()}</CardContent></Card>
        <Card><CardHeader><CardTitle>Subscribers</CardTitle></CardHeader><CardContent>{repository.subscribers_current.toLocaleString()}</CardContent></Card>
        <Card><CardHeader><CardTitle>Open Issues</CardTitle></CardHeader><CardContent>{repository.open_issues_current.toLocaleString()}</CardContent></Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>趋势数据</CardTitle>
          <CardDescription>这里先放表格，下一步再接折线图。</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-mutedForeground">
                  <th className="py-3 pr-4">日期</th>
                  <th className="py-3 pr-4">Stars</th>
                  <th className="py-3 pr-4">Forks</th>
                  <th className="py-3 pr-4">Subscribers</th>
                  <th className="py-3 pr-4">Open Issues</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((metric) => (
                  <tr className="border-b last:border-0" key={metric.metric_date}>
                    <td className="py-3 pr-4">{metric.metric_date}</td>
                    <td className="py-3 pr-4">{metric.stars.toLocaleString()}</td>
                    <td className="py-3 pr-4">{metric.forks.toLocaleString()}</td>
                    <td className="py-3 pr-4">{metric.subscribers.toLocaleString()}</td>
                    <td className="py-3 pr-4">{metric.open_issues.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
