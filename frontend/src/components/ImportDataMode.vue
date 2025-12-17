<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import type { LifeDestinyResult } from '../types';
import { Copy, CheckCircle, AlertCircle, Upload, Sparkles, MessageSquare, ArrowRight } from 'lucide-vue-next';

const BAZI_SYSTEM_INSTRUCTION = `
你是一位八字命理大师，精通加密货币市场周期。根据用户提供的四柱干支和大运信息，生成"人生K线图"数据和命理报告。

**核心规则:**
1. **年龄计算**: 采用虚岁，从 1 岁开始。
2. **K线详批**: 每年的 \`reason\` 字段必须**控制在20-30字以内**，简洁描述吉凶趋势即可。
3. **评分机制**: 所有维度给出 0-10 分。
4. **数据起伏**: 让评分呈现明显波动，体现"牛市"和"熊市"区别，禁止输出平滑直线。

**大运规则:**
- 顺行: 甲子 -> 乙丑 -> 丙寅...
- 逆行: 甲子 -> 癸亥 -> 壬戌...
- 以用户指定的第一步大运为起点，每步管10年。

**关键字段:**
- \`superLuck\`: 大运干支 (10年不变)
- \`ganZhi\`: 流年干支 (每年一变)

**输出JSON结构:**

{
  "bazi": ["年柱", "月柱", "日柱", "时柱"],
  "summary": "命理总评（100字）",
  "summaryScore": 8,
  "personality": "性格分析（80字）",
  "personalityScore": 8,
  "industry": "事业分析（80字）",
  "industryScore": 7,
  "geomancy": "风水建议：方位、地理环境、开运建议（80字）",
  "geomancyScore": 8,
  "wealth": "财富分析（80字）",
  "wealthScore": 9,
  "marriage": "婚姻分析（80字）",
  "marriageScore": 6,
  "health": "健康分析（60字）",
  "healthScore": 5,
  "family": "六亲分析（60字）",
  "familyScore": 7,
  "crypto": "币圈分析（60字）",
  "cryptoScore": 8,
  "cryptoYear": "暴富流年",
  "cryptoStyle": "链上Alpha/高倍合约/现货定投",
  "chartPoints": [
    {"age":1,"year":1990,"superLuck":"童限","ganZhi":"庚午","open":50,"close":55,"high":60,"low":45,"score":55,"reason":"开局平稳，家庭呵护"},
    ... (共100条，reason控制在20-30字)
  ]
}

**币圈分析逻辑:**
- 偏财旺、身强 -> "链上Alpha"
- 七杀旺、胆大 -> "高倍合约"
- 正财旺、稳健 -> "现货定投"
`;

const emit = defineEmits<{
  (e: 'data-import', data: LifeDestinyResult): void;
}>();

const step = ref<1 | 2 | 3>(1);
const baziInfo = reactive({
  name: '',
  gender: 'Male',
  birthYear: '',
  yearPillar: '',
  monthPillar: '',
  dayPillar: '',
  hourPillar: '',
  startAge: '',
  firstSuperLuck: '',
});

const jsonInput = ref('');
const copied = ref(false);
const error = ref<string | null>(null);

const getSuperLuckDirection = computed(() => {
  if (!baziInfo.yearPillar) return { isForward: true, text: '顺行 (Forward)' };
  const firstChar = baziInfo.yearPillar.trim().charAt(0);
  const yangStems = ['甲', '丙', '戊', '庚', '壬'];
  const isYangYear = yangStems.includes(firstChar);
  const isForward = baziInfo.gender === 'Male' ? isYangYear : !isYangYear;
  return {
    isForward,
    text: isForward ? '顺行 (Forward)' : '逆行 (Backward)'
  };
});

