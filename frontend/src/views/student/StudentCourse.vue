<template>
  <div class="student-course">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 16px; font-weight: bold;">课时管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            <span>新增</span>
          </el-button>
        </div>
      </template>

      <div class="filter-container" style="margin-bottom: 16px;">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="学生姓名">
            <el-input v-model="filters.student_name" clearable placeholder="请输入学生姓名" style="width: 200px;"></el-input>
          </el-form-item>
          <el-form-item label="课程名称">
            <el-select v-model="filters.course_id" placeholder="请选择课程" clearable filterable style="width: 200px;">
              <el-option label="全部" :value="''"></el-option>
              <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchStudentCourses">
              <el-icon><Search /></el-icon>
              <span>查询</span>
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="studentCourses" v-loading="loading" stripe style="width: 100%;">
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
        <el-table-column label="操作">
          <template #default="{row}">
            <el-button type="primary" size="small" @click="handleViewHistory(row)">
              <el-icon><View /></el-icon>
              <span>查看历史</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :prev-text="'上一页'"
          :next-text="'下一页'"
          :page-size-text="'条/页'"
          :jumper-text="'前往'"
          :total-text="'共 '"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="添加课时" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="form.student_id" placeholder="请选择学生" filterable>
            <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.english_name})`" :value="s.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="form.course_id" placeholder="请选择课程" filterable>
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="课时数" prop="total_hours">
          <el-input-number v-model="form.total_hours" :min="0.5" :step="0.5" :precision="1"></el-input-number>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注信息"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">
          <el-icon><Close /></el-icon>
          <span>取消</span>
        </el-button>
        <el-button type="success" @click="handleSubmit">
          <el-icon><Check /></el-icon>
          <span>确定</span>
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="historyDialogVisible" title="课时历史记录" width="800px">
      <el-table :data="hoursHistory" v-loading="historyLoading" stripe style="width: 100%;">
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column prop="hours_added" label="增加课时"></el-table-column>
        <el-table-column prop="operator_name" label="操作人"></el-table-column>
        <el-table-column prop="remark" label="备注"></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="200px">
          <template #default="{row}">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="historyDialogVisible = false">
          <el-icon><Close /></el-icon>
          <span>关闭</span>
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import { Plus, Close, Check, View, Search } from '@element-plus/icons-vue'

const studentCourses = ref([])
const students = ref([])
const courses = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const historyDialogVisible = ref(false)
const hoursHistory = ref([])
const historyLoading = ref(false)

const filters = ref({
  student_name: '',
  course_id: ''
})

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const form = ref({
  student_id: '',
  course_id: '',
  total_hours: 10,
  remark: ''
})

const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  total_hours: [{ required: true, message: '请输入课时数', trigger: 'blur' }]
}

const fetchStudentCourses = async () => {
  loading.value = true
  try {
    const response = await api.get('/reports/student-hours', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value,
        student_name: filters.value.student_name,
        course_id: filters.value.course_id
      }
    })
    studentCourses.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取课时信息失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchStudentCourses()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  fetchStudentCourses()
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students')
    students.value = response.data.items || []
  } catch (error) {
    console.error(error)
  }
}

const fetchCourses = async () => {
  try {
    const response = await api.get('/courses')
    courses.value = response.data.items || []
  } catch (error) {
    console.error(error)
  }
}

const handleAdd = () => {
  form.value = { student_id: '', course_id: '', total_hours: 10, remark: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await api.post(`/students/${form.value.student_id}/hours`, form.value)
        ElMessage.success('添加成功')
        dialogVisible.value = false
        fetchStudentCourses()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    }
  })
}

const fetchHoursHistory = async (studentId) => {
  historyLoading.value = true
  try {
    const response = await api.get(`/students/${studentId}/hours/history`)
    hoursHistory.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取课时历史记录失败')
  } finally {
    historyLoading.value = false
  }
}

const handleViewHistory = (row) => {
  fetchHoursHistory(row.student_id)
  historyDialogVisible.value = true
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

onMounted(() => {
  fetchStudentCourses()
  fetchStudents()
  fetchCourses()
})
</script>
