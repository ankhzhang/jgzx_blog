import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { getApiBaseUrl } from '@/utils'

/**
 * API 响应格式
 */
export interface ApiResponse<T = any> {
  data: T
  message?: string
  [key: string]: any
}

/**
 * API 客户端类
 */
class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: getApiBaseUrl(),
      timeout: 30000,  // 30秒超时
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  /**
   * 配置拦截器
   */
  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // 从 localStorage 获取 token
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Token ${token}`  // Django Token 认证
        }

        // 如果是 FormData，不设置 Content-Type，让浏览器自动设置
        if (config.data instanceof FormData) {
          delete config.headers['Content-Type']
        }

        return config
      },
      (error: AxiosError) => {
        console.error('请求错误:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // 显示成功消息
        if (response.data?.message) {
          ElMessage.success(response.data.message)
        }
        return response
      },
      (error: AxiosError) => {
        if (error.response) {
          const { status, data } = error.response
          const responseData = data as any

          switch (status) {
            case 400:  // 表单验证错误
              if (responseData) {
                const messages: string[] = []

                if (typeof responseData.detail === 'string') {
                  messages.push(responseData.detail)
                }
                if (typeof responseData.error === 'string') {
                  messages.push(responseData.error)
                }

                Object.keys(responseData).forEach((key) => {
                  if (key === 'detail' || key === 'error') return
                  const errors = responseData[key]
                  if (Array.isArray(errors)) {
                    messages.push(...errors.map((item) => String(item)))
                  } else if (typeof errors === 'string') {
                    messages.push(errors)
                  }
                })

                if (messages.length > 0) {
                  messages.forEach((msg) => ElMessage.error(msg))
                } else {
                  ElMessage.error('提交失败，请检查输入')
                }
              }
              break

            case 401:  // 未授权
              ElMessage.error(responseData?.error || '登录已过期，请重新登录')
              // 清除本地存储
              localStorage.removeItem('token')
              localStorage.removeItem('user')
              // 跳转到登录页
              setTimeout(() => {
                window.location.href = '/login'
              }, 1500)
              break

            case 403:  // 权限不足
              ElMessage.error(responseData?.error || '没有权限执行此操作')
              break

            case 404:  // 资源不存在
              ElMessage.error(responseData?.error || '请求的资源不存在')
              break

            case 409:  // 冲突
              ElMessage.error(responseData?.error || '数据已存在，操作失败')
              break

            case 429:  // 请求过多
              ElMessage.error('请求过于频繁，请稍后再试')
              break

            case 500:  // 服务器错误
              ElMessage.error(responseData?.error || '服务器内部错误')
              break

            default:
              ElMessage.error(responseData?.error || `请求失败 (${status})`)
          }
        } else if (error.request) {
          // 请求已发送但没有收到响应
          ElMessage.error('网络连接失败，请检查网络设置')
        } else {
          // 请求配置出错
          ElMessage.error(`请求配置错误: ${error.message}`)
        }

        return Promise.reject(error)
      }
    )
  }

  /**
   * GET 请求
   */
  public get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.get<T>(url, config)
  }

  /**
   * POST 请求
   */
  public post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.post<T>(url, data, config)
  }

  /**
   * PUT 请求
   */
  public put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.put<T>(url, data, config)
  }

  /**
   * PATCH 请求
   */
  public patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.patch<T>(url, data, config)
  }

  /**
   * DELETE 请求
   */
  public delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.delete<T>(url, config)
  }
}

// 导出单例实例
export const api = new ApiClient()
export default api