const generateUserPrompt = () => {
  const { isForward, text: superLuckDirectionStr } = getSuperLuckDirection.value;
  const genderStr = baziInfo.gender === 'Male' ? '男 (乾造)' : '女 (坤造)';
  const startAgeInt = parseInt(baziInfo.startAge) || 1;

  const directionExample = isForward
    ? "例如：第一步是【戊申】，第二步则是【己酉】（顺排）"
    : "例如：第一步是【戊申】，第二步则是【丁未】（逆排）";

  const yearStemPolarity = (() => {
    const firstChar = baziInfo.yearPillar.trim().charAt(0);
    const yangStems = ['甲', '丙', '戊', '庚', '壬'];
    return yangStems.includes(firstChar) ? '阳' : '阴';
  })();

  return `请根据以下**已经排好的**八字四柱和**指定的大运信息**进行分析。

【基本信息】
性别：${genderStr}
姓名：${baziInfo.name || "未提供"}
出生年份：${baziInfo.birthYear}年 (阳历)

【八字四柱】
年柱：${baziInfo.yearPillar} (天干属性：${yearStemPolarity})
月柱：${baziInfo.monthPillar}
日柱：${baziInfo.dayPillar}
时柱：${baziInfo.hourPillar}

【大运核心参数】
1. 起运年龄：${baziInfo.startAge} 岁 (虚岁)。
2. 第一步大运：${baziInfo.firstSuperLuck}。
3. **排序方向**：${superLuckDirectionStr}。

【必须执行的算法 - 大运序列生成】
请严格按照以下步骤生成数据：

1. **锁定第一步**：确认【${baziInfo.firstSuperLuck}】为第一步大运。
2. **计算序列**：根据六十甲子顺序和方向（${superLuckDirectionStr}），推算出接下来的 9 步大运。
   ${directionExample}
3. **填充 JSON**：
   - Age 1 到 ${startAgeInt - 1}: superLuck = "童限"
   - Age ${startAgeInt} 到 ${startAgeInt + 9}: superLuck = [第1步大运: ${baziInfo.firstSuperLuck}]
   - Age ${startAgeInt + 10} 到 ${startAgeInt + 19}: superLuck = [第2步大运]
   - ...以此类推直到 100 岁。

【特别警告】
- **superLuck 字段**：必须填大运干支（10年一变），**绝对不要**填流年干支。
- **ganZhi 字段**：填入该年份的**流年干支**（每年一变，例如 2024=甲辰，2025=乙巳）。

任务：
1. 确认格局与喜忌。
2. 生成 **1-100 岁 (虚岁)** 的人生流年K线数据。
3. 在 \`reason\` 字段中提供流年详批。
4. 生成带评分的命理分析报告（包含性格分析、币圈交易分析、发展风水分析）。

请严格按照系统指令生成 JSON 数据。务必只返回纯JSON格式数据，不要包含任何markdown代码块标记或其他文字说明。`;
};

const copyFullPrompt = async () => {
  const fullPrompt = `=== 系统指令 (System Prompt) ===\n\n${BAZI_SYSTEM_INSTRUCTION}\n\n=== 用户提示词 (User Prompt) ===\n\n${generateUserPrompt()}`;
  try {
    await navigator.clipboard.writeText(fullPrompt);
    copied.value = true;
    setTimeout(() => copied.value = false, 2000);
  } catch (err) {
    console.error('复制失败', err);
  }
};

const handleImport = () => {
  error.value = null;
  if (!jsonInput.value.trim()) {
    error.value = '请粘贴 AI 返回的 JSON 数据';
    return;
  }

  try {
    let jsonContent = jsonInput.value.trim();
    const jsonMatch = jsonContent.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (jsonMatch && jsonMatch[1]) {
        jsonContent = jsonMatch[1].trim();
      } else {
      const jsonStartIndex = jsonContent.indexOf('{');
      const jsonEndIndex = jsonContent.lastIndexOf('}');
      if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
        jsonContent = jsonContent.substring(jsonStartIndex, jsonEndIndex + 1);
      }
    }

    const data = JSON.parse(jsonContent);

    if (!data.chartPoints || !Array.isArray(data.chartPoints)) {
      throw new Error('数据格式不正确：缺少 chartPoints 数组');
    }
    if (data.chartPoints.length < 10) {
      throw new Error('数据不完整：chartPoints 数量太少');
    }

    const result: LifeDestinyResult = {
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

    emit('data-import', result);
  } catch (err: any) {
    error.value = `解析失败：${err.message}`;
  }
};

const isStep1Valid = computed(() => {
  return baziInfo.birthYear && baziInfo.yearPillar && baziInfo.monthPillar &&
    baziInfo.dayPillar && baziInfo.hourPillar && baziInfo.startAge && baziInfo.firstSuperLuck;
});
</script>

