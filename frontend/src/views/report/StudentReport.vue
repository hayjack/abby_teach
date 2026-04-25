<template>
  <div class="student-report">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-select v-model="filters.student_id" placeholder="筛选学生" clearable filterable style="width: 100%;">
          <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.english_name})`" :value="s.id"></el-option>
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

      <el-divider></el-divider>

      <h4>学生上课记录明细</h4>
      <el-table :data="attendanceDetail" stripe>
        <el-table-column prop="student_name" label="学生姓名" width="120"></el-table-column>
        <el-table-column prop="class_name" label="班级" width="150"></el-table-column>
        <el-table-column prop="course_name" label="课程" width="150"></el-table-column>
        <el-table-column prop="teacher_name" label="教师" width="120"></el-table-column>
        <el-table-column prop="class_date" label="上课日期" width="120"></el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="100"></el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="100"></el-table-column>
        <el-table-column prop="hours" label="课时" width="80"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status === '出勤' ? 'success' : row.status === '请假' ? 'warning' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="attendanceDetail.length > 0" style="margin-top: 30px;">
        <h4>上课记录日期分布</h4>
        <div ref="chartRef" style="width: 100%; height: 400px;"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const stats = ref([])
const hoursData = ref([])
const attendanceDetail = ref([])
const students = ref([])
const loading = ref(false)
const filters = ref({ student_id: '', start_date: '', end_date: '' })
const chartRef = ref(null)
const chart = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.student_id) params.student_id = filters.value.student_id
    if (filters.value.start_date) params.start_date = new Date(filters.value.start_date).toISOString().split('T')[0]
    if (filters.value.end_date) params.end_date = new Date(filters.value.end_date).toISOString().split('T')[0]

    const [res1, res2, res3] = await Promise.all([
      api.get('/reports/student_attendance', { params }),
      api.get('/reports/student-hours', { params }),
      api.get('/reports/student_attendance_detail', { params })
    ])
    stats.value = res1.data
    hoursData.value = res2.data
    attendanceDetail.value = res3.data
    
    // 延迟渲染图表，确保DOM已更新
    nextTick(() => {
      renderChart()
    })
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students')
    students.value = response.data.items || []
  } catch (error) { console.error(error) }
}

const renderChart = () => {
  if (!chartRef.value) return
  
  // 销毁旧图表
  if (chart.value) {
    chart.value.dispose()
  }
  
  // 初始化新图表
  chart.value = echarts.init(chartRef.value)
  
  // 处理数据，按日期分组
  const dateMap = {}
  attendanceDetail.value.forEach(item => {
    const date = item.class_date
    if (!dateMap[date]) {
      dateMap[date] = {
        total: 0,
        present: 0,
        leave: 0,
        absent: 0
      }
    }
    dateMap[date].total++
    if (item.status === '出勤') {
      dateMap[date].present++
    } else if (item.status === '请假') {
      dateMap[date].leave++
    } else {
      dateMap[date].absent++
    }
  })
  
  // 转换为图表数据格式
  const dates = Object.keys(dateMap).sort()
  const series = [
    {
      name: '出勤',
      type: 'bar',
      stack: 'total',
      data: dates.map(date => dateMap[date].present),
      itemStyle: { color: '#67C23A' }
    },
    {
      name: '请假',
      type: 'bar',
      stack: 'total',
      data: dates.map(date => dateMap[date].leave),
      itemStyle: { color: '#E6A23C' }
    },
    {
      name: '旷课',
      type: 'bar',
      stack: 'total',
      data: dates.map(date => dateMap[date].absent),
      itemStyle: { color: '#F56C6C' }
    }
  ]
  
  // 图表配置
  const option = {
    title: {
      text: '上课记录日期分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['出勤', '请假', '旷课'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '次数'
    },
    series: series
  }
  
  // 渲染图表
  chart.value.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.value?.resize()
  })
}

onMounted(() => {
  fetchData()
  fetchStudents()
})

// 监听窗口大小变化，调整图表尺寸
watch(() => window.innerWidth, () => {
  chart.value?.resize()
})
</script>
