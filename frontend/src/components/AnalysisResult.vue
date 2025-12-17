<script setup lang="ts">
import type { AnalysisData } from '../types';
import { 
  TrendingUp, 
  User, 
  Briefcase, 
  Compass, 
  Coins, 
  Heart, 
  Activity, 
  Users, 
  Bitcoin 
} from 'lucide-vue-next';

defineProps<{
  analysis: AnalysisData;
}>();

// Helper to determine score color
const getScoreColor = (score: number) => {
  if (score >= 8) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
  if (score >= 6) return 'text-indigo-600 bg-indigo-50 border-indigo-200';
  if (score >= 4) return 'text-amber-600 bg-amber-50 border-amber-200';
  return 'text-red-600 bg-red-50 border-red-200';
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 break-before-page">
    
    <!-- Summary Card -->
    <div class="md:col-span-2 bg-gradient-to-br from-indigo-50 to-white p-6 rounded-2xl border border-indigo-100 shadow-sm relative overflow-hidden group hover:shadow-md transition-all">
      <div class="absolute top-0 right-0 w-32 h-32 bg-indigo-100 rounded-full blur-3xl opacity-50 -mr-16 -mt-16 pointer-events-none"></div>
      
      <div class="flex items-start justify-between mb-4 relative z-10">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-indigo-600 rounded-lg text-white shadow-lg shadow-indigo-200">
            <TrendingUp class="w-6 h-6" />
          </div>
          <h3 class="text-xl font-bold text-gray-800 font-serif-sc">命理总评</h3>
        </div>
        <div :class="`px-3 py-1 rounded-full text-sm font-bold border ${getScoreColor(analysis.summaryScore)}`">
          综合评分：{{ analysis.summaryScore }}
        </div>
      </div>
      
      <p class="text-gray-700 leading-relaxed text-justify relative z-10">
        {{ analysis.summary }}
      </p>

      <!-- Bazi Pillars Display -->
      <div class="mt-6 flex justify-around items-center bg-white/60 p-4 rounded-xl border border-indigo-50 backdrop-blur-sm">
         <div v-for="(pillar, index) in analysis.bazi" :key="index" class="text-center">
            <div class="text-xs text-gray-400 mb-1 uppercase tracking-wider">{{ ['年柱', '月柱', '日柱', '时柱'][index] }}</div>
            <div class="text-xl font-bold font-serif-sc text-gray-800">{{ pillar }}</div>
         </div>
      </div>
    </div>

    <!-- Personality -->
    <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2 text-gray-800 font-bold">
           <User class="w-5 h-5 text-blue-500 group-hover:scale-110 transition-transform" />
           <h3>性格分析</h3>
        </div>
        <span :class="`text-xs font-bold px-2 py-0.5 rounded border ${getScoreColor(analysis.personalityScore)}`">
          {{ analysis.personalityScore }}分
        </span>
      </div>
      <p class="text-sm text-gray-600 leading-relaxed text-justify">{{ analysis.personality }}</p>
    </div>

    <!-- Industry -->
    <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2 text-gray-800 font-bold">
           <Briefcase class="w-5 h-5 text-purple-500 group-hover:scale-110 transition-transform" />
           <h3>事业发展</h3>
        </div>
        <span :class="`text-xs font-bold px-2 py-0.5 rounded border ${getScoreColor(analysis.industryScore)}`">
          {{ analysis.industryScore }}分
        </span>
      </div>
      <p class="text-sm text-gray-600 leading-relaxed text-justify">{{ analysis.industry }}</p>
    </div>

    <!-- Wealth -->
    <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2 text-gray-800 font-bold">
           <Coins class="w-5 h-5 text-amber-500 group-hover:scale-110 transition-transform" />
           <h3>财富运势</h3>
        </div>
        <span :class="`text-xs font-bold px-2 py-0.5 rounded border ${getScoreColor(analysis.wealthScore)}`">
          {{ analysis.wealthScore }}分
        </span>
      </div>
      <p class="text-sm text-gray-600 leading-relaxed text-justify">{{ analysis.wealth }}</p>
    </div>

    <!-- Feng Shui -->
    <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2 text-gray-800 font-bold">
           <Compass class="w-5 h-5 text-emerald-500 group-hover:scale-110 transition-transform" />
           <h3>发展风水</h3>
        </div>
        <span :class="`text-xs font-bold px-2 py-0.5 rounded border ${getScoreColor(analysis.geomancyScore)}`">
          {{ analysis.geomancyScore }}分
        </span>
      </div>
      <p class="text-sm text-gray-600 leading-relaxed text-justify">{{ analysis.geomancy }}</p>
    </div>

    <!-- Crypto / Web3 Special -->
    <div class="md:col-span-2 bg-gray-900 text-gray-100 p-6 rounded-2xl border border-gray-800 shadow-lg relative overflow-hidden group">
       <!-- Decoration -->
       <div class="absolute -right-10 -top-10 text-gray-800 opacity-20 transform rotate-12">
          <Bitcoin class="w-48 h-48" />
       </div>

       <div class="flex items-start justify-between mb-4 relative z-10">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-amber-500 rounded-lg text-white shadow-lg shadow-amber-900/50">
            <Bitcoin class="w-6 h-6" />
          </div>
          <div>
            <h3 class="text-xl font-bold text-white font-serif-sc">Web3 / 币圈特别分析</h3>
            <p class="text-xs text-gray-400">基于偏财与七杀运势推演</p>
          </div>
        </div>
        <div :class="`px-3 py-1 rounded-full text-sm font-bold border border-gray-600 bg-gray-800 text-amber-400`">
          投机指数：{{ analysis.cryptoScore }}
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
        <div class="md:col-span-2">
           <p class="text-gray-300 text-sm leading-relaxed text-justify border-l-2 border-amber-500 pl-4">
             {{ analysis.crypto }}
           </p>
        </div>
        <div class="space-y-3">
           <div class="bg-gray-800 p-3 rounded-lg border border-gray-700">
              <div class="text-xs text-gray-500 mb-1">建议风格</div>
              <div class="font-bold text-amber-300">{{ analysis.cryptoStyle }}</div>
           </div>
           <div class="bg-gray-800 p-3 rounded-lg border border-gray-700">
              <div class="text-xs text-gray-500 mb-1">暴富流年</div>
              <div class="font-bold text-emerald-400">{{ analysis.cryptoYear }}</div>
           </div>
        </div>
      </div>
    </div>

    <!-- Marriage -->
    <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2 text-gray-800 font-bold">
           <Heart class="w-5 h-5 text-pink-500 group-hover:scale-110 transition-transform" />
           <h3>婚姻情感</h3>
        </div>
        <span :class="`text-xs font-bold px-2 py-0.5 rounded border ${getScoreColor(analysis.marriageScore)}`">
          {{ analysis.marriageScore }}分
        </span>
      </div>
      <p class="text-sm text-gray-600 leading-relaxed text-justify">{{ analysis.marriage }}</p>
    </div>

    <!-- Health -->
    <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2 text-gray-800 font-bold">
           <Activity class="w-5 h-5 text-green-500 group-hover:scale-110 transition-transform" />
           <h3>健康状况</h3>
        </div>
        <span :class="`text-xs font-bold px-2 py-0.5 rounded border ${getScoreColor(analysis.healthScore)}`">
          {{ analysis.healthScore }}分
        </span>
      </div>
      <p class="text-sm text-gray-600 leading-relaxed text-justify">{{ analysis.health }}</p>
    </div>

    <!-- Family -->
    <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group md:col-span-2">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2 text-gray-800 font-bold">
           <Users class="w-5 h-5 text-cyan-500 group-hover:scale-110 transition-transform" />
           <h3>六亲关系</h3>
        </div>
        <span :class="`text-xs font-bold px-2 py-0.5 rounded border ${getScoreColor(analysis.familyScore)}`">
          {{ analysis.familyScore }}分
        </span>
      </div>
      <p class="text-sm text-gray-600 leading-relaxed text-justify">{{ analysis.family }}</p>
    </div>

  </div>
</template>