<template>
  <div class="w-full max-w-2xl bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
    <!-- Steps Indicator -->
    <div class="flex items-center justify-center gap-2 mb-8">
      <template v-for="s in [1, 2, 3]" :key="s">
        <div
          class="w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all"
          :class="step === s ? 'bg-indigo-600 text-white scale-110' : step > s ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'"
        >
          <CheckCircle v-if="step > s" class="w-5 h-5" />
          <span v-else>{{ s }}</span>
        </div>
        <div v-if="s < 3" class="w-16 h-1 rounded" :class="step > s ? 'bg-green-500' : 'bg-gray-200'"></div>
      </template>
    </div>

    <!-- Step 1 -->
    <div v-if="step === 1" class="space-y-6">
      <div class="text-center">
        <h2 class="text-2xl font-bold font-serif-sc text-gray-800 mb-2">第一步：输入八字信息</h2>
        <p class="text-gray-500 text-sm">填写您的四柱与大运信息</p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-gray-600 mb-1">姓名 (可选)</label>
          <input type="text" v-model="baziInfo.name" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="姓名" />
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-600 mb-1">性别</label>
          <select v-model="baziInfo.gender" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none">
            <option value="Male">乾造 (男)</option>
            <option value="Female">坤造 (女)</option>
          </select>
        </div>
      </div>

      <div class="bg-amber-50 p-4 rounded-xl border border-amber-100">
        <div class="flex items-center gap-2 mb-3 text-amber-800 text-sm font-bold">
          <Sparkles class="w-4 h-4" />
          <span>四柱干支</span>
        </div>
        <div class="mb-4">
          <label class="block text-xs font-bold text-gray-600 mb-1">出生年份 (阳历)</label>
          <input type="number" v-model="baziInfo.birthYear" placeholder="如: 2003" class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white font-bold" />
        </div>
        <div class="grid grid-cols-4 gap-3">
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">年柱</label>
            <input type="text" v-model="baziInfo.yearPillar" placeholder="甲子" class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">月柱</label>
            <input type="text" v-model="baziInfo.monthPillar" placeholder="乙丑" class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">日柱</label>
            <input type="text" v-model="baziInfo.dayPillar" placeholder="丙寅" class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">时柱</label>
            <input type="text" v-model="baziInfo.hourPillar" placeholder="丁卯" class="w-full px-3 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none bg-white text-center font-serif-sc font-bold" />
          </div>
        </div>
      </div>

      <div class="bg-indigo-50 p-4 rounded-xl border border-indigo-100">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">起运年龄 (虚岁)</label>
            <input type="number" v-model="baziInfo.startAge" placeholder="如: 8" class="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none bg-white text-center font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 mb-1">第一步大运</label>
            <input type="text" v-model="baziInfo.firstSuperLuck" placeholder="如: 辛酉" class="w-full px-3 py-2 border border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none bg-white text-center font-serif-sc font-bold" />
          </div>
        </div>
        <p class="text-xs text-indigo-600/70 mt-2 text-center">
          大运方向：<span class="font-bold text-indigo-900">{{ getSuperLuckDirection.text }}</span>
        </p>
      </div>

      <button @click="step = 2" :disabled="!isStep1Valid" class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2">
        下一步：生成提示词 <ArrowRight class="w-5 h-5" />
      </button>
    </div>

    <!-- Step 2 -->
    <div v-if="step === 2" class="space-y-6">
      <div class="text-center">
        <h2 class="text-2xl font-bold font-serif-sc text-gray-800 mb-2">第二步：复制提示词</h2>
        <p class="text-gray-500 text-sm">将提示词粘贴到任意 AI 聊天工具</p>
      </div>

      <div class="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-200">
        <div class="flex items-center gap-3 mb-4">
          <MessageSquare class="w-6 h-6 text-blue-600" />
          <div>
            <h3 class="font-bold text-gray-800">支持的 AI 工具</h3>
            <p class="text-sm text-gray-600">ChatGPT、Claude、Gemini、通义千问、文心一言 等</p>
          </div>
        </div>

        <div class="bg-white rounded-lg p-4 border border-gray-200 max-h-64 overflow-y-auto mb-4">
          <pre class="text-xs text-gray-700 whitespace-pre-wrap font-mono">{{ generateUserPrompt().substring(0, 500) }}...</pre>
        </div>

        <button @click="copyFullPrompt" class="w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all" :class="copied ? 'bg-green-500 text-white' : 'bg-indigo-600 hover:bg-indigo-700 text-white'">
          <template v-if="copied">
            <CheckCircle class="w-5 h-5" /> 已复制到剪贴板！
          </template>
          <template v-else>
            <Copy class="w-5 h-5" /> 复制完整提示词
          </template>
        </button>
      </div>

      <div class="flex gap-4">
        <button @click="step = 1" class="flex-1 py-3 rounded-xl font-bold border-2 border-gray-300 text-gray-700 hover:bg-gray-50 transition-all">← 上一步</button>
        <button @click="step = 3" class="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2">
          下一步：导入数据 <ArrowRight class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Step 3 -->
    <div v-if="step === 3" class="space-y-6">
      <div class="text-center">
        <h2 class="text-2xl font-bold font-serif-sc text-gray-800 mb-2">第三步：导入 AI 回复</h2>
        <p class="text-gray-500 text-sm">粘贴 AI 返回的 JSON 数据</p>
      </div>

      <div class="bg-gray-50 p-4 rounded-xl border border-gray-200">
        <label class="block text-sm font-bold text-gray-700 mb-2">
          <Upload class="w-4 h-4 inline mr-2" /> 粘贴 AI 返回的 JSON 数据
        </label>
        <textarea v-model="jsonInput" placeholder='将 AI 返回的 JSON 数据粘贴到这里...&#10;&#10;例如:&#10;{&#10;  "bazi": ["癸未", "壬戌", "丙子", "庚寅"],&#10;  "chartPoints": [...],&#10;  ...&#10;}' class="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-xs resize-none"></textarea>
      </div>

      <div v-if="error" class="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg border border-red-200">
        <AlertCircle class="w-5 h-5 flex-shrink-0" />
        <p class="text-sm">{{ error }}</p>
      </div>

      <div class="flex gap-4">
        <button @click="step = 2" class="flex-1 py-3 rounded-xl font-bold border-2 border-gray-300 text-gray-700 hover:bg-gray-50 transition-all">← 上一步</button>
        <button @click="handleImport" class="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-3 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2">
          <Sparkles class="w-5 h-5" /> 生成人生K线
        </button>
      </div>
    </div>
  </div>
</template>
