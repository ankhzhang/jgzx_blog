<template>
  <div class="project-list-page">
    <el-card class="toolbar-card">
      <div class="toolbar flex-between">
        <h3 class="page-title">项目广场</h3>
        <div class="actions">
          <template v-if="authStore.isAuthenticated">
            <el-button type="primary" @click="$router.push('/projects/create')">
              <el-icon><Plus /></el-icon>
              发布项目
            </el-button>
            <el-button @click="$router.push('/projects/my')">我的项目</el-button>
          </template>
          <template v-else>
            <el-button type="primary" @click="$router.push('/login')">登录</el-button>
            <el-button @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
      <div class="filters">
        <el-select
          v-model="filters.category"
          placeholder="类别"
          clearable
          style="width: 120px; margin-right: 12px"
          @change="fetchList"
        >
          <el-option label="教师科研项目" value="teacher_research" />
          <el-option label="学科竞赛" value="subject_competition" />
          <el-option label="大创项目-创新类" value="innovation_innov" />
          <el-option label="大创项目-创业类" value="innovation_venture" />
        </el-select>
        <el-select
          v-model="filters.publisher_role"
          placeholder="发布者"
          clearable
          style="width: 120px; margin-right: 12px"
          @change="fetchList"
        >
          <el-option label="学生项目" value="student" />
          <el-option label="教师项目" value="teacher" />
        </el-select>
        <!-- 你的状态筛选 -->
        <el-select
          v-model="filters.status"
          placeholder="状态"
          clearable
          style="width: 140px; margin-right: 12px"
          @change="fetchList"
        >
          <el-option label="已发布" value="published" />
          <el-option label="已招满" value="recruit_full" />
          <el-option label="已结束" value="ended" />
        </el-select>
        <el-input
          v-model="filters.q"
          placeholder="搜索标题/描述"
          clearable
          style="width: 220px; margin-right: 12px"
          @keyup.enter="fetchList"
        />
        <!-- 你的标签筛选 -->
        <el-input
          v-model="filters.tags"
          placeholder="标签筛选，逗号分隔"
          clearable
          style="width: 200px; margin-right: 12px"
          @keyup.enter="fetchList"
        />
        <el-button type="primary" @click="fetchList">查询</el-button>
      </div>
    </el-card>

    <el-card v-loading="loading" class="list-card">
      <template v-if="list.length === 0">
        <el-empty description="暂无项目" />
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
            <el-tag size="small" type="info">{{ item.publisher_role_display }}</el-tag>
            <span class="meta-text">招募 {{ item.recruit_count }} 人</span>
            <span class="meta-text">截止 {{ formatDate(item.deadline, 'YYYY-MM-DD') }}</span>
          </div>
          <div class="card-footer">
            <span class="publisher">{{ item.publisher_name }}</span>
            <span class="date">{{ formatDate(item.created_at, 'YYYY-MM-DD') }}</span>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { projectAPI } from '@/api/project'
import { formatDate } from '@/utils'
import type { ProjectListItem, ProjectCategory, PublisherRole, ProjectStatus } from '@/types/project'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const loading = ref(false)
const list = ref<ProjectListItem[]>([])

const filters = reactive<{
  category: ProjectCategory | ''
  publisher_role: PublisherRole | ''
  status: ProjectStatus | ''
  q: string
  tags: string
}>({
  category: '',
  publisher_role: '',
  status: '',
  q: '',
  tags: ''
})

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
      category: filters.category || undefined,
      publisher_role: filters.publisher_role || undefined,
      status: filters.status || undefined,
      q: filters.q || undefined,
      tags: filters.tags || undefined  // ← 你的 tags 参数
    })
    list.value = res.data ?? []
  } finally {
    loading.value = false
  }
}

function initFromRoute() {
  const { category, status, q, tags } = route.query
  filters.category = (category as ProjectCategory) || ''
  filters.status = (status as ProjectStatus) || ''
  filters.q = (q as string) || ''
  filters.tags = (tags as string) || ''  // ← 你的 tags 路由同步
}

onMounted(() => {
  initFromRoute()
  fetchList()
})

watch(
  () => route.query,
  () => {
    initFromRoute()
    fetchList()
  }
)
</script>

<style scoped>
.project-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
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
  display: flex;
  justify-content: space-between;
}
</style>