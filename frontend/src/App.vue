<script setup lang="ts">
import { ref, computed } from 'vue';
import type { UserInput, LifeDestinyResult } from './types';
import { analyzeDestiny } from './api';
import BaziForm from './components/BaziForm.vue';
import LifeKLineChart from './components/LifeKLineChart.vue';
import AnalysisResult from './components/AnalysisResult.vue';
import ImportDataMode from './components/ImportDataMode.vue';
import { Sparkles, AlertCircle, Download, Printer, Trophy, FileDown, FileUp } from 'lucide-vue-next';

const result = ref<LifeDestinyResult | null>(null);
const error = ref<string | null>(null);
const isLoading = ref(false);
const showQuotaModal = ref(false);
const userName = ref('');

const handleFormSubmit = async (data: UserInput) => {
  isLoading.value = true;
  error.value = null;
  showQuotaModal.value = false;
  userName.value = data.name || '';
  try {
    const response = await analyzeDestiny(data);
    result.value = response;
  } catch (err: any) {
    if (err.response?.status === 402) {
      showQuotaModal.value = true;
    } else {
      error.value = err.response?.data?.detail || err.message || '未知错误';
    }
  } finally {
    isLoading.value = false;
  }
};

const handleDataImport = (data: LifeDestinyResult) => {
  result.value = data;
  userName.value = ''; // Reset username as it's not in the JSON usually, unless we add it
  error.value = null;
};

