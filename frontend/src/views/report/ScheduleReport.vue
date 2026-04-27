<template>
  <div class="schedule-report">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 16px; font-weight: bold;">课程表</span>
        </div>
      </template>

      <div class="filter-container">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="教师">
            <el-select v-model="filters.teacher_id" placeholder="选择教师" clearable filterable style="width: 200px;">
              <el-option v-for="t in teachers" :key="t.id" :label="`${t.name} (${t.english_name})`" :value="t.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="班级">
            <el-select v-model="filters.class_id" placeholder="选择班级" clearable filterable style="width: 200px;">
              <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="排课日期">
            <el-select v-model="filters.day_of_week" placeholder="选择星期" clearable filterable style="width: 150px;">
              <el-option label="周一" :value="1"></el-option>
              <el-option label="周二" :value="2"></el-option>
              <el-option label="周三" :value="3"></el-option>
              <el-option label="周四" :value="4"></el-option>
              <el-option label="周五" :value="5"></el-option>
              <el-option label="周六" :value="6"></el-option>
              <el-option label="周日" :value="7"></el-option>
            </el-select>
          </el-form-item>
        </el-form>
        <div class="filter-row">
          <el-form :inline="true" :model="filters" class="filter-form">
            <el-form-item label="开始时间">
              <el-time-picker v-model="filters.start_time" format="HH:mm" placeholder="选择开始时间" style="width: 180px;"></el-time-picker>
            </el-form-item>
            <el-form-item label="结束时间">
              <el-time-picker v-model="filters.end_time" format="HH:mm" placeholder="选择结束时间" style="width: 180px;"></el-time-picker>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchData">
                <el-icon><Search /></el-icon>
                <span>查询</span>
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <el-table :data="schedules" v-loading="loading" stripe style="width: 100%;">
        <el-table-column prop="teacher_name" label="教师" width="150"></el-table-column>
        <el-table-column prop="class_name" label="班级" width="150"></el-table-column>
        <el-table-column prop="course_name" label="课程" width="150"></el-table-column>
        <el-table-column prop="day_of_week" label="排课日期" width="100">
          <template #default="{row}">
            {{ getDayOfWeekText(row.day_of_week) }}
          </template>
        </el-table-column>
        <el-table-column label="排课时间" width="200">
          <template #default="{row}">
            <span :style="{ color: row.is_conflict ? 'red' : '' }">
              {{ row.start_time }} - {{ row.end_time }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="is_conflict" label="是否冲突" width="100">
          <template #default="{row}">
            <el-tag :type="row.is_conflict ? 'danger' : 'success'">
              {{ row.is_conflict ? '有冲突' : '无冲突' }}
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
import { Search } from '@element-plus/icons-vue'
import { getTeachers } from '../../utils/services'

const loading = ref(false)
const schedules = ref([])
const teachers = ref([])
const classes = ref([])

const filters = ref({
  teacher_id: null,
  class_id: null,
  day_of_week: null,
  start_time: null,
  end_time: null
})

const fetchTeachers = async () => {
  try {
    teachers.value = await getTeachers()
  } catch (error) {
    console.error(error)
  }
}

const fetchClasses = async () => {
  try {
    const response = await api.get('/classes', { params: { page: 1, per_page: 100 } })
    classes.value = response.data.items || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取班级列表失败')
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    // 格式化时间
    const formatTime = (date) => {
      if (!date) return null
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    }
    
    const params = {
      teacher_id: filters.value.teacher_id,
      class_id: filters.value.class_id,
      day_of_week: filters.value.day_of_week,
      start_time: formatTime(filters.value.start_time),
      end_time: formatTime(filters.value.end_time)
    }
    
    const response = await api.get('/schedules', { params })
    schedules.value = response.data.data || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取课程表失败')
  } finally {
    loading.value = false
  }
}

const getDayOfWeekText = (day) => {
  const days = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return days[day] || ''
}

onMounted(() => {
  fetchTeachers()
  fetchClasses()
  fetchData()
})
</script>

<style scoped>
.schedule-report {
  padding: 20px;
}

.filter-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.filter-form {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.filter-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}
</style>