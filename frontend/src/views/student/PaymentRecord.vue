<template>
  <div class="payment-record">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 16px; font-weight: bold;">缴费记录</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            <span>新增</span>
          </el-button>
        </div>
      </template>

      <el-table :data="payments" v-loading="loading" stripe style="width: 100%;">
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="amount" label="金额">
          <template #default="{row}">
            {{ row.amount }} 元
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="缴费日期"></el-table-column>
        <el-table-column prop="payment_type" label="缴费类型"></el-table-column>
        <el-table-column prop="remark" label="备注"></el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" type="danger" @click="handleDelete(row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增缴费记录" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="form.student_id" placeholder="请选择学生" filterable>
            <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.english_name})`" :value="s.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="缴费日期" prop="payment_date">
          <el-date-picker v-model="form.payment_date" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <el-form-item label="缴费类型" prop="payment_type">
          <el-select v-model="form.payment_type" placeholder="请选择">
            <el-option label="现金" value="现金"></el-option>
            <el-option label="微信" value="微信"></el-option>
            <el-option label="支付宝" value="支付宝"></el-option>
            <el-option label="银行转账" value="银行转账"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea"></el-input>
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
import { Plus, Delete, Close, Check } from '@element-plus/icons-vue'

const payments = ref([])
const students = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)

const form = ref({
  student_id: '',
  amount: '',
  payment_date: '',
  payment_type: '',
  remark: ''
})

const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  payment_date: [{ required: true, message: '请选择缴费日期', trigger: 'change' }],
  payment_type: [{ required: true, message: '请选择缴费类型', trigger: 'change' }]
}

const fetchPayments = async () => {
  loading.value = true
  try {
    const response = await api.get('/payments')
    payments.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取缴费记录失败')
  } finally {
    loading.value = false
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students')
    students.value = response.data.items || []
  } catch (error) {
    console.error(error)
  }
}

const handleAdd = () => {
  form.value = { student_id: '', amount: '', payment_date: '', payment_type: '', remark: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await api.post('/payments', form.value)
        ElMessage.success('创建成功')
        dialogVisible.value = false
        fetchPayments()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    }
  })
}

const handleDelete = async (id) => {
  try {
    await api.delete(`/payments/${id}`)
    ElMessage.success('删除成功')
    fetchPayments()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

onMounted(() => {
  fetchPayments()
  fetchStudents()
})
</script>
