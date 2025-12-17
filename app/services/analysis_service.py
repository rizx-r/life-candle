import json
import re
import os
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schemas import UserInput, LifeDestinyResult, Gender
from app.services.random_gen import generate_random_life_result
from app.utils.bazi import get_stem_polarity
from app.models.db_models import AnalysisResult
from app.db.redis_ import get_redis
from app.db.database import AsyncSessionLocal

BAZI_SYSTEM_INSTRUCTION = """
你是一位八字命理大师，精通加密货币市场周期。根据用户提供的四柱干支和大运信息，生成"人生K线图"数据和命理报告。

**核心规则:**
1. **年龄计算**: 采用虚岁，从 1 岁开始。
2. **K线详批**: 每年的 `reason` 字段必须**控制在20-30字以内**，简洁描述吉凶趋势即可。
3. **评分机制**: 所有维度给出 0-10 分。
4. **数据起伏**: 让评分呈现明显波动，体现"牛市"和"熊市"区别，禁止输出平滑直线。

**大运规则:**
- 顺行: 甲子 -> 乙丑 -> 丙寅...
- 逆行: 甲子 -> 癸亥 -> 壬戌...
- 以用户指定的第一步大运为起点，每步管10年。

**关键字段:**
- `superLuck`: 大运干支 (10年不变)
- `ganZhi`: 流年干支 (每年一变)

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
"""


def get_stem_polarity(pillar: str) -> str:
    if not pillar:
        return 'YANG'
    first_char = pillar.strip()[0]
    yang_stems = ['甲', '丙', '戊', '庚', '壬']
    if first_char in yang_stems:
        return 'YANG'
    return 'YIN'


