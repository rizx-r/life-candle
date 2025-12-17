<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import * as echarts from 'echarts';
import type { KLinePoint } from '../types';

const props = defineProps<{
  data: KLinePoint[];
}>();

const chartContainer = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const transformedData = computed(() => {
  return props.data.map(item => {
    // ECharts candlestick: [open, close, low, high]
    return [item.open, item.close, item.low, item.high];
  });
});

const categoryData = computed(() => {
  return props.data.map(item => `${item.age}岁`);
});

const superLuckMarkLines = computed(() => {
  const markLines: any[] = [];
  props.data.forEach((d, i) => {
    if (i > 0) {
      const prev = props.data[i - 1];
      if (prev && d.superLuck !== prev.superLuck) {
        markLines.push({
          xAxis: i,
          label: {
            formatter: d.superLuck,
            position: 'start',
            color: '#6366f1',
            fontWeight: 'bold'
          },
          lineStyle: {
              type: 'dashed',
              color: '#cbd5e1'
          }
        });
      }
    }
  });
  return markLines;
});

const maxHighIndex = computed(() => {
    let max = -Infinity;
    let idx = -1;
    props.data.forEach((d, i) => {
        if (d.high > max) {
            max = d.high;
            idx = i;
        }
    });
    return idx;
});

const initChart = () => {
  if (!chartContainer.value) return;

  chartInstance = echarts.init(chartContainer.value);

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params: any) => {
        if (!Array.isArray(params) || params.length === 0) return '';
        const param = params[0];
        const index = param.dataIndex;
        const item = props.data[index];
        if (!item) return '';
        
        const isUp = item.close >= item.open;
        const trend = isUp ? '<span style="color:green">吉 ▲</span>' : '<span style="color:red">凶 ▼</span>';
        
        return `
          <div style="width: 300px; white-space: normal;">
            <div style="border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 5px;">
              <span style="font-weight: bold; font-size: 16px;">${item.year} ${item.ganZhi}年 (${item.age}岁)</span>
              <br/>
              <span style="color: #6366f1;">大运：${item.superLuck || '未知'}</span>
              <span style="float: right;">${trend}</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 5px; background: #f9fafb; padding: 5px; border-radius: 4px; font-size: 12px; text-align: center;">
              <div>开: <b>${item.open}</b></div>
              <div>收: <b>${item.close}</b></div>
              <div>高: <b>${item.high}</b></div>
              <div>低: <b>${item.low}</b></div>
            </div>
            <div style="margin-top: 8px; font-size: 13px; line-height: 1.5; color: #374151;">
              ${item.reason}
            </div>
          </div>
        `;
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      data: categoryData.value,
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#6b7280', interval: 9 }, // Show every 10 years roughly
    },
    yAxis: {
      scale: true,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
      axisLabel: { color: '#6b7280' }
    },
    series: [
      {
        type: 'candlestick',
        data: transformedData.value,
        itemStyle: {
          color: '#22c55e',        // Up color (Green)
          color0: '#ef4444',       // Down color (Red)
          borderColor: '#15803d',  // Up border
          borderColor0: '#b91c1c'  // Down border
        },
        markLine: {
            symbol: ['none', 'none'],
            data: superLuckMarkLines.value,
            animation: false
        },
        markPoint: {
            data: (() => {
                if (maxHighIndex.value >= 0 && props.data[maxHighIndex.value]) {
                    const peakItem = props.data[maxHighIndex.value]!;
                    return [
                        {
                            name: '人生巅峰',
                            coord: [maxHighIndex.value, peakItem.high],
                            value: peakItem.high,
                            itemStyle: { color: '#ef4444' },
                            label: {
                                show: true,
                                position: 'top',
                                formatter: '★ {c}'
                            }
                        }
                    ];
                }
                return [];
            })()
        }
      }
    ]
  };

  chartInstance.setOption(option);
};

watch(() => props.data, () => {
  if (chartInstance) {
    chartInstance.dispose();
  }
  initChart();
}, { deep: true });

onMounted(() => {
  initChart();
  window.addEventListener('resize', () => chartInstance?.resize());
});
</script>

<template>
  <div class="w-full h-[600px] bg-white p-2 md:p-6 rounded-xl border border-gray-200 shadow-sm relative">
    <div class="mb-6 flex justify-between items-center px-2">
      <h3 class="text-xl font-bold text-gray-800 font-serif-sc">人生流年大运K线图</h3>
      <div class="flex gap-4 text-xs font-medium">
         <span class="flex items-center text-green-700 bg-green-50 px-2 py-1 rounded"><div class="w-2 h-2 bg-green-500 mr-2 rounded-full"></div> 吉运 (涨)</span>
         <span class="flex items-center text-red-700 bg-red-50 px-2 py-1 rounded"><div class="w-2 h-2 bg-red-500 mr-2 rounded-full"></div> 凶运 (跌)</span>
      </div>
    </div>
    
    <div ref="chartContainer" class="w-full h-[90%]" />
  </div>
</template>
