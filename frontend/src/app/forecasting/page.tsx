"use client";

import { useEffect, useState } from "react";
import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";

type Forecast = {
  disease: string;
  district: string;
  state: string;
  horizon_months: number;
  model_name: string;
  points: { date: string; predicted: number; lower?: number; upper?: number }[];
};

export default function ForecastingPage() {
  const router = useRouter();
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [disease, setDisease] = useState("DENGUE");
  const [district, setDistrict] = useState("Pune");

  useEffect(() => {
    const token = getToken();
    if (!token) return router.push("/login");
    api<Forecast>(`/api/v1/analytics/forecast?disease=${disease}&district=${district}&horizon=6`, {}, token)
      .then(setForecast)
      .catch(() => {});
  }, [disease, district, router]);

  return (
    <AppShell title="Disease Case Forecasting">
      <div className="mb-6 flex flex-wrap gap-4">
        <select value={disease} onChange={(e) => setDisease(e.target.value)} className="rounded-lg border px-3 py-2 dark:bg-slate-900">
          {["DENGUE", "MALARIA", "CHOLERA", "CHIKUNGUNYA", "AES", "ADD"].map((d) => (
            <option key={d}>{d}</option>
          ))}
        </select>
        <input value={district} onChange={(e) => setDistrict(e.target.value)} className="rounded-lg border px-3 py-2 dark:bg-slate-900" placeholder="District" />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>
            {forecast?.disease ?? disease} — {forecast?.district ?? district} ({forecast?.horizon_months ?? 6} month horizon)
          </CardTitle>
          <p className="text-sm text-slate-500">Model: {forecast?.model_name ?? "ensemble"}</p>
        </CardHeader>
        <CardContent>
          <div className="h-80 min-h-[320px] min-w-0 w-full">
            <ResponsiveContainer width="100%" height="100%" minHeight={320}>
              <LineChart data={forecast?.points ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="predicted" stroke="#2563eb" strokeWidth={2} />
                <Line type="monotone" dataKey="lower" stroke="#94a3b8" strokeDasharray="4 4" />
                <Line type="monotone" dataKey="upper" stroke="#94a3b8" strokeDasharray="4 4" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
