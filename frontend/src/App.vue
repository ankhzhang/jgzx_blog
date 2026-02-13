<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <!-- 只在登录后显示导航栏 -->
    <el-container v-if="authStore.isAuthenticated">
      <el-header>
        <div class="header-content">
          <div class="logo">
            <h2>JGZX 平台</h2>
          </div>
          <div class="nav-menu">
            <router-link to="/">首页</router-link>
            <router-link to="/profile">个人资料</router-link>
            <router-link to="/projects">项目</router-link>
            <router-link v-if="authStore.isAdmin" to="/admin">管理</router-link>
          </div>
          <div class="user-info">
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                {{ authStore.fullName }}
                <el-icon><arrow-down /></el-icon>
              </span>
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
                  <el-dropdown-item command="createProject">
                    <el-icon><Plus /></el-icon>
                    发布项目
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" command="admin">
                    <el-icon><Setting /></el-icon>
                    管理后台
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>

    <!-- 未登录时只显示路由内容（登录页/注册页） -->
    <router-view v-else />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import {ArrowDown, Lock, Plus, Setting, User} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const handleCommand = async (command: string) => {
  if (command === 'logout') {
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
  } else {
    router.push(command)
  }
}
</script>

<style scoped>
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  color: #409eff;
  font-weight: 600;
}

.nav-menu {
  flex: 1;
  margin-left: 40px;
}

.nav-menu a {
  margin-right: 20px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
}

.nav-menu a.router-link-active {
  color: #409eff;
  font-weight: 500;
}

.user-dropdown {
  cursor: pointer;
  color: #333;
}

.el-main {
  flex: 1;
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
