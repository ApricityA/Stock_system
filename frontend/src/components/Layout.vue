<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-title">量化核心</div>
        <div class="logo-version">终端 V2.4</div>
      </div>
      <div class="new-trade">
        <el-button type="primary" class="w-full">
          <el-icon><Plus /></el-icon>
          新建交易
        </el-button>
      </div>
      <nav class="nav-menu">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { Plus, Monitor, Filter, EditPen, Star, Bell } from '@element-plus/icons-vue'

const menuItems = [
  { path: '/', name: '大盘看板', icon: Monitor },
  { path: '/review', name: '复盘日志', icon: EditPen },
  { path: '/own-stock', name: '自选股', icon: Star },
]
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background-color: #0d1117;
}

.sidebar {
  width: 256px;
  background-color: #161b22;
  border-right: 1px solid #30363d;
  padding: 24px 8px;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 0 16px;
}

.logo-title {
  font-size: 18px;
  font-weight: 900;
  color: #f0f6fc;
  letter-spacing: -0.05em;
}

.logo-version {
  font-size: 10px;
  color: #8b949e;
  font-weight: 700;
  letter-spacing: 0.15em;
  margin-top: 4px;
  text-transform: uppercase;
  opacity: 0.6;
}

.new-trade {
  margin-top: 16px;
  padding: 0 8px;
}

.nav-menu {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  color: #8b949e;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.15s;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.nav-item:hover {
  color: #f0f6fc;
  background-color: #21262d;
}

.nav-item.active {
  background-color: #0d1117;
  color: #58a6ff;
  border-left: 2px solid #58a6ff;
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}
</style>
