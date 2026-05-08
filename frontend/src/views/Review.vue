<template>
  <div class="review-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button :type="viewMode === 'calendar' ? 'primary' : 'default'" @click="viewMode = 'calendar'">
          <el-icon><Calendar /></el-icon>
          日历模式
        </el-button>
        <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
          <el-icon><List /></el-icon>
          列表模式
        </el-button>
      </div>
      <div class="toolbar-right">
        <span class="market-status">休市: <span class="positive">交易中 (UTC)</span></span>
      </div>
    </div>

    <div class="main-content">
      <div class="calendar-panel">
        <div class="panel-header">
          <span>复盘日历</span>
          <div class="month-nav">
            <el-icon @click="prevMonth"><ArrowLeft /></el-icon>
            <span>{{ currentMonth }}</span>
            <el-icon @click="nextMonth"><ArrowRight /></el-icon>
          </div>
        </div>
        <div class="calendar-grid">
          <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
          <div 
            v-for="date in calendarDates" 
            :key="date.day"
            :class="['date-cell', { 
              'has-log': date.hasLog,
              'today': date.isToday,
              'other-month': !date.isCurrentMonth,
              'selected': date.isSelected
            }]"
            @click="selectDate(date)"
          >
            {{ date.day }}
            <div v-if="date.hasLog" class="log-indicator"></div>
          </div>
        </div>

        <div class="monthly-stats">
          <div class="stat-card">
            <div class="stat-label">月度胜率</div>
            <div class="stat-value positive">64.5%</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">总盈亏 (10月)</div>
            <div class="stat-value positive">+$12,408.00</div>
          </div>
        </div>
      </div>

      <div class="editor-panel">
        <div class="editor-header">
          <div>
            <div class="editor-title">当日复盘编辑</div>
            <div class="editor-date">{{ selectedDate }} — 周一交易时段</div>
          </div>
          <div class="editor-actions">
            <div class="sentiment-rating">
              <span>市场情绪:</span>
              <el-rate v-model="sentiment" :colors="['#ffb4ab', '#ffb4ab', '#58a6ff', '#58a6ff', '#26a641']" />
            </div>
            <el-button type="primary" @click="saveReview">保存记录</el-button>
          </div>
        </div>

        <div class="editor-content">
          <div class="editor-row">
            <div class="editor-field">
              <label>大盘总结</label>
              <el-input 
                v-model="marketSummary" 
                type="textarea" 
                :rows="6" 
                placeholder="总结今日指数表现、热点板块、情绪描述..."
                class="review-textarea"
              />
            </div>
            <div class="editor-field">
              <label>涨跌停统计</label>
              <el-input 
                v-model="limitStats" 
                type="textarea" 
                :rows="6" 
                placeholder="输入今日涨停、跌停家数及其他宽度指标..."
                class="review-textarea"
              />
            </div>
          </div>

          <div class="editor-field full-width">
            <label>个股复盘与标的分析</label>
            <div class="stock-tabs">
              <span :class="['tab', activeStock === 'NVDA' ? 'active' : '']" @click="activeStock = 'NVDA'">NVDA (+4.2%)</span>
              <span :class="['tab', activeStock === 'TSLA' ? 'active' : '']" @click="activeStock = 'TSLA'">TSLA (-1.8%)</span>
              <span class="tab add-stock">+ 添加标的</span>
            </div>
            <el-input 
              v-model="stockReview" 
              type="textarea" 
              :rows="8" 
              placeholder="详细记录关注个股今日走势、买卖逻辑、操作得失..."
              class="review-textarea"
            />
          </div>

          <div class="editor-field full-width">
            <label>
              <el-icon><Promotion /></el-icon>
              明日策略计划
            </label>
            <el-input 
              v-model="tomorrowPlan" 
              type="textarea" 
              :rows="4" 
              placeholder="明日关注板块、重点个股及具体操作计划..."
              class="review-textarea plan-textarea"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const viewMode = ref('calendar')
const sentiment = ref(4)
const marketSummary = ref('')
const limitStats = ref('')
const stockReview = ref('')
const tomorrowPlan = ref('')
const activeStock = ref('NVDA')
const selectedDate = ref('2023年10月09日')

const weekDays = ['一', '二', '三', '四', '五', '六', '日']
const currentMonth = ref('2023年10月')

