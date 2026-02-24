<template>
  <div class="project-detail-page">
    <el-card v-loading="loading" class="detail-card">
      <template v-if="!project">
        <el-empty v-if="!loading" description="项目不存在或无权查看" />
      </template>
      <template v-else>
        <div class="detail-header flex-between">
          <div>
            <h2 class="title">{{ project.title }}</h2>
            <div class="meta-row">
              <el-tag :type="statusTagType(project.status)">{{ project.status_display }}</el-tag>
              <el-tag>{{ project.category_display }}</el-tag>
              <el-tag type="info">{{ project.publisher_role_display }}</el-tag>
              <span class="meta-text">招募 {{ project.recruit_count }} 人</span>
              <span class="meta-text">截止 {{ formatDate(project.deadline) }}</span>
            </div>
          </div>
          <div v-if="isOwnerOrAdmin" class="actions">
            <el-button v-if="canEdit" @click="$router.push(`/projects/${project.id}/edit`)">
              编辑
            </el-button>
            <template v-if="project.status === 'draft'">
              <el-button type="primary" :loading="actionLoading" @click="doSubmit">提交审核</el-button>
              <el-button type="danger" :loading="actionLoading" @click="doDelete">删除</el-button>
            </template>
            <template v-else-if="project.status === 'pending'">
              <el-button :loading="actionLoading" @click="doWithdraw">撤回审核</el-button>
            </template>
            <template v-else-if="['published', 'recruit_full', 'ended'].includes(project.status)">
              <el-button
                v-if="project.status === 'published'"
                :loading="actionLoading"
                @click="openCloseRecruit"
              >
                关闭招募
              </el-button>
              <el-button type="primary" link @click="openVisibility">
                {{ project.is_visible_when_ended ? '设为结束不可见' : '设为结束可见' }}
              </el-button>
            </template>
            <template v-if="project.status === 'offline' && isAdmin">
              <el-button type="primary" :loading="actionLoading" @click="doRestore">恢复上架</el-button>
            </template>
          </div>
        </div>

        <el-alert
          v-if="project.reject_reason"
          type="warning"
          :title="'驳回原因：' + project.reject_reason"
          show-icon
          class="reject-alert"
        />
        <el-alert
          v-if="project.status === 'offline' && project.offline_reason"
          type="error"
          :title="'下架原因：' + project.offline_reason"
          show-icon
          class="offline-alert"
        />

        <el-divider />

        <div class="detail-body">
          <h4>项目描述</h4>
          <div class="description">{{ project.description }}</div>
          <h4 v-if="skillList.length">技能要求</h4>
          <ul v-if="skillList.length" class="skill-list">
            <li v-for="(s, i) in skillList" :key="i">
              {{ typeof s === 'string' ? s : `${(s as { desc: string }).desc}（${(s as { count: number }).count} 人）` }}
            </li>
          </ul>
          <div class="publisher-info">
            <span>发布人：{{ project.publisher_name }}</span>
            <span>发布时间：{{ formatDate(project.created_at) }}</span>
            <span v-if="project.published_at">审核通过：{{ formatDate(project.published_at) }}</span>
          </div>
        </div>
      </template>
    </el-card>

    <el-dialog v-model="closeRecruitVisible" title="关闭招募" width="400px">
      <el-radio-group v-model="closeTarget">
        <el-radio value="recruit_full">已招满</el-radio>
        <el-radio value="ended">已结束</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="closeRecruitVisible = false">取消</el-button>
        <el-button type="primary" :loading="actionLoading" @click="doCloseRecruit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="visibilityVisible" title="结束可见性" width="400px">
      <p>已招满/已结束后是否对他人可见？</p>
      <el-switch v-model="visibilityValue" />
      <template #footer>
        <el-button @click="visibilityVisible = false">取消</el-button>
        <el-button type="primary" :loading="actionLoading" @click="doSetVisibility">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectAPI } from '@/api/project'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils'
