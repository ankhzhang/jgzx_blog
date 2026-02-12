<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-left">
        <div class="brand">
          <h1>JGZX 平台</h1>
          <p>学生项目协同平台</p>
        </div>
        <div class="features">
          <div class="feature-item">
            <el-icon><User /></el-icon>
            <span>学生/教师身份支持</span>
          </div>
          <div class="feature-item">
            <el-icon><Document /></el-icon>
            <span>项目发布与管理</span>
          </div>
          <div class="feature-item">
            <el-icon><ChatDotRound /></el-icon>
            <span>实时交流互动</span>
          </div>
        </div>
      </div>

      <div class="login-right">
        <el-card class="login-card" shadow="never">
          <template #header>
            <div class="login-header">
              <h2>登录账号</h2>
              <p class="subtitle">使用学号/工号登录</p>
            </div>
          </template>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="学号/工号"
                size="large"
                :prefix-icon="User"
                clearable
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                clearable
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <div class="login-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="authStore.isLoading"
                @click="handleLogin"
                class="login-button"
              >
                登录
              </el-button>
            </el-form-item>

            <div class="register-prompt">
              还没有账号？
              <router-link to="/register" class="register-link">
                立即注册
              </router-link>
            </div>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Document, ChatDotRound } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入学号/工号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

onMounted(() => {
  const savedUsername = localStorage.getItem('remembered_username')
  if (savedUsername) {
    loginForm.username = savedUsername
    rememberMe.value = true
  }
})

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()

    const result = await authStore.login(loginForm)

    if (result.success) {
      if (rememberMe.value) {
        localStorage.setItem('remembered_username', loginForm.username)
      } else {
        localStorage.removeItem('remembered_username')
      }

      ElMessage.success('登录成功')

      const redirect = router.currentRoute.value.query.redirect as string
      router.push(redirect || '/')
    }
  } catch (error) {
    console.error('登录失败:', error)
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-wrapper {
  display: flex;
  max-width: 1000px;
  width: 100%;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand h1 {
  font-size: 36px;
  margin: 0 0 10px;
  font-weight: 700;
}

.brand p {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
}

.features {
  margin-top: 60px;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
  font-size: 16px;
}

.feature-item .el-icon {
  margin-right: 15px;
  font-size: 24px;
}

.login-right {
  flex: 1;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 100%;
  max-width: 360px;
  border: none;
  background: transparent;
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 700;
}

.login-header .subtitle {
  margin: 8px 0 0;
  color: #999;
  font-size: 14px;
}

.login-options {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.register-prompt {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.register-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
    max-width: 400px;
  }

  .login-left {
    padding: 40px 20px;
  }

  .login-right {
    padding: 30px 20px;
  }
}
</style>
