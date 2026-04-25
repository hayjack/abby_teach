<template>
  <div class="app">
    <el-container style="height: 100vh; width: 100vw;">
      <!-- 侧边栏 -->
      <el-aside width="215px" style="background-color: #303133;">
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
            <el-menu-item index="/student/attendance">上课记录</el-menu-item>
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
            <el-menu-item index="/report/class">班级统计</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header style="background-color: #fff; border-bottom: 1px solid #e4e7ed; display: flex; flex-direction: column; align-items: flex-start; padding: 10px 20px;">
          <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div class="welcome-message">
              <span>尊敬的<span style="font-weight: bold; color: #409EFF;">{{ user.name }}</span>，您好！</span>
              <span style="margin-left: 20px;">今天是 {{ currentDate }}</span>
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
          </div>
          <div class="header-left" style="width: 100%;">
            <el-button type="text" @click="collapseMenu">
              <el-icon><Menu /></el-icon>
            </el-button>
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
import { useRouter } from 'vue-router'
import { useUserStore } from './store'
import { House, Setting, User, FolderOpened, Reading, Calendar, Postcard, DataAnalysis, Menu, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('/dashboard')
const user = ref({ name: '管理员' })

// 计算当前日期
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 监听用户信息变化
watch(() => userStore.userInfo, (newUserInfo) => {
  if (newUserInfo) {
    user.value = newUserInfo
  }
}, { immediate: true })

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
  userStore.logout()
  router.push('/login')
}

// 初始化用户信息
onMounted(() => {
  // 从store获取用户信息
  if (userStore.userInfo) {
    user.value = userStore.userInfo
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
