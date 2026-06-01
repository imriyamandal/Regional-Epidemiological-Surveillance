"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";

type Explain = {
  disease: string;
  district: string;
  prediction: number;
  risk_level: string;
  top_features: { feature: string; importance: number }[];
  shap_summary: { feature: string; mean_shap: number }[];
  shap_waterfall: { feature: string; value: number; cumulative: number }[];
};

export default function ExplainabilityPage() {
  const router = useRouter();
  const [data, setData] = useState<Explain | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) return router.push("/login");
    api<Explain>("/api/v1/explainability?disease=DENGUE&district=Pune", {}, token)
      .then(setData)
      .catch(() => {});
  }, [router]);

  return (
    <AppShell title="Explainable AI Insights">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>SHAP Feature Importance</CardTitle>
            <p className="text-sm text-slate-500">
              {data?.disease} — {data?.district} | Predicted: {data?.prediction?.toFixed(0)} cases
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-72 min-h-[288px] min-w-0 w-full">
              <ResponsiveContainer width="100%" height="100%" minHeight={288}>
                <BarChart data={data?.shap_summary ?? []} layout="vertical">
                  <XAxis type="number" />
                  <YAxis dataKey="feature" type="category" width={120} tick={{ fontSize: 10 }} />
                  <Tooltip />
                  <Bar dataKey="mean_shap" fill="#6366f1" radius={4} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>SHAP Waterfall</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {(data?.shap_waterfall ?? []).map((w) => (
                <li key={w.feature} className="flex items-center justify-between text-sm border-b py-2 dark:border-slate-800">
                  <span>{w.feature}</span>
                  <span className="font-mono text-cyan-600">+{w.value.toFixed(3)}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
      <Card className="mt-6">
        <CardHeader><CardTitle>Top Disease Drivers</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {(data?.top_features ?? []).map((f) => (
              <div key={f.feature} className="rounded-lg border p-3 dark:border-slate-800">
                <p className="font-medium">{f.feature}</p>
                <p className="text-2xl font-bold text-indigo-600">{(f.importance * 100).toFixed(1)}%</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
