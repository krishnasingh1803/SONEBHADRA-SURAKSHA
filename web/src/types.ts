export type UserRole = 'admin' | 'citizen';

export interface User {
  id: number;
  email: string;
  role: UserRole;
  full_name: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Cluster {
  cluster_id: number;
  n_accidents: number;
  killed: number;
  injured: number;
  score: number;
  centroid_lat: number;
  centroid_lon: number;
  radius_m: number;
  peak_time_bucket: string;
  peak_weekday: string;
  top_vehicle: string;
  label: string;
  rank_by_score: number;
  rank_by_count: number;
  recommended_action?: string;
}

export interface Accident {
  id: number;
  date: string;
  time: string;
  place_text: string;
  district: string;
  vehicle_types: string;
  injured: number;
  killed: number;
  source_url: string;
  source_name: string;
  lat: number;
  lon: number;
  geocode_quality: string;
  time_bucket: string;
  weekday: string;
  cluster_id: number;
}

export interface Stats {
  district: string;
  total_records: number;
  unique_accidents: number;
  total_killed: number;
  total_injured: number;
  total_casualties: number;
  total_clusters: number;
  peak_time_window: string;
  noise_share: number;
  geocoded_rate: number;
  accuracy_verified: string;
  source_scope: string;
}

export interface TopClusterBreakdown {
  cluster_id: number;
  label: string;
  rank: number;
  score: number;
  time_buckets: Record<string, number>;
}

export interface Patterns {
  time_bucket: Record<string, number>;
  weekday: Record<string, number>;
  vehicle_types: Record<string, number>;
  top_clusters_breakdown: TopClusterBreakdown[];
}

export interface CitizenReport {
  id: number;
  citizen_name: string;
  contact?: string;
  landmark: string;
  date: string;
  time?: string;
  hazard_type: string;
  vehicles?: string;
  severity: string;
  details?: string;
  lat: number;
  lon: number;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  reviewed_at?: string;
  reviewed_by?: string;
}
