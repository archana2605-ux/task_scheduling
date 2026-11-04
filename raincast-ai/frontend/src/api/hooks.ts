import { useQuery, useMutation } from '@tanstack/react-query';
import type { ForecastModel } from '../types';
import {
  fetchHealth,
  fetchForecastSummary,
  fetchLatestCycle,
  fetchAvailableSteps,
  fetchLocationForecast,
  searchLocations,
  fetchModelComparison,
  fetchRainfallCategories,
  fetchIndiaRegions,
  fetchModelInfo,
  triggerDownload,
  fetchCachedForecasts,
  fetchIndiaCities,
} from './client';

// Query keys
export const QUERY_KEYS = {
  health: ['health'],
  forecastSummary: (model: ForecastModel) => ['forecast-summary', model],
  latestCycle: (model: ForecastModel) => ['latest-cycle', model],
  availableSteps: (model: ForecastModel, cycle: number, maxStep: number) =>
    ['available-steps', model, cycle, maxStep],
  locationForecast: (lat: number, lon: number, model: ForecastModel, maxStep: number) =>
    ['location-forecast', lat, lon, model, maxStep],
  searchLocations: (q: string) => ['search-locations', q],
  modelComparison: (lat: number, lon: number, maxStep: number) =>
    ['model-comparison', lat, lon, maxStep],
  rainfallCategories: ['rainfall-categories'],
  indiaRegions: ['india-regions'],
  modelInfo: ['model-info'],
  cachedForecasts: ['cached-forecasts'],
  cities: (state?: string) => ['cities', state],
};

// ─── Health ───────────────────────────────────────────────────────────────────

export const useHealth = () =>
  useQuery({
    queryKey: QUERY_KEYS.health,
    queryFn: fetchHealth,
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

// ─── Forecasts ────────────────────────────────────────────────────────────────

export const useForecastSummary = (model: ForecastModel) =>
  useQuery({
    queryKey: QUERY_KEYS.forecastSummary(model),
    queryFn: () => fetchForecastSummary(model),
    refetchInterval: 5 * 60_000,
    staleTime: 2 * 60_000,
  });

export const useLatestCycle = (model: ForecastModel) =>
  useQuery({
    queryKey: QUERY_KEYS.latestCycle(model),
    queryFn: () => fetchLatestCycle(model),
    refetchInterval: 10 * 60_000,
    staleTime: 5 * 60_000,
  });

export const useAvailableSteps = (model: ForecastModel, cycle: number, maxStep = 72) =>
  useQuery({
    queryKey: QUERY_KEYS.availableSteps(model, cycle, maxStep),
    queryFn: () => fetchAvailableSteps(model, cycle, maxStep),
    staleTime: 60 * 60_000,
  });

export const useCachedForecasts = () =>
  useQuery({
    queryKey: QUERY_KEYS.cachedForecasts,
    queryFn: fetchCachedForecasts,
    staleTime: 60_000,
  });

export const useDownloadForecast = () =>
  useMutation({
    mutationFn: ({
      model,
      date,
      cycle,
      maxStep,
    }: {
      model: ForecastModel;
      date?: string;
      cycle?: number;
      maxStep?: number;
    }) => triggerDownload(model, date, cycle, maxStep),
  });

// ─── Locations ────────────────────────────────────────────────────────────────

export const useLocationSearch = (q: string) =>
  useQuery({
    queryKey: QUERY_KEYS.searchLocations(q),
    queryFn: () => searchLocations(q),
    enabled: q.length >= 2,
    staleTime: 10 * 60_000,
  });

export const useLocationForecast = (
  lat: number | null,
  lon: number | null,
  model: ForecastModel,
  maxStep = 72
) =>
  useQuery({
    queryKey: QUERY_KEYS.locationForecast(lat!, lon!, model, maxStep),
    queryFn: () => fetchLocationForecast(lat!, lon!, model, maxStep),
    enabled: lat !== null && lon !== null,
    staleTime: 10 * 60_000,
    retry: 1,
  });

export const useCities = (state?: string) =>
  useQuery({
    queryKey: QUERY_KEYS.cities(state),
    queryFn: () => fetchIndiaCities(state),
    staleTime: 60 * 60_000,
  });

// ─── Comparison ───────────────────────────────────────────────────────────────

export const useModelComparison = (lat: number, lon: number, maxStep = 72) =>
  useQuery({
    queryKey: QUERY_KEYS.modelComparison(lat, lon, maxStep),
    queryFn: () => fetchModelComparison(lat, lon, maxStep),
    enabled: !!(lat && lon),
    staleTime: 10 * 60_000,
    retry: 1,
  });

export const useModelInfo = () =>
  useQuery({
    queryKey: QUERY_KEYS.modelInfo,
    queryFn: fetchModelInfo,
    staleTime: Infinity,
  });

// ─── Analytics ────────────────────────────────────────────────────────────────

export const useRainfallCategories = () =>
  useQuery({
    queryKey: QUERY_KEYS.rainfallCategories,
    queryFn: fetchRainfallCategories,
    staleTime: Infinity,
  });

export const useIndiaRegions = () =>
  useQuery({
    queryKey: QUERY_KEYS.indiaRegions,
    queryFn: fetchIndiaRegions,
    staleTime: Infinity,
  });
