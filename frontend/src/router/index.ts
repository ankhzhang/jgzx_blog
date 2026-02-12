import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由配置表
const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '首页',
      requiresAuth: true  // 需要登录
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/Login.vue'),
    meta: {
      title: '登录',
      requiresGuest: true  // 仅游客可访问
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/Register.vue'),
    meta: {
      title: '注册',
      requiresGuest: true  // 仅游客可访问
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/user/Profile.vue'),
    meta: {
      title: '个人资料',
      requiresAuth: true  // 需要登录
    }
  },
  {
    path: '/change-password',
    name: 'changePassword',
    component: () => import('@/views/user/ChangePassword.vue'),
    meta: {
      title: '修改密码',
      requiresAuth: true  // 需要登录
    }
  },
  // {
  //   path: '/admin',
  //   name: 'admin',
  //   redirect: '/admin/users',
  //   meta: {
  //     title: '管理后台',
  //     requiresAuth: true,
  //     requiresAdmin: true  // 需要管理员权限
  //   }
  // },
  // {
  //   path: '/admin/users',
  //   name: 'userList',
  //   component: () => import('@/views/admin/UserList.vue'),
  //   meta: {
  //     title: '用户管理',
  //     requiresAuth: true,
  //     requiresAdmin: true  // 需要管理员权限
  //   }
  // },
  // {
  //   path: '/admin/users/:id',
  //   name: 'userDetail',
  //   component: () => import('@/views/admin/UserDetail.vue'),
  //   meta: {
  //     title: '用户详情',
  //     requiresAuth: true,
  //     requiresAdmin: true  // 需要管理员权限
  //   }
  // },
  {
    path: '/403',
    name: 'forbidden',
    component: () => import('@/views/errors/Forbidden.vue'),
    meta: {
      title: '无权限访问'
    }
  },
  {
    path: '/404',
    name: 'notFound',
    component: () => import('@/views/errors/NotFound.vue'),
    meta: {
      title: '页面不存在'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 返回顶部
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'JGZX平台'} - JGZX平台`

  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  const isAdmin = authStore.isAdmin

  // 需要登录的页面
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // 未登录，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }  // 保存重定向地址
      })
      return
    }

    // 需要管理员权限的页面
    if (to.meta.requiresAdmin && !isAdmin) {
      next('/403')  // 无权限
      return
    }
  }

  // 仅游客可访问的页面（登录后不可访问）
  if (to.meta.requiresGuest && isAuthenticated) {
    next('/')  // 已登录，跳转到首页
    return
  }

  next()
})

// 全局后置守卫
router.afterEach((to) => {
  // 可以在这里做统计等操作
  console.log(`页面访问: ${to.fullPath}`)
})

export default router
