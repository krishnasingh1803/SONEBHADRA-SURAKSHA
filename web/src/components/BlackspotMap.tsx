import React, { useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  Popup,
  useMap,
  useMapEvents,
} from 'react-leaflet';
import type { Cluster, Accident } from '../types';
import { ExternalLink } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

interface BlackspotMapProps {
  clusters?: Cluster[];
  accidents?: Accident[];
  selectedClusterId?: number | null;
  onSelectCluster?: (clusterId: number) => void;
  interactivePick?: boolean;
  onLocationPicked?: (lat: number, lon: number) => void;
  pickedLocation?: { lat: number; lon: number } | null;
  height?: string;
}

// Subcomponent to adjust map bounds to Sonbhadra district clusters
const BoundsAdjuster: React.FC<{ clusters?: Cluster[]; accidents?: Accident[] }> = ({
  clusters,
  accidents,
}) => {
  const map = useMap();

  useEffect(() => {
    const points: [number, number][] = [];

    if (clusters && clusters.length > 0) {
      clusters.forEach((c) => {
        if (c.centroid_lat && c.centroid_lon) {
          points.push([c.centroid_lat, c.centroid_lon]);
        }
      });
    } else if (accidents && accidents.length > 0) {
      accidents.forEach((a) => {
        if (a.lat && a.lon) {
          points.push([a.lat, a.lon]);
        }
      });
    }

    if (points.length > 0) {
      map.fitBounds(points, { padding: [40, 40], maxZoom: 14 });
    }
  }, [clusters, accidents, map]);

  return null;
};

