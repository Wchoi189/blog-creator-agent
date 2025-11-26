/**
 * Custom hook for authentication
 */

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';

export function useAuth(requireAuth: boolean = true) {
  const { user, isAuthenticated, isLoading, fetchCurrentUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  useEffect(() => {
    if (!isLoading && requireAuth && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, requireAuth, router]);

  return { user, isAuthenticated, isLoading };
}
