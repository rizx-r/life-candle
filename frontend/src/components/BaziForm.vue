<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import type { UserInput } from '../types';
import { Gender } from '../types';
import { Loader2, Sparkles, TrendingUp, Settings, ChevronDown, ChevronRight } from 'lucide-vue-next';

const { isLoading } = defineProps<{
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: 'submit', data: UserInput): void;
}>();

const showAdvancedSettings = ref(false);

const formData = reactive<UserInput>({
  name: '',
  gender: Gender.MALE,
  birthYear: '',
  yearPillar: '',
  monthPillar: '',
  dayPillar: '',
  hourPillar: '',
  startAge: '',
  firstSuperLuck: '',
  modelName: '',
  apiBaseUrl: '',
  apiKey: '',
});

const formErrors = reactive<{ modelName?: string, apiBaseUrl?: string, apiKey?: string }>({});

// 60 Jiazi (Sexagenary cycle)
const heavenlyStems = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'] as const;
const earthlyBranches = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'] as const;

const jiaziList = Array.from({ length: 60 }, (_, i) => {
  const stem = heavenlyStems[i % 10]!;
  const branch = earthlyBranches[i % 12]!;
  return stem + branch;
});


// const clearError = (field: keyof typeof formErrors) => {
//   formErrors[field] = undefined;
// };

const handleSubmit = () => {
  // Clear previous errors
  Object.keys(formErrors).forEach(key => formErrors[key as keyof typeof formErrors] = undefined);
  
  // No required check for API fields as they are optional/fallback to backend
  emit('submit', { ...formData });
};

const superLuckDirectionInfo = computed(() => {
  if (!formData.yearPillar) return '等待输入年柱...';

  const firstChar = formData.yearPillar.trim().charAt(0);
  const yinStems = ['乙', '丁', '己', '辛', '癸'];

  let isYangYear = true;
  if (yinStems.includes(firstChar)) isYangYear = false;

  let isForward = false;
  if (formData.gender === Gender.MALE) {
    isForward = isYangYear;
  } else {
    isForward = !isYangYear;
  }

  return isForward ? '顺行 (阳男/阴女)' : '逆行 (阴男/阳女)';
});
</script>

