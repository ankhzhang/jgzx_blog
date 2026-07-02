import api from './index'
import type { MyCommentListResponse } from '@/types/comment'

export const commentAPI = {
  getMyComments() {
    return api.get<MyCommentListResponse>('/comments/mine/')
  },

  markRepliesRead() {
    return api.post<{ marked_count: number }>('/comments/replies/mark-read/')
  }
}
