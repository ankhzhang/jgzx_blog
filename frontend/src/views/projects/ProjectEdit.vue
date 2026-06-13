<template>
  <div class="project-edit-page">
    <el-card v-loading="loading" class="form-card">
      <template #header>
        <div class="card-header flex-between">
          <h3>编辑项目</h3>
          <el-button @click="$router.push(`/projects/${id}`)">返回详情</el-button>
        </div>
      </template>

      <template v-if="project">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="project-form"
        >
          <el-form-item label="项目标题" prop="title">
            <el-input v-model="form.title" placeholder="1–100 字" maxlength="100" show-word-limit />
          </el-form-item>
          <el-form-item label="项目类别" prop="category">
            <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
              <el-option label="教师科研项目" value="teacher_research" />
              <el-option label="学科竞赛" value="subject_competition" />
              <el-option label="大创项目-创新类" value="innovation_innov" />
              <el-option label="大创项目-创业类" value="innovation_venture" />
            </el-select>
          </el-form-item>
          <el-form-item label="自定义标签">
            <el-input-tag
              v-model="form.tags"
              placeholder="输入后按回车添加，如 AI、深度学习"
              :max="5"
              style="width: 100%"
            />
            <div class="form-tip block-tip">用于补充项目方向，与上方类别不同，最多 5 个，每个不超过 20 字</div>
          </el-form-item>
          <el-form-item label="项目描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="8"
              placeholder="至少 100 字"
              maxlength="5000"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="招募人数" prop="recruit_count">
            <el-input-number v-model="form.recruit_count" :min="1" :max="20" />
          </el-form-item>
          <el-form-item label="联系方式" prop="contact_info">
            <el-input
              v-model="form.contact_info"
              placeholder="如：手机号、微信号、邮箱等"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="技能要求">
            <div class="skill-editor">
              <div
                v-for="(item, index) in form.skill_requirements"
                :key="index"
                class="skill-row"
              >
                <el-input
                  v-model="(item as { desc: string; count: number }).desc"
                  placeholder="描述"
                  style="flex: 1; margin-right: 8px"
                />
                <el-input-number
                  v-model="(item as { desc: string; count: number }).count"
                  :min="1"
                  :max="10"
                  style="width: 100px"
                />
                <el-button type="danger" link @click="form.skill_requirements.splice(index, 1)">
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
          <el-form-item label="结束后可见">
            <el-switch v-model="form.is_visible_when_ended" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
            <el-button @click="$router.push(`/projects/${id}`)">取消</el-button>
          </el-form-item>
        </el-form>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { projectAPI } from '@/api/project'
import type { ProjectDetail, ProjectCreateUpdatePayload, SkillItem } from '@/types/project'

const route = useRoute()
const router = useRouter()
const id = computed(() => Number(route.params.id))

const loading = ref(true)
const submitting = ref(false)
const project = ref<ProjectDetail | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<ProjectCreateUpdatePayload & { skill_requirements: { desc: string; count: number }[]; tags: string[] }>({
  title: '',
  description: '',
  category: 'teacher_research',
  recruit_count: 1,
  contact_info: '',
  tags: [],
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
  contact_info: [
    { required: true, message: '请填写联系方式', trigger: 'blur' },
    { min: 1, max: 200, message: '1–200 字', trigger: 'blur' }
  ],
  deadline: [{ required: true, message: '请选择截止时间', trigger: 'change' }]
}

function disabledDate(time: Date) {
  return time.getTime() < Date.now()
}

async function loadProject() {
  if (!id.value) return
  loading.value = true
  try {
    const res = await projectAPI.getDetail(id.value)
    project.value = res.data
    const p = res.data
    if (!p) return
    form.title = p.title
    form.description = p.description
    form.category = p.category
    form.recruit_count = p.recruit_count
    form.contact_info = p.contact_info || ''
    form.tags = [...(p.tags || [])]
    form.deadline = p.deadline
    form.is_visible_when_ended = p.is_visible_when_ended
    const skills = p.skill_requirements || []
    form.skill_requirements = skills.map((s: SkillItem) =>
      typeof s === 'string' ? { desc: s, count: 1 } : { desc: s.desc, count: s.count }
    )
    if (form.skill_requirements.length === 0) form.skill_requirements.push({ desc: '', count: 1 })
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!formRef.value || !project.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  const skills: SkillItem[] = form.skill_requirements
    .filter((s) => (s as { desc: string }).desc?.trim())
    .map((s) => ({ desc: (s as { desc: string }).desc.trim(), count: (s as { count: number }).count }))
  submitting.value = true
  try {
    const tags = form.tags.map((t) => t.trim()).filter(Boolean)
    await projectAPI.update(project.value.id, {
      title: form.title,
      description: form.description,
      category: form.category,
      recruit_count: form.recruit_count,
      contact_info: form.contact_info,
      tags,
      skill_requirements: skills.length ? skills : undefined,
      deadline: form.deadline,
      is_visible_when_ended: form.is_visible_when_ended
    }, project.value.version)
    ElMessage.success('保存成功')
    router.push(`/projects/${project.value.id}`)
  } finally {
    submitting.value = false
  }
}

onMounted(loadProject)
</script>

<style scoped>
.project-edit-page {
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
  font-size: 12px;
  color: #909399;
}

.block-tip {
  margin-top: 6px;
}
</style>
