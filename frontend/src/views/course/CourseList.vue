<template>
  <div class="course-list">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>课程信息</span>
          <el-button type="primary" @click="handleAdd">新增课程</el-button>
        </div>
      </template>

      <el-table :data="courses" v-loading="loading">
        <el-table-column prop="name" label="课程名称"></el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column prop="total_hours" label="总课时"></el-table-column>
        <el-table-column prop="price" label="价格">
          <template #default="{row}">
            {{ row.price ? row.price + ' 元' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea"></el-input>
        </el-form-item>
        <el-form-item label="总课时" prop="total_hours">
          <el-input-number v-model="form.total_hours" :min="1"></el-input-number>
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2"></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'

const courses = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增课程')
const formRef = ref(null)

const form = ref({ name: '', description: '', total_hours: 10, price: null })
const rules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  total_hours: [{ required: true, message: '请输入总课时', trigger: 'blur' }]
}

const fetchCourses = async () => {
  loading.value = true
  try {
    const response = await api.get('/courses')
    courses.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取课程列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增课程'
  form.value = { name: '', description: '', total_hours: 10, price: null }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑课程'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.value.id) {
          await api.put(`/courses/${form.value.id}`, form.value)
          ElMessage.success('更新成功')
        } else {
          await api.post('/courses', form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchCourses()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    }
  })
}

const handleDelete = async (id) => {
  try {
    await api.delete(`/courses/${id}`)
    ElMessage.success('删除成功')
    fetchCourses()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

onMounted(() => { fetchCourses() })
</script>
