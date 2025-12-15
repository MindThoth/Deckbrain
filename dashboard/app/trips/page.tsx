'use client';

/**
 * Trips page - Main dashboard view
 * Displays trip list sidebar and map with track visualization
 */

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import TripList from '@/features/trips/components/TripList';
import type { Trip, TrackGeoJSON } from '@/core/api/types';
import { getTripTrack } from '@/core/api/client';

// Import MapView dynamically to avoid SSR issues with Leaflet
const MapView = dynamic(
  () => import('@/features/trips/components/MapView'),
  { ssr: false }
);

export default function TripsPage() {
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);
  const [trackData, setTrackData] = useState<TrackGeoJSON | null>(null);
  const [loadingTrack, setLoadingTrack] = useState(false);
  const [trackError, setTrackError] = useState<string | null>(null);

  // Fetch track data when trip is selected
  useEffect(() => {
    async function fetchTrack() {
      if (!selectedTrip) {
        setTrackData(null);
        return;
      }

      try {
        setLoadingTrack(true);
        setTrackError(null);
        const data = await getTripTrack(selectedTrip.id, true);
        setTrackData(data);
      } catch (err) {
        setTrackError(err instanceof Error ? err.message : 'Failed to load track');
        console.error('Error fetching track:', err);
      } finally {
        setLoadingTrack(false);
      }
    }

    fetchTrack();
  }, [selectedTrip]);

  return (
    <div className="flex h-screen bg-nautical-50">
      {/* Sidebar */}
      <div className="w-96 bg-white border-r border-nautical-200 overflow-y-auto flex-shrink-0">
        <div className="p-4 border-b border-nautical-200 bg-ocean-600">
          <h1 className="text-xl font-bold text-white">DeckBrain</h1>
          <p className="text-ocean-100 text-sm">Trip Dashboard</p>
        </div>
        
        <TripList
          onTripSelect={setSelectedTrip}
          selectedTripId={selectedTrip?.id || null}
        />
      </div>

      {/* Map Area */}
      <div className="flex-1 relative">
        {loadingTrack && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-white shadow-lg rounded-lg px-4 py-2">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-ocean-600" />
              <span className="text-sm text-nautical-700">Loading track...</span>
            </div>
          </div>
        )}

        {trackError && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-red-50 border border-red-200 shadow-lg rounded-lg px-4 py-2">
            <p className="text-sm text-red-800">{trackError}</p>
          </div>
        )}

        {selectedTrip && (
          <div className="absolute top-4 right-4 z-[1000] bg-white shadow-lg rounded-lg px-4 py-3">
            <div className="font-medium text-nautical-900">
              {selectedTrip.name || `Trip ${selectedTrip.id}`}
            </div>
            <div className="text-xs text-nautical-600 mt-1 space-y-1">
              {selectedTrip.duration_hours && (
                <div>Duration: {selectedTrip.duration_hours.toFixed(1)} hours</div>
              )}
              {selectedTrip.distance_nm && (
                <div>Distance: {selectedTrip.distance_nm.toFixed(1)} nautical miles</div>
              )}
            </div>
          </div>
        )}

        {!selectedTrip && (
          <div className="absolute inset-0 flex items-center justify-center z-[999] bg-nautical-50/80">
            <div className="text-center">
              <div className="text-6xl mb-4">🗺️</div>
              <h2 className="text-2xl font-semibold text-nautical-800 mb-2">
                Welcome to DeckBrain
              </h2>
              <p className="text-nautical-600">
                Select a trip from the sidebar to view track data
              </p>
            </div>
          </div>
        )}

        <MapView trackData={trackData} className="h-full" />
      </div>
    </div>
  );
}

