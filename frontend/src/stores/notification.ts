import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectAPI } from '@/api/project'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCommentCount = ref(0)
  const pollingTimer = ref<number | null>(null)

  async function refreshUnreadCount() {
    try {
      const res = await projectAPI.getUnreadCommentCount()
      unreadCommentCount.value = res.data?.unread_count ?? 0
    } catch (error: any) {
      unreadCommentCount.value = 0
      if (error?.response?.status === 401) {
        stopPolling()
      }
    }
  }

  function startPolling() {
    stopPolling()
    refreshUnreadCount()
    pollingTimer.value = window.setInterval(() => {
      refreshUnreadCount()
    }, 45000)
  }

  function stopPolling() {
    if (pollingTimer.value) {
      window.clearInterval(pollingTimer.value)
      pollingTimer.value = null
    }
  }

  function clear() {
    unreadCommentCount.value = 0
    stopPolling()
  }

  return {
    unreadCommentCount,
    refreshUnreadCount,
    startPolling,
    stopPolling,
    clear
  }
})
