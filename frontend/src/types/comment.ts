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

export interface MyCommentListResponse {
  my_comments: MyCommentItem[]
  replies_to_me: MyCommentItem[]
}
