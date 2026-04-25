import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  // 系统管理
  {
    path: '/system',
    redirect: '/system/users'
  },
  {
    path: '/system/users',
    name: 'UserManagement',
    component: () => import('../views/system/UserManagement.vue')
  },
  {
    path: '/system/roles',
    name: 'RoleManagement',
    component: () => import('../views/system/RoleManagement.vue')
  },
  {
    path: '/system/menus',
    name: 'MenuManagement',
    component: () => import('../views/system/MenuManagement.vue')
  },
  // 学生管理
  {
    path: '/student',
    redirect: '/student/list'
  },
  {
    path: '/student/list',
    name: 'StudentList',
    component: () => import('../views/student/StudentList.vue')
  },
  {
    path: '/student/payment',
    name: 'PaymentRecord',
    component: () => import('../views/student/PaymentRecord.vue')
  },
  { path: '/student/course', name: 'StudentCourse', component: () => import('../views/student/StudentCourse.vue') },
  { path: '/student/attendance', name: 'StudentAttendance', component: () => import('../views/student/StudentAttendance.vue') },
  // 班级管理
  {
    path: '/class',
    redirect: '/class/list'
  },
  {
    path: '/class/list',
    name: 'ClassList',
    component: () => import('../views/class/ClassList.vue')
  },
  {
    path: '/class/students',
    name: 'ClassStudents',
    component: () => import('../views/class/ClassStudents.vue')
  },
  {
    path: '/class/teachers',
    name: 'ClassTeachers',
    component: () => import('../views/class/ClassTeachers.vue')
  },
  // 课程管理
  {
    path: '/course',
    redirect: '/course/list'
  },
  {
    path: '/course/list',
    name: 'CourseList',
    component: () => import('../views/course/CourseList.vue')
  },
  {
    path: '/course/class',
    name: 'ClassCourse',
    component: () => import('../views/course/ClassCourse.vue')
  },
  // 上课记录
  {
    path: '/record',
    redirect: '/record/list'
  },
  {
    path: '/record/list',
    name: 'ClassRecordList',
    component: () => import('../views/record/ClassRecordList.vue')
  },
  {
    path: '/record/attendance',
    name: 'AttendanceRecord',
    component: () => import('../views/record/AttendanceRecord.vue')
  },
  // 请假记录
  {
    path: '/leave',
    redirect: '/leave/list'
  },
  {
    path: '/leave/list',
    name: 'LeaveRecordList',
    component: () => import('../views/leave/LeaveRecordList.vue')
  },
  {
    path: '/leave/approve',
    name: 'LeaveApprove',
    component: () => import('../views/leave/LeaveApprove.vue')
  },
  // 报表统计
  {
    path: '/report',
    redirect: '/report/student'
  },
  {
    path: '/report/student',
    name: 'StudentReport',
    component: () => import('../views/report/StudentReport.vue')
  },
  {
    path: '/report/teacher',
    name: 'TeacherReport',
    component: () => import('../views/report/TeacherReport.vue')
  },
  {    path: '/report/class',    name: 'ClassReport',    component: () => import('../views/report/ClassReport.vue')  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
