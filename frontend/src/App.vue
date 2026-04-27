<template>
  <div class="app">
    <el-container style="height: 100vh; width: 100vw;">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '215px'" style="background-color: #303133; transition: width 0.3s;">
        <div class="logo" :style="{ width: isCollapse ? '64px' : '215px' }">
          <span v-if="!isCollapse">教学管理系统</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          :collapse="isCollapse"
          background-color="#303133"
          text-color="#fff"
          active-text-color="#409EFF"
          router
          :collapse-transition="false"
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-sub-menu index="/system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/users">教师管理</el-menu-item>
            <el-menu-item index="/system/roles">角色管理</el-menu-item>
            <el-menu-item index="/system/menus">菜单管理</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/student">
            <template #title>
              <el-icon><User /></el-icon>
              <span>学生管理</span>
            </template>
            <el-menu-item index="/student/list">学生信息</el-menu-item>
            <el-menu-item index="/student/payment">缴费记录</el-menu-item>
            <el-menu-item index="/student/course">课时管理</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/class">
            <template #title>
              <el-icon><FolderOpened /></el-icon>
              <span>班级管理</span>
            </template>
            <el-menu-item index="/class/list">班级信息</el-menu-item>
            <el-menu-item index="/class/students">班级学生</el-menu-item>
            <el-menu-item index="/class/teachers">班级教师</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/course">
            <template #title>
              <el-icon><Reading /></el-icon>
              <span>课程管理</span>
            </template>
            <el-menu-item index="/course/list">课程信息</el-menu-item>
            <el-menu-item index="/course/class">班级课程</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/record">
            <template #title>
              <el-icon><Calendar /></el-icon>
              <span>上课记录</span>
            </template>
            <el-menu-item index="/record/list">教师上课</el-menu-item>
            <el-menu-item index="/record/student">学生上课</el-menu-item>
            <el-menu-item index="/record/attendance">考勤记录</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/leave">
            <template #title>
              <el-icon><Postcard /></el-icon>
              <span>请假记录</span>
            </template>
            <el-menu-item index="/leave/list">请假记录</el-menu-item>
            <el-menu-item index="/leave/approve">请假审批</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/report">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>报表统计</span>
            </template>
            <el-menu-item index="/report/student">学生统计</el-menu-item>
            <el-menu-item index="/report/teacher">教师统计</el-menu-item>
            <el-menu-item index="/report/class">班级统计</el-menu-item>
            <el-menu-item index="/report/schedule">课程表</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header style="background-color: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px;">
          <div class="header-content">
            <div class="header-left">
              <el-button type="text" @click="toggleCollapse" class="menu-toggle">
                <el-icon><Menu /></el-icon>
              </el-button>
              <el-breadcrumb separator="/" style="margin-left: 20px;">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item v-for="(item, index) in breadcrumbItems" :key="index">
                  {{ item.label }}
                </el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="header-right">
              <div class="welcome-message">
                <span>尊敬的<span style="font-weight: bold; color: #409EFF;">{{ user.name }}</span>，您好！</span>
                <span style="margin-left: 20px;">今天是 {{ currentDate }}</span>
              </div>
              <el-dropdown class="user-dropdown">
                <span class="el-dropdown-link">
                  {{ user.name }} <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        
        <!-- 内容区域 -->
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './store'
import { House, Setting, User, FolderOpened, Reading, Calendar, Postcard, DataAnalysis, Menu, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const activeMenu = ref('/dashboard')
const user = ref({ name: '管理员' })
const isCollapse = ref(false)

// 计算当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 面包屑导航数据
const breadcrumbItems = ref([])

// 路由路径映射到面包屑标签
const routeMap = {
  '/dashboard': '首页',
  '/system': '系统管理',
  '/system/users': '教师管理',
  '/system/roles': '角色管理',
  '/system/menus': '菜单管理',
  '/student': '学生管理',
  '/student/list': '学生信息',
  '/student/payment': '缴费记录',
  '/student/course': '课时管理',
  '/student/attendance': '上课记录',
  '/class': '班级管理',
  '/class/list': '班级信息',
  '/class/students': '班级学生',
  '/class/teachers': '班级教师',
  '/course': '课程管理',
  '/course/list': '课程信息',
  '/course/class': '班级课程',
  '/record': '上课记录',
  '/record/list': '教师上课',
  '/record/student': '学生上课',
  '/record/attendance': '考勤记录',
  '/leave': '请假记录',
  '/leave/list': '请假记录',
  '/leave/approve': '请假审批',
  '/report': '报表统计',
  '/report/student': '学生统计',
  '/report/teacher': '教师统计',
  '/report/class': '班级统计',
  '/report/schedule': '课程表'
}

// 生成面包屑导航
const generateBreadcrumb = (path) => {
  const items = []
  const pathParts = path.split('/').filter(Boolean)
  let currentPath = ''
  
  pathParts.forEach(part => {
    currentPath += `/${part}`
    if (routeMap[currentPath]) {
      items.push({ path: currentPath, label: routeMap[currentPath] })
    }
  })
  
  return items
}

// 监听用户信息变化
watch(() => userStore.userInfo, (newUserInfo) => {
  if (newUserInfo) {
    user.value = newUserInfo
  }
}, { immediate: true })

// 监听路由变化，更新激活的菜单和面包屑
watch(() => route.path, (newPath) => {
  activeMenu.value = newPath
  breadcrumbItems.value = generateBreadcrumb(newPath)
}, { immediate: true })

// 切换菜单折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 初始化用户信息
onMounted(() => {
  // 从store获取用户信息
  if (userStore.userInfo) {
    user.value = userStore.userInfo
  }
  // 初始化面包屑
  breadcrumbItems.value = generateBreadcrumb(route.path)
})
</script>

<style scoped>
.app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #409EFF;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.el-menu-vertical-demo {
  border-right: none;
  min-height: calc(100vh - 60px);
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.welcome-message {
  font-size: 14px;
  color: #606266;
}

.user-dropdown {
  margin-left: 16px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.el-dropdown-link:hover {
  background-color: #f5f7fa;
  color: #409EFF;
}

.menu-toggle {
  font-size: 18px;
  color: #606266;
  transition: all 0.3s;
}

.menu-toggle:hover {
  color: #409EFF;
}

.el-main {
  padding: 24px;
  background-color: #f5f7fa;
  overflow-y: auto;
}

/* 自定义滚动条 */
.el-main::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.el-main::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.el-main::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.el-main::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
