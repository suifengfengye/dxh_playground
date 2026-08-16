export type Repository = {
  id: number;
  owner: string;
  name: string;
  full_name: string;
  repo_url: string;
  description: string | null;
  language: string | null;
  default_branch: string | null;
  stars_current: number;
  forks_current: number;
  subscribers_current: number;
  open_issues_current: number;
  topics: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DailyMetric = {
  metric_date: string;
  stars: number;
  forks: number;
  subscribers: number;
  open_issues: number;
  pushed_at: string | null;
};
