import api from './index'
import type { MyCommentListResponse } from '@/types/comment'

export const commentAPI = {
  getMyComments() {
    return api.get<MyCommentListResponse>('/comments/mine/')
  }
}
