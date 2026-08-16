import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function TrendCard({
  title,
  value,
  helper
}: {
  title: string;
  value: string;
  helper: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm text-mutedForeground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-semibold">{value}</div>
        <p className="mt-2 text-sm text-mutedForeground">{helper}</p>
      </CardContent>
    </Card>
  );
}
