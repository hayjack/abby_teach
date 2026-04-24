<template>
  <div class="app">
    <el-container style="height: 100vh; width: 100vw;">
      <!-- 侧边栏 -->
      <el-aside width="200px" style="background-color: #303133;">
        <div class="logo">教学管理系统</div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical-demo"
          background-color="#303133"
          text-color="#fff"
          active-text-color="#409EFF"
          router
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
            <el-menu-item index="/record/list">上课记录</el-menu-item>
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
            <el-menu-item index="/report/course">课程统计</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header style="background-color: #fff; border-bottom: 1px solid #e4e7ed; display: flex; justify-content: space-between; align-items: center;">
          <div class="header-left">
            <el-button type="text" @click="collapseMenu">
              <el-icon><Menu /></el-icon>
            </el-button>
          </div>
          <div class="header-right">
            <el-dropdown>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './store'
import { House, Setting, User, FolderOpened, Reading, Calendar, Postcard, DataAnalysis, Menu, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('/dashboard')
const user = ref({ name: '管理员' })

// 监听路由变化，更新激活的菜单
router.beforeEach((to, from, next) => {
  activeMenu.value = to.path
  next()
})

// 折叠菜单
const collapseMenu = () => {
  // 实现菜单折叠功能
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

// 初始化用户信息
onMounted(() => {
  // 从localStorage获取用户信息
  const userInfo = localStorage.getItem('user')
  if (userInfo) {
    user.value = JSON.parse(userInfo)
  }
})
</script>

<style scoped>
.app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #409EFF;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