// Subcomponent to handle map clicks for coordinate selection
const LocationPickerHandler: React.FC<{
  onLocationPicked?: (lat: number, lon: number) => void;
}> = ({ onLocationPicked }) => {
  useMapEvents({
    click(e) {
      if (onLocationPicked) {
        onLocationPicked(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
};

export const BlackspotMap: React.FC<BlackspotMapProps> = ({
  clusters = [],
  accidents = [],
  selectedClusterId = null,
  onSelectCluster,
  interactivePick = false,
  onLocationPicked,
  pickedLocation,
  height = '520px',
}) => {
  // Center of Sonbhadra District, UP (Robertsganj / Churk coordinates)
  const defaultCenter: [number, number] = [24.6052, 83.0548];

  const getColorByRank = (rank: number) => {
    if (rank <= 3) return '#D32F2F'; // Danger red
    if (rank <= 6) return '#F59E0B'; // Warning amber
    return '#007eb4'; // Institutional blue
  };

  const getRadiusByScore = (score: number) => {
    return Math.max(8, Math.min(22, 6 + Math.sqrt(score) * 2));
  };

  return (
    <div
      style={{ height }}
      className="w-full relative rounded-[4px] border border-[#DFE3E8] overflow-hidden bg-[#F4F6F8]"
    >
      <MapContainer
        center={defaultCenter}
        zoom={10}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        {/* Standard Light OpenStreetMap Tiles as required */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        <BoundsAdjuster clusters={clusters} accidents={accidents} />

        {interactivePick && <LocationPickerHandler onLocationPicked={onLocationPicked} />}

        {/* 1. Clustered Blackspots with circles */}
        {clusters.map((cluster) => {
          const rank = cluster.rank_by_score || 1;
          const markerColor = getColorByRank(rank);
          const isSelected = selectedClusterId === cluster.cluster_id;
          const markerRadius = getRadiusByScore(cluster.score);

          return (
            <React.Fragment key={`cluster-${cluster.cluster_id}`}>
              {/* Outer boundary radius representation */}
              <Circle
                center={[cluster.centroid_lat, cluster.centroid_lon]}
                radius={cluster.radius_m || 250}
                pathOptions={{
                  color: markerColor,
                  fillColor: markerColor,
                  fillOpacity: isSelected ? 0.25 : 0.12,
                  weight: isSelected ? 2.5 : 1.2,
                }}
                eventHandlers={{
                  click: () => onSelectCluster && onSelectCluster(cluster.cluster_id),
                }}
              />

              {/* Centroid Severity Marker */}
              <CircleMarker
                center={[cluster.centroid_lat, cluster.centroid_lon]}
                radius={markerRadius}
                pathOptions={{
                  color: '#FFFFFF',
                  fillColor: markerColor,
                  fillOpacity: 0.95,
                  weight: 2,
                }}
                eventHandlers={{
                  click: () => onSelectCluster && onSelectCluster(cluster.cluster_id),
                }}
              >
                <Popup>
                  <div className="p-1 space-y-2 text-[#1A1A1A] max-w-xs">
                    <div className="flex items-center justify-between border-b border-[#DFE3E8] pb-1.5 gap-2">
                      <span
                        className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-[2px] text-white"
                        style={{ backgroundColor: markerColor }}
                      >
                        Rank #{rank} Blackspot
                      </span>
                      <span className="text-xs font-semibold text-[#5B6770]">
                        Score: <strong>{cluster.score.toFixed(1)}</strong>
                      </span>
                    </div>

                    <h4 className="text-xs font-bold leading-tight text-[#1A1A1A]">
                      {cluster.label || `Cluster ${cluster.cluster_id}`}
                    </h4>

                    <div className="grid grid-cols-2 gap-2 text-[11px] bg-[#F4F6F8] p-2 rounded-[4px] border border-[#DFE3E8]">
                      <div>
                        <span className="text-[#5B6770] block">Incidents:</span>
                        <span className="font-bold text-[#1A1A1A]">{cluster.n_accidents}</span>
                      </div>
                      <div>
                        <span className="text-[#5B6770] block">Fatalities:</span>
                        <span className="font-bold text-[#D32F2F]">{cluster.killed}</span>
                      </div>
                      <div>
                        <span className="text-[#5B6770] block">Injuries:</span>
                        <span className="font-bold text-[#F59E0B]">{cluster.injured}</span>
                      </div>
                      <div>
                        <span className="text-[#5B6770] block">Peak Shift:</span>
                        <span className="font-bold text-[#007eb4] capitalize">
                          {cluster.peak_time_bucket}
                        </span>
                      </div>
                    </div>

                    <div className="text-[11px] text-[#5B6770]">
                      Primary Vehicle:{' '}
                      <strong className="text-[#1A1A1A] capitalize">{cluster.top_vehicle}</strong>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            </React.Fragment>
          );
        })}

        {/* 2. Individual Accident Dots (when viewing filtered raw incidents) */}
        {accidents.map((accident) => (
          <CircleMarker
            key={`acc-${accident.id}`}
            center={[accident.lat, accident.lon]}
            radius={4}
            pathOptions={{
              color: accident.killed > 0 ? '#D32F2F' : '#5B6770',
              fillColor: accident.killed > 0 ? '#D32F2F' : '#5B6770',
              fillOpacity: 0.8,
              weight: 1,
            }}
          >
            <Popup>
              <div className="p-1 space-y-1.5 text-[#1A1A1A] max-w-xs text-xs">
                <div className="font-bold text-[#1A1A1A]">{accident.place_text}</div>
                <div className="text-[11px] text-[#5B6770]">
                  Date: {accident.date} • {accident.time_bucket}
                </div>
                <div className="text-[11px]">
                  Casualties: <strong className="text-[#D32F2F]">{accident.killed} Killed</strong>,{' '}
                  <strong className="text-[#F59E0B]">{accident.injured} Injured</strong>
                </div>
                <div className="text-[11px] text-[#5B6770]">
                  Vehicles: <span className="capitalize">{accident.vehicle_types}</span>
                </div>
                {accident.source_url && (
                  <a
                    href={accident.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] text-[#007eb4] hover:underline flex items-center gap-1 pt-1 border-t border-[#DFE3E8]"
                  >
                    <span>View Media Source</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* 3. Picked Location Marker for Citizen Hazard Form */}
        {pickedLocation && (
          <CircleMarker
            center={[pickedLocation.lat, pickedLocation.lon]}
            radius={8}
            pathOptions={{
              color: '#005a82',
              fillColor: '#007eb4',
              fillOpacity: 1,
              weight: 3,
            }}
          >
            <Popup>
              <div className="text-xs p-1">
                <strong>Selected Coordinate:</strong>
                <div>
                  {pickedLocation.lat.toFixed(5)}, {pickedLocation.lon.toFixed(5)}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        )}
      </MapContainer>

      {/* Floating Map Legend */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-white/95 border border-[#DFE3E8] p-2.5 rounded-[4px] shadow-sm text-xs text-[#1A1A1A] space-y-1.5 backdrop-blur-xs">
        <div className="text-[10px] font-bold uppercase tracking-wider text-[#5B6770]">
          Blackspot Severity
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#D32F2F] flex-shrink-0" />
          <span>Ranks 1–3 (Critical Priority)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#F59E0B] flex-shrink-0" />
          <span>Ranks 4–6 (High Priority)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#007eb4] flex-shrink-0" />
          <span>Ranks 7+ (Medium Priority)</span>
        </div>
      </div>
    </div>
  );
};