<template>
  <div class="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
    <div class="text-center mb-6">
      <h2 class="text-3xl font-serif-sc font-bold text-gray-800 mb-2">八字排盘</h2>
      <p class="text-gray-500 text-sm">请输入四柱与大运信息以生成分析</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Name & Gender -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">姓名 (可选)</label>
          <input
            type="text"
            v-model="formData.name"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
            placeholder="姓名"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">性别</label>
          <div class="flex bg-gray-100 rounded-lg p-1">
            <button
              type="button"
              @click="formData.gender = Gender.MALE"
              class="flex-1 py-1.5 rounded-md text-xs font-medium transition"
              :class="formData.gender === Gender.MALE ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            >
              乾造 (男)
            </button>
            <button
              type="button"
              @click="formData.gender = Gender.FEMALE"
              class="flex-1 py-1.5 rounded-md text-xs font-medium transition"
              :class="formData.gender === Gender.FEMALE ? 'bg-white text-pink-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            >
              坤造 (女)
            </button>
          </div>
        </div>
      </div>

      <!-- Four Pillars Manual Input -->
      <div class="bg-amber-50 p-4 rounded-xl border border-amber-100">
        <div class="flex items-center gap-2 mb-3 text-amber-800 text-sm font-bold">
          <Sparkles class="w-4 h-4" />
          <span>输入四柱干支 (必填)</span>
        </div>

        <div class="mb-4">
          <label class="block text-xs font-bold text-gray-600 mb-1">出生年份 (阳历)</label>
          <input
            type="number"
            required
            min="1900"
            max="2100"
            v-model="formData.birthYear"
            placeholder="如: 1990"
            class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white font-bold"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">年柱 (Year)</label>
            <select
              required
              v-model="formData.yearPillar"
              class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold appearance-none cursor-pointer"
            >
              <option value="" disabled selected>如: 甲子</option>
              <option v-for="item in jiaziList" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">月柱 (Month)</label>
            <select
              required
              v-model="formData.monthPillar"
              class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold appearance-none cursor-pointer"
            >
              <option value="" disabled selected>如: 丙寅</option>
              <option v-for="item in jiaziList" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">日柱 (Day)</label>
            <select
              required
              v-model="formData.dayPillar"
              class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold appearance-none cursor-pointer"
            >
              <option value="" disabled selected>如: 戊辰</option>
              <option v-for="item in jiaziList" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">时柱 (Hour)</label>
            <select
              required
              v-model="formData.hourPillar"
              class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold appearance-none cursor-pointer"
            >
              <option value="" disabled selected>如: 壬戌</option>
              <option v-for="item in jiaziList" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Da Yun Manual Input -->
      <div class="bg-indigo-50 p-4 rounded-xl border border-indigo-100">
        <div class="flex items-center gap-2 mb-3 text-indigo-800 text-sm font-bold">
          <TrendingUp class="w-4 h-4" />
          <span>大运排盘信息 (必填)</span>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">起运年龄 (虚岁)</label>
            <input
              type="number"
              required
              min="1"
              max="100"
              v-model="formData.startAge"
              placeholder="如: 3"
              class="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none bg-white text-center font-bold"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">第一步大运</label>
            <select
              required
              v-model="formData.firstSuperLuck"
              class="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none bg-white text-center font-serif-sc font-bold appearance-none cursor-pointer"
            >
              <option value="" disabled selected>如: 丁卯</option>
              <option v-for="item in jiaziList" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>
        </div>
        <p class="text-xs text-indigo-600/70 mt-2 text-center">
          当前大运排序规则：
          <span class="font-bold text-indigo-900">{{ superLuckDirectionInfo }}</span>
        </p>
      </div>

      <!-- API Configuration Section (Collapsible) -->
      <div class="border border-gray-200 rounded-xl overflow-hidden">
        <button 
          type="button"
          @click="showAdvancedSettings = !showAdvancedSettings"
          class="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center gap-2 text-gray-700 text-sm font-bold">
            <Settings class="w-4 h-4" />
            <span>高级设置 / 自定义 API</span>
          </div>
          <component :is="showAdvancedSettings ? ChevronDown : ChevronRight" class="w-4 h-4 text-gray-500" />
        </button>
        
        <div v-if="showAdvancedSettings" class="p-4 bg-white border-t border-gray-200 space-y-3">
          <p class="text-xs text-gray-500 mb-2">默认使用服务器内置 API Key。如果服务器额度耗尽，请在此填入您自己的 Key。</p>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">使用模型 (可选)</label>
            <input
              type="text"
              v-model="formData.modelName"
              placeholder="默认: gemini-3-pro-preview"
              class="w-full px-3 py-2 border rounded-lg text-xs font-mono outline-none border-gray-300 focus:ring-2 focus:ring-gray-400"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">API Base URL (可选)</label>
            <input
              type="text"
              v-model="formData.apiBaseUrl"
              placeholder="默认: https://max.openai365.top/v1"
              class="w-full px-3 py-2 border rounded-lg text-xs font-mono outline-none border-gray-300 focus:ring-2 focus:ring-gray-400"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">API Key (可选)</label>
            <input
              type="password"
              v-model="formData.apiKey"
              placeholder="留空则使用服务器默认 Key"
              class="w-full px-3 py-2 border rounded-lg text-xs font-mono outline-none border-gray-300 focus:ring-2 focus:ring-gray-400"
            />
          </div>
        </div>
      </div>

      <button
        type="submit"
        :disabled="isLoading"
        class="w-full bg-gradient-to-r from-indigo-900 to-gray-900 hover:from-black hover:to-black text-white font-bold py-3.5 rounded-xl shadow-lg transform transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <template v-if="isLoading">
          <Loader2 class="animate-spin h-5 w-5" />
          <span>大师推演中(3-5分钟)</span>
        </template>
        <template v-else>
          <Sparkles class="h-5 w-5 text-amber-300" />
          <span>生成人生K线</span>
        </template>
      </button>
    </form>
  </div>
</template>
