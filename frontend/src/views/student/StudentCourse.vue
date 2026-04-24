<template>
  <div class="student-course">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>课时管理</span>
          <el-button type="primary" @click="handleAdd">添加课时</el-button>
        </div>
      </template>

      <el-table :data="studentCourses" v-loading="loading">
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column prop="total_hours" label="总课时"></el-table-column>
        <el-table-column prop="remaining_hours" label="剩余课时">
          <template #default="{row}">
            <el-tag :type="row.remaining_hours > 5 ? 'success' : row.remaining_hours > 0 ? 'warning' : 'danger'">
              {{ row.remaining_hours }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期"></el-table-column>
        <el-table-column prop="end_date" label="结束日期"></el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加课时" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="form.student_id" placeholder="请选择学生" filterable>
            <el-option v-for="s in students" :key="s.id" :label="s.name" :value="s.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="form.course_id" placeholder="请选择课程" filterable>
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="课时数" prop="total_hours">
          <el-input-number v-model="form.total_hours" :min="1"></el-input-number>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="form.end_date" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'

const studentCourses = ref([])
const students = ref([])
const courses = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)

const form = ref({
  student_id: '',
  course_id: '',
  total_hours: 10,
  start_date: '',
  end_date: ''
})

const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  total_hours: [{ required: true, message: '请输入课时数', trigger: 'blur' }]
}

const fetchStudentCourses = async () => {
  loading.value = true
  try {
    const response = await api.get('/reports/student-hours')
    studentCourses.value = response.data
  } catch (error) {
    ElMessage.error('获取课时信息失败')
  } finally {
    loading.value = false
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students')
    students.value = response.data
  } catch (error) {
    console.error(error)
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

const handleAdd = () => {
  form.value = { student_id: '', course_id: '', total_hours: 10, start_date: '', end_date: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await api.post(`/students/${form.value.student_id}/courses`, form.value)
        ElMessage.success('添加成功')
        dialogVisible.value = false
        fetchStudentCourses()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

onMounted(() => {
  fetchStudentCourses()
  fetchStudents()
  fetchCourses()
})
</script>
