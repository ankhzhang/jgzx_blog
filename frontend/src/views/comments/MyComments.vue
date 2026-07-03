<template>
  <div class="my-comments-page">
    <el-card class="toolbar-card">
      <div class="toolbar flex-between">
        <h3 class="page-title">我的评论</h3>
        <div class="actions">
          <el-button @click="$router.push('/projects')">项目广场</el-button>
        </div>
      </div>
    </el-card>

    <el-card v-loading="loading" class="list-card">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane name="mine">
          <template #label>
            <span class="tab-label">我发表的 ({{ myComments.length }})</span>
          </template>
          <template v-if="myComments.length === 0">
            <el-empty description="还没有发表过评论">
              <el-button type="primary" @click="$router.push('/projects')">去项目广场看看</el-button>
            </el-empty>
          </template>
          <div v-else class="comment-list">
            <div
              v-for="item in myComments"
              :key="item.id"
              class="comment-card"
              @click="goProject(item.project_id)"
            >
              <div class="card-header flex-between">
                <span class="project-title">{{ item.project_title }}</span>
                <el-tag v-if="item.parent_id" size="small" type="info">回复</el-tag>
                <el-tag v-else size="small">评论</el-tag>
              </div>
              <div v-if="item.parent_id && item.parent_content" class="parent-quote">
                回复 @{{ item.parent_author_name || item.parent_author_username }}：
                {{ item.parent_content }}
              </div>
              <div class="comment-content">{{ item.content }}</div>
              <div class="card-footer">
                <span class="time">{{ formatDate(item.created_at) }}</span>
                <el-button type="primary" link @click.stop="goProject(item.project_id)">
                  查看项目
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="replies">
          <template #label>
            <span class="tab-label">
              收到的回复 ({{ repliesToMe.length }})
              <span v-if="unreadReplyCount > 0" class="tab-dot" />
            </span>
          </template>
          <template v-if="repliesToMe.length === 0">
            <el-empty description="暂无他人回复" />
          </template>
          <div v-else class="comment-list">
            <div
              v-for="item in repliesToMe"
              :key="item.id"
              class="comment-card reply-card"
              @click="goProject(item.project_id)"
            >
              <div class="card-header flex-between">
                <span class="author">
                  {{ item.author_name || item.author_username }}
                </span>
                <span class="project-title">{{ item.project_title }}</span>
              </div>
              <div v-if="item.parent_content" class="parent-quote">
                我的评论：{{ item.parent_content }}
              </div>
              <div class="comment-content">{{ item.content }}</div>
              <div class="card-footer">
                <span class="time">{{ formatDate(item.created_at) }}</span>
                <el-button type="primary" link @click.stop="goProject(item.project_id)">
                  查看项目
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="project_new">
          <template #label>
            <span class="tab-label">
              我项目下的新增评论 ({{ projectNewComments.length }})
              <span v-if="unreadProjectCommentCount > 0" class="tab-dot" />
            </span>
          </template>
          <template v-if="projectNewComments.length === 0">
            <el-empty description="暂无新增评论" />
          </template>
          <div v-else class="comment-list">
            <div
              v-for="item in projectNewComments"
              :key="item.project_id"
              class="comment-card project-new-card"
            >
              <div class="card-header flex-between">
                <span class="project-title">{{ item.project_title }}</span>
                <el-tag type="danger" size="small">{{ item.unread_count }} 条新评论</el-tag>
              </div>
              <div class="card-footer">
                <span class="hint-text">点击查看项目中的评论</span>
                <el-button type="primary" link @click="goProject(item.project_id)">
                  查看项目
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { commentAPI } from '@/api/comment'
import { formatDate } from '@/utils'
import type { MyCommentItem, ProjectNewCommentSummary } from '@/types/comment'

const router = useRouter()

const loading = ref(false)
const activeTab = ref('mine')
const myComments = ref<MyCommentItem[]>([])
const repliesToMe = ref<MyCommentItem[]>([])
const projectNewComments = ref<ProjectNewCommentSummary[]>([])
const unreadProjectCommentCount = ref(0)
const unreadReplyCount = ref(0)

async function fetchList() {
  loading.value = true
  try {
    const res = await commentAPI.getMyComments()
    myComments.value = res.data?.my_comments ?? []
    repliesToMe.value = res.data?.replies_to_me ?? []
    projectNewComments.value = res.data?.project_new_comments ?? []
    unreadProjectCommentCount.value = res.data?.unread_project_comment_count ?? 0
    unreadReplyCount.value = res.data?.unread_reply_count ?? 0
  } finally {
    loading.value = false
  }
}

async function onTabChange(tabName: string | number) {
  if (tabName === 'replies' && unreadReplyCount.value > 0) {
    await commentAPI.markRepliesRead()
    unreadReplyCount.value = 0
  }
}

function goProject(projectId: number) {
  router.push(`/projects/${projectId}`)
}

onMounted(fetchList)
</script>

<style scoped>
.my-comments-page {
  max-width: 960px;
  margin: 0 auto;
}

.toolbar-card {
  margin-bottom: 16px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.list-card {
  min-height: 320px;
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.tab-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #f56c6c;
  flex-shrink: 0;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.comment-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.12);
}

.reply-card {
  border-left: 3px solid #409eff;
}

.project-new-card {
  border-left: 3px solid #f56c6c;
  cursor: default;
}

.card-header {
  margin-bottom: 8px;
  gap: 12px;
}

.project-title {
  font-weight: 600;
  color: #303133;
}

.author {
  font-weight: 500;
  color: #409eff;
}

.parent-quote {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.comment-content {
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.time,
.hint-text {
  font-size: 12px;
  color: #909399;
}
</style>
