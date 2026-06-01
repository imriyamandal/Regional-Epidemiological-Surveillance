"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

type Alert = {
  id: number;
  level: string;
  title: string;
  message: string;
  state: string;
  district: string;
  risk_score: number;
  is_read: boolean;
  created_at: string;
};

const LEVEL_STYLES: Record<string, string> = {
  green: "border-l-emerald-500 bg-emerald-50 dark:bg-emerald-950/30",
  yellow: "border-l-yellow-500 bg-yellow-50 dark:bg-yellow-950/30",
  orange: "border-l-orange-500 bg-orange-50 dark:bg-orange-950/30",
  red: "border-l-red-500 bg-red-50 dark:bg-red-950/30",
};

export default function AlertsPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) return router.push("/login");
    api<Alert[]>("/api/v1/alerts", {}, token).then(setAlerts).catch(() => {});
  }, [router]);

  return (
    <AppShell title="Smart Alert System">
      <div className="mb-4 flex gap-2 text-sm">
        {["green", "yellow", "orange", "red"].map((l) => (
          <span key={l} className={cn("rounded-full px-3 py-1 capitalize", LEVEL_STYLES[l])}>
            {l}
          </span>
        ))}
      </div>
      <div className="space-y-3">
        {alerts.map((a) => (
          <Card key={a.id} className={cn("border-l-4", LEVEL_STYLES[a.level])}>
            <CardContent className="p-4">
              <div className="flex justify-between">
                <h3 className="font-semibold">{a.title}</h3>
                <span className="text-xs text-slate-500">{new Date(a.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{a.message}</p>
              <p className="mt-2 text-xs text-slate-500">
                {a.district}, {a.state} — Risk {(a.risk_score * 100).toFixed(0)}%
              </p>
            </CardContent>
          </Card>
        ))}
        {!alerts.length && <p className="text-slate-500">No active alerts.</p>}
      </div>
    </AppShell>
  );
}
