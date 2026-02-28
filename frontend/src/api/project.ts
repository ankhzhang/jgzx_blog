import api from './index'
import type {
  ProjectListItem,
  ProjectDetail,
  ProjectCreateUpdatePayload,
  ProjectListParams
} from '@/types/project'

const BASE = '/projects'

export const projectAPI = {
  /** 列表：GET /api/projects/ ，mine=true 为「我的项目」 */
  getList(params?: ProjectListParams) {
    const p: Record<string, string | number | boolean> = {}
    if (params?.mine) p.mine = 'true'
    if (params?.category) p.category = params.category
    if (params?.publisher_role) p.publisher_role = params.publisher_role
    if (params?.status) p.status = params.status
    if (params?.q) p.q = params.q
    if (params?.tags) p.tags = params.tags
    return api.get<ProjectListItem[]>(BASE + '/', { params: p })
  },

  /** 创建：POST /api/projects/ */
    return api.get<ProjectListItem[]>(BASE + '/', { params: p })
  },

  create(data: ProjectCreateUpdatePayload) {
    return api.post<ProjectDetail>(BASE + '/', data)
  },

  /** 详情：GET /api/projects/:id/ */
  getDetail(id: number) {
    return api.get<ProjectDetail>(`${BASE}/${id}/`)
  },

  /** 更新：PUT /api/projects/:id/edit/ */
  update(id: number, data: Partial<ProjectCreateUpdatePayload>, version?: number) {
    const body = version !== undefined ? { ...data, version } : data
    return api.put<ProjectDetail>(`${BASE}/${id}/edit/`, body)
  },

  /** 提交审核：POST /api/projects/:id/submit/ */
  submit(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/submit/`)
  },

  /** 撤回审核：POST /api/projects/:id/withdraw/ */
  withdraw(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/withdraw/`)
  },

  /** 审核通过：POST /api/projects/:id/approve/ */
  approve(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/approve/`)
  },

  /** 审核驳回：POST /api/projects/:id/reject/ */
  reject(id: number, reject_reason: string) {
    return api.post<ProjectDetail>(`${BASE}/${id}/reject/`, { reject_reason })
  },

  /** 关闭招募/已结束：POST /api/projects/:id/close-recruit/ */
  closeRecruit(id: number, target: 'recruit_full' | 'ended') {
    return api.post<ProjectDetail>(`${BASE}/${id}/close-recruit/`, { target })
  },

  /** 下架：POST /api/projects/:id/offline/ */
  offline(id: number, offline_reason: string) {
    return api.post<ProjectDetail>(`${BASE}/${id}/offline/`, { offline_reason })
  },

  /** 恢复下架：POST /api/projects/:id/restore/ */
  restore(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/restore/`)
  },

  /** 修改结束可见：PATCH /api/projects/:id/visibility/ */
  setVisibility(id: number, is_visible_when_ended: boolean) {
    return api.patch<ProjectDetail>(`${BASE}/${id}/visibility/`, {
      is_visible_when_ended
    })
  },

  /** 删除（仅草稿）：DELETE /api/projects/:id/delete/ */
  delete(id: number) {
    return api.delete(`${BASE}/${id}/delete/`)
  }
}
