<template>
  <div class="class-course">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 16px; font-weight: bold;">班级课程</span>
          <el-button type="primary" @click="handleAddCourse">
            <el-icon><Plus /></el-icon>
            <span>新增</span>
          </el-button>
        </div>
      </template>

      <el-table :data="classList" v-loading="loading" stripe style="width: 100%; cursor: pointer;">
        <el-table-column prop="id" label="班级ID" width="80"></el-table-column>
        <el-table-column prop="name" label="班级名称"></el-table-column>
        <el-table-column label="课程" width="300">
          <template #default="{row}">
            <el-tag v-for="course in row.courses" :key="course.course_id" style="margin-right: 4px;" type="info">
              {{ course.course_name }}
            </el-tag>
            <span v-if="!row.courses || row.courses.length === 0" style="color: #999;">暂无课程</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" @click="showCourses(row)">
              <el-icon><Setting /></el-icon>
              <span>管理课程</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增课程弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增课程" width="500px">
      <el-form :model="addForm" :rules="addRules" ref="addFormRef" label-width="100px">
        <el-form-item label="选择班级" prop="class_id">
          <el-select v-model="addForm.class_id" placeholder="请选择班级" style="width: 300px;">
            <el-option v-for="class_ in classList" :key="class_.id" :label="class_.name" :value="class_.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="选择课程" prop="course_id">
          <el-select v-model="addForm.course_id" placeholder="请选择课程" style="width: 300px;">
            <el-option v-for="course in allCourses" :key="course.id" :label="course.name" :value="course.id"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">
          <el-icon><Close /></el-icon>
          <span>取消</span>
        </el-button>
        <el-button type="success" @click="submitAddCourse">
          <el-icon><Check /></el-icon>
          <span>确定</span>
        </el-button>
      </template>
    </el-dialog>

    <!-- 管理课程弹窗 -->
    <el-dialog v-model="dialogVisible" :title="'管理课程 - ' + (currentClass?.name || '')" width="600px">
      <div style="margin-bottom: 10px; display: flex; align-items: center;">
        <el-select v-model="selectedCourseId" placeholder="选择要添加的课程" style="width: 300px; margin-right: 10px;" filterable>
          <el-option v-for="course in availableCourses" :key="course.id" :label="course.name" :value="course.id"></el-option>
        </el-select>
        <el-button type="primary" @click="addCourse">
          <el-icon><Plus /></el-icon>
          <span>添加</span>
        </el-button>
      </div>

      <el-table :data="classCourses" stripe style="width: 100%;">
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button size="small" type="danger" @click="removeCourse(row)">
              <el-icon><Delete /></el-icon>
              <span>移除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import { Plus, Setting, Close, Check, Delete } from '@element-plus/icons-vue'

const classList = ref([])
const classCourses = ref([])
const allCourses = ref([])
const currentClass = ref(null)
const selectedCourseId = ref(null)
const dialogVisible = ref(false)
const addDialogVisible = ref(false)
const loading = ref(false)

// 新增课程表单
const addForm = ref({ class_id: null, course_id: null })
const addRules = {
  class_id: [{ required: true, message: '请选择班级', trigger: 'blur' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'blur' }]
}
const addFormRef = ref(null)

// 计算可选课程（排除已添加的课程）
const availableCourses = computed(() => {
  const addedIds = classCourses.value.map(c => c.course_id)
  return allCourses.value.filter(c => !addedIds.includes(c.id))
})

const fetchClasses = async () => {
  loading.value = true
  try {
    const response = await api.get('/classes', { params: { page: 1, per_page: 100 } })
    // 处理不同的数据格式
    classList.value = response.data.items || response.data || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取班级列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCourses = async () => {
  try {
    const response = await api.get('/courses', { params: { page: 1, per_page: 100 } })
    // 处理不同的数据格式
    allCourses.value = response.data.items || response.data || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取课程列表失败')
  }
}

const showCourses = async (class_) => {
  currentClass.value = class_
  dialogVisible.value = true
  selectedCourseId.value = null
  try {
    const response = await api.get(`/classes/${class_.id}`)
    classCourses.value = response.data.courses || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取课程列表失败')
  }
}

const handleAddCourse = () => {
  addForm.value = { class_id: null, course_id: null }
  addDialogVisible.value = true
}

const submitAddCourse = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await api.post(`/classes/${addForm.value.class_id}/courses`, { course_id: addForm.value.course_id })
        ElMessage.success('添加成功')
        addDialogVisible.value = false
        fetchClasses()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '添加失败')
      }
    }
  })
}

const addCourse = async () => {
  if (!selectedCourseId.value || !currentClass.value) {
    ElMessage.warning('请先选择课程')
    return
  }
  try {
    await api.post(`/classes/${currentClass.value.id}/courses`, { course_id: selectedCourseId.value })
    ElMessage.success('添加成功')
    showCourses(currentClass.value)
    fetchClasses()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '添加失败')
  }
}

const removeCourse = async (row) => {
  try {
    await api.delete(`/classes/${currentClass.value.id}/courses/${row.course_id}`)
    ElMessage.success('移除成功')
    showCourses(currentClass.value)
    fetchClasses()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '移除失败')
  }
}

onMounted(() => {
  fetchClasses()
  fetchCourses()
})
</script>
