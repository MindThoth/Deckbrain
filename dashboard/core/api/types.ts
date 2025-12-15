/**
 * TypeScript types for Core API responses
 */

export interface Trip {
  id: number;
  device_id: number;
  start_time: string;
  end_time: string | null;
  name: string | null;
  distance_nm: number | null;
  duration_hours: number | null;
  bounds: {
    min_lat: number;
    max_lat: number;
    min_lon: number;
    max_lon: number;
  } | null;
  created_at: string;
}

export interface Tow {
  id: number;
  tow_number: number | null;
  name: string | null;
  start_time: string;
  end_time: string | null;
  distance_nm: number | null;
  duration_hours: number | null;
  avg_depth_m: number | null;
  min_depth_m: number | null;
  max_depth_m: number | null;
}

export interface TripDetail extends Trip {
  tows: Tow[];
}

export interface TripsListResponse {
  trips: Trip[];
  total: number;
  device_id: string;
}

export interface TripDetailResponse {
  trip: TripDetail;
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'LineString';
    coordinates: [number, number][]; // [lon, lat]
  };
  properties: {
    type: string;
    start_time?: string;
    end_time?: string;
    points_count?: number;
    points?: Array<{
      timestamp: string;
      depth: number;
      latitude: number;
      longitude: number;
      speed_knots?: number | null;
      course_deg?: number | null;
      water_temp?: number | null;
    }>;
    // Tow properties
    tow_id?: number;
    tow_number?: number | null;
    name?: string | null;
    distance_nm?: number | null;
    duration_hours?: number | null;
    avg_depth_m?: number | null;
    min_depth_m?: number | null;
    max_depth_m?: number | null;
  };
}

export interface TrackGeoJSON {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

