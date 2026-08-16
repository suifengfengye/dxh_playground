import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI Trend",
  description: "Watchlist + breakout alert for GitHub AI repositories"
};

export default function RootLayout({
  children
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="mx-auto min-h-screen max-w-7xl px-6 py-10">{children}</div>
      </body>
    </html>
  );
}
