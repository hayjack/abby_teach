<template>
  <div class="leave-approve">
    <el-card>
      <template #header><span>请假审批</span></template>

      <el-table :data="pendingLeaves" v-loading="loading" style="margin-bottom: 20px;">
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="course_name" label="课程"></el-table-column>
        <el-table-column prop="start_date" label="开始日期"></el-table-column>
        <el-table-column prop="end_date" label="结束日期"></el-table-column>
        <el-table-column prop="reason" label="请假原因"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" type="success" @click="handleApprove(row.id)">批准</el-button>
            <el-button size="small" type="danger" @click="handleReject(row.id)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-divider>已审批记录</el-divider>

      <el-table :data="approvedLeaves" v-loading="loading2">
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
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const pendingLeaves = ref([])
const approvedLeaves = ref([])
const loading = ref(false)
const loading2 = ref(false)

const fetchPending = async () => {
  loading.value = true
  try {
    const response = await api.get('/leaves', { params: { status: '待审批' } })
    pendingLeaves.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取待审批列表失败')
  } finally {
    loading.value = false
  }
}

const fetchApproved = async () => {
  loading2.value = true
  try {
    const response = await api.get('/leaves', { params: { status: '已批准' } })
    const response2 = await api.get('/leaves', { params: { status: '已拒绝' } })
    approvedLeaves.value = [...response.data, ...response2.data]
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取已审批列表失败')
  } finally {
    loading2.value = false
  }
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

onMounted(() => {
  fetchPending()
  fetchApproved()
})
</script>
