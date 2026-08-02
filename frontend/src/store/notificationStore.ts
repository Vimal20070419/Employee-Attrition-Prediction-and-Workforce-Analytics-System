import { create } from 'zustand'

export interface NotificationItem {
  id: string
  type: string
  title: string
  message: string
  read: boolean
  created_at: string
}

interface NotificationState {
  notifications: NotificationItem[]
  unreadCount: number
  setNotifications: (items: NotificationItem[]) => void
  markAsRead: (id: string) => void
  clearAll: () => void
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  unreadCount: 0,

  setNotifications: (items) => set({
    notifications: items,
    unreadCount: items.filter((n) => !n.read).length,
  }),

  markAsRead: (id) => set((state) => {
    const updated = state.notifications.map((n) => n.id === id ? { ...n, read: true } : n)
    return {
      notifications: updated,
      unreadCount: updated.filter((n) => !n.read).length,
    }
  }),

  clearAll: () => set({ notifications: [], unreadCount: 0 }),
}))
