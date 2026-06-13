<template>
  <div class="comment-thread">
    <div class="title-row">
      <h3>互动讨论区</h3>
      <span class="sub">用于咨询、申请意向与答疑交流</span>
    </div>

    <el-input
      v-model="newContent"
      type="textarea"
      :rows="3"
      maxlength="2000"
      show-word-limit
      placeholder="请输入留言内容，例如：自我介绍、项目咨询、申请意向"
    />
    <div class="new-actions">
      <el-button type="primary" :loading="posting" @click="submitNewComment">发布评论</el-button>
    </div>

    <div class="list" v-loading="loading">
      <el-empty v-if="!loading && items.length === 0" description="还没有评论，来发第一条吧" />
      <CommentItem
        v-for="item in items"
        :key="item.id"
        :comment="item"
        :replying-id="replyingId"
        @reply="onReply"
        @cancel-reply="replyingId = null"
        @submit-reply="submitReply"
        @delete="deleteComment"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectAPI } from '@/api/project'
import type { ProjectComment } from '@/types/project'
import CommentItem from './CommentItem.vue'

const props = defineProps<{
  projectId: number
  canPost: boolean
}>()

const loading = ref(false)
const posting = ref(false)
const items = ref<ProjectComment[]>([])
const newContent = ref('')
const replyingId = ref<number | null>(null)

async function fetchComments() {
  loading.value = true
  try {
    const res = await projectAPI.getComments(props.projectId)
    items.value = res.data?.items ?? []
  } finally {
    loading.value = false
  }
}

async function submitNewComment() {
  if (!props.canPost) {
    ElMessage.warning('请先登录后再评论')
    return
  }
  const content = newContent.value.trim()
  if (content.length < 2) {
    ElMessage.warning('评论内容至少 2 个字符')
    return
  }
  posting.value = true
  try {
    await projectAPI.createComment(props.projectId, { content })
    newContent.value = ''
    await fetchComments()
    ElMessage.success('评论发布成功')
  } finally {
    posting.value = false
  }
}

function onReply(commentId: number) {
  if (!props.canPost) {
    ElMessage.warning('请先登录后再回复')
    return
  }
  replyingId.value = commentId
}

async function submitReply(commentId: number, content: string) {
  const text = (content || '').trim()
  if (text.length < 2) {
    ElMessage.warning('回复内容至少 2 个字符')
    return
  }
  posting.value = true
  try {
    await projectAPI.createComment(props.projectId, { content: text, parent_id: commentId })
    replyingId.value = null
    await fetchComments()
    ElMessage.success('回复成功')
  } finally {
    posting.value = false
  }
}

async function deleteComment(commentId: number) {
  try {
    await ElMessageBox.confirm('确认删除该评论？', '提示', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }
  posting.value = true
  try {
    await projectAPI.deleteComment(commentId)
    await fetchComments()
    ElMessage.success('已删除')
  } finally {
    posting.value = false
  }
}

defineExpose({
  fetchComments
})

onMounted(fetchComments)
</script>

<style scoped>
.comment-thread {
  margin-top: 20px;
}
.title-row {
  margin-bottom: 10px;
}
.title-row h3 {
  margin: 0;
}
.sub {
  color: #909399;
  font-size: 12px;
}
.new-actions {
  margin-top: 8px;
  margin-bottom: 14px;
}
.list {
  display: grid;
  gap: 12px;
}
</style>
