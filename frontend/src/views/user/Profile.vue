<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8" :md="6">
        <el-card class="profile-card">
          <div class="profile-avatar">
            <el-avatar
              :size="120"
              :src="user?.avatar || undefined"
            >
              {{ fullName.charAt(0) }}
            </el-avatar>
            <div class="user-name">{{ fullName }}</div>
            <div class="user-role">
              <el-tag :type="user?.identity === 'teacher' ? 'success' : 'info'">
                {{ user?.identity === 'teacher' ? '教师' : '学生' }}
              </el-tag>
            </div>
          </div>

          <el-divider />

          <div class="profile-stats">
            <div class="stat-item">
              <div class="stat-label">发布项目</div>
              <div class="stat-value">{{ user?.project_count || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">评论数量</div>
              <div class="stat-value">{{ user?.comment_count || 0 }}</div>
            </div>
          </div>

          <div class="profile-info">
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span>用户名：{{ user?.username }}</span>
            </div>
            <div class="info-item">
              <el-icon><OfficeBuilding /></el-icon>
              <span>院系：{{ user?.department || '未填写' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Phone /></el-icon>
              <span>手机：{{ user?.phone || '未填写' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Message /></el-icon>
              <span>邮箱：{{ user?.email || '未设置' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Clock /></el-icon>
              <span>注册时间：{{ formatDate(user?.date_joined) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="16" :md="18">
        <el-card class="profile-edit-card">
          <template #header>
            <div class="card-header">
              <h3>编辑个人资料</h3>
            </div>
          </template>

          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="80px"
          >
            <el-form-item label="院系" prop="department">
              <el-select
                v-model="profileForm.department"
                placeholder="请选择院系"
                style="width: 100%"
              >
                <el-option
                  v-for="dept in departments"
                  :key="dept"
                  :label="dept"
                  :value="dept"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="profileForm.phone"
                placeholder="请输入手机号"
              />
            </el-form-item>

            <el-form-item label="个人简介" prop="bio">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="4"
                placeholder="介绍一下自己吧"
              />
            </el-form-item>

            <el-divider />

            <div class="form-actions">
              <el-button
                type="primary"
                :loading="authStore.isLoading"
                @click="handleSubmit"
              >
                保存修改
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </div>
          </el-form>
        </el-card>

        <el-card class="profile-edit-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <h3>账号安全</h3>
            </div>
          </template>

          <div class="security-items">
            <div class="security-item">
              <div class="security-info">
                <div class="security-title">登录密码</div>
                <div class="security-desc">定期更改密码可以提高账号安全性</div>
              </div>
              <div class="security-action">
                <el-button type="primary" link @click="$router.push('/change-password')">
                  修改密码
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, OfficeBuilding, Phone, Message, Clock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils'

const authStore = useAuthStore()
const profileFormRef = ref<FormInstance>()

const user = computed(() => authStore.user)
const fullName = computed(() => authStore.fullName)

const profileForm = reactive({
  department: '',
  phone: '',
  bio: ''
})

const departments = [
  '管理学院',
  '统计学院',
  '物流学院',
]

const profileRules: FormRules = {
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

onMounted(() => {
  if (user.value) {
    profileForm.department = user.value.department || ''
    profileForm.phone = user.value.phone || ''
    profileForm.bio = user.value.bio || ''
  }
})

const handleSubmit = async () => {
  if (!profileFormRef.value) return

  try {
    await profileFormRef.value.validate()

    const result = await authStore.updateProfile(profileForm)

    if (result.success) {
      ElMessage.success('个人资料更新成功')
    }
  } catch (error) {
    console.error('更新失败:', error)
  }
}

const resetForm = () => {
  if (user.value) {
    profileForm.department = user.value.department || ''
    profileForm.phone = user.value.phone || ''
    profileForm.bio = user.value.bio || ''
  }
}
</script>

<style scoped>
.profile-container {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card {
  text-align: center;
}

.profile-avatar {
  padding: 30px 0 20px;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-top: 10px;
}

.user-role {
  margin-top: 8px;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.profile-info {
  text-align: left;
  padding: 0 10px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.info-item .el-icon {
  margin-right: 10px;
  color: #409eff;
  font-size: 16px;
}

.profile-edit-card {
  border-radius: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
}

.security-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.security-desc {
  font-size: 14px;
  color: #999;
}
</style>
