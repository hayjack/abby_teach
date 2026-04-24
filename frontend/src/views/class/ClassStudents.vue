<template>
  <div class="class-students">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>班级学生管理</span>
          <el-button type="primary" @click="handleAdd">添加学生到班级</el-button>
        </div>
      </template>

      <el-table :data="classList" v-loading="loading">
        <el-table-column prop="id" label="班级ID"></el-table-column>
        <el-table-column prop="name" label="班级名称"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" @click="showStudents(row)">查看/编辑学生</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="'班级: ' + currentClass.name" width="600px">
      <div style="margin-bottom: 16px;">
        <el-select v-model="selectedStudent" placeholder="选择要添加的学生" filterable style="width: 300px;">
          <el-option v-for="s in students" :key="s.id" :label="s.name + ' (' + s.english_name + ')'" :value="s.id"></el-option>
        </el-select>
        <el-button type="primary" style="margin-left: 10px;" @click="addStudentToClass">添加</el-button>
      </div>

      <el-table :data="classStudents">
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="joined_date" label="加入日期"></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button size="small" type="danger" @click="removeStudent(row.student_id)">移除</el-button>
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

const classList = ref([])
const students = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentClass = ref({})
const classStudents = ref([])
const selectedStudent = ref(null)

const fetchClasses = async () => {
  loading.value = true
  try {
    const response = await api.get('/classes')
    classList.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取班级列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students')
    students.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const showStudents = async (cls) => {
  currentClass.value = cls
  dialogVisible.value = true
  try {
    const response = await api.get(`/classes/${cls.id}`)
    classStudents.value = response.data.students || []
  } catch (error) {
    classStudents.value = []
  }
}

const addStudentToClass = async () => {
  if (!selectedStudent.value) {
    ElMessage.warning('请先选择学生')
    return
  }
  try {
    await api.post(`/classes/${currentClass.value.id}/students`, { student_id: selectedStudent.value })
    ElMessage.success('添加成功')
    showStudents(currentClass.value)
    selectedStudent.value = null
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '添加失败')
  }
}

const removeStudent = async (studentId) => {
  try {
    await api.delete(`/classes/${currentClass.value.id}/students/${studentId}`)
    ElMessage.success('移除成功')
    showStudents(currentClass.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '移除失败')
  }
}

onMounted(() => {
  fetchClasses()
  fetchStudents()
})
</script>