const calendarDates = ref([
  { day: 25, isCurrentMonth: false },
  { day: 26, isCurrentMonth: false },
  { day: 27, isCurrentMonth: false },
  { day: 28, isCurrentMonth: false },
  { day: 29, isCurrentMonth: false },
  { day: 30, isCurrentMonth: false },
  { day: 1, isCurrentMonth: true },
  { day: 2, isCurrentMonth: true, hasLog: true },
  { day: 3, isCurrentMonth: true, hasLog: true },
  { day: 4, isCurrentMonth: true },
  { day: 5, isCurrentMonth: true, hasLog: true },
  { day: 6, isCurrentMonth: true, hasLog: true },
  { day: 7, isCurrentMonth: true },
  { day: 8, isCurrentMonth: true },
  { day: 9, isCurrentMonth: true, isToday: true, isSelected: true },
  { day: 10, isCurrentMonth: true },
  { day: 11, isCurrentMonth: true },
  { day: 12, isCurrentMonth: true },
  { day: 13, isCurrentMonth: true },
  { day: 14, isCurrentMonth: false },
  { day: 15, isCurrentMonth: false },
])

const selectDate = (date) => {
  calendarDates.value.forEach(d => d.isSelected = false)
  date.isSelected = true
  selectedDate.value = `2023年10月${String(date.day).padStart(2, '0')}日`
}

const prevMonth = () => {}
const nextMonth = () => {}

const saveReview = () => {
  console.log('Saving review...')
}
</script>

<style scoped>
.review-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.market-status {
  font-size: 12px;
  color: #8b949e;
  font-family: 'Consolas', 'Monaco', monospace;
}

.positive { color: #26a641; }

.main-content {
  display: flex;
  gap: 12px;
  flex: 1;
  overflow: hidden;
}

.calendar-panel {
  width: 33%;
  background: #161b22;
  border: 1px solid #30363d;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 8px 16px;
  border-bottom: 1px solid #30363d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.month-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: bold;
  color: #e0e2ea;
  letter-spacing: 0.15em;
}

.month-nav .el-icon {
  cursor: pointer;
  color: #8b949e;
}

.month-nav .el-icon:hover {
  color: #e0e2ea;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  padding: 16px;
}

.weekday {
  padding: 8px 0;
  text-align: center;
  font-size: 10px;
  font-weight: bold;
  color: #8b949e;
}

.date-cell {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  font-size: 12px;
  cursor: pointer;
  position: relative;
  transition: all 0.15s;
}

.date-cell:hover {
  background: #21262d;
}

.date-cell.other-month {
  color: #414752;
}

.date-cell.has-log {
  border-color: #30363d;
  background: #0d1117;
}

.date-cell.today {
  border: 2px solid #58a6ff;
  background: #21262d;
  color: #58a6ff;
  font-weight: 900;
}

.date-cell.selected {
  background: #21262d;
}

.log-indicator {
  position: absolute;
  bottom: 4px;
  width: 4px;
  height: 4px;
  background: #58a6ff;
  border-radius: 50%;
}

.monthly-stats {
  margin-top: 24px;
  padding: 0 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-card {
  background: #0d1117;
  border: 1px solid #30363d;
  padding: 16px;
}

.stat-label {
  font-size: 10px;
  color: #8b949e;
  text-transform: uppercase;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.editor-panel {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-header {
  padding: 8px 16px;
  border-bottom: 1px solid #30363d;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.editor-date {
  font-size: 10px;
  color: #8b949e;
  font-family: 'Consolas', 'Monaco', monospace;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sentiment-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: #8b949e;
  text-transform: uppercase;
  font-weight: bold;
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.editor-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.editor-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-field.full-width {
  grid-column: 1 / -1;
}

.editor-field label {
  font-size: 10px;
  font-weight: 900;
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  display: flex;
  align-items: center;
  gap: 4px;
}

.review-textarea :deep(.el-textarea__inner) {
  background: #0d1117;
  border: 1px solid #30363d;
  color: #e0e2ea;
  font-size: 14px;
  line-height: 1.5;
}

.review-textarea :deep(.el-textarea__inner):focus {
  border-color: #58a6ff;
}

.plan-textarea :deep(.el-textarea__inner) {
  border-color: rgba(38, 166, 65, 0.3);
}

.plan-textarea :deep(.el-textarea__inner):focus {
  border-color: #26a641;
}

.stock-tabs {
  display: flex;
  background: #0d1117;
  border: 1px solid #30363d;
  padding: 4px 12px;
  gap: 12px;
}

.tab {
  font-size: 10px;
  font-weight: bold;
  cursor: pointer;
  padding: 2px 0;
}

.tab.active {
  color: #58a6ff;
}

.tab.add-stock {
  color: #8b949e;
}
</style>
