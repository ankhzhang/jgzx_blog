/**
 * 用户资料接口
 * 完全适配后端 UserProfileSerializer
 */
export interface UserProfile {
  id: number
  username: string        // 学号/工号
  real_name: string       // 真实姓名
  identity: 'student' | 'teacher'  // 身份标签
  phone: string          // 联系电话
  department: string     // 部门/院系
  avatar: string | null  // 头像URL
  bio: string           // 个人简介
  project_count: number  // 发布项目数
  comment_count: number  // 评论数
  is_banned: boolean    // 是否封禁
  date_joined: string   // 注册时间
  created_at: string    // 资料创建时间
  updated_at: string    // 资料更新时间
  is_staff: boolean     // 是否为管理员
}

/**
 * 登录请求参数
 */
export interface LoginCredentials {
  username: string  // 学号/工号
  password: string
}

/**
 * 注册请求参数
 * 完全适配后端 UserRegisterSerializer
 */
export interface RegisterData {
  username: string    // 学号/工号
  password: string
  password2: string   // 确认密码
  real_name: string   // 真实姓名
  identity: 'student' | 'teacher'  // 身份
  phone: string      // 联系电话（必填）
  department?: string // 部门/院系（可选）
}

/**
 * 更新个人资料请求参数
 * 完全适配后端 UserUpdateSerializer
 */
export interface UpdateProfileData {
  phone?: string      // 联系电话
  department?: string // 部门/院系
  bio?: string        // 个人简介
  avatar?: File       // 头像文件
}

/**
 * 修改密码请求参数
 * 完全适配后端 ChangePasswordSerializer
 */
export interface ChangePasswordData {
  old_password: string
  new_password: string
  confirm_password: string
}

/**
 * 批量注册用户数据
 */
export interface BulkRegisterUser {
  username: string    // 学号/工号
  password: string
  real_name: string   // 真实姓名
  identity: 'student' | 'teacher'
  phone?: string
  department?: string
}

/**
 * 批量注册请求
 */
export interface BulkRegisterRequest {
  users: BulkRegisterUser[]
}

/**
 * 批量注册响应
 * 适配后端 BulkUserRegisterSerializer 返回格式
 */
export interface BulkRegisterResponse {
  total: number
  success_count: number
  error_count: number
  errors: Array<{
    row_index: number
    username: string
    error: string
  }>
  success_usernames: string[]
}

/**
 * 登录响应
 */
export interface LoginResponse {
  user: UserProfile
  token: string
  message: string
}

/**
 * 注册响应
 */
export interface RegisterResponse {
  user: UserProfile
  token: string
  message: string
}

/**
 * 更新资料响应
 */
export interface UpdateProfileResponse {
  user: UserProfile
  message: string
}

/**
 * API 错误响应
 */
export interface ApiError {
  [key: string]: string | string[]
}

/**
 * 用户列表查询参数
 */
export interface UserListParams {
  search?: string
  identity?: 'student' | 'teacher'
  is_banned?: boolean
}
