<template>
  <div class="teacher-report">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-select v-model="filters.teacher_id" placeholder="筛选教师" clearable filterable style="width: 100%;">
          <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id"></el-option>
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
      <template #header><span>教师上课统计</span></template>

      <el-table :data="stats" stripe>
        <el-table-column prop="teacher_name" label="教师姓名"></el-table-column>
        <el-table-column prop="total_classes" label="上课次数" width="120">
          <template #default="{row}"><strong>{{ row.total_classes }}</strong></template>
        </el-table-column>
        <el-table-column prop="total_hours" label="总课时" width="120">
          <template #default="{row}"><strong>{{ row.total_hours }}</strong></template>
        </el-table-column>
        <el-table-column label="平均每次课时" width="140">
          <template #default="{row}">
            {{ row.total_classes > 0 ? (row.total_hours / row.total_classes).toFixed(1) : '-' }}
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
const teachers = ref([])
const loading = ref(false)
const chartRef = ref(null)
const filters = ref({ teacher_id: '', start_date: '', end_date: '' })

let chartInstance = null

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.teacher_id) params.teacher_id = filters.value.teacher_id
    if (filters.value.start_date) params.start_date = new Date(filters.value.start_date).toISOString().split('T')[0]
    if (filters.value.end_date) params.end_date = new Date(filters.value.end_date).toISOString().split('T')[0]

    const response = await api.get('/reports/teacher_classes', { params })
    stats.value = response.data

    await nextTick()
    renderChart()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const fetchTeachers = async () => {
  try {
    const response = await api.get('/users')
    teachers.value = response.data
  } catch (error) { console.error(error) }
}

const renderChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()

  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['上课次数', '总课时'] },
    xAxis: { type: 'category', data: stats.value.map(s => s.teacher_name) },
    yAxis: [
      { type: 'value', name: '上课次数' },
      { type: 'value', name: '总课时' }
    ],
    series: [
      { name: '上课次数', type: 'bar', data: stats.value.map(s => s.total_classes) },
      { name: '总课时', type: 'bar', data: stats.value.map(s => s.total_hours) }
    ]
  })
}

onMounted(() => {
  fetchData()
  fetchTeachers()
})
</script>