async def generate_life_analysis(input_data: UserInput) -> LifeDestinyResult:
    # 1. Resolve API Config (User Input > System Env)
    api_key = input_data.apiKey.strip() if input_data.apiKey else os.getenv("GEMINI_API_KEY", "").strip()
    base_url = input_data.apiBaseUrl.strip().rstrip('/') if input_data.apiBaseUrl else os.getenv("GEMINI_BASE_URL",
                                                                                                 "https://max.openai365.top/v1").strip().rstrip(
        '/')
    model_name = input_data.modelName.strip() if input_data.modelName else os.getenv("GEMINI_MODEL_NAME",
                                                                                     "gemini-3-pro-preview").strip()

    if api_key.lower() == 'demo':
        print('🎯 使用本地演示模式')
        with open('mock_data.json', 'r', encoding='utf-8') as f:
            mock_data = json.load(f)

        return LifeDestinyResult(
            chartData=mock_data['chartPoints'],
            analysis={
                'bazi': mock_data.get('bazi', []),
                'summary': mock_data.get('summary', "无摘要"),
                'summaryScore': mock_data.get('summaryScore', 5),
                'personality': mock_data.get('personality', "无性格分析"),
                'personalityScore': mock_data.get('personalityScore', 5),
                'industry': mock_data.get('industry', "无"),
                'industryScore': mock_data.get('industryScore', 5),
                'geomancy': mock_data.get('geomancy', "建议多亲近自然，保持心境平和。"),
                'geomancyScore': mock_data.get('geomancyScore', 5),
                'wealth': mock_data.get('wealth', "无"),
                'wealthScore': mock_data.get('wealthScore', 5),
                'marriage': mock_data.get('marriage', "无"),
                'marriageScore': mock_data.get('marriageScore', 5),
                'health': mock_data.get('health', "无"),
                'healthScore': mock_data.get('healthScore', 5),
                'family': mock_data.get('family', "无"),
                'familyScore': mock_data.get('familyScore', 5),
                'crypto': mock_data.get('crypto', "暂无交易分析"),
                'cryptoScore': mock_data.get('cryptoScore', 5),
                'cryptoYear': mock_data.get('cryptoYear', "待定"),
                'cryptoStyle': mock_data.get('cryptoStyle', "现货定投"),
            }
        )
    elif api_key.lower() == 'random':
        print('🎲 使用随机生成模式')
        return generate_random_life_result(input_data)

    # Random Data Mode (handled above)

    # Validation: If no key is found at all
    if not api_key:
        # 402 Payment Required allows frontend to identify "Quota/Key Missing" state
        raise HTTPException(status_code=402, detail="服务器免费额度已用完，请在'高级设置'中填写您自己的 API Key。")

    if not base_url:
        raise HTTPException(status_code=400, detail="API Base URL 配置缺失。")

    gender_str = '男 (乾造)' if input_data.gender == Gender.MALE else '女 (坤造)'

    try:
        start_age_int = int(input_data.startAge)
    except (ValueError, TypeError):
        start_age_int = 1

    year_stem_polarity = get_stem_polarity(input_data.yearPillar)

    if input_data.gender == Gender.MALE:
        is_forward = (year_stem_polarity == 'YANG')
    else:
        is_forward = (year_stem_polarity == 'YIN')

    da_yun_direction_str = '顺行 (Forward)' if is_forward else '逆行 (Backward)'
    direction_example = "例如：第一步是【戊申】，第二步则是【己酉】（顺排）" if is_forward else "例如：第一步是【戊申】，第二步则是【丁未】（逆排）"

    user_prompt = f"""
    请根据以下**已经排好的**八字四柱和**指定的大运信息**进行分析。

    【基本信息】
    性别：{gender_str}
    姓名：{input_data.name or "未提供"}
    出生年份：{input_data.birthYear}年 (阳历)

    【八字四柱】
    年柱：{input_data.yearPillar} (天干属性：{'阳' if year_stem_polarity == 'YANG' else '阴'})
    月柱：{input_data.monthPillar}
    日柱：{input_data.dayPillar}
    时柱：{input_data.hourPillar}

    【大运核心参数】
    1. 起运年龄：{input_data.startAge} 岁 (虚岁)。
    2. 第一步大运：{input_data.firstSuperLuck}。
    3. **排序方向**：{da_yun_direction_str}。

    【必须执行的算法 - 大运序列生成】
    请严格按照以下步骤生成数据：

    1. **锁定第一步**：确认【{input_data.firstSuperLuck}】为第一步大运。
    2. **计算序列**：根据六十甲子顺序和方向（{da_yun_direction_str}），推算出接下来的 9 步大运。
       {direction_example}
    3. **填充 JSON**：
       - Age 1 到 {start_age_int - 1}: superLuck = "童限"
       - Age {start_age_int} 到 {start_age_int + 9}: superLuck = [第1步大运: {input_data.firstSuperLuck}]
       - Age {start_age_int + 10} 到 {start_age_int + 19}: superLuck = [第2步大运]
       - Age {start_age_int + 20} 到 {start_age_int + 29}: superLuck = [第3步大运]
       - ...以此类推直到 100 岁。

    【特别警告】
    - **superLuck 字段**：必须填大运干支（10年一变），**绝对不要**填流年干支。
    - **ganZhi 字段**：填入该年份的**流年干支**（每年一变，例如 2024=甲辰，2025=乙巳）。

    任务：
    1. 确认格局与喜忌。
    2. 生成 **1-100 岁 (虚岁)** 的人生流年K线数据。
    3. 在 `reason` 字段中提供流年详批。
    4. 生成带评分的命理分析报告（包含性格分析、币圈交易分析、发展风水分析）。

    请严格按照系统指令生成 JSON 数据。
    """

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                json={
                    'model': model_name,
                    'messages': [
                        {"role": "system",
                         "content": BAZI_SYSTEM_INSTRUCTION + "\n\n请务必只返回纯JSON格式数据，不要包含任何markdown代码块标记。"},
                        {"role": "user", "content": user_prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 30000
                }
            )

            if response.status_code == 401 or response.status_code == 402 or response.status_code == 429:
                # Propagate these specific errors so frontend knows to ask user for key
                raise HTTPException(status_code=402,
                                    detail=f"API 调用失败 ({response.status_code})：服务器免费额度可能已耗尽，请尝试提供您自己的 API Key。")

            if response.status_code != 200:
                raise Exception(f"API 请求失败: {response.status_code} - {response.text}")

            json_result = response.json()
            content = json_result['choices'][0]['message']['content']

            if not content:
                raise Exception("模型未返回任何内容。")

            # Extract JSON from markdown code blocks if present
            json_content = content
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
            if json_match:
                json_content = json_match.group(1).strip()
            else:
                json_start_index = content.find('{')
                json_end_index = content.rfind('}')
                if json_start_index != -1 and json_end_index != -1:
                    json_content = content[json_start_index:json_end_index + 1]

            data = json.loads(json_content)

            # Basic Validation
            if 'chartPoints' not in data or not isinstance(data['chartPoints'], list):
                raise ValueError("模型返回的数据格式不正确（缺失 chartPoints）。")

            return LifeDestinyResult(
                chartData=data['chartPoints'],
                analysis={
                    'bazi': data.get('bazi', []),
                    'summary': data.get('summary', "无摘要"),
                    'summaryScore': data.get('summaryScore', 5),
                    'personality': data.get('personality', "无性格分析"),
                    'personalityScore': data.get('personalityScore', 5),
                    'industry': data.get('industry', "无"),
                    'industryScore': data.get('industryScore', 5),
                    'geomancy': data.get('geomancy', "建议多亲近自然，保持心境平和。"),
                    'geomancyScore': data.get('geomancyScore', 5),
                    'wealth': data.get('wealth', "无"),
                    'wealthScore': data.get('wealthScore', 5),
                    'marriage': data.get('marriage', "无"),
                    'marriageScore': data.get('marriageScore', 5),
                    'health': data.get('health', "无"),
                    'healthScore': data.get('healthScore', 5),
                    'family': data.get('family', "无"),
                    'familyScore': data.get('familyScore', 5),
                    'crypto': data.get('crypto', "暂无交易分析"),
                    'cryptoScore': data.get('cryptoScore', 5),
                    'cryptoYear': data.get('cryptoYear', "待定"),
                    'cryptoStyle': data.get('cryptoStyle', "现货定投"),
                }
            )

    except Exception as e:
        print(f"Gemini/OpenAI API Error: {e}")
        # Only raise 402 if it looks like an API quota issue, otherwise re-raise or 500
        # For now keeping original behavior but fixing variable reference
        raise HTTPException(status_code=402,
                            detail=f"API 调用失败：{str(e)}。服务器免费额度可能已耗尽，请尝试提供您自己的 API Key。")


async def get_cached_analysis(input_hash: str) -> LifeDestinyResult | None:
    redis = await get_redis()
    try:
        cached_data = await redis.get(f"analysis:{input_hash}")
        if cached_data:
            try:
                data = json.loads(cached_data)
                return LifeDestinyResult(**data)
            except Exception as e:
                print(f"Error parsing cached data: {e}")
                return None
    except Exception as e:
        print(f"Redis error: {e}")
    return None

async def get_db_analysis(db: AsyncSession, input_hash: str) -> LifeDestinyResult | None:
    try:
        result = await db.execute(select(AnalysisResult).filter(AnalysisResult.input_hash == input_hash))
        record = result.scalars().first()
        if record:
            try:
                return LifeDestinyResult(**record.data)
            except Exception as e:
                print(f"Error parsing db data: {e}")
                return None
    except Exception as e:
        print(f"DB error: {e}")
    return None

async def save_analysis_async(input_hash: str, result: LifeDestinyResult):
    # Save to Redis
    try:
        redis = await get_redis()
        await redis.set(f"analysis:{input_hash}", result.model_dump_json(), ex=3600*24*7) # Cache for 7 days
    except Exception as e:
        print(f"Error saving to Redis: {e}")
    
    # Save to DB
    async with AsyncSessionLocal() as session:
        try:
            # Check if exists again to avoid race conditions (simple check)
            existing = await session.execute(select(AnalysisResult).filter(AnalysisResult.input_hash == input_hash))
            if not existing.scalars().first():
                new_record = AnalysisResult(input_hash=input_hash, data=result.model_dump(mode='json'))
                session.add(new_record)
                await session.commit()
        except Exception as e:
            print(f"Error saving to DB: {e}")
            await session.rollback()
