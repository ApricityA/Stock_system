<template>
  <div class="own-stock-page">
    <div class="main-layout">
      <aside class="groups-sidebar">
        <div class="groups-header">
          <h2>自选分组</h2>
          <el-icon @click="createGroup"><FolderAdd /></el-icon>
        </div>
        <div class="groups-list">
          <div 
            v-for="group in groups" 
            :key="group.name"
            :class="['group-item', { active: group.name === activeGroup }]"
            @click="activeGroup = group.name"
          >
            <div class="group-info">
              <el-icon><component :is="group.name === activeGroup ? 'FolderOpened' : 'Folder'" /></el-icon>
              <div>
                <p class="group-name">{{ group.name }}</p>
                <p class="group-stats">{{ group.count }} 只标的 • {{ group.change }} 今日</p>
              </div>
            </div>
            <span :class="['group-count', { active: group.name === activeGroup }]">{{ group.count }}</span>
          </div>
        </div>
        <div class="quick-stats">
          <div class="stats-header">
            <span>快速统计</span>
            <span class="positive">看多</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <p class="stat-label">平均收益</p>
              <p class="stat-value positive">看多</p>
            </div>
            <div class="stat-item">
              <p class="stat-label">波动率</p>
              <p class="stat-value warning">1.42σ</p>
            </div>
          </div>
        </div>
      </aside>

      <section class="watchlist-section">
        <div class="table-controls">
          <div class="controls-left">
            <el-checkbox v-model="selectAll" @change="toggleSelectAll" />
            <span class="view-label">视图:</span>
            <el-button size="small" @click="batchDelete">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
            <el-button size="small" @click="batchMove">
              <el-icon><DArrowRight /></el-icon>
              移动分组
            </el-button>
          </div>
          <div class="controls-right">
            <span class="view-label">视图:</span>
            <el-select v-model="viewType" size="small" class="view-select">
              <el-option label="详细列表" value="detail" />
              <el-option label="MINIMAL" value="minimal" />
              <el-option label="CHART GRID" value="chart" />
            </el-select>
          </div>
        </div>

        <div class="table-container">
          <el-table 
            :data="watchlist" 
            style="width: 100%" 
            class="watchlist-table"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="48" />
            <el-table-column prop="code" label="代码" width="100">
              <template #default="{ row }">
                <span class="code-cell">{{ row.code }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="price" label="价格" align="right" width="120">
              <template #default="{ row }">
                <span class="price-cell">{{ row.price }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌幅 %" align="right" width="120">
              <template #default="{ row }">
                <span :class="row.changeNum > 0 ? 'positive' : 'negative'">{{ row.change }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" align="right" width="120" />
            <el-table-column prop="addDate" label="添加日期" width="120" />
            <el-table-column label="操作" align="center" width="120">
              <template #default>
                <div class="action-buttons">
                  <el-icon @click="setAlert"><Bell /></el-icon>
                  <el-icon @click="deleteStock"><Delete /></el-icon>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeGroup = ref('成长策略')
const selectAll = ref(false)
const viewType = ref('detail')
const selectedStocks = ref([])

const groups = [
  { name: '短线交易', count: 12, change: '+2.4%' },
  { name: '成长策略', count: 8, change: '-0.8%' },
  { name: '指数追踪', count: 5, change: '+0.1%' },
  { name: '加密货币/其他', count: 24, change: '+12.4%' },
]

const watchlist = [
  { code: 'NVDA', name: 'NVIDIA Corporation', price: '128.45', change: '+4.25%', changeNum: 4.25, volume: '42.8M', addDate: '2023-11-14' },
  { code: 'AAPL', name: 'Apple Inc.', price: '182.10', change: '-1.12%', changeNum: -1.12, volume: '68.2M', addDate: '2023-11-10' },
  { code: 'TSLA', name: 'Tesla, Inc.', price: '234.56', change: '+2.18%', changeNum: 2.18, volume: '95.1M', addDate: '2023-11-08' },
  { code: 'MSFT', name: 'Microsoft Corporation', price: '378.90', change: '+0.85%', changeNum: 0.85, volume: '28.4M', addDate: '2023-11-05' },
  { code: 'GOOGL', name: 'Alphabet Inc.', price: '141.25', change: '-0.32%', changeNum: -0.32, volume: '22.6M', addDate: '2023-11-01' },
]

const toggleSelectAll = () => {}
const handleSelectionChange = (selection) => {
  selectedStocks.value = selection
}
const batchDelete = () => {}
const batchMove = () => {}
const createGroup = () => {}
const setAlert = () => {}
const deleteStock = () => {}
</script>

<style scoped>
.own-stock-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.main-layout {
  display: flex;
  gap: 12px;
  flex: 1;
  overflow: hidden;
}

.groups-sidebar {
  width: 288px;
  background: #161b22;
  border: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.groups-header {
  padding: 16px;
  border-bottom: 1px solid #30363d;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.groups-header h2 {
  font-size: 11px;
  color: #c0c7d4;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin: 0;
}

.groups-header .el-icon {
  cursor: pointer;
  color: #8b949e;
}

.groups-header .el-icon:hover {
  color: #58a6ff;
}

.groups-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.group-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.15s;
  border-left: 2px solid transparent;
}

.group-item:hover {
  background: #1f242b;
  border-left-color: #58a6ff;
}

.group-item.active {
  background: #0d1117;
  border-left-color: #58a6ff;
}

.group-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-name {
  font-size: 12px;
  font-weight: bold;
  color: #f0f6fc;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.group-item.active .group-name {
  color: #58a6ff;
}

.group-stats {
  font-size: 10px;
  color: #8b949e;
  font-family: 'Consolas', 'Monaco', monospace;
  margin: 0;
}

.group-count {
  font-size: 10px;
  background: #21262d;
  color: #8b949e;
  padding: 2px 6px;
}

.group-count.active {
  background: #161b22;
  color: #58a6ff;
  border: 1px solid #30363d;
}

.quick-stats {
  padding: 16px;
  background: #0d1117;
  border-top: 1px solid #30363d;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stats-header span:first-child {
  font-size: 10px;
  font-weight: bold;
  color: #8b949e;
}

.positive { color: #26a641; }
.negative { color: #ffb4ab; }
.warning { color: #ffb4ac; }

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-item {
  padding: 8px;
  background: #161b22;
  border: 1px solid #30363d;
}

.stat-label {
  font-size: 9px;
  color: #8b949e;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.watchlist-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.table-controls {
  background: #161b22;
  border: 1px solid #30363d;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.controls-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.controls-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-label {
  font-size: 10px;
  color: #8b949e;
  font-weight: bold;
  text-transform: uppercase;
}

.view-select {
  width: 120px;
}

.view-select :deep(.el-input__inner) {
  background: #0d1117;
  border-color: #30363d;
  color: #f0f6fc;
  font-size: 10px;
  font-weight: bold;
}

.table-container {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  overflow: hidden;
}

.watchlist-table :deep(.el-table) {
  background: transparent;
}

.watchlist-table :deep(.el-table th),
.watchlist-table :deep(.el-table td) {
  background: transparent;
  color: #e0e2ea;
  border-color: #30363d;
}

.watchlist-table :deep(.el-table__body tr:hover > td) {
  background: #1f242b !important;
}

.watchlist-table :deep(.el-table__header) {
  background: #1c2128;
}

.watchlist-table :deep(.el-table th) {
  font-size: 11px;
  text-transform: uppercase;
  color: #8b949e;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.code-cell {
  font-size: 12px;
  font-weight: bold;
  color: #f0f6fc;
  font-family: 'Consolas', 'Monaco', monospace;
}

.price-cell {
  font-size: 12px;
  color: #f0f6fc;
  font-family: 'Consolas', 'Monaco', monospace;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.15s;
}

.watchlist-table :deep(.el-table__body tr:hover) .action-buttons {
  opacity: 1;
}

.action-buttons .el-icon {
  cursor: pointer;
  color: #8b949e;
}

.action-buttons .el-icon:hover:first-child {
  color: #58a6ff;
}

.action-buttons .el-icon:hover:last-child {
  color: #ffb4ab;
}
</style>
