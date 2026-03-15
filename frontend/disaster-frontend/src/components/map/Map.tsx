"use client";

import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { useEffect, useState } from "react";
import L from "leaflet";

// Standard Leaflet CSS is all we need
import "leaflet/dist/leaflet.css";

// Fix for the markers using CDN links to bypass Turbopack pathing issues
const DefaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Apply the icon fix globally
L.Marker.prototype.options.icon = DefaultIcon;

function MapController({ regions, selectedId }: any) {
  const map = useMap();

  useEffect(() => {
    if (selectedId) {
      const region = regions.find((r: any) => r.id === selectedId);
      if (region && region.latitude && region.longitude) {
        map.flyTo([region.latitude, region.longitude], 10, {
          duration: 1.5,
        });
      }
    }
  }, [selectedId, regions, map]);

  return null;
}

export default function Map({ regions, selectedId }: any) {
  // We use a small state to ensure Leaflet only initializes in the browser
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return <div className="absolute inset-0 bg-slate-900 animate-pulse" />;
  }

  return (
    <div className="absolute inset-0 z-0 bg-slate-900">
      <MapContainer
        center={[22.5937, 78.9629]}
        zoom={5}
        style={{ width: "100%", height: "100%" }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapController regions={regions} selectedId={selectedId} />

        {regions.map((region: any) => (
          <Marker key={region.id} position={[region.latitude, region.longitude]}>
            <Popup>
              <div className="p-1">
                <div className="font-bold text-slate-900">{region.name}</div>
                <div className="text-xs text-slate-500 font-medium">{region.admin_level}</div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}