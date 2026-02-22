<template>
  <div class="manage-users-page">
    <el-card class="toolbar-card">
      <div class="toolbar flex-between">
        <h3 class="page-title">用户管理（管理员）</h3>
        <el-input
          v-model="keyword"
          placeholder="按学号/工号、姓名或院系搜索"
          clearable
          style="width: 260px"
          @keyup.enter="fetchList"
        >
          <template #append>
            <el-button @click="fetchList">搜索</el-button>
          </template>
        </el-input>
      </div>
    </el-card>

    <el-card v-loading="loading" class="table-card">
      <el-table :data="list" stripe style="width: 100%">
        <el-table-column prop="username" label="学号/工号" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="identity" label="身份" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.identity === 'teacher' ? 'success' : 'info'">
              {{ row.identity === 'teacher' ? '教师' : '学生' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="院系" min-width="140" show-overflow-tooltip />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column prop="is_staff" label="管理员" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.is_staff" type="warning" size="small">管理员</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_banned" label="封禁" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.is_banned" type="danger" size="small">已封禁</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="ban_reason" label="封禁原因" min-width="160" show-overflow-tooltip />
        <el-table-column prop="banned_until" label="封禁截止" width="140">
          <template #default="{ row }">
            {{ row.banned_until ? formatDate(row.banned_until) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="toggleAdmin(row)">
              {{ row.is_staff ? '取消管理员' : '设为管理员' }}
            </el-button>
            <el-divider direction="vertical" />
            <el-button
              v-if="!row.is_banned"
              type="danger"
              link
              @click="openBan(row)"
            >
              封禁
            </el-button>
            <el-button
              v-else
              type="success"
              link
              @click="unban(row)"
            >
              解封
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="banVisible" title="封禁用户" width="420px">
      <p>封禁用户：{{ currentUser?.real_name }}（{{ currentUser?.username }}）</p>
      <el-form :model="banForm" label-width="80px" style="margin-top: 12px">
        <el-form-item label="原因">
          <el-input
            v-model="banForm.ban_reason"
            type="textarea"
            :rows="3"
            placeholder="请填写封禁原因"
          />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="banForm.banned_until"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="可选，留空为永久封禁"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="banVisible = false">取消</el-button>
        <el-button type="primary" :loading="banSubmitting" @click="doBan">确定封禁</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authAPI } from '@/api/auth'
import { formatDate } from '@/utils'
import type { UserProfile } from '@/types/user'

const loading = ref(false)
const list = ref<UserProfile[]>([])
const keyword = ref('')

const banVisible = ref(false)
const banSubmitting = ref(false)
const currentUser = ref<UserProfile | null>(null)
const banForm = ref<{
  ban_reason: string
  banned_until: string | null
}>({
  ban_reason: '',
  banned_until: null
})

async function fetchList() {
  loading.value = true
  try {
    if (keyword.value.trim()) {
      const res = await authAPI.searchUsers(keyword.value.trim())
      list.value = res.data ?? []
    } else {
      const res = await authAPI.getUsers()
      list.value = res.data ?? []
    }
  } finally {
    loading.value = false
  }
}

async function toggleAdmin(user: UserProfile) {
  const target = !user.is_staff
  try {
    await ElMessageBox.confirm(
      target
        ? `确定将 ${user.real_name} 设为管理员吗？`
        : `确定取消 ${user.real_name} 的管理员权限吗？`,
      '提示',
      {
        type: 'warning'
      }
    )
  } catch {
    return
  }
  try {
    const res = await authAPI.setUserAdmin(user.id, target)
    const updated = res.data
    list.value = list.value.map((u) => (u.id === updated.id ? updated : u))
    ElMessage.success(target ? '已设为管理员' : '已取消管理员')
  } catch (e) {
    console.error(e)
  }
}

function openBan(user: UserProfile) {
  currentUser.value = user
  banForm.value.ban_reason = ''
  banForm.value.banned_until = null
  banVisible.value = true
}

async function doBan() {
  if (!currentUser.value) return
  if (!banForm.value.ban_reason.trim()) {
    ElMessage.warning('请填写封禁原因')
    return
  }
  banSubmitting.value = true
  try {
    const res = await authAPI.banUser(currentUser.value.id, {
      ban_reason: banForm.value.ban_reason.trim(),
      banned_until: banForm.value.banned_until
    })
    const updated = res.data
    list.value = list.value.map((u) => (u.id === updated.id ? updated : u))
    ElMessage.success('已封禁用户')
    banVisible.value = false
  } finally {
    banSubmitting.value = false
  }
}

async function unban(user: UserProfile) {
  try {
    await ElMessageBox.confirm(`确定要解封 ${user.real_name} 吗？`, '提示', {
      type: 'warning'
    })
  } catch {
    return
  }
  try {
    const res = await authAPI.unbanUser(user.id)
    const updated = res.data
    list.value = list.value.map((u) => (u.id === updated.id ? updated : u))
    ElMessage.success('已解封用户')
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.manage-users-page {
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

.table-card {
  border-radius: 12px;
}
</style>
