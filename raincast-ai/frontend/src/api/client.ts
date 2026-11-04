import axios from 'axios';
import type {
  ForecastSummary,
  RainfallForecast,
  LocationResult,
  LocationForecastResponse,
  ModelComparisonResponse,
  RainfallCategory,
  IndiaRegion,
  HealthStatus,
  LatestCycleInfo,
  ForecastModel,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Health ───────────────────────────────────────────────────────────────────

export const fetchHealth = async (): Promise<HealthStatus> => {
  const { data } = await api.get<HealthStatus>('/health');
  return data;
};

// ─── Forecasts ────────────────────────────────────────────────────────────────

export const fetchForecastSummary = async (model: ForecastModel): Promise<ForecastSummary> => {
  const { data } = await api.get<ForecastSummary>('/forecasts/summary', { params: { model } });
  return data;
};

export const fetchLatestCycle = async (model: ForecastModel): Promise<LatestCycleInfo> => {
  const { data } = await api.get<LatestCycleInfo>('/forecasts/latest-cycle', { params: { model } });
  return data;
};

export const fetchAvailableSteps = async (
  model: ForecastModel,
  cycle: number,
  maxStep: number = 72
): Promise<{ steps: number[]; count: number }> => {
  const { data } = await api.get('/forecasts/available-steps', {
    params: { model, cycle, max_step: maxStep },
  });
  return data;
};

export const fetchAvailableParameters = async (model: ForecastModel) => {
  const { data } = await api.get('/forecasts/available-parameters', { params: { model } });
  return data;
};

export const triggerDownload = async (
  model: ForecastModel,
  date?: string,
  cycle?: number,
  maxStep: number = 72
) => {
  const { data } = await api.post('/forecasts/download', null, {
    params: { model, date, cycle, max_step: maxStep },
  });
  return data;
};

export const fetchCachedForecasts = async () => {
  const { data } = await api.get('/forecasts/cache');
  return data;
};

// ─── Locations ────────────────────────────────────────────────────────────────

export const searchLocations = async (q: string, limit = 10): Promise<LocationResult[]> => {
  const { data } = await api.get<{ results: LocationResult[] }>('/locations/search', {
    params: { q, limit },
  });
  return data.results;
};

export const fetchIndiaStates = async (): Promise<string[]> => {
  const { data } = await api.get<{ states: string[] }>('/locations/states');
  return data.states;
};

export const fetchIndiaCities = async (state?: string): Promise<LocationResult[]> => {
  const { data } = await api.get<{ cities: LocationResult[] }>('/locations/cities', {
    params: state ? { state } : {},
  });
  return data.cities;
};

export const fetchLocationForecast = async (
  lat: number,
  lon: number,
  model: ForecastModel = 'ifs',
  maxStep: number = 72
): Promise<LocationForecastResponse> => {
  const { data } = await api.get<LocationForecastResponse>('/locations/forecast', {
    params: { lat, lon, model, max_step: maxStep },
  });
  return data;
};

export const getLocationForecastCsvUrl = (
  lat: number,
  lon: number,
  model: ForecastModel,
  locationName?: string
): string => {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    model,
    ...(locationName ? { location_name: locationName } : {}),
  });
  return `${BASE_URL}/locations/forecast/csv?${params}`;
};

// ─── Comparison ───────────────────────────────────────────────────────────────

export const fetchModelComparison = async (
  lat: number,
  lon: number,
  maxStep: number = 72
): Promise<ModelComparisonResponse> => {
  const { data } = await api.get<ModelComparisonResponse>('/comparison/', {
    params: { lat, lon, max_step: maxStep },
  });
  return data;
};

export const fetchModelInfo = async () => {
  const { data } = await api.get('/comparison/info');
  return data;
};

// ─── Analytics ────────────────────────────────────────────────────────────────

export const fetchRainfallCategories = async (): Promise<{ categories: RainfallCategory[] }> => {
  const { data } = await api.get<{ categories: RainfallCategory[] }>('/analytics/rainfall-categories');
  return data;
};

export const fetchIndiaRegions = async (): Promise<{ regions: IndiaRegion[] }> => {
  const { data } = await api.get<{ regions: IndiaRegion[] }>('/analytics/india-regions');
  return data;
};

export default api;
