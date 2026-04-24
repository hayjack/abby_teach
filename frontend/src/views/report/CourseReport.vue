<template>
  <div class="course-report">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-select v-model="filters.course_id" placeholder="筛选课程" clearable filterable style="width: 100%;">
          <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"></el-option>
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
      <template #header><span>课程出勤统计</span></template>

      <el-table :data="stats" stripe>
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
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

      <div ref="chartRef" style="height: 400px;"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const stats = ref([])
const courses = ref([])
const loading = ref(false)
const chartRef = ref(null)
const filters = ref({ course_id: '', start_date: '', end_date: '' })

let chartInstance = null

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.course_id) params.course_id = filters.value.course_id
    if (filters.value.start_date) params.start_date = new Date(filters.value.start_date).toISOString().split('T')[0]
    if (filters.value.end_date) params.end_date = new Date(filters.value.end_date).toISOString().split('T')[0]

    const response = await api.get('/reports/course_attendance', { params })
    stats.value = response.data

    await nextTick()
    renderChart()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const fetchCourses = async () => {
  try {
    const response = await api.get('/courses')
    courses.value = response.data
  } catch (error) { console.error(error) }
}

const renderChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()

  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      data: stats.value.map(s => ({ name: s.course_name, value: s.total }))
    }]
  })
}

onMounted(() => {
  fetchData()
  fetchCourses()
})
</script>
