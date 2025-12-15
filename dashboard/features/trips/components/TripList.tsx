'use client';

/**
 * Trip list sidebar component
 */

import { useEffect, useState } from 'react';
import { format } from 'date-fns';
import { getTrips } from '@/core/api/client';
import type { Trip } from '@/core/api/types';
import { config } from '@/core/config';

interface TripListProps {
  onTripSelect: (trip: Trip) => void;
  selectedTripId: number | null;
}

export default function TripList({ onTripSelect, selectedTripId }: TripListProps) {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchTrips() {
      try {
        setLoading(true);
        setError(null);
        const data = await getTrips(config.defaultDeviceId);
        setTrips(data.trips);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load trips');
        console.error('Error fetching trips:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchTrips();
  }, []);

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-nautical-200 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm font-medium">Error loading trips</p>
          <p className="text-red-600 text-xs mt-1">{error}</p>
          <p className="text-red-500 text-xs mt-2">
            Make sure the Core API is running at {config.apiUrl}
          </p>
        </div>
      </div>
    );
  }

  if (trips.length === 0) {
    return (
      <div className="p-4">
        <div className="bg-nautical-100 border border-nautical-200 rounded-lg p-4">
          <p className="text-nautical-600 text-sm">No trips found</p>
          <p className="text-nautical-500 text-xs mt-1">
            Run the seed script to create mock trips
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-lg font-semibold text-nautical-900 mb-4">Trips</h2>
      
      {trips.map((trip) => (
        <button
          key={trip.id}
          onClick={() => onTripSelect(trip)}
          className={`
            w-full text-left p-4 rounded-lg border-2 transition-all
            ${
              selectedTripId === trip.id
                ? 'border-ocean-500 bg-ocean-50 shadow-md'
                : 'border-nautical-200 bg-white hover:border-ocean-300 hover:shadow'
            }
          `}
        >
          <div className="font-medium text-nautical-900 mb-1">
            {trip.name || `Trip ${trip.id}`}
          </div>
          
          <div className="text-xs text-nautical-600 space-y-1">
            {trip.start_time && (
              <div>
                {format(new Date(trip.start_time), 'MMM d, yyyy h:mm a')}
              </div>
            )}
            
            <div className="flex gap-4">
              {trip.duration_hours !== null && (
                <span>⏱ {trip.duration_hours.toFixed(1)}h</span>
              )}
              {trip.distance_nm !== null && (
                <span>📏 {trip.distance_nm.toFixed(1)} nm</span>
              )}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

