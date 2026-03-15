"use client";

import { Activity, MapPin, ThermometerSun, Droplets, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";
import dynamic from 'next/dynamic';

// FIXED: Uncommented the dynamic import so Next.js can load the Leaflet map
const Map = dynamic(() => import('../components/map/Map'), { 
  ssr: false,
  loading: () => <div className="h-full w-full bg-slate-900 animate-pulse" /> 
});

function Sidebar({ regions, selectedId, onSelect }: any) {
  const [riskData, setRiskData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedId) {
      setLoading(true);
      fetch(`http://127.0.0.1:8000/api/risk/${selectedId}`)
        .then((res) => res.json())
        .then((data) => {
          setRiskData(data);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [selectedId]);

  return (
    <div className="w-96 shrink-0 h-full bg-slate-950 border-r border-slate-800 flex flex-col shadow-[10px_0_30px_rgba(0,0,0,0.5)] z-20 relative">
      
      {/* Header */}
      <div className="p-6 border-b border-slate-800 bg-slate-950 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600/20 rounded-lg">
            <Activity className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">GeoSat Engine</h1>
            <p className="text-xs text-slate-400 font-medium tracking-wider uppercase">Disaster Intelligence</p>
          </div>
        </div>
      </div>

      {/* Region List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-950 custom-scrollbar">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 px-2">Monitoring Zones</h3>
        {regions.map((region: any) => (
          <div
            key={region.id}
            onClick={() => onSelect(region.id)}
            className={`group relative p-4 rounded-xl border cursor-pointer transition-all duration-300 overflow-hidden ${
              selectedId === region.id 
                ? "bg-blue-900/20 border-blue-500/50" 
                : "bg-slate-900/40 border-slate-800 hover:bg-slate-800/80 hover:border-slate-700"
            }`}
          >
            {selectedId === region.id && (
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]" />
            )}
            <div className="flex items-center gap-3 relative z-10">
              <MapPin className={`w-5 h-5 transition-colors ${selectedId === region.id ? "text-blue-400" : "text-slate-500 group-hover:text-slate-400"}`} />
              <div>
                <div className={`font-semibold transition-colors ${selectedId === region.id ? "text-white" : "text-slate-300"}`}>
                  {region.name}
                </div>
                <div className="text-xs text-slate-500 mt-0.5">{region.admin_level}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI Analytics Panel */}
      <div className="p-6 bg-[#0B1121] border-t border-slate-800 shrink-0 shadow-[0_-10px_30px_rgba(0,0,0,0.5)] relative z-30">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            Live AI Risk Analysis
          </h3>
          {loading && <span className="flex h-3 w-3 relative"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span></span>}
        </div>

        {!selectedId ? (
          <div className="text-center py-6 border border-dashed border-slate-700 rounded-lg">
            <p className="text-sm text-slate-500">Select a region to run inference</p>
          </div>
        ) : riskData ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm w-full pr-1">
                <span className="text-slate-300 flex items-center gap-2">
                  <ThermometerSun className="w-4 h-4 text-amber-500" />
                  Heatwave Model
                </span>
                <span className={`font-mono font-bold ${riskData.heatwave_score > 80 ? 'text-rose-400' : 'text-amber-400'}`}>
                  {riskData.heatwave_score}%
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-slate-700">
                <div className="h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r from-amber-500 to-rose-500" style={{ width: `${riskData.heatwave_score}%` }} />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm w-full pr-1">
                <span className="text-slate-300 flex items-center gap-2">
                  <Droplets className="w-4 h-4 text-cyan-500" />
                  Flood Model
                </span>
                <span className={`font-mono font-bold ${riskData.flood_score > 80 ? 'text-rose-400' : 'text-cyan-400'}`}>
                  {riskData.flood_score}%
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-slate-700">
                <div className="h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r from-blue-500 to-cyan-400" style={{ width: `${riskData.flood_score}%` }} />
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function Home() {
  const [regions, setRegions] = useState([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/regions")
      .then((res) => res.json())
      .then((data) => setRegions(data))
      .catch((err) => console.error("Failed to load regions:", err));
  }, []);

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-slate-950">
      <Sidebar regions={regions} selectedId={selectedId} onSelect={setSelectedId} />
      <div className="flex-1 relative bg-slate-900">
         <Map regions={regions} selectedId={selectedId} />
      </div>
    </main>
  );
}