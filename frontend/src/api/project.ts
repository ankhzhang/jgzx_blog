import api from './index'
import type {
  ProjectListItem,
  ProjectDetail,
  ProjectCreateUpdatePayload,
  ProjectListParams
} from '@/types/project'

const BASE = '/projects'

export const projectAPI = {
  getList(params?: ProjectListParams) {
    const p: Record<string, string | number | boolean> = {}
    if (params?.mine) p.mine = 'true'
    if (params?.category) p.category = params.category
    if (params?.publisher_role) p.publisher_role = params.publisher_role
    if (params?.status) p.status = params.status
    if (params?.q) p.q = params.q
    return api.get<ProjectListItem[]>(BASE + '/', { params: p })
  },

  create(data: ProjectCreateUpdatePayload) {
    return api.post<ProjectDetail>(BASE + '/', data)
  },

  getDetail(id: number) {
    return api.get<ProjectDetail>(`${BASE}/${id}/`)
  },

  update(id: number, data: Partial<ProjectCreateUpdatePayload>, version?: number) {
    const body = version !== undefined ? { ...data, version } : data
    return api.put<ProjectDetail>(`${BASE}/${id}/edit/`, body)
  },

  submit(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/submit/`)
  },

  withdraw(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/withdraw/`)
  },

  approve(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/approve/`)
  },

  reject(id: number, reject_reason: string) {
    return api.post<ProjectDetail>(`${BASE}/${id}/reject/`, { reject_reason })
  },

  closeRecruit(id: number, target: 'recruit_full' | 'ended') {
    return api.post<ProjectDetail>(`${BASE}/${id}/close-recruit/`, { target })
  },

  offline(id: number, offline_reason: string) {
    return api.post<ProjectDetail>(`${BASE}/${id}/offline/`, { offline_reason })
  },

  restore(id: number) {
    return api.post<ProjectDetail>(`${BASE}/${id}/restore/`)
  },

  setVisibility(id: number, is_visible_when_ended: boolean) {
    return api.patch<ProjectDetail>(`${BASE}/${id}/visibility/`, {
      is_visible_when_ended
    })
  },

  delete(id: number) {
    return api.delete(`${BASE}/${id}/delete/`)
  }
}
