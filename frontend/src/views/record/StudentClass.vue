<template>
  <div class="student-class">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span style="font-size: 16px; font-weight: bold;">学生上课记录</span>
        </div>
      </template>
      
      <div class="search-form" style="margin-bottom: 20px;">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-select v-model="searchForm.class_id" placeholder="选择班级" clearable filterable style="width: 100%;" @change="handleClassChange">
              <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id"></el-option>
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-select v-model="searchForm.student_id" placeholder="选择学生" clearable filterable style="width: 100%;">
              <el-option v-for="s in filteredStudents" :key="s.id" :label="`${s.name} (${s.english_name})`" :value="s.id"></el-option>
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-select v-model="searchForm.is_makeup" placeholder="上课方式" clearable style="width: 100%;">
              <el-option label="班课" :value="false"></el-option>
              <el-option label="补课" :value="true"></el-option>
            </el-select>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 10px;">
          <el-col :span="16">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%"
              clearable
            />
          </el-col>
          <el-col :span="8" style="display: flex; align-items: center; justify-content: flex-end;">
            <el-button type="primary" @click="handleSearch" style="width: 120px;">
              <el-icon><Search /></el-icon>
              <span>查询</span>
            </el-button>
          </el-col>
        </el-row>
      </div>
      
      <el-table :data="attendanceList" style="width: 100%" border stripe>
        <el-table-column prop="student_name" label="学生姓名" width="120" />
        <el-table-column prop="class_name" label="班级" width="150" />
        <el-table-column prop="course_name" label="课程" width="150" />
        <el-table-column prop="teacher_name" label="教师" width="120" />
        <el-table-column prop="class_date" label="上课日期" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="100" />
        <el-table-column prop="end_time" label="结束时间" width="100" />
        <el-table-column prop="hours" label="课时" width="80" />
        <el-table-column label="上课方式" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_makeup ? 'warning' : 'info'">
              {{ scope.row.is_makeup ? '补课' : '班课' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="出勤状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '出勤' ? 'success' : scope.row.status === '请假' ? 'warning' : 'danger'">
              {{ scope.row.status }}
            </el-tag>
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
      
      <div v-else class="empty-state">
        <el-empty description="暂无上课记录" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api, { getStudents, getStudentAttendance } from '@/utils/api'

const attendanceList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const dateRange = ref([])
const searchForm = ref({
  class_id: '',
  student_id: '',
  is_makeup: ''
})

// 获取学生列表（用于搜索）
const students = ref([])
const classes = ref([])

// 班级学生列表
const classStudents = ref([])

// 计算属性：根据选择的班级筛选学生
const filteredStudents = computed(() => {
  if (!searchForm.value.class_id) {
    return students.value
  }
  return classStudents.value
})

onMounted(async () => {
  await fetchStudents()
  await fetchClasses()
  await fetchAttendanceList()
})

const fetchStudents = async () => {
  try {
    const response = await getStudents({ page: 1, per_page: 100 })
    // 处理不同的数据格式
    students.value = response.data.items || response.data || []
  } catch (error) {
    ElMessage.error('获取学生列表失败')
  }
}

const fetchClasses = async () => {
  try {
    const response = await api.get('/classes')
    // 处理不同的数据格式
    classes.value = response.data.items || response.data || []
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  }
}

const fetchClassStudents = async (classId) => {
  if (!classId) {
    classStudents.value = []
    return
  }
  try {
    const response = await api.get(`/classes/${classId}/students`)
    // 处理不同的数据格式
    classStudents.value = response.data || []
  } catch (error) {
    ElMessage.error('获取班级学生列表失败')
    classStudents.value = []
  }
}

const handleClassChange = async () => {
  // 当班级变化时，重置学生选择
  searchForm.value.student_id = ''
  // 获取班级学生列表
  await fetchClassStudents(searchForm.value.class_id)
}

const fetchAttendanceList = async () => {
  try {
    let allAttendance = []
    
    // 确定要查询的学生ID列表
    let targetStudents = []
    if (searchForm.value.student_id) {
      // 如果选择了特定学生，只查询该学生
      targetStudents = [searchForm.value.student_id]
    } else if (searchForm.value.class_id) {
      // 如果选择了班级，查询该班级的所有学生
      // 这里简化处理，实际应该根据班级ID从后端获取学生列表
      // 由于当前没有班级学生关联的API，暂时查询所有学生
      targetStudents = students.value.map(s => s.id)
    } else {
      // 否则查询所有学生
      const studentsResponse = await getStudents({ page: 1, per_page: 100 })
      const allStudents = studentsResponse.data.items || studentsResponse.data || []
      targetStudents = allStudents.map(s => s.id)
    }
    
    // 收集学生的考勤记录
    for (const studentId of targetStudents) {
      try {
        const params = {}
        // 添加日期区间参数
        if (dateRange.value && dateRange.value.length === 2) {
          params.start_date = dateRange.value[0].toISOString().split('T')[0]
          params.end_date = dateRange.value[1].toISOString().split('T')[0]
        }
        // 添加上课方式参数
        if (searchForm.value.is_makeup !== '') {
          params.is_makeup = searchForm.value.is_makeup
        }
        
        const attendanceResponse = await getStudentAttendance(studentId, params)
        const studentAttendances = attendanceResponse.data || []
        allAttendance = allAttendance.concat(studentAttendances)
      } catch (error) {
        console.warn(`获取学生 ${studentId} 的考勤记录失败:`, error)
      }
    }
    
    console.log('All attendance:', allAttendance)
    
    // 如果有搜索关键词，过滤记录
    if (searchQuery.value) {
      allAttendance = allAttendance.filter(item => 
        item.student_name.includes(searchQuery.value)
      )
      console.log('Filtered attendance:', allAttendance)
    }
    
    // 分页处理
    total.value = allAttendance.length
    console.log('Total:', total.value)
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    attendanceList.value = allAttendance.slice(start, end)
    console.log('Attendance list:', attendanceList.value)
  } catch (error) {
    console.error('Error fetching attendance:', error)
    ElMessage.error('获取上课记录失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchAttendanceList()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchAttendanceList()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  fetchAttendanceList()
}
</script>

<style scoped>
.student-class {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  margin: 50px 0;
  text-align: center;
}
</style>