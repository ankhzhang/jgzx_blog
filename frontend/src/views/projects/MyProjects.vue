<template>
  <div class="my-projects-page">
    <el-card class="toolbar-card">
      <div class="toolbar flex-between">
        <h3 class="page-title">我的项目</h3>
        <div class="actions">
          <el-button type="primary" @click="$router.push('/projects/create')">
            <el-icon><Plus /></el-icon>
            发布项目
          </el-button>
          <el-button @click="$router.push('/projects')">项目广场</el-button>
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
          <el-option label="草稿" value="draft" />
          <el-option label="待审" value="pending" />
          <el-option label="已发布" value="published" />
          <el-option label="已招满" value="recruit_full" />
          <el-option label="已结束" value="ended" />
          <el-option label="已下架" value="offline" />
        </el-select>
        <el-button type="primary" @click="fetchList">查询</el-button>
      </div>
    </el-card>

    <el-card v-loading="loading" class="list-card">
      <template v-if="list.length === 0">
        <el-empty description="暂无项目">
          <el-button type="primary" @click="$router.push('/projects/create')">去发布</el-button>
        </el-empty>
      </template>
      <div v-else class="project-cards">
        <el-card
          v-for="item in list"
          :key="item.id"
          class="project-card"
          shadow="hover"
          @click="$router.push(`/projects/${item.id}`)"
        >
          <div class="card-header flex-between">
            <span class="title">{{ item.title }}</span>
            <el-tag :type="statusTagType(item.status)" size="small">
              {{ item.status_display }}
            </el-tag>
          </div>
          <div class="card-meta">
            <el-tag size="small">{{ item.category_display }}</el-tag>
            <span class="meta-text">招募 {{ item.recruit_count }} 人</span>
            <span class="meta-text">截止 {{ formatDate(item.deadline, 'YYYY-MM-DD') }}</span>
          </div>
          <div class="card-footer">
            <span class="date">{{ formatDate(item.created_at, 'YYYY-MM-DD') }}</span>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { projectAPI } from '@/api/project'
import { formatDate } from '@/utils'
import type { ProjectListItem, ProjectStatus } from '@/types/project'

const loading = ref(false)
const list = ref<ProjectListItem[]>([])
const statusFilter = ref<ProjectStatus | ''>('')

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
      mine: true,
      status: statusFilter.value || undefined
    })
    list.value = res.data ?? []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.my-projects-page {
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

.filters {
  margin-top: 16px;
}

.list-card {
  border-radius: 12px;
}

.project-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.project-card {
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow);
}

.card-header .title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
}

.card-meta {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.meta-text {
  font-size: 12px;
  color: #909399;
}

.card-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  color: #909399;
}
</style>
