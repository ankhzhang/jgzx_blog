<template>
  <div class="project-create-page">
    <el-card class="form-card">
      <template #header>
        <div class="card-header flex-between">
          <h3>发布项目</h3>
          <el-button @click="$router.push('/projects')">返回列表</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="project-form"
      >
        <el-form-item label="项目标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="1–100 字"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="项目类别" prop="category">
          <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
            <el-option label="教师科研项目" value="teacher_research" />
            <el-option label="学科竞赛" value="subject_competition" />
            <el-option label="大创项目-创新类" value="innovation_innov" />
            <el-option label="大创项目-创业类" value="innovation_venture" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="8"
            placeholder="至少 100 字，不超过 5000 字"
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="招募人数" prop="recruit_count">
          <el-input-number
            v-model="form.recruit_count"
            :min="1"
            :max="20"
          />
        </el-form-item>
        <el-form-item label="技能要求" prop="skill_requirements">
          <div class="skill-editor">
            <div
              v-for="(item, index) in form.skill_requirements"
              :key="index"
              class="skill-row"
            >
              <el-input
                v-model="(item as { desc: string; count: number }).desc"
                placeholder="如：会 Python，大二优先"
                style="flex: 1; margin-right: 8px"
              />
              <el-input-number
                v-model="(item as { desc: string; count: number }).count"
                :min="1"
                :max="10"
                style="width: 100px"
              />
              <el-button
                type="danger"
                link
                @click="form.skill_requirements.splice(index, 1)"
              >
                删除
              </el-button>
            </div>
            <el-button
              v-if="form.skill_requirements.length < 10"
              type="primary"
              link
              @click="form.skill_requirements.push({ desc: '', count: 1 })"
            >
              + 添加一条
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker
            v-model="form.deadline"
            type="datetime"
            placeholder="选择截止时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="结束后可见" prop="is_visible_when_ended">
          <el-switch v-model="form.is_visible_when_ended" />
          <span class="form-tip">已招满/已结束后是否对他人可见</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit(true)">
            保存草稿
          </el-button>
          <el-button type="success" :loading="submitting" @click="submit(false)">
            提交发布
          </el-button>
          <el-button @click="$router.push('/projects')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { projectAPI } from '@/api/project'
import type { ProjectCreateUpdatePayload, SkillItem } from '@/types/project'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive<ProjectCreateUpdatePayload & { skill_requirements: { desc: string; count: number }[] }>({
  title: '',
  description: '',
  category: 'teacher_research',
  recruit_count: 1,
  skill_requirements: [],
  deadline: '',
  is_visible_when_ended: true
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 1, max: 100, message: '1–100 字', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入项目描述', trigger: 'blur' },
    { min: 100, message: '至少 100 字', trigger: 'blur' }
  ],
  category: [{ required: true, message: '请选择类别', trigger: 'change' }],
  recruit_count: [
    { required: true, message: '请填写招募人数', trigger: 'blur' },
    { type: 'number', min: 1, max: 20, message: '1–20', trigger: 'blur' }
  ],
  deadline: [{ required: true, message: '请选择截止时间', trigger: 'change' }]
}

function disabledDate(time: Date) {
  return time.getTime() < Date.now()
}

async function submit(isDraft: boolean) {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  const skills: SkillItem[] = form.skill_requirements
    .filter((s) => (s as { desc: string }).desc?.trim())
    .map((s) => ({ desc: (s as { desc: string }).desc.trim(), count: (s as { count: number }).count }))
  if (skills.length > 0) {
    const total = skills.reduce((a, b) => a + (typeof b === 'object' && 'count' in b ? b.count : 1), 0)
    if (total > form.recruit_count) {
      ElMessage.warning('技能需求总人数不能超过招募人数')
      return
    }
  }
  submitting.value = true
  try {
    const res = await projectAPI.create({
      ...form,
      skill_requirements: skills,
      is_draft: isDraft
    })
    ElMessage.success(isDraft ? '草稿已保存' : '已提交审核')
    router.push(res.data?.id ? `/projects/${res.data.id}` : '/projects/my')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.project-create-page {
  max-width: 800px;
  margin: 0 auto;
}

.form-card {
  border-radius: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.skill-editor .skill-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.form-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
