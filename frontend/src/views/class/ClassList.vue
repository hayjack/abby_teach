<template>
  <div class="class-list">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 16px; font-weight: bold;">班级信息</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            <span>新增</span>
          </el-button>
        </div>
      </template>

      <el-table :data="classes" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="name" label="班级名称"></el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120">
          <template #default="{row}">
            {{ row.start_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="end_date" label="结束日期" width="120">
          <template #default="{row}">
            {{ row.end_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :prev-text="'上一页'"
          :next-text="'下一页'"
          :page-size-text="'条/页'"
          :jumper-text="'前往'"
          :total-text="'共 '"
        />
      </div>
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
        <el-button @click="dialogVisible = false">
          <el-icon><Close /></el-icon>
          <span>取消</span>
        </el-button>
        <el-button type="success" @click="handleSubmit">
          <el-icon><Check /></el-icon>
          <span>确定</span>
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'
import { Plus, Edit, Delete, Close, Check } from '@element-plus/icons-vue'

const classes = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增班级')
const formRef = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const form = ref({ name: '', description: '', start_date: '', end_date: '' })
const rules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }]
}

const fetchClasses = async () => {
  loading.value = true
  try {
    const response = await api.get('/classes', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value
      }
    })
    classes.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取班级列表失败')
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
  form.value = { 
    id: row.id,
    name: row.name || '', 
    description: row.description || '', 
    start_date: row.start_date || '', 
    end_date: row.end_date || '' 
  }
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
        ElMessage.error(error.response?.data?.message || '操作失败')
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
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchClasses()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  fetchClasses()
}

onMounted(() => { fetchClasses() })
</script>

<style scoped>
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
