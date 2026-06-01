"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";

type RiskItem = {
  state: string;
  district: string;
  disease: string;
  risk_level: string;
  risk_score: number;
  predicted_cases: number;
};

const RISK_COLORS: Record<string, string> = {
  safe: "#22c55e",
  low_risk: "#84cc16",
  medium_risk: "#eab308",
  high_risk: "#f97316",
  critical_risk: "#ef4444",
};

export default function RiskPage() {
  const router = useRouter();
  const [risks, setRisks] = useState<RiskItem[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) return router.push("/login");
    api<RiskItem[]>("/api/v1/analytics/risk?limit=50", {}, token).then(setRisks).catch(() => {});
  }, [router]);

  const chartData = risks.slice(0, 15).map((r) => ({
    name: r.district.slice(0, 12),
    score: +(r.risk_score * 100).toFixed(0),
    level: r.risk_level,
  }));

  return (
    <AppShell title="Outbreak Risk Analysis">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Risk Score Distribution</CardTitle></CardHeader>
          <CardContent>
            <div className="h-72 min-h-[288px] min-w-0 w-full">
              <ResponsiveContainer width="100%" height="100%" minHeight={288}>
                <BarChart data={chartData} layout="vertical">
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="score" radius={4}>
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={RISK_COLORS[entry.level] || "#3b82f6"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Critical Regions</CardTitle></CardHeader>
          <CardContent className="max-h-72 overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="pb-2">District</th>
                  <th>Disease</th>
                  <th>Risk</th>
                  <th>Cases</th>
                </tr>
              </thead>
              <tbody>
                {risks.filter((r) => ["high_risk", "critical_risk"].includes(r.risk_level)).map((r) => (
                  <tr key={`${r.district}-${r.disease}`} className="border-b border-slate-100 dark:border-slate-800">
                    <td className="py-2">{r.district}, {r.state}</td>
                    <td>{r.disease}</td>
                    <td>
                      <span className="rounded px-2 py-0.5 text-xs text-white" style={{ background: RISK_COLORS[r.risk_level] }}>
                        {(r.risk_score * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td>{r.predicted_cases.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
