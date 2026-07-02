/** 个人评论中心 — 类型定义 */

export interface MyCommentItem {
  id: number
  project_id: number
  parent_id: number | null
  content: string
  is_deleted: boolean
  author_name: string
  author_username: string
  project_title: string
  parent_content: string
  parent_author_name: string
  parent_author_username: string
  created_at: string
  updated_at: string
}

export interface ProjectNewCommentSummary {
  project_id: number
  project_title: string
  unread_count: number
}

export interface MyCommentListResponse {
  my_comments: MyCommentItem[]
  replies_to_me: MyCommentItem[]
  project_new_comments: ProjectNewCommentSummary[]
  unread_project_comment_count: number
  unread_reply_count: number
}
