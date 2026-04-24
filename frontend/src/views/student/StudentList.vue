<template>
  <div class="student-list">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>学生信息</span>
          <el-button type="primary" @click="handleAdd">新增学生</el-button>
        </div>
      </template>

      <el-table :data="students" v-loading="loading">
        <el-table-column prop="name" label="姓名"></el-table-column>
        <el-table-column prop="english_name" label="英文名"></el-table-column>
        <el-table-column prop="gender" label="性别"></el-table-column>
        <el-table-column prop="parent_name" label="家长姓名"></el-table-column>
        <el-table-column prop="parent_phone" label="家长手机号"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="英文名" prop="english_name">
          <el-input v-model="form.english_name"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" placeholder="请选择">
            <el-option label="男" value="男"></el-option>
            <el-option label="女" value="女"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="form.birthday" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <el-form-item label="家长姓名" prop="parent_name">
          <el-input v-model="form.parent_name"></el-input>
        </el-form-item>
        <el-form-item label="家长手机号" prop="parent_phone">
          <el-input v-model="form.parent_phone"></el-input>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" type="textarea"></el-input>
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

const students = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增学生')
const formRef = ref(null)

const form = ref({
  name: '',
  english_name: '',
  gender: '',
  birthday: '',
  parent_name: '',
  parent_phone: '',
  address: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  english_name: [{ required: true, message: '请输入英文名', trigger: 'blur' }],
  parent_name: [{ required: true, message: '请输入家长姓名', trigger: 'blur' }],
  parent_phone: [{ required: true, message: '请输入家长手机号', trigger: 'blur' }]
}

const fetchStudents = async () => {
  loading.value = true
  try {
    const response = await api.get('/students')
    students.value = response.data
  } catch (error) {
    ElMessage.error('获取学生列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增学生'
  form.value = { name: '', english_name: '', gender: '', birthday: '', parent_name: '', parent_phone: '', address: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑学生'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.value.id) {
          await api.put(`/students/${form.value.id}`, form.value)
          ElMessage.success('更新成功')
        } else {
          await api.post('/students', form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchStudents()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const handleDelete = async (id) => {
  try {
    await api.delete(`/students/${id}`)
    ElMessage.success('删除成功')
    fetchStudents()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchStudents()
})
</script>
