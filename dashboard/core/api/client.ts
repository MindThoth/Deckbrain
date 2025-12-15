/**
 * API client for DeckBrain Core API
 */

import { config } from '../config';
import type {
  TripsListResponse,
  TripDetailResponse,
  TrackGeoJSON,
} from './types';

const API_URL = config.apiUrl;

/**
 * Fetch trips for a device
 */
export async function getTrips(
  deviceId: string,
  options?: {
    limit?: number;
    offset?: number;
  }
): Promise<TripsListResponse> {
  const params = new URLSearchParams({
    device_id: deviceId,
    ...(options?.limit && { limit: options.limit.toString() }),
    ...(options?.offset && { offset: options.offset.toString() }),
  });

  const response = await fetch(`${API_URL}/api/trips?${params}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch trips: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch trip details including tows
 */
export async function getTripDetail(tripId: number): Promise<TripDetailResponse> {
  const response = await fetch(`${API_URL}/api/trips/${tripId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch trip detail: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch trip track as GeoJSON
 */
export async function getTripTrack(
  tripId: number,
  includeTows: boolean = false
): Promise<TrackGeoJSON> {
  const params = new URLSearchParams({
    ...(includeTows && { include_tows: 'true' }),
  });
  
  const url = `${API_URL}/api/trips/${tripId}/track${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch trip track: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch tow track as GeoJSON
 */
export async function getTowTrack(
  tripId: number,
  towId: number
): Promise<TrackGeoJSON> {
  const response = await fetch(
    `${API_URL}/api/trips/${tripId}/tows/${towId}/track`
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch tow track: ${response.statusText}`);
  }
  
  return response.json();
}

