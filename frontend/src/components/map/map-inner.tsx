"use client";

import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { Hotspot } from "./outbreak-map";
import { useEffect } from "react";

function FitIndia({ hotspots }: { hotspots: Hotspot[] }) {
  const map = useMap();
  useEffect(() => {
    if (hotspots.length) {
      const lats = hotspots.map((h) => h.latitude);
      const lngs = hotspots.map((h) => h.longitude);
      map.fitBounds([
        [Math.min(...lats) - 1, Math.min(...lngs) - 1],
        [Math.max(...lats) + 1, Math.max(...lngs) + 1],
      ]);
    } else {
      map.setView([22.5, 78.9], 5);
    }
  }, [hotspots, map]);
  return null;
}

const riskColor: Record<string, string> = {
  safe: "#22c55e",
  low_risk: "#84cc16",
  medium_risk: "#eab308",
  high_risk: "#f97316",
  critical_risk: "#ef4444",
};

export default function MapInner({ hotspots }: { hotspots: Hotspot[] }) {
  return (
    <MapContainer center={[22.5, 78.9]} zoom={5} className="h-[500px] w-full rounded-xl z-0">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitIndia hotspots={hotspots} />
      {hotspots.map((h, i) => (
        <CircleMarker
          key={`${h.district}-${i}`}
          center={[h.latitude, h.longitude]}
          radius={8 + h.risk_score * 20}
          pathOptions={{
            color: riskColor[h.risk_level] || "#3b82f6",
            fillColor: riskColor[h.risk_level] || "#3b82f6",
            fillOpacity: 0.6,
          }}
        >
          <Popup>
            <div className="text-sm">
              <strong>{h.district}</strong>, {h.state}
              <br />
              {h.disease} — Risk: {(h.risk_score * 100).toFixed(0)}%
              <br />
              Cases: {h.case_count}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
