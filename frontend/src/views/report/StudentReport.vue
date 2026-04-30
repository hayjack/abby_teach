<template>
  <div class="student-report">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="5">
        <el-select v-model="filters.class_id" placeholder="筛选班级" clearable filterable style="width: 100%;" @change="handleClassChange">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id"></el-option>
        </el-select>
      </el-col>
      <el-col :span="5">
        <el-select v-model="filters.student_id" placeholder="筛选学生" clearable filterable style="width: 100%;">
          <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.english_name})`" :value="s.id"></el-option>
        </el-select>
      </el-col>
      <el-col :span="10">
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
      <el-col :span="4" style="display: flex; align-items: center; justify-content: flex-end;">
        <el-button type="primary" @click="fetchData">
          <el-icon><Search /></el-icon>
          <span>查询</span>
        </el-button>
      </el-col>
    </el-row>

    <el-card v-loading="loading">
      <template #header><span style="font-weight: bold; font-size: 16px;">学生出勤统计</span></template>

      <el-table :data="stats" stripe>
        <el-table-column prop="student_name" label="学生姓名" ></el-table-column>
        <el-table-column prop="total" label="总次数" ></el-table-column>
        <el-table-column prop="present" label="出勤" >
          <template #default="{row}"><el-tag type="success">{{ row.present }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="leave" label="请假">
          <template #default="{row}"><el-tag type="warning">{{ row.leave }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="absent" label="旷课" >
          <template #default="{row}"><el-tag type="danger">{{ row.absent }}</el-tag></template>
        </el-table-column>
        <el-table-column label="出勤率" >
          <template #default="{row}">
            {{ row.total > 0 ? ((row.present / row.total) * 100).toFixed(1) + '%' : '-' }}
          </template>
        </el-table-column>
      </el-table>

      <el-divider></el-divider>

      <h4 style="font-weight: bold; font-size: 16px;">学生课时使用情况</h4>
      <el-table :data="hoursData" stripe>
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="course_name" label="课程名称"></el-table-column>
        <el-table-column prop="total_hours" label="总课时" ></el-table-column>
        <el-table-column prop="used_hours" label="已用课时" ></el-table-column>
        <el-table-column prop="remaining_hours" label="剩余课时" >
          <template #default="{row}">
            <el-tag :type="row.remaining_hours > 5 ? 'success' : row.remaining_hours > 0 ? 'warning' : 'danger'">
              {{ row.remaining_hours }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button type="primary" size="small" @click="showAttendanceDetail(row.student_id, row.course_id, row.student_name, row.course_name)">
              <el-icon><View /></el-icon>
              <span>详情</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 上课记录明细对话框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="860px">
        <el-table :data="currentAttendanceDetail" stripe>
          <el-table-column prop="class_name" label="班级" width="100"></el-table-column>
          <el-table-column prop="course_name" label="课程" width="100"></el-table-column>
          <el-table-column prop="teacher_name" label="教师" width="120"></el-table-column>
          <el-table-column prop="class_date" label="上课日期" width="100"></el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="100"></el-table-column>
          <el-table-column prop="end_time" label="结束时间" width="100"></el-table-column>
          <el-table-column prop="hours" label="课时" width="60"></el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{row}">
              <el-tag :type="row.status === '出勤' ? 'success' : row.status === '请假' ? 'warning' : 'danger'">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="currentAttendanceDetail.length > 0" style="margin-top: 30px;">
          <h4>上课记录日期分布</h4>
          <div ref="detailChartRef" style="width: 100%; height: 400px;"></div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Search, View } from '@element-plus/icons-vue'

const stats = ref([])
const hoursData = ref([])
const attendanceDetail = ref([])
const currentAttendanceDetail = ref([])
const students = ref([])
const allStudents = ref([])
const classes = ref([])
const loading = ref(false)
const filters = ref({ class_id: '', student_id: '' })
const dateRange = ref([])
const chartRef = ref(null)
const detailChartRef = ref(null)
const chart = ref(null)
const detailChart = ref(null)
const dialogVisible = ref(false)
const dialogTitle = ref('')

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.class_id) params.class_id = filters.value.class_id
    if (filters.value.student_id) params.student_id = filters.value.student_id
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = new Date(dateRange.value[0]).toISOString().split('T')[0]
      params.end_date = new Date(dateRange.value[1]).toISOString().split('T')[0]
    }

    const [res1, res2] = await Promise.all([
      api.get('/reports/student_attendance', { params }),
      api.get('/reports/student-hours', { params })
    ])
    stats.value = res1.data
    hoursData.value = res2.data.items || res2.data
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const fetchClasses = async () => {
  try {
    const response = await api.get('/classes')
    classes.value = response.data.items || []
  } catch (error) { console.error(error) }
}

const showAttendanceDetail = async (studentId, courseId, studentName, courseName) => {
  try {
    const params = {
      student_id: studentId
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = new Date(dateRange.value[0]).toISOString().split('T')[0]
      params.end_date = new Date(dateRange.value[1]).toISOString().split('T')[0]
    }

    const response = await api.get('/reports/student_attendance_detail', { params })
    // 过滤出该课程的记录
    currentAttendanceDetail.value = response.data.filter(item => item.course_id == courseId)
    dialogTitle.value = `${studentName} - ${courseName} 上课记录明细`
    dialogVisible.value = true
    
    // 延迟渲染图表，确保DOM已更新
    nextTick(() => {
      renderDetailChart()
    })
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取上课记录明细失败')
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students')
    allStudents.value = response.data.items || []
    students.value = allStudents.value
  } catch (error) { console.error(error) }
}

const handleClassChange = async () => {
  // 重置学生选择
  filters.value.student_id = ''
  
  if (!filters.value.class_id) {
    // 如果没有选择班级，显示所有学生
    students.value = allStudents.value
    return
  }
  
  try {
    // 获取该班级的学生列表
    const response = await api.get(`/classes/${filters.value.class_id}/students`)
    students.value = response.data || []
  } catch (error) {
    console.error(error)
    students.value = []
  }
}

const renderDetailChart = () => {
  if (!detailChartRef.value) return
  
  // 销毁旧图表
  if (detailChart.value) {
    detailChart.value.dispose()
  }
  
  // 初始化新图表
  detailChart.value = echarts.init(detailChartRef.value)
  
  // 处理数据，按日期分组
  const dateMap = {}
  currentAttendanceDetail.value.forEach(item => {
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
  detailChart.value.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    detailChart.value?.resize()
  })
}

onMounted(() => {
  fetchData()
  fetchStudents()
  fetchClasses()
})

// 监听窗口大小变化，调整图表尺寸
watch(() => window.innerWidth, () => {
  detailChart.value?.resize()
})
</script>
