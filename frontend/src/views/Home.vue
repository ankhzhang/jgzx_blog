<!-- frontend/src/views/Home.vue -->
<template>
  <div class="home">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="logo">
            <h2>JGZX 平台</h2>
          </div>
          <div class="user-info flex-center">
            <span class="welcome">欢迎，{{ authStore.fullName }}</span>
            <el-dropdown @command="handleCommand">
              <el-avatar 
                :size="32" 
                :src="authStore.user?.avatar || undefined"
                class="cursor-pointer"
              >
                {{ authStore.fullName?.charAt(0) || '用' }}
              </el-avatar>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人资料
                  </el-dropdown-item>
                  <el-dropdown-item command="changePassword">
                    <el-icon><Lock /></el-icon>
                    修改密码
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isTeacher" command="createProject">
                    <el-icon><Plus /></el-icon>
                    发布项目
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" command="admin">
                    <el-icon><Setting /></el-icon>
                    管理后台
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <el-card class="welcome-card" shadow="hover">
          <template #header>
            <div class="card-header flex-between">
              <h3>系统公告</h3>
              <el-tag type="success">最新</el-tag>
            </div>
          </template>
          
          <el-result
            icon="success"
            :title="`欢迎回来，${authStore.fullName}`"
            :sub-title="`您是${authStore.isStudent ? '学生' : '教师'}身份`"
          >
            <template #extra>
              <el-button type="primary" @click="goToProfile">
                查看个人资料
              </el-button>
              <el-button @click="goToProjects">
                浏览项目
              </el-button>
            </template>
          </el-result>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { User, Lock, Plus, Setting, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'changePassword':
      router.push('/change-password')
      break
    case 'createProject':
      router.push('/projects/create')
      break
    case 'admin':
      router.push('/admin')
      break
    case 'logout':
      await handleLogout()
      break
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    // 用户取消操作
  }
}

// 跳转到个人资料
const goToProfile = () => {
  router.push('/profile')
}

// 跳转到项目列表
const goToProjects = () => {
  router.push('/projects')
}

onMounted(() => {
  console.log('首页已加载')
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

.el-header {
  background-color: var(--el-bg-color);
  box-shadow: var(--el-box-shadow-light);
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  color: var(--el-color-primary);
  font-weight: 600;
}

.user-info {
  gap: 16px;
}

.welcome {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.el-main {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 24px;
}

.welcome-card {
  margin-top: 20px;
  border-radius: 8px;
  transition: all 0.3s;
}

.welcome-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow);
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
}
</style>