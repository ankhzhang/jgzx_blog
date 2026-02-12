import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import type {
  UserProfile,
  RegisterData,
  UpdateProfileData,
  ChangePasswordData
} from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  // ========== State ==========
  const user = ref<UserProfile | null>(null)
  const token = ref<string>('')
  const isLoading = ref<boolean>(false)

  // ========== Getters ==========
  const isAuthenticated = computed(() => !!token.value)
  const isStudent = computed(() => user.value?.identity === 'student')
  const isTeacher = computed(() => user.value?.identity === 'teacher')
  const isAdmin = computed(() => {
    // 管理员判断：可以从用户信息或本地存储判断
    // 暂时简单处理：教师身份且后端会返回管理员标记
    return user.value?.identity === 'teacher' || localStorage.getItem('isAdmin') === 'true'
  })
  const fullName = computed(() => user.value?.real_name || user.value?.username || '')

  // ========== Actions ==========
  /**
   * 从 localStorage 初始化认证状态
   */
  const initAuth = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')

    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('解析用户数据失败:', e)
        clearAuth()
      }
    }
  }

  /**
   * 登录
   */
  const login = async (credentials: { username: string; password: string }) => {
    isLoading.value = true
    try {
      const response = await authAPI.login(credentials)

      if (response.data.token && response.data.user) {
        token.value = response.data.token
        user.value = response.data.user

        // 保存到 localStorage
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        return { success: true, data: response.data }
      }
      return { success: false, error: '登录失败：响应数据不完整' }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || '登录失败'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 注册
   */
  const register = async (data: RegisterData) => {
    isLoading.value = true
    try {
      const response = await authAPI.register(data)

      if (response.data.token && response.data.user) {
        token.value = response.data.token
        user.value = response.data.user

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        return { success: true, data: response.data }
      }
      return { success: false, error: '注册失败：响应数据不完整' }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || '注册失败'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 登出
   */
  const logout = async () => {
    isLoading.value = true
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      clearAuth()
      isLoading.value = false
    }
  }

  /**
   * 获取用户资料
   */
  const fetchProfile = async () => {
    if (!token.value) return

    isLoading.value = true
    try {
      const response = await authAPI.getProfile()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true, data: response.data }
    } catch (error: any) {
      console.error('获取用户资料失败:', error)
      if (error.response?.status === 401) {
        clearAuth()
      }
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新个人资料
   */
  const updateProfile = async (data: UpdateProfileData) => {
    isLoading.value = true
    try {
      const response = await authAPI.updateProfile(data)

      if (response.data.user) {
        user.value = response.data.user
        localStorage.setItem('user', JSON.stringify(user.value))
      }

      return { success: true, data: response.data }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || '更新失败'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 修改密码
   */
  const changePassword = async (data: ChangePasswordData) => {
    isLoading.value = true
    try {
      const response = await authAPI.changePassword(data)
      // 修改密码成功后清除 token，需要重新登录
      clearAuth()
      return { success: true, data: response.data }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || '修改密码失败'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 清除认证信息
   */
  const clearAuth = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('isAdmin')
  }

  // 初始化
  initAuth()

  return {
    // State
    user,
    token,
    isLoading,
    // Getters
    isAuthenticated,
    isStudent,
    isTeacher,
    isAdmin,
    fullName,
    // Actions
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    clearAuth
  }
}, {
  // Pinia 持久化配置
  persist: {
    key: 'auth',           // 存储键名
    storage: localStorage, // 存储方式
    pick: ['user', 'token'], // 持久化的字段
  }
})
