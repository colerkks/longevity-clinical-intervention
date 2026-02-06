import axios from 'axios';
import type { User, LoginRequest, RegisterRequest, Token, HealthProfile } from '@/types/user';

const API_BASE = '/api/v1';

export const authApi = {
  // 注册
  register: (data: RegisterRequest) =>
    api.post<User>('/auth/register', data),

  // 登录
  login: (data: LoginRequest) =>
    api.post<Token>('/auth/login', data),

  // 登出
  logout: (refreshToken: string) =>
    api.post('/auth/logout', { refresh_token: refreshToken }),

  // 刷新令牌
  refreshToken: (refreshToken: string) =>
    api.post<Token>('/auth/refresh', { refresh_token: refreshToken }),

  // 获取当前用户信息
  getCurrentUser: (token: string) =>
    api.get<User>('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    }),

  // 更新用户信息
  updateCurrentUser: (token: string, data: Partial<User>) =>
    api.put<User>('/auth/me', data, {
      headers: { Authorization: `Bearer ${token}` }
    }),

  // 创建健康档案
  createHealthProfile: (token: string, data: HealthProfile) =>
    api.post<HealthProfile>('/auth/health-profile', data, {
      headers: { Authorization: `Bearer ${token}` }
    }),

  // 更新健康档案
  updateHealthProfile: (token: string, data: HealthProfile) =>
    api.put<HealthProfile>('/auth/health-profile', data, {
      headers: { Authorization: `Bearer ${token}` }
    }),

  // 获取健康档案
  getHealthProfile: (token: string) =>
    api.get<HealthProfile>('/auth/health-profile', {
      headers: { Authorization: `Bearer ${token}` }
    }),
};
