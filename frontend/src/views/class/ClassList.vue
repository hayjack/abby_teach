<template>
  <div class="class-list">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>班级信息</span>
          <el-button type="primary" @click="handleAdd">新增班级</el-button>
        </div>
      </template>

      <el-table :data="classes" v-loading="loading">
        <el-table-column prop="name" label="班级名称"></el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column prop="start_date" label="开始日期"></el-table-column>
        <el-table-column prop="end_date" label="结束日期"></el-table-column>
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
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea"></el-input>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date"></el-date-picker>
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="form.end_date" type="date"></el-date-picker>
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

const classes = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增班级')
const formRef = ref(null)

const form = ref({ name: '', description: '', start_date: '', end_date: '' })
const rules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }]
}

const fetchClasses = async () => {
  loading.value = true
  try {
    const response = await api.get('/classes')
    classes.value = response.data
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增班级'
  form.value = { name: '', description: '', start_date: '', end_date: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑班级'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.value.id) {
          await api.put(`/classes/${form.value.id}`, form.value)
          ElMessage.success('更新成功')
        } else {
          await api.post('/classes', form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchClasses()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const handleDelete = async (id) => {
  try {
    await api.delete(`/classes/${id}`)
    ElMessage.success('删除成功')
    fetchClasses()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => { fetchClasses() })
</script>
