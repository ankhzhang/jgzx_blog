// import './assets/main.css'
//
// import { createApp } from 'vue'
// import { createPinia } from 'pinia'
//
// import App from './App.vue'
// import router from './router'
//
// const app = createApp(App)
//
// app.use(createPinia())
// app.use(router)
//
// app.mount('#app')


import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'  // 中文语言包
import App from './App.vue'
import router from './router'
import './styles/main.css'

// 创建 Vue 应用实例
const app = createApp(App)

// 创建 Pinia 实例并添加持久化插件
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,  // 使用中文
  size: 'default',  // 组件默认尺寸
  zIndex: 3000  // 弹窗默认z-index
})

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err)
  console.error('错误信息:', info)
}

// 全局挂载
app.mount('#app')

// 开发环境提示
if (import.meta.env.DEV) {
  console.log('应用运行在开发环境')
  console.log('API地址:', import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api')
}
