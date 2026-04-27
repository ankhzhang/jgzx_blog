/**
 * 项目发布模块 — 类型定义
 * 与后端 Project 序列化器对应
 */

export type ProjectCategory =
  | 'teacher_research'
  | 'subject_competition'
  | 'innovation_innov'
  | 'innovation_venture'
export type ProjectStatus =
  | 'draft'
  | 'pending'
  | 'published'
  | 'recruit_full'
  | 'ended'
  | 'offline'
export type PublisherRole = 'student' | 'teacher'

/** 技能要求：带人数 或 简单字符串 */
export type SkillItem =
  | { desc: string; count: number }
  | string

export interface ProjectListItem {
  id: number
  title: string
  category: ProjectCategory
  category_display: string
  status: ProjectStatus
  status_display: string
  publisher_role: PublisherRole
  publisher_role_display: string
  publisher_name: string
  recruit_count: number
  deadline: string
  created_at: string
  published_at: string | null
  is_visible_when_ended: boolean
  version: number
}

export interface ProjectDetail extends ProjectListItem {
  description: string
  publisher_id: number
  publisher_username: string
  skill_requirements: SkillItem[]
  offline_reason: string
  offline_at: string | null
  reject_reason: string
  submitted_at: string | null
  updated_at: string
}

/** 创建/编辑项目请求体 */
export interface ProjectCreateUpdatePayload {
  title: string
  description: string
  category: ProjectCategory
  recruit_count: number
  skill_requirements?: SkillItem[]
  deadline: string
  is_visible_when_ended?: boolean
  /** 创建时：true=草稿，false=直接提交审核 */
  is_draft?: boolean
}

export interface ProjectListParams {
  mine?: boolean
  category?: ProjectCategory
  publisher_role?: PublisherRole
  status?: ProjectStatus
  q?: string
  tag?: string
}

export interface ProjectComment {
  id: number
  project_id: number
  parent_id: number | null
  content: string
  is_deleted: boolean
  author_name: string
  author_username: string
  created_at: string
  updated_at: string
  can_delete: boolean
  replies?: ProjectComment[]
}

export interface ProjectCommentTreeResponse {
  project_id: number
  items: ProjectComment[]
}

export interface ProjectCommentPayload {
  content: string
  parent_id?: number | null
}
