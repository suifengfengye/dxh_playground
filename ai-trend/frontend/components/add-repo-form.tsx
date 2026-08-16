"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import { addToWatchlist } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export function AddRepoForm() {
  const [repoUrl, setRepoUrl] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const repository = await addToWatchlist(repoUrl);
      setMessage(`已加入 watchlist: ${repository.full_name}`);
      setRepoUrl("");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "添加失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>添加仓库</CardTitle>
        <CardDescription>输入 GitHub 仓库地址，保存到 watchlist 并采集当前指标。</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="flex flex-col gap-3 md:flex-row" onSubmit={handleSubmit}>
          <Input
            placeholder="https://github.com/langgenius/dify"
            value={repoUrl}
            onChange={(event) => setRepoUrl(event.target.value)}
          />
          <Button disabled={loading} type="submit">
            {loading ? "添加中..." : "加入 Watchlist"}
          </Button>
        </form>
        {message ? <p className="mt-3 text-sm text-mutedForeground">{message}</p> : null}
      </CardContent>
    </Card>
  );
}
