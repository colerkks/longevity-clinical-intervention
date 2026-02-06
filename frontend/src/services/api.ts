import axios from 'axios';
import type { Intervention, Evidence, Recommendation, InterventionWithScores } from '@/types';

const API_BASE = '/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// ==================== Interventions ====================

export const interventionsApi = {
  list: (params?: { skip?: number; limit?: number; category?: string }) =>
    api.get<Intervention[]>('/interventions', { params }),

  get: (id: number) =>
    api.get<Intervention>(`/interventions/${id}`),

  create: (data: Partial<Intervention>) =>
    api.post<Intervention>('/interventions', data),

  update: (id: number, data: Partial<Intervention>) =>
    api.put<Intervention>(`/interventions/${id}`, data),

  delete: (id: number) =>
    api.delete(`/interventions/${id}`),

  search: (query: string) =>
    api.get<Intervention[]>(`/interventions/search/by-name?query=${query}`),

  getByEvidenceLevel: (level: number) =>
    api.get<Intervention[]>(`/interventions/by-evidence-level/${level}`),
};

// ==================== Evidence ====================

export const evidenceApi = {
  list: (interventionId: number, params?: { skip?: number; limit?: number }) =>
    api.get<Evidence[]>(`/evidence/intervention/${interventionId}`, { params }),

  get: (id: number) =>
    api.get<Evidence>(`/evidence/${id}`),

  create: (data: Partial<Evidence>) =>
    api.post<Evidence>('/evidence', data),

  getByQuality: (minQuality: number) =>
    api.get<Evidence[]>(`/evidence/by-quality?min_quality=${minQuality}`),

  getMetaAnalyses: () =>
    api.get<Evidence[]>('/evidence/meta-analyses'),

  getRandomizedTrials: () =>
    api.get<Evidence[]>('/evidence/randomized-trials'),
};

// ==================== Recommendations ====================

export const recommendationsApi = {
  create: (data: Partial<Recommendation>) =>
    api.post<Recommendation>('/recommendations', data),

  getUser: (userId: string, params?: { skip?: number; limit?: number }) =>
    api.get<Recommendation[]>(`/recommendations/user/${userId}`, { params }),

  get: (id: number) =>
    api.get<Recommendation>(`/recommendations/${id}`),

  getTopInterventions: (limit = 10) =>
    api.get<InterventionWithScores[]>(`/recommendations/top-interventions?limit=${limit}`),
};
