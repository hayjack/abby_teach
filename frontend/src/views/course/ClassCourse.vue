<template>
  <div class="class-course">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>班级课程管理</span>
          <el-button type="primary" @click="handleAdd">为班级添加课程</el-button>
        </div>
      </template>

      <el-table :data="classList" v-loading="loading">
        <el-table-column prop="id" label="班级ID"></el-table-column>
        <el-table-column prop="name" label="班级名称"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" @click="showCourses(row)">查看/编辑课程</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="'班级: ' + currentClass.name" width="600px">
      <div style="margin-bottom: 16px;">
        <el-select v-model="selectedCourse" placeholder="选择要添加的课程" filterable style="width: 300px;">
          <el-option v-for="c in courses" :key="c.id" :label="c.name + ' (' + c.total_hours + '课时)'" :value="c.id"></el-option>
        </el-select>
        <el-button type="primary" style="margin-left: 10px;" @click="addCourseToClass">添加</el-button>
      </div>

      <el-table :data="classCourses">
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button size="small" type="danger" @click="removeCourse(row.course_id)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'

const classList = ref([])
const courses = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentClass = ref({})
const classCourses = ref([])
const selectedCourse = ref(null)

const fetchClasses = async () => {
  loading.value = true
  try {
    const response = await api.get('/classes')
    classList.value = response.data
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCourses = async () => {
  try {
    const response = await api.get('/courses')
    courses.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const showCourses = async (cls) => {
  currentClass.value = cls
  dialogVisible.value = true
  try {
    const response = await api.get(`/classes/${cls.id}`)
    classCourses.value = response.data.courses || []
  } catch (error) {
    classCourses.value = []
  }
}

const addCourseToClass = async () => {
  if (!selectedCourse.value) {
    ElMessage.warning('请先选择课程')
    return
  }
  try {
    await api.post(`/classes/${currentClass.value.id}/courses`, { course_id: selectedCourse.value })
    ElMessage.success('添加成功')
    showCourses(currentClass.value)
    selectedCourse.value = null
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '添加失败')
  }
}

const removeCourse = async (courseId) => {
  try {
    await api.delete(`/classes/${currentClass.value.id}/courses/${courseId}`)
    ElMessage.success('移除成功')
    showCourses(currentClass.value)
  } catch (error) {
    ElMessage.error('移除失败')
  }
}

onMounted(() => {
  fetchClasses()
  fetchCourses()
})
</script>
