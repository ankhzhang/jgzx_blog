import api from './index'
import type {
  UserProfile,
  LoginCredentials,
  RegisterData,
  UpdateProfileData,
  ChangePasswordData,
  BulkRegisterRequest,
  BulkRegisterResponse,
  LoginResponse,
  RegisterResponse,
  UpdateProfileResponse,
  UserListParams
} from '@/types/user'

/**
 * 用户认证相关 API
 * 完全适配后端的 userviews.py
 */
export const authAPI = {
  /**
   * 1. 用户注册
   * POST /api/register/
   * @param data 注册数据
   * @returns Promise<RegisterResponse>
   */
  register(data: RegisterData) {
    return api.post<RegisterResponse>('/register/', data)
  },

  /**
   * 2. 批量注册（管理员）
   * POST /api/bulk-register/
   * @param data 批量注册数据
   * @returns Promise<BulkRegisterResponse>
   */
  bulkRegister(data: BulkRegisterRequest) {
    return api.post<BulkRegisterResponse>('/bulk-register/', data)
  },

  /**
   * 3. 用户登录
   * POST /api/login/
   * @param data 登录凭证
   * @returns Promise<LoginResponse>
   */
  login(data: LoginCredentials) {
    return api.post<LoginResponse>('/login/', data)
  },

  /**
   * 4. 用户登出
   * POST /api/logout/
   * @returns Promise
   */
  logout() {
    return api.post('/logout/')
  },

  /**
   * 5. 获取当前用户资料
   * GET /api/profile/
   * @returns Promise<UserProfile>
   */
  getProfile() {
    return api.get<UserProfile>('/profile/')
  },

  /**
   * 6. 更新个人资料
   * PUT /api/profile/
   * @param data 更新数据
   * @returns Promise<UpdateProfileResponse>
   */
  updateProfile(data: UpdateProfileData) {
    // 如果有文件上传，使用 FormData
    if (data.avatar instanceof File) {
      const formData = new FormData()

      // 添加非空字段
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (key === 'avatar' && value instanceof File) {
            formData.append(key, value)
          } else {
            formData.append(key, String(value))
          }
        }
      })

      return api.put<UpdateProfileResponse>('/profile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    // 普通 JSON 数据
    return api.put<UpdateProfileResponse>('/profile/', data)
  },

  /**
   * 7. 修改密码
   * POST /api/change-password/
   * @param data 密码数据
   * @returns Promise<{ message: string }>
   */
  changePassword(data: ChangePasswordData) {
    return api.post('/change-password/', data)
  },

  /**
   * 8. 获取用户列表（管理员）
   * GET /api/users/
   * @param params 查询参数
   * @returns Promise<UserProfile[]>
   */
  getUsers(params?: UserListParams) {
    return api.get<UserProfile[]>('/users/', { params })
  },

  /**
   * 9. 搜索用户（管理员）
   * GET /api/users/?search=keyword
   * @param keyword 搜索关键词
   * @returns Promise<UserProfile[]>
   */
  searchUsers(keyword: string) {
    return api.get<UserProfile[]>('/users/', {
      params: { search: keyword }
    })
  },

  /**
   * 10. 获取用户详情（管理员）
   * GET /api/users/{user_id}/
   * @param userId 用户ID
   * @returns Promise<UserProfile>
   */
  getUserDetail(userId: number) {
    return api.get<UserProfile>(`/users/${userId}/`)
  },

  /**
   * 11. 删除用户（管理员）
   * DELETE /api/users/{user_id}/
   * @param userId 用户ID
   * @returns Promise
   */
  deleteUser(userId: number) {
    return api.delete(`/users/${userId}/`)
  }
}
