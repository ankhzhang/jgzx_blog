// frontend/src/utils/index.ts
import dayjs from 'dayjs'

/**
 * 获取 API 基础URL
 * 从环境变量获取，默认指向本地开发服务器
 */
export const getApiBaseUrl = (): string => {
  if (import.meta.env.DEV) {
    return '/api'
  }
  // 生产环境（打包后）才使用完整的环境变量地址
  return import.meta.env.VITE_API_BASE_URL || '/api'
}

/**
 * 获取应用标题
 */
export const getAppTitle = (): string => {
  return import.meta.env.VITE_APP_TITLE || 'JGZX平台'
}

/**
 * 格式化日期
 * @param date - 日期字符串或Date对象
 * @param format - 格式化模板，默认：YYYY-MM-DD HH:mm:ss
 * @returns 格式化后的日期字符串
 */
export const formatDate = (date: string | Date | undefined, format = 'YYYY-MM-DD HH:mm:ss'): string => {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 格式化手机号
 * 将 13800138000 格式化为 138****8000
 * @param phone - 手机号
 * @returns 格式化后的手机号
 */
export const formatPhone = (phone: string): string => {
  if (!phone) return ''
  if (phone.length === 11) {
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
  }
  return phone
}

/**
 * 延迟函数
 * @param ms - 延迟毫秒数
 * @returns Promise
 */
export const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 从URL获取文件名
 * @param url - 文件URL
 * @returns 文件名
 */
export const getFileNameFromUrl = (url: string): string => {
  if (!url) return ''
  try {
    const urlObj = new URL(url)
    return urlObj.pathname.substring(urlObj.pathname.lastIndexOf('/') + 1)
  } catch {
    // 如果不是完整URL，尝试直接从路径获取
    return url.substring(url.lastIndexOf('/') + 1)
  }
}

/**
 * 下载文件
 * @param url - 文件URL
 * @param filename - 自定义文件名（可选）
 */
export const downloadFile = (url: string, filename?: string): void => {
  const link = document.createElement('a')
  link.href = url
  link.download = filename || getFileNameFromUrl(url)
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 深拷贝
 * @param obj - 要拷贝的对象
 * @returns 拷贝后的新对象
 */
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as any
  if (obj instanceof RegExp) return new RegExp(obj) as any
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as any
  }
  if (obj instanceof Object) {
    const copy = {} as T
    Object.keys(obj).forEach(key => {
      copy[key as keyof T] = deepClone((obj as any)[key])
    })
    return copy
  }
  return obj
}

/**
 * 存储数据到 localStorage
 * @param key - 键名
 * @param value - 值
 */
export const setStorage = <T>(key: string, value: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.error('存储数据失败:', error)
  }
}

/**
 * 从 localStorage 获取数据
 * @param key - 键名
 * @returns 存储的数据
 */
export const getStorage = <T>(key: string): T | null => {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : null
  } catch (error) {
    console.error('获取数据失败:', error)
    return null
  }
}

/**
 * 移除 localStorage 数据
 * @param key - 键名
 */
export const removeStorage = (key: string): void => {
  try {
    localStorage.removeItem(key)
  } catch (error) {
    console.error('移除数据失败:', error)
  }
}

/**
 * 验证手机号
 * @param phone - 手机号
 * @returns 是否有效
 */
export const isValidPhone = (phone: string): boolean => {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 验证邮箱
 * @param email - 邮箱
 * @returns 是否有效
 */
export const isValidEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * 生成随机字符串
 * @param length - 长度
 * @returns 随机字符串
 */
export const randomString = (length = 8): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 防抖函数
 * @param fn - 要执行的函数
 * @param delay - 延迟时间（毫秒）
 * @returns 防抖后的函数
 */
export const debounce = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timer: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

/**
 * 节流函数
 * @param fn - 要执行的函数
 * @param delay - 延迟时间（毫秒）
 * @returns 节流后的函数
 */
export const throttle = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let lastTime = 0
  return (...args: Parameters<T>) => {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn(...args)
      lastTime = now
    }
  }
}
