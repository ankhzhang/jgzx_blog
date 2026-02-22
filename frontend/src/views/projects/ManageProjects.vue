<template>
  <div class="manage-projects-page">
    <el-card class="toolbar-card">
      <div class="toolbar flex-between">
        <h3 class="page-title">项目审核面板</h3>
        <div class="toolbar-right">
          <el-input
            v-model="keyword"
            placeholder="按标题/描述关键词搜索"
            clearable
            style="width: 260px; margin-right: 12px"
            @keyup.enter="fetchList"
          >
            <template #append>
              <el-button @click="fetchList">搜索</el-button>
            </template>
          </el-input>
          <el-button @click="$router.push('/projects')">返回项目广场</el-button>
        </div>
      </div>
      <div class="filters">
        <el-select
          v-model="statusFilter"
          placeholder="状态"
          clearable
          style="width: 120px; margin-right: 12px"
          @change="fetchList"
        >
          <el-option label="待审" value="pending" />
          <el-option label="已发布" value="published" />
          <el-option label="已下架" value="offline" />
          <el-option label="草稿" value="draft" />
          <el-option label="已招满" value="recruit_full" />
          <el-option label="已结束" value="ended" />
        </el-select>
        <el-button type="primary" @click="fetchList">查询</el-button>
      </div>
    </el-card>

    <el-card v-loading="loading" class="table-card">
      <el-table :data="list" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column prop="category_display" label="类别" width="100" />
        <el-table-column prop="publisher_role_display" label="身份" width="100" />
        <el-table-column prop="publisher_name" label="发布人" width="100" />
        <el-table-column prop="status_display" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="100">
          <template #default="{ row }">{{ formatDate(row.created_at, 'YYYY-MM-DD') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/projects/${row.id}`)">
              详情
            </el-button>
            <template v-if="row.status === 'pending'">
              <el-button type="success" link :loading="actionId === row.id" @click="approve(row)">
                通过
              </el-button>
              <el-button type="warning" link @click="openReject(row)">驳回</el-button>
            </template>
            <template v-else-if="row.status !== 'offline'">
              <el-button type="danger" link @click="openOffline(row)">下架</el-button>
            </template>
            <template v-else>
              <el-button type="primary" link :loading="actionId === row.id" @click="restore(row)">
                恢复
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="rejectVisible" title="驳回原因" width="400px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="3"
        placeholder="请输入驳回原因"
      />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="primary" :loading="actionLoading" @click="doReject">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="offlineVisible" title="下架原因" width="400px">
      <el-input
        v-model="offlineReason"
        type="textarea"
        :rows="3"
        placeholder="请输入下架原因"
      />
      <template #footer>
        <el-button @click="offlineVisible = false">取消</el-button>
        <el-button type="primary" :loading="actionLoading" @click="doOffline">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { projectAPI } from '@/api/project'
import { formatDate } from '@/utils'
import type { ProjectListItem, ProjectStatus } from '@/types/project'

const loading = ref(false)
const actionLoading = ref(false)
const actionId = ref<number | null>(null)
const list = ref<ProjectListItem[]>([])
const statusFilter = ref<ProjectStatus | ''>('pending')
const keyword = ref('')

const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectRow = ref<ProjectListItem | null>(null)
const offlineVisible = ref(false)
const offlineReason = ref('')
const offlineRow = ref<ProjectListItem | null>(null)

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

async function fetchList() {
  loading.value = true
  try {
    const res = await projectAPI.getList({
      status: statusFilter.value || undefined,
      q: keyword.value || undefined
    })
    list.value = res.data ?? []
  } finally {
    loading.value = false
  }
}

async function approve(row: ProjectListItem) {
  actionId.value = row.id
  try {
    await projectAPI.approve(row.id)
    ElMessage.success('已通过')
    fetchList()
  } finally {
    actionId.value = null
  }
}

function openReject(row: ProjectListItem) {
  rejectRow.value = row
  rejectReason.value = ''
  rejectVisible.value = true
}

async function doReject() {
  if (!rejectRow.value || !rejectReason.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  actionLoading.value = true
  try {
    await projectAPI.reject(rejectRow.value.id, rejectReason.value.trim())
    ElMessage.success('已驳回')
    rejectVisible.value = false
    fetchList()
  } finally {
    actionLoading.value = false
  }
}

function openOffline(row: ProjectListItem) {
  offlineRow.value = row
  offlineReason.value = ''
  offlineVisible.value = true
}

async function doOffline() {
  if (!offlineRow.value || !offlineReason.value.trim()) {
    ElMessage.warning('请填写下架原因')
    return
  }
  actionLoading.value = true
  try {
    await projectAPI.offline(offlineRow.value.id, offlineReason.value.trim())
    ElMessage.success('已下架')
    offlineVisible.value = false
    fetchList()
  } finally {
    actionLoading.value = false
  }
}

async function restore(row: ProjectListItem) {
  actionId.value = row.id
  try {
    await projectAPI.restore(row.id)
    ElMessage.success('已恢复上架')
    fetchList()
  } finally {
    actionId.value = null
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.manage-projects-page {
  max-width: 1200px;
  margin: 0 auto;
}

.toolbar-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.filters {
  margin-top: 16px;
}

.table-card {
  border-radius: 12px;
}
</style>
