"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

// Simple Sidebar Component defined inside for now to avoid import errors
function Sidebar({ regions, selectedId, onSelect }: any) {
  return (
    <div className="p-6 h-full flex flex-col bg-white">
      <h1 className="text-2xl font-bold text-slate-800 mb-6">Disaster Dashboard</h1>
      <div className="space-y-2">
        {regions.length === 0 && <p className="text-slate-400 italic">No regions found. Check FastAPI!</p>}
        {regions.map((region: any) => (
          <div
            key={region.id}
            onClick={() => onSelect(region.id)}
            className={`p-3 rounded border cursor-pointer ${
              selectedId === region.id ? "bg-blue-600 text-white" : "bg-slate-50 text-slate-700"
            }`}
          >
            {region.name}
          </div>
        ))}
      </div>
    </div>
  );
}

const DisasterMap = dynamic(() => import("@/components/map/Map"), {
  ssr: false,
  loading: () => <div className="h-full w-full bg-slate-200 animate-pulse flex items-center justify-center">Loading Map...</div>,
});

export default function Home() {
  const [regions, setRegions] = useState([]);
  const [selectedRegionId, setSelectedRegionId] = useState<number | null>(null);

useEffect(() => {
  fetch("http://127.0.0.1:8000/api/regions") // Changed localhost to 127.0.0.1
    .then((res) => res.json())
    .then((data) => setRegions(data))
    .catch(err => console.error("FastAPI Error:", err));
}, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <div className="w-[350px] h-full border-r z-20">
        <Sidebar regions={regions} selectedId={selectedRegionId} onSelect={setSelectedRegionId} />
      </div>
      <div className="flex-1 h-full relative bg-slate-100">
        <DisasterMap regions={regions} selectedId={selectedRegionId} />
      </div>
    </div>
  );
}