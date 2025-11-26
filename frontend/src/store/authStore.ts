/**
 * Authentication state management with Zustand
 */

import { create } from 'zustand';
import { User } from '@/types/api';
import { authAPI } from '@/lib/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  isInitialized: true,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.login(email, password);
      const { access_token, refresh_token } = response.data;

      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Fetch user data
      const userResponse = await authAPI.getCurrentUser();
      set({
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
        isInitialized: true,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
        isInitialized: true,
      });
      throw error;
    }
  },

  register: async (email, password, fullName) => {
    set({ isLoading: true, error: null });
    try {
      await authAPI.register({ email, password, full_name: fullName });

      // Auto-login after registration (login will set isInitialized)
      await useAuthStore.getState().login(email, password);
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
        isInitialized: true,
      });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false, isInitialized: true });
  },

  fetchCurrentUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, isLoading: false, isInitialized: true });
      return;
    }

    set({ isLoading: true });
    try {
      const response = await authAPI.getCurrentUser();
      set({
        user: response.data,
        isAuthenticated: true,
        isLoading: false,
        isInitialized: true,
      });
    } catch (error) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isInitialized: true,
      });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  clearError: () => set({ error: null }),
}));
