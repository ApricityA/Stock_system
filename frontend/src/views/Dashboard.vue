<template>
  <div class="dashboard">
    <div class="index-cards">
      <div v-for="index in marketIndices" :key="index.name" class="card">
        <div class="card-header">
          <span class="label">{{ index.name }}</span>
          <el-icon :class="index.trend"><component :is="index.trend === 'up' ? 'TrendCharts' : 'TrendCharts'" /></el-icon>
        </div>
        <div :class="['value', index.trend === 'up' ? 'positive' : 'negative']">{{ index.value }}</div>
        <div class="card-footer">
          <span :class="index.trend === 'up' ? 'positive' : 'negative'">{{ index.change }}</span>
          <span class="divider">|</span>
          <span class="volume">{{ index.volume }}</span>
        </div>
      </div>
    </div>

    <div class="middle-section">
      <div class="hot-sectors">
        <div class="section-header">
          <span>今日热点板块</span>
          <el-icon><FullScreen /></el-icon>
        </div>
        <el-table :data="hotSectors" style="width: 100%" class="sector-table">
          <el-table-column prop="name" label="板块名称" />
          <el-table-column prop="change" label="涨跌幅" align="right">
            <template #default="{ row }">
              <span :class="row.changeNum > 0 ? 'positive' : 'negative'">{{ row.change }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="leader" label="龙头股" />
          <el-table-column prop="netFlow" label="净流入" align="right">
            <template #default="{ row }">
              <span :class="row.flowNum > 0 ? 'positive' : 'negative'">{{ row.netFlow }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="sentiment-panel">
        <div class="section-header">市场情绪分析</div>
        <div class="sentiment-content">
          <div class="northbound">
            <div class="northbound-header">
              <span>今日北向资金净流入</span>
              <span class="positive bold">+¥5.42B</span>
            </div>
            <el-progress :percentage="75" :show-text="false" :stroke-width="6" class="progress-bar" />
          </div>

          <div class="limit-stats">
            <div class="stat-card">
              <div class="stat-label">涨停家数</div>
              <div class="stat-value positive">84</div>
              <div class="stat-change positive">+12 vs Prev</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">跌停家数</div>
              <div class="stat-value negative">12</div>
              <div class="stat-change negative">-5 vs Prev</div>
            </div>
          </div>

          <div class="market-breadth">
            <div class="breadth-header">
              <span>市场宽度</span>
              <span class="positive">看多</span>
            </div>
            <div class="breadth-bar">
              <div class="breadth-up" style="width: 65%"></div>
              <div class="breadth-flat" style="width: 10%"></div>
              <div class="breadth-down" style="width: 25%"></div>
            </div>
            <div class="breadth-stats">
              <span class="positive">上涨: 3,240</span>
              <span class="flat">平盘: 450</span>
              <span class="negative">下跌: 1,200</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-section">
      <div class="chart-header">
        <div class="chart-title">
          <span>上证指数分时图 (000001)</span>
          <div class="chart-tabs">
            <button :class="['tab', activeTab === 'minute' ? 'active' : '']" @click="activeTab = 'minute'">分时</button>
            <button :class="['tab', activeTab === 'daily' ? 'active' : '']" @click="activeTab = 'daily'">日K</button>
            <button :class="['tab', activeTab === 'weekly' ? 'active' : '']" @click="activeTab = 'weekly'">周K</button>
            <button :class="['tab', activeTab === 'monthly' ? 'active' : '']" @click="activeTab = 'monthly'">月K</button>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item">
            <div class="legend-dot blue"></div>
            <span>当前: 3,248.55</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot green"></div>
            <span>均线: 3,212.10</span>
          </div>
        </div>
      </div>
      <div class="chart-container">
        <div ref="chartRef" class="echarts-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { TrendCharts, FullScreen } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const activeTab = ref('minute')
const chartRef = ref(null)

const marketIndices = [
  { name: '上证指数', value: '3,248.55', change: '+1.24%', volume: '428.5B Vol', trend: 'up' },
  { name: '深证成指', value: '10,482.12', change: '+0.89%', volume: '612.4B Vol', trend: 'up' },
  { name: '创业板指', value: '2,118.90', change: '-0.45%', volume: '256.1B Vol', trend: 'down' },
  { name: '科创50', value: '982.44', change: '+2.15%', volume: '108.9B Vol', trend: 'up' },
]

const hotSectors = [
  { name: '半导体', change: '+4.52%', changeNum: 4.52, leader: 'SMIC 688981', netFlow: '+4.2B', flowNum: 4.2 },
  { name: '新能源车', change: '+3.88%', changeNum: 3.88, leader: 'BYD 002594', netFlow: '+2.8B', flowNum: 2.8 },
  { name: '人工智能', change: '+3.21%', changeNum: 3.21, leader: 'IFLYTEK 002230', netFlow: '+1.5B', flowNum: 1.5 },
  { name: '银行', change: '-0.42%', changeNum: -0.42, leader: 'ICBC 601398', netFlow: '-0.8B', flowNum: -0.8 },
  { name: '房地产', change: '-1.15%', changeNum: -1.15, leader: 'VANKE 000002', netFlow: '-1.2B', flowNum: -1.2 },
]

onMounted(() => {
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    const option = {
      grid: { top: 20, right: 60, bottom: 30, left: 60 },
      xAxis: {
        type: 'category',
        data: ['09:30', '10:00', '10:30', '11:00', '11:30', '13:00', '13:30', '14:00', '14:30', '15:00'],
        axisLine: { lineStyle: { color: '#30363d' } },
        axisLabel: { color: '#8b949e' },
      },
      yAxis: {
        type: 'value',
        min: 3200,
        max: 3300,
        splitLine: { lineStyle: { color: '#30363d', type: 'dashed' } },
        axisLabel: { color: '#8b949e' },
      },
      series: [
        {
          data: [3220, 3235, 3228, 3245, 3240, 3250, 3248, 3255, 3245, 3248.55],
          type: 'line',
          smooth: true,
          lineStyle: { color: '#58a6ff', width: 2 },
          itemStyle: { color: '#58a6ff' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(88, 166, 255, 0.3)' },
                { offset: 1, color: 'rgba(88, 166, 255, 0.05)' },
              ],
            },
          },
        },
      ],
      tooltip: { trigger: 'axis' },
    }
    chart.setOption(option)
    window.addEventListener('resize', () => chart.resize())
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.index-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.card {
  background: #161b22;
  border: 1px solid #30363d;
  padding: 16px;
  transition: border-color 0.2s;
}

.card:hover {
  border-color: rgba(88, 166, 255, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.label {
  font-size: 11px;
  color: #c0c7d4;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.value {
  font-size: 24px;
  font-weight: bold;
  font-family: 'Consolas', 'Monaco', monospace;
}

.positive { color: #26a641; }
.negative { color: #ffb4ab; }

.card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 12px;
}

.divider { color: #414752; }
.volume { color: #c0c7d4; font-size: 12px; }

.middle-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
}

.hot-sectors, .sentiment-panel {
  background: #161b22;
  border: 1px solid #30363d;
}

.section-header {
  padding: 8px 16px;
  border-bottom: 1px solid #30363d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(33, 38, 45, 0.5);
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.sector-table :deep(.el-table__body tr:hover > td) {
  background: #1f242b !important;
}

.sector-table :deep(.el-table) {
  background: transparent;
}

.sector-table :deep(.el-table th),
.sector-table :deep(.el-table td) {
  background: transparent;
  color: #e0e2ea;
  border-color: #30363d;
}

.sentiment-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-grow: 1;
}

.northbound {
  background: #0d1117;
  border: 1px solid #30363d;
  padding: 16px;
}

.northbound-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #c0c7d4;
}

.bold { font-weight: bold; }

.progress-bar { margin-top: 8px; }

.limit-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-card {
  background: #0d1117;
  border: 1px solid #30363d;
  padding: 16px;
  text-align: center;
}

.stat-label {
  font-size: 10px;
  color: #c0c7d4;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  font-family: 'Consolas', 'Monaco', monospace;
}

.stat-change {
  font-size: 10px;
  margin-top: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.market-breadth {
  padding-top: 8px;
  border-top: 1px solid #30363d;
}

.breadth-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 12px;
  color: #c0c7d4;
}

.breadth-bar {
  display: flex;
  height: 48px;
}

.breadth-up {
  background: #26a641;
}

.breadth-flat {
  background: #414752;
}

.breadth-down {
  background: #ffb4ab;
}

.breadth-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 10px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.flat { color: #8b949e; }

.chart-section {
  background: #161b22;
  border: 1px solid #30363d;
}

.chart-header {
  padding: 8px 16px;
  border-bottom: 1px solid #30363d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.chart-tabs {
  display: flex;
  background: #0d1117;
  border: 1px solid #30363d;
  padding: 2px;
}

.tab {
  padding: 4px 12px;
  font-size: 11px;
  font-weight: bold;
  border: none;
  background: transparent;
  color: #8b949e;
  cursor: pointer;
  transition: all 0.15s;
}

.tab:hover { color: #f0f6fc; }

.tab.active {
  background: #30363d;
  color: #58a6ff;
}

.chart-legend {
  display: flex;
  align-items: center;
  gap: 24px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #c0c7d4;
  font-family: 'Consolas', 'Monaco', monospace;
}

.legend-dot {
  width: 12px;
  height: 12px;
}

.legend-dot.blue { background: #58a6ff; }
.legend-dot.green { background: #26a641; }

.chart-container {
  height: 400px;
  background: #0d1117;
  padding: 12px;
}

.echarts-container {
  width: 100%;
  height: 100%;
}
</style>
