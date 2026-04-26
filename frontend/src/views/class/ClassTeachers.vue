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
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" @click="showTeachers(row)">
              <el-icon><View /></el-icon>
              <span>查看/编辑教师</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import { Plus, View, Delete } from '@element-plus/icons-vue'
import { getTeachers } from '../../utils/services'

const classList = ref([])
const teachers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentClass = ref({})
const classTeachers = ref([])
const selectedTeacher = ref(null)

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

onMounted(() => {
  fetchClasses()
  fetchTeachers()
})
</script>
