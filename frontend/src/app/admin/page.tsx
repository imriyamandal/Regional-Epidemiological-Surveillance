"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function AdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<{ email: string; full_name: string; role: string }[]>([]);
  const [datasets, setDatasets] = useState<Record<string, unknown> | null>(null);
  const [models, setModels] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) return router.push("/login");
    Promise.all([
      api<{ email: string; full_name: string; role: string }[]>("/api/v1/admin/users", {}, token),
      api<Record<string, unknown>>("/api/v1/admin/datasets/stats", {}, token),
      api<Record<string, unknown>[]>("/api/v1/admin/models", {}, token),
    ])
      .then(([u, d, m]) => {
        setUsers(u);
        setDatasets(d);
        setModels(m);
      })
      .catch(() => router.push("/login"));
  }, [router]);

  return (
    <AppShell title="Admin Panel">
      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>Users</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            {users.map((u) => (
              <div key={u.email} className="flex justify-between border-b py-2 dark:border-slate-800">
                <span>{u.full_name}</span>
                <span className="text-slate-500">{u.role}</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Datasets</CardTitle></CardHeader>
          <CardContent className="text-sm space-y-2">
            {datasets && Object.entries(datasets).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="capitalize">{k.replace(/_/g, " ")}</span>
                <span className="font-semibold">{String(v)}</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Models</CardTitle></CardHeader>
          <CardContent className="text-sm">
            {models.length ? (
              <p>{models.length} registered models in MLflow registry.</p>
            ) : (
              <p className="text-slate-500">Run ML training pipeline to register models.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
