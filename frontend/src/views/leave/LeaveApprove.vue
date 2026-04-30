<template>
  <div class="leave-approve">
    <el-card>
      <template #header><span>请假审批</span></template>

      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="8">
          <el-select v-model="filters.class_id" placeholder="选择班级" clearable filterable style="width: 100%;" @change="handleClassChange">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id"></el-option>
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select v-model="filters.student_id" placeholder="选择学生" clearable filterable style="width: 100%;">
            <el-option v-for="s in filteredStudents" :key="s.id" :label="`${s.name} (${s.english_name})`" :value="s.id"></el-option>
          </el-select>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="16">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
            clearable
          />
        </el-col>
        <el-col :span="8" style="display: flex; align-items: center; justify-content: flex-end;">
          <el-button type="primary" @click="fetchData">
            <el-icon><Search /></el-icon>
            <span>查询</span>
          </el-button>
        </el-col>
      </el-row>

      <el-table :data="pendingLeaves" v-loading="loading" style="margin-bottom: 20px;" stripe>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="course_name" label="课程"></el-table-column>
        <el-table-column prop="start_date" label="开始日期"></el-table-column>
        <el-table-column prop="end_date" label="结束日期"></el-table-column>
        <el-table-column prop="reason" label="请假原因"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" type="success" @click="handleApprove(row.id)">
              <el-icon><Check /></el-icon>
              <span>批准</span>
            </el-button>
            <el-button size="small" type="danger" @click="handleReject(row.id)">
              <el-icon><Close /></el-icon>
              <span>拒绝</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-divider>已审批记录</el-divider>

      <el-table :data="approvedLeaves" v-loading="loading2" stripe>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="course_name" label="课程"></el-table-column>
        <el-table-column prop="start_date" label="开始日期"></el-table-column>
        <el-table-column prop="end_date" label="结束日期"></el-table-column>
        <el-table-column prop="reason" label="请假原因"></el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{row}">
            <el-tag :type="row.status === '已批准' ? 'success' : 'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close, Search } from '@element-plus/icons-vue'

const pendingLeaves = ref([])
const approvedLeaves = ref([])
const loading = ref(false)
const loading2 = ref(false)
const classes = ref([])
const students = ref([])
const filters = ref({ class_id: '', student_id: '' })
const dateRange = ref([])

// 过滤学生列表
const filteredStudents = ref([])

// 班级变化处理
const handleClassChange = async () => {
  filters.value.student_id = ''
  if (filters.value.class_id) {
    try {
      const response = await api.get(`/classes/${filters.value.class_id}/students`)
      filteredStudents.value = response.data
    } catch (error) {
      console.error('获取班级学生失败:', error)
      filteredStudents.value = []
    }
  } else {
    filteredStudents.value = students.value
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await api.get('/classes')
    classes.value = response.data.items || []
  } catch (error) {
    console.error(error)
  }
}

// 获取学生列表
const fetchStudents = async () => {
  try {
    // 获取所有学生，设置较大的每页数量
    const response = await api.get('/students', { params: { page: 1, per_page: 1000 } })
    students.value = response.data.items || []
  } catch (error) {
    console.error(error)
  }
}

// 构建查询参数
const buildParams = (status) => {
  const params = {
    status,
    page: 1,
    per_page: 100,
    sort_by: 'created_at',
    sort_order: 'desc'
  }
  
  if (filters.value.class_id) params.class_id = filters.value.class_id
  if (filters.value.student_id) params.student_id = filters.value.student_id
  if (dateRange.value && dateRange.value.length === 2) {
    params.start_date = new Date(dateRange.value[0]).toISOString().split('T')[0]
    params.end_date = new Date(dateRange.value[1]).toISOString().split('T')[0]
  }
  
  return params
}

const fetchPending = async () => {
  loading.value = true
  try {
    const params = buildParams('待审批')
    const response = await api.get('/leaves', { params })
    pendingLeaves.value = response.data.items || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取待审批列表失败')
  } finally {
    loading.value = false
  }
}

const fetchApproved = async () => {
  loading2.value = true
  try {
    const params1 = buildParams('已批准')
    const params2 = buildParams('已拒绝')
    
    const response = await api.get('/leaves', { params: params1 })
    const response2 = await api.get('/leaves', { params: params2 })
    approvedLeaves.value = [...(response.data.items || []), ...(response2.data.items || [])]
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取已审批列表失败')
  } finally {
    loading2.value = false
  }
}

// 统一查询方法
const fetchData = () => {
  fetchPending()
  fetchApproved()
}

const handleApprove = async (id) => {
  try {
    await ElMessageBox.confirm('确定批准该请假申请？', '确认')
    const response = await api.put(`/leaves/${id}/approve`)
    const msg = response.data?.message || '已批准'
    ElMessage.success(msg)
    fetchPending()
    fetchApproved()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const handleReject = async (id) => {
  try {
    await ElMessageBox.confirm('确定拒绝该请假申请？', '确认')
    await api.put(`/leaves/${id}/reject`)
    ElMessage.success('已拒绝')
    fetchPending()
    fetchApproved()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

onMounted(async () => {
  await fetchPending()
  await fetchApproved()
  await fetchClasses()
  await fetchStudents()
  // 初始化学生列表
  filteredStudents.value = students.value
})
</script>