const handleExportJson = () => {
  if (!result.value) return;

  const exportData = {
    bazi: result.value.analysis.bazi,
    summary: result.value.analysis.summary,
    summaryScore: result.value.analysis.summaryScore,
    personality: result.value.analysis.personality,
    personalityScore: result.value.analysis.personalityScore,
    industry: result.value.analysis.industry,
    industryScore: result.value.analysis.industryScore,
    geomancy: result.value.analysis.geomancy,
    geomancyScore: result.value.analysis.geomancyScore,
    wealth: result.value.analysis.wealth,
    wealthScore: result.value.analysis.wealthScore,
    marriage: result.value.analysis.marriage,
    marriageScore: result.value.analysis.marriageScore,
    health: result.value.analysis.health,
    healthScore: result.value.analysis.healthScore,
    family: result.value.analysis.family,
    familyScore: result.value.analysis.familyScore,
    crypto: result.value.analysis.crypto,
    cryptoScore: result.value.analysis.cryptoScore,
    cryptoYear: result.value.analysis.cryptoYear,
    cryptoStyle: result.value.analysis.cryptoStyle,
    chartPoints: result.value.chartData,
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `命理分析_${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const handlePrint = () => {
  window.print();
};

const handleSaveHtml = () => {
    if (!result.value) return;

    // const now = new Date();
    // const timeString = now.toLocaleString('zh-CN');

    // Simple HTML export strategy:
    // Since we can't easily inline the canvas chart (ECharts), we might just export the data table and text.
    // Or we could try to get dataURL from chart instance if we had access. 
    // For now, let's just export a simplified report or alert user to use Print->Save as PDF.
    alert("请使用 '保存PDF' 功能 (Print to PDF) 以获得最佳效果。网页保存功能在此版本简化。");
    window.print();
};

const handleImportJsonFile = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string;
      const data = JSON.parse(content);

      if (!data.chartPoints || !Array.isArray(data.chartPoints)) {
        throw new Error('无效的数据格式：缺少 chartPoints');
      }

      const importedResult: LifeDestinyResult = {
        chartData: data.chartPoints,
        analysis: {
            bazi: data.bazi || [],
            summary: data.summary || "无摘要",
            summaryScore: data.summaryScore || 5,
            personality: data.personality || "无性格分析",
            personalityScore: data.personalityScore || 5,
            industry: data.industry || "无",
            industryScore: data.industryScore || 5,
            geomancy: data.geomancy || "建议多亲近自然，保持心境平和。",
            geomancyScore: data.geomancyScore || 5,
            wealth: data.wealth || "无",
            wealthScore: data.wealthScore || 5,
            marriage: data.marriage || "无",
            marriageScore: data.marriageScore || 5,
            health: data.health || "无",
            healthScore: data.healthScore || 5,
            family: data.family || "无",
            familyScore: data.familyScore || 5,
            crypto: data.crypto || "暂无交易分析",
            cryptoScore: data.cryptoScore || 5,
            cryptoYear: data.cryptoYear || "待定",
            cryptoStyle: data.cryptoStyle || "现货定投",
        },
      };

      result.value = importedResult;
      error.value = null;
    } catch (err: any) {
      error.value = `文件解析失败：${err.message}`;
    }
  };
  reader.readAsText(file);
  target.value = '';
};

const peakYearItem = computed(() => {
  if (!result.value || !result.value.chartData.length) return null;
  return result.value.chartData.reduce((prev, current) => (prev.high > current.high) ? prev : current);
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center">
    <!-- Header -->
    <header class="w-full bg-white border-b border-gray-200 py-6 sticky top-0 z-50 no-print">
      <div class="max-w-7xl mx-auto px-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="bg-black text-white p-2 rounded-lg">
            <Sparkles class="w-6 h-6" />
          </div>
          <div>
            <h1 class="text-2xl font-serif-sc font-bold text-gray-900 tracking-wide">人生K线</h1>
            <p class="text-xs text-gray-500 uppercase tracking-widest">Life Destiny K-Line</p>
          </div>
        </div>
        <div class="flex items-center gap-2 text-sm text-gray-500 font-medium bg-gray-100 px-3 py-1.5 rounded-full">
          <Sparkles class="w-4 h-4 text-amber-500" />
          基于 AI 大模型驱动
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="w-full max-w-7xl mx-auto px-4 py-8 md:py-12 flex flex-col gap-12">
      
      <!-- Intro & Form -->
      <div v-if="!result" class="flex flex-col items-center justify-center min-h-[60vh] gap-8 animate-fade-in">
        <div class="text-center max-w-2xl flex flex-col items-center">
          <h2 class="text-4xl md:text-5xl font-serif-sc font-bold text-gray-900 mb-6">
            洞悉命运起伏 <br />
            <span class="text-indigo-600">预见人生轨迹</span>
          </h2>
          <p class="text-gray-600 text-lg leading-relaxed mb-6">
            结合<strong>传统八字命理</strong>与<strong>金融可视化技术</strong>，
            将您的一生运势绘制成类似股票行情的K线图。
          </p>

          <!-- Usage -->
          <div class="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-100 mb-6 text-left w-full max-w-lg">
            <h3 class="font-bold text-indigo-800 mb-2">📝 使用方法</h3>
            <ol class="text-sm text-gray-600 space-y-1 list-decimal list-inside">
              <li>填写八字信息，生成专属提示词 (或直接输入 Key)</li>
              <li>如果使用 API Key，直接点击生成</li>
              <li>如果没有 Key，可使用导入模式手动粘贴 AI 结果</li>
            </ol>
          </div>

          <!-- Import JSON File -->
          <label class="flex items-center gap-3 px-6 py-3 bg-white border-2 border-dashed border-emerald-300 rounded-xl cursor-pointer hover:border-emerald-500 hover:bg-emerald-50 transition-all group mb-4">
            <FileUp class="w-6 h-6 text-emerald-500 group-hover:text-emerald-600" />
            <span class="text-base font-medium text-gray-600 group-hover:text-emerald-700">已有 JSON 文件？点击直接导入</span>
            <input type="file" accept=".json" @change="handleImportJsonFile" class="hidden" />
          </label>
        </div>

        <!-- Mode Selection: Currently showing both Form (API) and ImportMode below each other for simplicity, or we could tab them. 
             The React version had ImportDataMode below. I'll stick to that structure. -->
        
        <BaziForm :isLoading="isLoading" @submit="handleFormSubmit" />

        <div class="w-full max-w-2xl border-t border-gray-200 pt-8 mt-8">
            <h3 class="text-center text-gray-500 font-bold mb-4">或者：手动导入 AI 生成的数据</h3>
            <ImportDataMode @data-import="handleDataImport" />
        </div>

        <div v-if="error" class="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg border border-red-100 max-w-md w-full animate-bounce-short">
          <AlertCircle class="w-5 h-5 flex-shrink-0" />
          <p class="text-sm font-bold">{{ error }}</p>
        </div>
      </div>

      <!-- Results View -->
      <div v-else class="animate-fade-in space-y-12">
        <div class="flex flex-col md:flex-row justify-between items-end md:items-center border-b border-gray-200 pb-4 gap-4">
          <h2 class="text-2xl font-bold font-serif-sc text-gray-800">
            {{ userName ? `${userName}的` : '' }}命盘分析报告
          </h2>

          <div class="flex flex-wrap gap-3 no-print">
            <button @click="handleExportJson" class="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white border border-emerald-600 rounded-lg hover:bg-emerald-700 transition-all font-medium text-sm shadow-sm">
              <FileDown class="w-4 h-4" /> 导出JSON
            </button>
            <button @click="handlePrint" class="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white border border-indigo-600 rounded-lg hover:bg-indigo-700 transition-all font-medium text-sm shadow-sm">
              <Printer class="w-4 h-4" /> 保存PDF
            </button>
            <button @click="handleSaveHtml" class="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white border border-indigo-600 rounded-lg hover:bg-indigo-700 transition-all font-medium text-sm shadow-sm">
              <Download class="w-4 h-4" /> 保存网页
            </button>
            <button @click="result = null" class="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all font-medium text-sm">
              ← 重新排盘
            </button>
          </div>
        </div>

        <!-- Chart Section -->
        <section class="space-y-4 break-inside-avoid">
          <div class="flex flex-col gap-1">
            <h3 class="text-xl font-bold text-gray-700 flex items-center gap-2">
              <span class="w-1 h-6 bg-indigo-600 rounded-full"></span>
              流年大运走势图 (100年)
            </h3>
            <p v-if="peakYearItem" class="text-sm font-bold text-indigo-800 bg-indigo-50 border border-indigo-100 rounded px-2 py-1 inline-flex items-center gap-2 self-start mt-1">
              <Trophy class="w-3 h-3 text-amber-500" />
              人生巅峰年份：{{ peakYearItem.year }}年 ({{ peakYearItem.ganZhi }}) - {{ peakYearItem.age }}岁，评分 <span class="text-amber-600 text-lg">{{ peakYearItem.high }}</span>
            </p>
          </div>

          <p class="text-sm text-gray-500 mb-2 no-print">
            <span class="text-green-600 font-bold">绿色K线</span> 代表运势上涨（吉），
            <span class="text-red-600 font-bold">红色K线</span> 代表运势下跌（凶）。
            <span class="text-red-500 font-bold">★</span> 标记为全盘最高运势点。
          </p>
          
          <LifeKLineChart :data="result.chartData" />
        </section>

        <!-- Analysis Report -->
        <section id="analysis-result-container">
          <AnalysisResult :analysis="result.analysis" />
        </section>

        <!-- Print Table -->
        <div class="hidden print:block mt-8 break-before-page">
            <div class="p-4 border-b border-gray-100 bg-gray-50 flex items-center gap-2 mb-4">
            <div class="w-1 h-5 bg-indigo-600 rounded-full"></div>
            <h3 class="text-xl font-bold text-gray-800 font-serif-sc">流年详批全表</h3>
            </div>
            <table class="w-full text-left border-collapse text-sm">
            <thead>
                <tr class="bg-gray-100 text-gray-600 font-bold uppercase tracking-wider">
                <th class="p-2 border border-gray-200 text-center w-16">年龄</th>
                <th class="p-2 border border-gray-200 text-center w-24">流年</th>
                <th class="p-2 border border-gray-200 text-center w-24">大运</th>
                <th class="p-2 border border-gray-200 text-center w-16">评分</th>
                <th class="p-2 border border-gray-200">运势批断</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="item in result.chartData" :key="item.age" class="border-b border-gray-100 break-inside-avoid">
                <td class="p-2 border border-gray-100 text-center font-mono">{{ item.age }}</td>
                <td class="p-2 border border-gray-100 text-center font-bold">{{ item.year }} {{ item.ganZhi }}</td>
                <td class="p-2 border border-gray-100 text-center">{{ item.superLuck || '-' }}</td>
                <td class="p-2 border border-gray-100 text-center font-bold" :class="item.close >= item.open ? 'text-green-600' : 'text-red-600'">
                    {{ item.score }}
                </td>
                <td class="p-2 border border-gray-100 text-gray-700 text-justify text-xs leading-relaxed">
                    {{ item.reason }}
                </td>
                </tr>
            </tbody>
            </table>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="w-full bg-gray-900 text-gray-400 py-8 mt-auto no-print">
      <div class="max-w-7xl mx-auto px-4 text-center text-sm">
        <p>&copy; {{ new Date().getFullYear() }} 人生K线 | 仅供娱乐与文化研究，请勿迷信</p>
      </div>
    </footer>

    <!-- Quota Exceeded Modal -->
    <div v-if="showQuotaModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-red-100 transform transition-all scale-100">
        <div class="flex items-start gap-4 mb-4">
          <div class="p-3 bg-red-100 rounded-full flex-shrink-0">
            <AlertCircle class="w-8 h-8 text-red-600" />
          </div>
          <div>
            <h3 class="text-xl font-bold text-gray-900 mb-2">服务额度已耗尽</h3>
            <p class="text-gray-600 text-sm leading-relaxed">
              抱歉，服务器的免费 AI 调用额度暂时用完了。
            </p>
          </div>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-6 text-sm text-gray-700">
          <p class="font-bold mb-2">如何继续使用？</p>
          <ol class="list-decimal list-inside space-y-1 text-gray-600">
            <li>在下方表单中找到 <span class="font-bold text-indigo-700">"高级设置"</span></li>
            <li>展开并填入您自己的 <strong>API Key</strong></li>
            <li>再次点击生成即可</li>
          </ol>
        </div>

        <div class="flex justify-end">
          <button 
            @click="showQuotaModal = false"
            class="px-6 py-2.5 bg-gray-900 hover:bg-black text-white font-bold rounded-xl transition-colors shadow-lg"
          >
            我知道了
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
