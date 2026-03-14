"use client";
import { useState, useEffect } from "react";

export function Sidebar({ regions, selectedId, onSelect }: any) {
  const [riskData, setRiskData] = useState<any>(null);

  // Fetch AI Risk scores whenever a new region is clicked
  useEffect(() => {
    if (selectedId) {
      fetch(`http://localhost:8000/api/risk/${selectedId}`)
        .then((res) => res.json())
        .then((data) => setRiskData(data));
    }
  }, [selectedId]);

  return (
    <div className="p-6 h-full flex flex-col">
      <h1 className="text-2xl font-bold text-slate-800 mb-6">Disaster Dashboard</h1>
      
      <div className="space-y-4 overflow-y-auto flex-1">
        {regions.map((region: any) => (
          <div
            key={region.id}
            onClick={() => onSelect(region.id)}
            className={`p-4 rounded-lg border cursor-pointer transition ${
              selectedId === region.id ? "bg-blue-50 border-blue-500 shadow-md" : "hover:bg-slate-50"
            }`}
          >
            <p className="font-semibold">{region.name}</p>
            <p className="text-xs text-slate-500 uppercase">{region.admin_level}</p>
          </div>
        ))}
      </div>

      {riskData && (
        <div className="mt-6 p-4 bg-slate-900 text-white rounded-xl shadow-inner">
          <h3 className="text-sm font-semibold text-slate-400 mb-3">AI RISK ANALYSIS</h3>
          <div className="flex justify-between items-center mb-2">
            <span>Heatwave (Transformer)</span>
            <span className={`font-bold ${riskData.heatwave_score > 80 ? "text-red-400" : "text-green-400"}`}>
              {riskData.heatwave_score}%
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span>Flood (BiLSTM)</span>
            <span className="text-blue-400 font-bold">{riskData.flood_score}%</span>
          </div>
        </div>
      )}
    </div>
  );
}