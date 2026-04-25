<template>
  <div class="dashboard">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用教学管理系统</span>
        </div>
      </template>
      <div class="welcome-content">
        <p>尊敬的{{ user.name }}，您好！</p>
        <p>今天是 {{ currentDate }}</p>
      </div>
    </el-card>
    
    <div class="stats-container">
      <el-card class="stat-card">
        <div class="stat-item">
          <el-icon class="stat-icon"><User /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ studentCount }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <el-icon class="stat-icon"><FolderOpened /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ classCount }}</div>
            <div class="stat-label">班级总数</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <el-icon class="stat-icon"><Reading /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ courseCount }}</div>
            <div class="stat-label">课程总数</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <el-icon class="stat-icon"><Calendar /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ classRecordCount }}</div>
            <div class="stat-label">本月上课次数</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <div class="charts-container">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>学生出勤情况</span>
          </div>
        </template>
        <div ref="attendanceChart" class="chart"></div>
      </el-card>
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>教师上课统计</span>
          </div>
        </template>
        <div ref="teacherChart" class="chart"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../store'
import { User, FolderOpened, Reading, Calendar } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '../utils/api'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const user = ref({ name: '管理员' })
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 统计数据
const studentCount = ref(0)
const classCount = ref(0)
const courseCount = ref(0)
const classRecordCount = ref(0)
const attendanceStats = ref({ present: 0, leave: 0, absent: 0 })
const topTeachers = ref([])

// 图表引用
const attendanceChart = ref(null)
const teacherChart = ref(null)

// 初始化图表
const initCharts = () => {
  // 学生出勤情况图表
  const attendanceChartInstance = echarts.init(attendanceChart.value)
  attendanceChartInstance.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: '出勤情况',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: attendanceStats.value.present, name: '出勤' },
          { value: attendanceStats.value.leave, name: '请假' },
          { value: attendanceStats.value.absent, name: '旷课' }
        ]
      }
    ]
  })
  
  // 教师上课统计图表
  const teacherChartInstance = echarts.init(teacherChart.value)
  teacherChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: topTeachers.value.map(teacher => teacher.teacher_name),
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: '上课次数',
        type: 'bar',
        barWidth: '60%',
        data: topTeachers.value.map(teacher => teacher.class_count)
      }
    ]
  })
  
  // 响应式调整
  window.addEventListener('resize', () => {
    attendanceChartInstance.resize()
    teacherChartInstance.resize()
  })
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await api.get('/reports/dashboard')
    const data = response.data
    
    studentCount.value = data.student_count
    classCount.value = data.class_count
    courseCount.value = data.course_count
    classRecordCount.value = data.class_record_count
    attendanceStats.value = data.attendance_stats
    topTeachers.value = data.top_teachers
    
    // 初始化图表
    initCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

onMounted(() => {
  // 从store获取用户信息
  if (userStore.userInfo) {
    user.value = userStore.userInfo
  }
  
  // 获取统计数据
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  gap: 20px;
  display: flex;
  flex-direction: column;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content {
  font-size: 16px;
  line-height: 1.5;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  padding: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
  color: #409EFF;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-card {
  padding: 20px;
}

.chart {
  height: 300px;
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .chart {
    height: 250px;
  }
}
</style>