import type { ProjectDetail, SkillItem } from '@/types/project'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const actionLoading = ref(false)
const project = ref<ProjectDetail | null>(null)
const closeRecruitVisible = ref(false)
const closeTarget = ref<'recruit_full' | 'ended'>('recruit_full')
const visibilityVisible = ref(false)
const visibilityValue = ref(true)

const isAdmin = computed(() => authStore.isAdmin)
const isOwnerOrAdmin = computed(() => {
  if (!project.value || !authStore.user) return false
  return project.value.publisher_id === authStore.user.id || authStore.isAdmin
})
const canEdit = computed(() => {
  const p = project.value
  if (!p) return false
  return ['draft', 'published'].includes(p.status)
})

const skillList = computed(() => project.value?.skill_requirements ?? [])

function statusTagType(status: string) {
  const map: Record<string, string> = {
    published: 'success',
    pending: 'warning',
    draft: 'info',
    recruit_full: 'success',
    ended: 'info',
    offline: 'danger'
  }
  return map[status] || 'info'
}

async function fetchDetail() {
  const id = Number(route.params.id)
  if (!id) return
  loading.value = true
  try {
    const res = await projectAPI.getDetail(id)
    project.value = res.data
  } catch {
    project.value = null
  } finally {
    loading.value = false
  }
}

async function doSubmit() {
  if (!project.value) return
  actionLoading.value = true
  try {
    const res = await projectAPI.submit(project.value.id)
    project.value = res.data
    ElMessage.success('已提交审核')
  } finally {
    actionLoading.value = false
  }
}

async function doWithdraw() {
  if (!project.value) return
  actionLoading.value = true
  try {
    const res = await projectAPI.withdraw(project.value.id)
    project.value = res.data
    ElMessage.success('已撤回')
  } finally {
    actionLoading.value = false
  }
}

async function doDelete() {
  if (!project.value) return
  try {
    await ElMessageBox.confirm('确定删除该草稿？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }
  actionLoading.value = true
  try {
    await projectAPI.delete(project.value.id)
    ElMessage.success('已删除')
    router.push('/projects/my')
  } finally {
    actionLoading.value = false
  }
}

function openCloseRecruit() {
  closeTarget.value = 'recruit_full'
  closeRecruitVisible.value = true
}

async function doCloseRecruit() {
  if (!project.value) return
  actionLoading.value = true
  try {
    const res = await projectAPI.closeRecruit(project.value.id, closeTarget.value)
    project.value = res.data
    closeRecruitVisible.value = false
    ElMessage.success('已更新状态')
  } finally {
    actionLoading.value = false
  }
}

function openVisibility() {
  visibilityValue.value = project.value?.is_visible_when_ended ?? true
  visibilityVisible.value = true
}

async function doSetVisibility() {
  if (!project.value) return
  actionLoading.value = true
  try {
    const res = await projectAPI.setVisibility(project.value.id, visibilityValue.value)
    project.value = res.data
    visibilityVisible.value = false
    ElMessage.success('已更新')
  } finally {
    actionLoading.value = false
  }
}

async function doRestore() {
  if (!project.value || !authStore.isAdmin) return
  actionLoading.value = true
  try {
    const res = await projectAPI.restore(project.value.id)
    project.value = res.data
    ElMessage.success('已恢复上架')
  } finally {
    actionLoading.value = false
  }
}

watch(() => route.params.id, fetchDetail)
onMounted(fetchDetail)
</script>

<style scoped>
.project-detail-page {
  max-width: 900px;
  margin: 0 auto;
}

.detail-card {
  border-radius: 12px;
}

.detail-header .title {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.meta-text {
  font-size: 13px;
  color: #909399;
}

.reject-alert,
.offline-alert {
  margin-top: 16px;
}

.detail-body h4 {
  margin: 16px 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.description {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #333;
}

.skill-list {
  margin: 0;
  padding-left: 20px;
}

.publisher-info {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 13px;
  color: #909399;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
</style>
