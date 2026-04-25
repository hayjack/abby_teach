<template>
  <div class="class-record-list">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>上课记录</span>
          <div>
            <el-button type="primary" @click="handleAdd">录入上课记录</el-button>
            <el-button type="success" @click="handleAddMakeup" style="margin-left: 10px;">录入补课记录</el-button>
          </div>
        </div>
      </template>

      <el-table :data="records" v-loading="loading">
        <el-table-column prop="class_name" label="班级"></el-table-column>
        <el-table-column prop="course_name" label="课程"></el-table-column>
        <el-table-column prop="teacher_name" label="教师"></el-table-column>
        <el-table-column prop="class_date" label="上课日期"></el-table-column>
        <el-table-column label="时间">
          <template #default="{row}">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="hours" label="课时"></el-table-column>
        <el-table-column label="上课方式" width="100">
          <template #default="{row}">
            <el-tag :type="row.is_makeup ? 'warning' : 'info'">
              {{ row.is_makeup ? '补课' : '班课' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" @click="handleView(row)">查看详情</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" title="录入上课记录" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" filterable @change="(val) => fetchClassCourses(val)">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="form.course_id" placeholder="请选择课程">
            <el-option v-for="c in availableCourses" :key="c.course_id" :label="c.course_name" :value="c.course_id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="上课日期" prop="class_date">
          <el-date-picker v-model="form.class_date" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker v-model="form.start_time" placeholder="选择时间"></el-time-picker>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker v-model="form.end_time" placeholder="选择时间"></el-time-picker>
        </el-form-item>
        <el-form-item label="课时数" prop="hours">
          <el-input-number v-model="form.hours" :min="0.5" :step="0.5" :precision="1"></el-input-number>
        </el-form-item>
        <el-form-item label="上课内容">
          <el-input v-model="form.content" type="textarea"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="考勤详情" width="600px">
      <el-table :data="attendances">
        <el-table-column prop="student_name" label="学生姓名"></el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{row}">
            <el-tag :type="row.status === '出勤' ? 'success' : row.status === '请假' ? 'warning' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="makeupDialogVisible" title="录入补课记录" width="600px">
      <el-form :model="makeupForm" :rules="makeupRules" ref="makeupFormRef" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="makeupForm.student_id" placeholder="请选择学生" filterable>
            <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.english_name})`" :value="s.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="makeupForm.course_id" placeholder="请选择课程" filterable>
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="上课日期" prop="class_date">
          <el-date-picker v-model="makeupForm.class_date" type="date" placeholder="选择日期"></el-date-picker>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker v-model="makeupForm.start_time" placeholder="选择时间"></el-time-picker>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker v-model="makeupForm.end_time" placeholder="选择时间"></el-time-picker>
        </el-form-item>
        <el-form-item label="课时数" prop="hours">
          <el-input-number v-model="makeupForm.hours" :min="0.5" :step="0.5" :precision="1"></el-input-number>
        </el-form-item>
        <el-form-item label="补课内容">
          <el-input v-model="makeupForm.content" type="textarea"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="makeupDialogVisible = false">取消</el-button>
        <el-button type="success" @click="handleMakeupSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'

const records = ref([])
const classes = ref([])
const courses = ref([])
const students = ref([])
const availableCourses = ref([])
const attendances = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const makeupDialogVisible = ref(false)
const formRef = ref(null)
const makeupFormRef = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const form = ref({
  class_id: '',
  course_id: '',
  class_date: '',
  start_time: '',
  end_time: '',
  hours: 1,
  content: ''
})

const rules = {
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  class_date: [{ required: true, message: '请选择上课日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

const makeupForm = ref({
  student_id: '',
  course_id: '',
  class_date: '',
  start_time: '',
  end_time: '',
  hours: 1,
  content: ''
})

const makeupRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  class_date: [{ required: true, message: '请选择上课日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const response = await api.get('/class_records', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value
      }
    })
    console.log('Response data:', response.data)
    records.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('Error fetching records:', error)
    ElMessage.error(error.response?.data?.message || '获取上课记录失败')
  } finally {
    loading.value = false
  }
}

const fetchClasses = async () => {
  try {
    const response = await api.get('/classes')
    classes.value = response.data.items || []
  } catch (error) {
    console.error(error)
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

const fetchCourses = async () => {
  try {
    const response = await api.get('/courses')
    courses.value = response.data.items || []
  } catch (error) {
    console.error(error)
  }
}

const fetchClassCourses = async (classId) => {
  if (!classId) {
    availableCourses.value = []
    return
  }
  form.value.course_id = ''
  try {
    const response = await api.get(`/classes/${classId}`)
    availableCourses.value = response.data.courses || []
  } catch (error) {
    availableCourses.value = []
  }
}

const handleAdd = () => {
  form.value = { class_id: '', course_id: '', class_date: '', start_time: '', end_time: '', hours: 1, content: '' }
  availableCourses.value = []
  dialogVisible.value = true
}

const handleAddMakeup = () => {
  makeupForm.value = { student_id: '', course_id: '', class_date: '', start_time: '', end_time: '', hours: 1, content: '' }
  makeupDialogVisible.value = true
}

const handleMakeupSubmit = async () => {
  if (!makeupFormRef.value) return
  await makeupFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await api.post('/class_records/makeup', makeupForm.value)
        ElMessage.success('补课记录录入成功，已自动扣除学生课时')
        makeupDialogVisible.value = false
        fetchRecords()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '录入失败')
      }
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await api.post('/class_records', form.value)
        ElMessage.success('录入成功，已自动扣除出勤学生课时')
        dialogVisible.value = false
        fetchRecords()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '录入失败')
      }
    }
  })
}

const handleView = async (record) => {
  try {
    const response = await api.get(`/class_records/${record.id}`)
    attendances.value = response.data.attendances || []
    detailVisible.value = true
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取考勤详情失败')
  }
}

const handleDelete = async (id) => {
  try {
    await api.delete(`/class_records/${id}`)
    ElMessage.success('删除成功（已恢复学生课时）')
    fetchRecords()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchRecords()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  fetchRecords()
}

onMounted(() => {
  fetchRecords()
  fetchClasses()
  fetchStudents()
  fetchCourses()
})
</script>

<style scoped>
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
