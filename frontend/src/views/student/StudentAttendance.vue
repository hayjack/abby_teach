<template>
  <div class="student-attendance">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>学生上课记录</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索学生姓名"
            style="width: 300px"
            clearable
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
      </template>
      
      <el-table :data="attendanceList" style="width: 100%" border>
        <el-table-column prop="student_name" label="学生姓名" width="120" />
        <el-table-column prop="class_name" label="班级" width="150" />
        <el-table-column prop="course_name" label="课程" width="150" />
        <el-table-column prop="teacher_name" label="教师" width="120" />
        <el-table-column prop="class_date" label="上课日期" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="100" />
        <el-table-column prop="end_time" label="结束时间" width="100" />
        <el-table-column prop="hours" label="课时" width="80" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="is_attended" label="出勤" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_attended ? 'success' : 'danger'">
              {{ scope.row.is_attended ? '是' : '否' }}
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
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api, { getStudents, getStudentAttendance } from '@/utils/api'

const attendanceList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')

// 获取学生列表（用于搜索）
const students = ref([])

onMounted(async () => {
  await fetchStudents()
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

const fetchAttendanceList = async () => {
  try {
    let allAttendance = []
    
    // 直接从学生考勤接口获取数据
    // 先获取所有学生
    const studentsResponse = await getStudents({ page: 1, per_page: 100 })
    const allStudents = studentsResponse.data.items || studentsResponse.data || []
    
    // 收集所有学生的考勤记录
    for (const student of allStudents) {
      try {
        const attendanceResponse = await getStudentAttendance(student.id)
        const studentAttendances = attendanceResponse.data || []
        allAttendance = allAttendance.concat(studentAttendances)
      } catch (error) {
        console.warn(`获取学生 ${student.name} 的考勤记录失败:`, error)
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
.student-attendance {
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