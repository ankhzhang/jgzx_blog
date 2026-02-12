<template>
  <div class="register-container">
    <el-card class="register-card" shadow="hover">
      <template #header>
        <div class="register-header">
          <h2>注册账号</h2>
          <p class="subtitle">请填写以下信息完成注册</p>
        </div>
      </template>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="身份" prop="identity">
          <el-radio-group v-model="registerForm.identity">
            <el-radio label="student" size="large">
              <span class="identity-option">
                <el-icon><User /></el-icon>
                <span>学生</span>
              </span>
            </el-radio>
<!--            <el-radio label="teacher" size="large">-->
<!--              <span class="identity-option">-->
<!--                <el-icon><Briefcase /></el-icon>-->
<!--                <span>教师</span>-->
<!--              </span>-->
<!--            </el-radio>-->
          </el-radio-group>
        </el-form-item>

        <el-divider content-position="left">账号信息</el-divider>

        <el-form-item
          :label="registerForm.identity === 'student' ? '学号' : '工号'"
          prop="username"
        >
          <el-input
            v-model="registerForm.username"
            :placeholder="registerForm.identity === 'student' ? '请输入学号' : '请输入工号'"
            :prefix-icon="Document"
            clearable
          />
        </el-form-item>

        <el-form-item label="姓名" prop="real_name">
          <el-input
            v-model="registerForm.real_name"
            placeholder="请输入真实姓名"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            clearable
          />
          <div class="form-tip">密码长度至少6位</div>
        </el-form-item>

        <el-form-item label="确认密码" prop="password2">
          <el-input
            v-model="registerForm.password2"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-divider content-position="left">联系方式</el-divider>

        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号"
            :prefix-icon="Phone"
            clearable
          />
        </el-form-item>

        <el-form-item label="院系" prop="department">
          <el-select
            v-model="registerForm.department"
            placeholder="请选择院系"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="dept in departments"
              :key="dept"
              :label="dept"
              :value="dept"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <el-button
              type="primary"
              :loading="authStore.isLoading"
              @click="handleRegister"
              class="submit-button"
              size="large"
            >
              立即注册
            </el-button>
            <el-button @click="$router.push('/login')" size="large">
              返回登录
            </el-button>
          </div>
        </el-form-item>

<!--        <div class="agreement">-->
<!--          <el-checkbox v-model="agreed">-->
<!--            我已阅读并同意-->
<!--            <el-link type="primary" :underline="false">《用户协议》</el-link>-->
<!--            和-->
<!--            <el-link type="primary" :underline="false">《隐私政策》</el-link>-->
<!--          </el-checkbox>-->
<!--        </div>-->
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Document, Phone, Briefcase } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { RegisterData } from '@/types/user'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref<FormInstance>()
const agreed = ref(false)

const registerForm = reactive<RegisterData>({
  identity: 'student',
  username: '',
  real_name: '',
  password: '',
  password2: '',
  phone: '',
  department: ''
})

const departments = [
  '管理学院',
  '统计学院',
  '物流学院',
]

const validateUsername = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error(registerForm.identity === 'student' ? '请输入学号' : '请输入工号'))
  } else {
    callback()
  }
}

const validatePassword = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

const validatePassword2 = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validatePhone = (rule: any, value: string, callback: any) => {
  if (value && !/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  identity: [
    { required: true, message: '请选择身份', trigger: 'change' }
  ],
  username: [
    { validator: validateUsername, trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  password2: [
    { validator: validatePassword2, trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择院系', trigger: 'change' }
  ]
}

watch(() => registerForm.identity, () => {
  registerForm.username = ''
})

const handleRegister = async () => {
  if (!registerFormRef.value) return

  // if (!agreed.value) {
  //   ElMessage.warning('请先阅读并同意用户协议和隐私政策')
  //   return
  // }

  try {
    await registerFormRef.value.validate()

    const result = await authStore.register(registerForm)

    if (result.success) {
      ElMessage.success('注册成功！')
      router.push('/')
    }
  } catch (error) {
    console.error('注册失败:', error)
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.register-card {
  width: 100%;
  max-width: 700px;
  border-radius: 16px;
}

.register-header {
  text-align: center;
  padding: 20px 0 10px;
}

.register-header h2 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 700;
}

.register-header .subtitle {
  margin: 8px 0 0;
  color: #999;
  font-size: 14px;
}

.identity-option {
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.submit-button {
  flex: 1;
  height: 48px;
  font-size: 16px;
}

.agreement {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}
</style>
