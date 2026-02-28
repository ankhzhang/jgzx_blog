export interface CommentItem {
  id: number
  project_id: number
  parent_id: number | null
  content: string
  created_at: string
  updated_at: string
  author_id: number
  author_name: string
  author_username: string
  author_identity: 'student' | 'teacher'
  is_deleted: boolean
  can_delete: boolean
  replies: CommentItem[]
}

export interface CreateCommentPayload {
  content: string
  parent?: number | null
}

