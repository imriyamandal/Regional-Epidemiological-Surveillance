"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { OutbreakMap, type Hotspot } from "@/components/map/outbreak-map";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function MapPage() {
  const router = useRouter();
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [level, setLevel] = useState<"india" | "state" | "district">("india");

  useEffect(() => {
    const token = getToken();
    if (!token) return router.push("/login");
    api<Hotspot[]>("/api/v1/analytics/map/hotspots", {}, token).then(setHotspots).catch(() => {});
  }, [router]);

  return (
    <AppShell title="Geographic Outbreak Tracking">
      <div className="mb-4 flex gap-2">
        {(["india", "state", "district"] as const).map((l) => (
          <button
            key={l}
            onClick={() => setLevel(l)}
            className={`rounded-lg px-4 py-2 text-sm font-medium capitalize ${
              level === l ? "bg-blue-600 text-white" : "bg-slate-200 dark:bg-slate-800"
            }`}
          >
            {l} view
          </button>
        ))}
      </div>
      <Card>
        <CardHeader>
          <CardTitle>India Outbreak Heatmap</CardTitle>
          <p className="text-sm text-slate-500">{hotspots.length} active hotspots — Leaflet + OpenStreetMap</p>
        </CardHeader>
        <CardContent>
          <OutbreakMap hotspots={hotspots} />
        </CardContent>
      </Card>
    </AppShell>
  );
}
