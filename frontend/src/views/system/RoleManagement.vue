<template>
  <div class="role-management">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>角色管理</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
        </div>
      </template>

      <el-table :data="roles" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60"></el-table-column>
        <el-table-column prop="name" label="角色名称"></el-table-column>
        <el-table-column prop="priority" label="优先级" width="100"></el-table-column>
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
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="form.priority" :min="0" :max="100" :step="10"></el-input-number>
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            优先级越高，角色权限越大（管理员:100, 校长:80, 教学主管:60, 教师:20）
          </div>
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

const roles = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const formRef = ref(null)

const form = ref({ name: '', priority: 0 })
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const fetchRoles = async () => {
  loading.value = true
  try {
    const response = await api.get('/roles')
    roles.value = response.data
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增角色'
  form.value = { name: '', priority: 0 }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑角色'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.value.id) {
          await api.put(`/roles/${form.value.id}`, form.value)
          ElMessage.success('更新成功')
        } else {
          await api.post('/roles', form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchRoles()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const handleDelete = async (id) => {
  try {
    await api.delete(`/roles/${id}`)
    ElMessage.success('删除成功')
    fetchRoles()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchRoles()
})
</script>
