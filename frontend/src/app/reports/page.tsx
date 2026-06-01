"use client";

import { useEffect, useState } from "react";
import { Download, FileText } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";

type Report = { id: number; title: string; type: string; created_at: string };

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<Report[]>([]);
  const [generating, setGenerating] = useState(false);

  const token = getToken();

  function load() {
    if (!token) return;
    api<Report[]>("/api/v1/reports", {}, token).then(setReports).catch(() => {});
  }

  useEffect(() => {
    if (!token) router.push("/login");
    else load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, token]);

  async function generate() {
    if (!token) return;
    setGenerating(true);
    try {
      await api("/api/v1/reports/generate", { method: "POST" }, token);
      load();
    } finally {
      setGenerating(false);
    }
  }

  return (
    <AppShell title="Health Intelligence Reports">
      <div className="mb-6 flex justify-between">
        <p className="text-slate-500">Automated PDF reports with outbreak statistics and risk summaries.</p>
        <Button onClick={generate} disabled={generating}>
          <FileText className="mr-2 h-4 w-4" />
          {generating ? "Generating..." : "Generate Report"}
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {reports.map((r) => (
          <Card key={r.id}>
            <CardHeader>
              <CardTitle className="text-base">{r.title}</CardTitle>
              <p className="text-xs text-slate-500">{new Date(r.created_at).toLocaleString()}</p>
            </CardHeader>
            <CardContent>
              <a
                href="#"
                onClick={async (e) => {
                  e.preventDefault();
                  const token = getToken();
                  if (!token) return;
                  const res = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/reports/${r.id}/download`,
                    { headers: { Authorization: `Bearer ${token}` } }
                  );
                  const blob = await res.blob();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `${r.title}.pdf`;
                  a.click();
                }}
                className="inline-flex items-center gap-2 text-sm text-blue-600 cursor-pointer"
              >
                <Download className="h-4 w-4" /> Download PDF
              </a>
            </CardContent>
          </Card>
        ))}
        {!reports.length && (
          <Card className="col-span-2 p-12 text-center text-slate-500">
            No reports yet. Generate your first intelligence report.
          </Card>
        )}
      </div>
    </AppShell>
  );
}
