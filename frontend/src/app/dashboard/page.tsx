"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  MapPin,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AppShell } from "@/components/layout/app-shell";
import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";

type DashboardStats = {
  total_cases: number;
  active_alerts: number;
  high_risk_areas: number;
  prediction_accuracy: number;
  diseases_monitored: number;
  districts_tracked: number;
  trend_change_percent: number;
};

type Trend = { date: string; cases: number; disease: string };

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<Trend[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }
    Promise.all([
      api<DashboardStats>("/api/v1/analytics/dashboard", {}, token),
      api<Trend[]>("/api/v1/analytics/trends?months=12", {}, token),
    ])
      .then(([s, t]) => {
        setStats(s);
        setTrends(t);
      })
      .catch(() => router.push("/login"));
  }, [router]);

  const chartData = trends.reduce<Record<string, number>>((acc, t) => {
    acc[t.date] = (acc[t.date] || 0) + t.cases;
    return acc;
  }, {});
  const series = Object.entries(chartData).map(([date, cases]) => ({ date, cases }));

  return (
    <AppShell title="Surveillance Dashboard">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Cases" value={stats?.total_cases?.toLocaleString() ?? "—"} icon={Users} accent="blue" change="+12.4% vs last period" />
        <StatCard title="Active Alerts" value={stats?.active_alerts ?? "—"} icon={AlertTriangle} accent="orange" />
        <StatCard title="High Risk Areas" value={stats?.high_risk_areas ?? "—"} icon={MapPin} accent="red" />
        <StatCard title="Model Accuracy" value={stats ? `${(stats.prediction_accuracy * 100).toFixed(1)}%` : "—"} icon={Target} accent="green" />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-cyan-500" />
              Disease Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-72 min-h-[288px] min-w-0 w-full">
              <ResponsiveContainer width="100%" height="100%" minHeight={288}>
                <AreaChart data={series}>
                  <defs>
                    <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-800" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="cases" stroke="#0891b2" fill="url(#colorCases)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              Coverage
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Diseases monitored</span>
              <span className="font-semibold">{stats?.diseases_monitored ?? "—"}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Districts tracked</span>
              <span className="font-semibold">{stats?.districts_tracked ?? "—"}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Trend change</span>
              <span className="font-semibold text-orange-600">+{stats?.trend_change_percent ?? 0}%</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
