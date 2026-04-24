<template>
  <div class="student-report">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-select v-model="filters.student_id" placeholder="筛选学生" clearable filterable style="width: 100%;">
          <el-option v-for="s in students" :key="s.id" :label="s.name" :value="s.id"></el-option>
        </el-select>
      </el-col>
      <el-col :span="8">
        <el-date-picker v-model="filters.start_date" type="date" placeholder="开始日期" style="width: 100%;"></el-date-picker>
      </el-col>
      <el-col :span="8">
        <el-date-picker v-model="filters.end_date" type="date" placeholder="结束日期" style="width: 100%;"></el-date-picker>
      </el-col>
    </el-row>

    <el-button type="primary" @click="fetchData" style="margin-bottom: 20px;">查询</el-button>

    <el-card v-loading="loading">
      <template #header><span>学生出勤统计</span></template>

      <el-table :data="stats" stripe>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="total" label="总次数" width="100"></el-table-column>
        <el-table-column prop="present" label="出勤" width="100">
          <template #default="{row}"><el-tag type="success">{{ row.present }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="leave" label="请假" width="100">
          <template #default="{row}"><el-tag type="warning">{{ row.leave }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="absent" label="旷课" width="100">
          <template #default="{row}"><el-tag type="danger">{{ row.absent }}</el-tag></template>
        </el-table-column>
        <el-table-column label="出勤率" width="120">
          <template #default="{row}">
            {{ row.total > 0 ? ((row.present / row.total) * 100).toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
      </el-table>

      <el-divider></el-divider>

      <h4>学生课时使用情况</h4>
      <el-table :data="hoursData" stripe>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column prop="total_hours" label="总课时" width="100"></el-table-column>
        <el-table-column prop="used_hours" label="已用课时" width="100"></el-table-column>
        <el-table-column prop="remaining_hours" label="剩余课时" width="100">
          <template #default="{row}">
            <el-tag :type="row.remaining_hours > 5 ? 'success' : row.remaining_hours > 0 ? 'warning' : 'danger'">
              {{ row.remaining_hours }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'

const stats = ref([])
const hoursData = ref([])
const students = ref([])
const loading = ref(false)
const filters = ref({ student_id: '', start_date: '', end_date: '' })

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.student_id) params.student_id = filters.value.student_id
    if (filters.value.start_date) params.start_date = new Date(filters.value.start_date).toISOString().split('T')[0]
    if (filters.value.end_date) params.end_date = new Date(filters.value.end_date).toISOString().split('T')[0]

    const [res1, res2] = await Promise.all([
      api.get('/reports/student_attendance', { params }),
      api.get('/reports/student-hours', { params })
    ])
    stats.value = res1.data
    hoursData.value = res2.data
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students')
    students.value = response.data
  } catch (error) { console.error(error) }
}

onMounted(() => { fetchData(); fetchStudents() })
</script>
