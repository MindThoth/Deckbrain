'use client';

/**
 * Map component for displaying trip tracks
 * Uses Leaflet for map rendering
 */

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { TrackGeoJSON } from '@/core/api/types';

// Fix Leaflet icon paths in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface MapViewProps {
  trackData: TrackGeoJSON | null;
  className?: string;
}

export default function MapView({ trackData, className = '' }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const trackLayer = useRef<L.GeoJSON | null>(null);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || mapInstance.current) return;

    // Create map centered on northeast US coast (approximate fishing area)
    const map = L.map(mapContainer.current).setView([42.3, -70.5], 8);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    mapInstance.current = map;

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, []);

  // Update track data
  useEffect(() => {
    if (!mapInstance.current || !trackData) return;

    const map = mapInstance.current;

    // Remove existing track layer
    if (trackLayer.current) {
      map.removeLayer(trackLayer.current);
      trackLayer.current = null;
    }

    // Add new track layer
    const geoJsonLayer = L.geoJSON(trackData as any, {
      style: (feature) => {
        // Style track lines
        if (feature?.geometry?.type === 'LineString') {
          return {
            color: feature?.properties?.type === 'tow' ? '#f59e0b' : '#0ea5e9',
            weight: feature?.properties?.type === 'tow' ? 4 : 3,
            opacity: 0.8,
          };
        }
        return {};
      },
      onEachFeature: (feature, layer) => {
        // Add popup with trip/tow info
        if (feature.properties) {
          const props = feature.properties;
          let popupContent = `<div class="p-2">`;
          
          if (props.type === 'track') {
            popupContent += `<strong>Trip Track</strong><br/>`;
            if (props.start_time) {
              popupContent += `Start: ${new Date(props.start_time).toLocaleString()}<br/>`;
            }
            if (props.end_time) {
              popupContent += `End: ${new Date(props.end_time).toLocaleString()}<br/>`;
            }
            if (props.points_count) {
              popupContent += `Points: ${props.points_count}<br/>`;
            }
          } else if (props.type === 'tow') {
            popupContent += `<strong>Tow ${props.tow_number || props.tow_id}</strong><br/>`;
            if (props.name) {
              popupContent += `${props.name}<br/>`;
            }
            if (props.avg_depth_m) {
              popupContent += `Avg Depth: ${props.avg_depth_m.toFixed(1)}m<br/>`;
            }
            if (props.duration_hours) {
              popupContent += `Duration: ${props.duration_hours.toFixed(1)}h<br/>`;
            }
          }
          
          popupContent += `</div>`;
          layer.bindPopup(popupContent);
        }

        // Add markers for start/end points
        if (feature.geometry?.type === 'LineString' && feature.properties?.type === 'track') {
          const coords = feature.geometry.coordinates;
          if (coords.length > 0) {
            // Start marker (green)
            L.circleMarker([coords[0][1], coords[0][0]], {
              radius: 6,
              fillColor: '#10b981',
              color: '#fff',
              weight: 2,
              opacity: 1,
              fillOpacity: 0.8,
            }).addTo(map).bindPopup('<strong>Trip Start</strong>');

            // End marker (red)
            const lastIdx = coords.length - 1;
            L.circleMarker([coords[lastIdx][1], coords[lastIdx][0]], {
              radius: 6,
              fillColor: '#ef4444',
              color: '#fff',
              weight: 2,
              opacity: 1,
              fillOpacity: 0.8,
            }).addTo(map).bindPopup('<strong>Trip End</strong>');
          }
        }
      },
    }).addTo(map);

    trackLayer.current = geoJsonLayer;

    // Fit map bounds to track
    const bounds = geoJsonLayer.getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [trackData]);

  return (
    <div 
      ref={mapContainer} 
      className={`w-full h-full ${className}`}
      style={{ minHeight: '400px' }}
    />
  );
}

