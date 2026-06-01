"use client";

import dynamic from "next/dynamic";

export type Hotspot = {
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  case_count: number;
  risk_level: string;
  risk_score: number;
  disease: string;
};

const MapInner = dynamic(() => import("./map-inner"), { ssr: false, loading: () => (
  <div className="flex h-[500px] items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-900">
    <p className="text-slate-500">Loading map...</p>
  </div>
)});

export function OutbreakMap({ hotspots }: { hotspots: Hotspot[] }) {
  return <MapInner hotspots={hotspots} />;
}
