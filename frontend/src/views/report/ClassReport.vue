<template>
  <div class="class-report">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-select v-model="filters.class_id" placeholder="筛选班级" clearable filterable style="width: 100%;">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id"></el-option>
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

    <el-card v-loading="classRecordsLoading" style="margin-bottom: 20px;">
      <template #header><span>班级上课记录</span></template>

      <el-table :data="classRecords" stripe>
        <el-table-column prop="class_name" label="班级名称"></el-table-column>
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column prop="teacher_name" label="教师名称"></el-table-column>
        <el-table-column prop="class_date" label="上课日期"></el-table-column>
        <el-table-column prop="start_time" label="开始时间"></el-table-column>
        <el-table-column prop="end_time" label="结束时间"></el-table-column>
      </el-table>

      <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-card v-loading="loading">
      <template #header><span>班级出勤统计</span></template>

      <el-table :data="stats" stripe>
        <el-table-column prop="class_name" label="班级名称"></el-table-column>
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
const classes = ref([])
const loading = ref(false)
const chartRef = ref(null)
const filters = ref({ class_id: '', start_date: '', end_date: '' })

// 班级上课记录相关
const classRecords = ref([])
const classRecordsLoading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

let chartInstance = null

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.class_id) params.class_id = filters.value.class_id
    if (filters.value.start_date) params.start_date = new Date(filters.value.start_date).toISOString().split('T')[0]
    if (filters.value.end_date) params.end_date = new Date(filters.value.end_date).toISOString().split('T')[0]

    const response = await api.get('/reports/class_attendance', { params })
    stats.value = response.data

    await nextTick()
    renderChart()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取统计数据失败')
  } finally {
    loading.value = false
  }
  
  // 同时获取班级上课记录
  fetchClassRecords()
}

const fetchClassRecords = async () => {
  classRecordsLoading.value = true
  try {
    const params = {
      page: pagination.value.current,
      per_page: pagination.value.pageSize
    }
    if (filters.value.class_id) params.class_id = filters.value.class_id
    if (filters.value.start_date) params.start_date = new Date(filters.value.start_date).toISOString().split('T')[0]
    if (filters.value.end_date) params.end_date = new Date(filters.value.end_date).toISOString().split('T')[0]

    const response = await api.get('/class_records', { params })
    classRecords.value = response.data.items
    pagination.value.total = response.data.total
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取上课记录失败')
  } finally {
    classRecordsLoading.value = false
  }
}

const fetchClasses = async () => {
  try {
    const response = await api.get('/classes')
    classes.value = response.data.items || []
  } catch (error) { console.error(error) }
}

const renderChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()

  chartInstance = echarts.init(chartRef.value)
  
  // 准备数据
  const classNames = stats.value.map(s => s.class_name)
  const presentData = stats.value.map(s => s.present)
  const leaveData = stats.value.map(s => s.leave)
  const absentData = stats.value.map(s => s.absent)

  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['出勤', '请假', '旷课'], bottom: 0 },
    xAxis: {
      type: 'category',
      data: classNames,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '出勤',
        type: 'bar',
        data: presentData,
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '请假',
        type: 'bar',
        data: leaveData,
        itemStyle: {
          color: '#E6A23C'
        }
      },
      {
        name: '旷课',
        type: 'bar',
        data: absentData,
        itemStyle: {
          color: '#F56C6C'
        }
      }
    ]
  })
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.value.pageSize = size
  fetchClassRecords()
}

const handleCurrentChange = (current) => {
  pagination.value.current = current
  fetchClassRecords()
}

onMounted(() => {
  fetchData()
  fetchClasses()
})
</script>
