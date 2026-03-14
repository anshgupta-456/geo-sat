"use client";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet-defaulticon-compatibility";
import { useEffect } from "react";

// Helper to auto-center map when a region is selected in sidebar
function RecenterMap({ lat, lon }: { lat: number, lon: number }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lon) map.setView([lat, lon], 10);
  }, [lat, lon, map]);
  return null;
}

export default function Map({ regions, selectedId }: any) {
  const selectedRegion = regions.find((r: any) => r.id === selectedId);

  return (
    <MapContainer
      center={[28.6139, 77.209]} // Default to Delhi
      zoom={5}
      className="h-full w-full"
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      
      {regions.map((region: any) => {
        // Extract lat/lon from your WKT or SRID string if necessary
        // Assuming your API returns region.latitude and region.longitude
        return (
          <Marker key={region.id} position={[region.latitude || 28.6, region.longitude || 77.2]}>
            <Popup>
              <strong>{region.name}</strong> <br />
              Status: Monitoring Active
            </Popup>
          </Marker>
        );
      })}

      {selectedRegion && (
        <RecenterMap lat={selectedRegion.latitude} lon={selectedRegion.longitude} />
      )}
    </MapContainer>
  );
}