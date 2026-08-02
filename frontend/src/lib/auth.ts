/**
 * AttritionIQ — Auth Utilities & Role Guards
 */

import { useAuthStore } from '@/store/authStore'

export function hasRole(requiredRoles: string[]): boolean {
  const { user } = useAuthStore.getState()
  if (!user) return false
  return requiredRoles.includes(user.role)
}

export function isAdmin(): boolean {
  return hasRole(['admin'])
}

export function isHRManager(): boolean {
  return hasRole(['admin', 'hr_manager'])
}

export function isHRAnalyst(): boolean {
  return hasRole(['admin', 'hr_manager', 'hr_analyst'])
}
