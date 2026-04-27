<template>
  <div class="comment-item">
    <div class="comment-main">
      <div class="comment-head">
        <span class="author">{{ comment.author_name || comment.author_username }}</span>
        <span class="time">{{ formatDate(comment.created_at) }}</span>
      </div>
      <div class="comment-content">{{ comment.content }}</div>
      <div class="comment-actions">
        <el-button type="primary" link @click="$emit('reply', comment.id)">回复</el-button>
        <el-button v-if="comment.can_delete" type="danger" link @click="$emit('delete', comment.id)">
          删除
        </el-button>
      </div>
      <div v-if="replyingId === comment.id" class="reply-box">
        <el-input
          v-model="replyContent"
          :rows="2"
          type="textarea"
          maxlength="2000"
          show-word-limit
          placeholder="输入回复内容"
        />
        <div class="reply-actions">
          <el-button size="small" @click="$emit('cancel-reply')">取消</el-button>
          <el-button size="small" type="primary" @click="$emit('submit-reply', comment.id, replyContent)">
            发送
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="comment.replies?.length" class="replies">
      <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
        <div class="comment-head">
          <span class="author">{{ reply.author_name || reply.author_username }}</span>
          <span class="time">{{ formatDate(reply.created_at) }}</span>
        </div>
        <div class="comment-content">{{ reply.content }}</div>
        <div class="comment-actions">
          <el-button v-if="reply.can_delete" type="danger" link @click="$emit('delete', reply.id)">
            删除
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { formatDate } from '@/utils'
import type { ProjectComment } from '@/types/project'

const props = defineProps<{
  comment: ProjectComment
  replyingId: number | null
}>()

defineEmits<{
  (e: 'reply', commentId: number): void
  (e: 'cancel-reply'): void
  (e: 'submit-reply', commentId: number, content: string): void
  (e: 'delete', commentId: number): void
}>()

const replyContent = ref('')

watch(
  () => props.replyingId,
  (val) => {
    if (val !== props.comment.id) {
      replyContent.value = ''
    }
  }
)
</script>

<style scoped>
.comment-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
}
.comment-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.author {
  font-weight: 600;
  color: #303133;
}
.time {
  color: #909399;
  font-size: 12px;
}
.comment-content {
  margin-top: 8px;
  white-space: pre-wrap;
  line-height: 1.6;
}
.comment-actions {
  margin-top: 8px;
}
.replies {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--el-border-color-lighter);
  display: grid;
  gap: 10px;
}
.reply-item {
  padding: 10px;
  background: #fafafa;
  border-radius: 6px;
}
.reply-box {
  margin-top: 10px;
}
.reply-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
