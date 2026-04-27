<template>
  <div class="class-teachers">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 16px; font-weight: bold;">班级教师</span>
        </div>
      </template>

      <el-table :data="classList" v-loading="loading" stripe style="width: 100%;">
        <el-table-column prop="id" label="班级ID"></el-table-column>
        <el-table-column prop="name" label="班级名称"></el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{row}">
            <el-button size="small" @click="showTeachers(row)">
              <el-icon><View /></el-icon>
              <span>查看/编辑教师</span>
            </el-button>
            <el-button size="small" type="primary" style="margin-left: 10px;" @click="showSchedule(row)">
              <el-icon><Calendar /></el-icon>
              <span>排课管理</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="'班级: ' + currentClass.name" width="600px">
      <div style="margin-bottom: 16px;">
        <el-select v-model="selectedTeacher" placeholder="选择要添加的教师" filterable style="width: 300px;">
            <el-option v-for="t in teachers" :key="t.id" :label="`${t.name} (${t.english_name})`" :value="t.id"></el-option>
          </el-select>
        <el-button type="primary" style="margin-left: 10px;" @click="addTeacherToClass">
          <el-icon><Plus /></el-icon>
          <span>添加</span>
        </el-button>
      </div>

      <el-table :data="classTeachers" stripe style="width: 100%;">
        <el-table-column prop="teacher_name" label="教师姓名"></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button size="small" type="danger" @click="removeTeacher(row.teacher_id)">
              <el-icon><Delete /></el-icon>
              <span>移除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 排课管理对话框 -->
    <el-dialog v-model="scheduleDialogVisible" :title="'班级: ' + currentClass.name + ' - 排课管理'" width="800px">
      <div style="margin-bottom: 16px; display: flex; align-items: center;">
        <el-select v-model="scheduleForm.teacher_id" placeholder="选择教师" style="width: 200px;">
          <el-option v-for="t in teachers" :key="t.id" :label="`${t.name} (${t.english_name})`" :value="t.id"></el-option>
        </el-select>
        <el-select v-model="scheduleForm.day_of_week" placeholder="选择星期" style="width: 100px; margin-left: 10px;">
          <el-option label="周一" :value="1"></el-option>
          <el-option label="周二" :value="2"></el-option>
          <el-option label="周三" :value="3"></el-option>
          <el-option label="周四" :value="4"></el-option>
          <el-option label="周五" :value="5"></el-option>
          <el-option label="周六" :value="6"></el-option>
          <el-option label="周日" :value="7"></el-option>
        </el-select>
        <el-time-picker v-model="scheduleForm.start_time" format="HH:mm" placeholder="开始时间" style="width: 120px; margin-left: 10px;"></el-time-picker>
        <span style="margin-left: 10px; margin-right: 10px;">至</span>
        <el-time-picker v-model="scheduleForm.end_time" format="HH:mm" placeholder="结束时间" style="width: 120px;"></el-time-picker>
        <el-button type="primary" style="margin-left: 10px;" @click="addSchedule">
          <el-icon><Plus /></el-icon>
          <span>添加排课</span>
        </el-button>
      </div>

      <el-table :data="classSchedules" stripe style="width: 100%;">
        <el-table-column prop="day_of_week" label="星期" width="80">
          <template #default="{row}">
            {{ getDayOfWeekText(row.day_of_week) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="100"></el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="100"></el-table-column>
        <el-table-column prop="teacher_name" label="教师姓名" width="150"></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button size="small" type="danger" @click="deleteSchedule(row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import { Plus, View, Delete, Calendar } from '@element-plus/icons-vue'
import { getTeachers } from '../../utils/services'

const classList = ref([])
const teachers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentClass = ref({})
const classTeachers = ref([])
const selectedTeacher = ref(null)

// 排课相关
const scheduleDialogVisible = ref(false)
const classSchedules = ref([])
const scheduleForm = ref({
  teacher_id: null,
  day_of_week: null,
  start_time: null,
  end_time: null
})

const fetchClasses = async () => {
  loading.value = true
  try {
    const response = await api.get('/classes', { params: { page: 1, per_page: 100 } })
    classList.value = response.data.items || []
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取班级列表失败')
  } finally {
    loading.value = false
  }
}

const fetchTeachers = async () => {
  try {
    teachers.value = await getTeachers()
  } catch (error) {
    console.error(error)
  }
}

const showTeachers = async (cls) => {
  currentClass.value = cls
  dialogVisible.value = true
  try {
    const response = await api.get(`/classes/${cls.id}`)
    classTeachers.value = response.data.teachers || []
  } catch (error) {
    classTeachers.value = []
  }
}

const addTeacherToClass = async () => {
  if (!selectedTeacher.value) {
    ElMessage.warning('请先选择教师')
    return
  }
  try {
    await api.post(`/classes/${currentClass.value.id}/teachers`, { teacher_id: selectedTeacher.value })
    ElMessage.success('添加成功')
    showTeachers(currentClass.value)
    selectedTeacher.value = null
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '添加失败')
  }
}

const removeTeacher = async (teacherId) => {
  try {
    await api.delete(`/classes/${currentClass.value.id}/teachers/${teacherId}`)
    ElMessage.success('移除成功')
    showTeachers(currentClass.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '移除失败')
  }
}

// 排课相关方法
const showSchedule = async (cls) => {
  currentClass.value = cls
  scheduleDialogVisible.value = true
  await fetchClassSchedules(cls.id)
}

const fetchClassSchedules = async (classId) => {
  try {
    const response = await api.get(`/classes/${classId}/schedules`)
    classSchedules.value = response.data.data || []
  } catch (error) {
    classSchedules.value = []
    ElMessage.error(error.response?.data?.message || '获取排课列表失败')
  }
}

const addSchedule = async () => {
  if (!scheduleForm.value.teacher_id) {
    ElMessage.warning('请选择教师')
    return
  }
  if (!scheduleForm.value.day_of_week) {
    ElMessage.warning('请选择星期')
    return
  }
  if (!scheduleForm.value.start_time) {
    ElMessage.warning('请选择开始时间')
    return
  }
  if (!scheduleForm.value.end_time) {
    ElMessage.warning('请选择结束时间')
    return
  }
  
  try {
    // 格式化时间为 HH:MM
    const formatTime = (date) => {
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    }
    
    const data = {
      teacher_id: scheduleForm.value.teacher_id,
      day_of_week: scheduleForm.value.day_of_week,
      start_time: formatTime(scheduleForm.value.start_time),
      end_time: formatTime(scheduleForm.value.end_time)
    }
    
    await api.post(`/classes/${currentClass.value.id}/schedules`, data)
    ElMessage.success('添加排课成功')
    await fetchClassSchedules(currentClass.value.id)
    // 重置表单
    scheduleForm.value = {
      teacher_id: null,
      day_of_week: null,
      start_time: null,
      end_time: null
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '添加排课失败')
  }
}

const deleteSchedule = async (scheduleId) => {
  try {
    await api.delete(`/classes/${currentClass.value.id}/schedules/${scheduleId}`)
    ElMessage.success('删除排课成功')
    await fetchClassSchedules(currentClass.value.id)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除排课失败')
  }
}

const getDayOfWeekText = (day) => {
  const days = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return days[day] || ''
}

onMounted(() => {
  fetchClasses()
  fetchTeachers()
})
</script>
