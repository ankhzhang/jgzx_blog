import api from './index'
import type { CommentItem, CreateCommentPayload } from '@/types/comment'

const BASE = '/projects'

export const commentAPI = {
  /** 列表：GET /api/projects/:id/comments/ */
  getList(projectId: number) {
    return api.get<CommentItem[]>(`${BASE}/${projectId}/comments/`)
  },

  /** 创建：POST /api/projects/:id/comments/ */
  create(projectId: number, data: CreateCommentPayload) {
    return api.post<CommentItem>(`${BASE}/${projectId}/comments/`, data)
  },

  /** 删除：DELETE /api/comments/:id/ */
  delete(commentId: number) {
    return api.delete<void>(`/comments/${commentId}/`)
  }
}

