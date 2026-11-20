import type { Accident, CitizenReport, Cluster, LoginResponse, Patterns, Stats, User } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('suraksha_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function loginApi(email: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Authentication failed' }));
    throw new Error(err.detail || 'Login failed');
  }
  return res.json();
}

export async function getMeApi(): Promise<User> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch user profile');
  }
  return res.json();
}

export async function getClustersApi(): Promise<Cluster[]> {
  const res = await fetch(`${API_BASE}/clusters`);
  if (!res.ok) throw new Error('Failed to fetch clusters');
  return res.json();
}

export async function getAccidentsApi(params?: {
  start_date?: string;
  end_date?: string;
  time_bucket?: string;
  vehicle?: string;
  min_severity?: number;
}): Promise<Accident[]> {
  const query = new URLSearchParams();
  if (params?.start_date) query.set('start_date', params.start_date);
  if (params?.end_date) query.set('end_date', params.end_date);
  if (params?.time_bucket && params.time_bucket !== 'All') query.set('time_bucket', params.time_bucket);
  if (params?.vehicle && params.vehicle !== 'All') query.set('vehicle', params.vehicle);
  if (params?.min_severity) query.set('min_severity', params.min_severity.toString());

  const res = await fetch(`${API_BASE}/accidents?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch accidents');
  return res.json();
}

export async function getStatsApi(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function getPatternsApi(): Promise<Patterns> {
  const res = await fetch(`${API_BASE}/patterns`);
  if (!res.ok) throw new Error('Failed to fetch patterns');
  return res.json();
}

export async function submitReportApi(report: Partial<CitizenReport>): Promise<{ id: number; message: string }> {
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(report),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to submit report' }));
    throw new Error(err.detail || 'Failed to submit report');
  }
  return res.json();
}

export async function getAdminReportsApi(statusFilter?: string): Promise<CitizenReport[]> {
  const query = statusFilter ? `?status_filter=${statusFilter}` : '';
  const res = await fetch(`${API_BASE}/reports${query}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch reports');
  return res.json();
}

export async function updateReportStatusApi(
  id: number,
  status: 'approved' | 'rejected'
): Promise<{ id: number; status: string; message: string }> {
  const res = await fetch(`${API_BASE}/reports/${id}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to update report' }));
    throw new Error(err.detail || 'Failed to update report');
  }
  return res.json();
}
