import random
from app.models.schemas import UserInput  # use compatibility wrapper
from app.models.schemas import LifeDestinyResult, KLinePoint, AnalysisData, UserInput as UIType

GAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}
WUXING_SCORE = {
    "木": 2,
    "火": 3,
    "土": 1,
    "金": 2,
    "水": 2,
}

def calc_base_score(day_pillar: str) -> float:
    gan = day_pillar[0]
    wuxing = GAN_WUXING.get(gan, "土")
    return 50 + WUXING_SCORE[wuxing] * 5
def calc_superluck_bonus(super_luck: str) -> float:
    if super_luck == "童限":
        return -5
    gan = super_luck[0]
    wuxing = GAN_WUXING.get(gan, "土")
    return WUXING_SCORE[wuxing] * 2
def calc_year_bonus(gan_zhi: str) -> float:
    gan = gan_zhi[0]
    wuxing = GAN_WUXING.get(gan, "土")
    return WUXING_SCORE[wuxing]
def calc_age_bonus(age: int) -> float:
    if age < 18:
        return -8
    elif age < 30:
        return 0
    elif age < 45:
        return 6
    elif age < 60:
        return 3
    else:
        return 1

def generate_life_result(input_data: UserInput) -> LifeDestinyResult:
    if not isinstance(input_data, UserInput):
        raise TypeError("参数必须是 UserInput 类型")

    try:
        start_year = int(input_data.birthYear)
    except Exception:
        start_year = 2024

    try:
        start_age = int(input_data.startAge)
    except Exception:
        start_age = 1

    gan_zhis = [
        "甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉",
        "甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未",
        "甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳",
        "甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯",
        "甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑",
        "甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥"
    ]

    superLucks = ["甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉"]

    chart_data = []
    current_year = start_year

    base_score = calc_base_score(input_data.dayPillar)

    for age in range(start_age, 101):
        gan_zhi = gan_zhis[(current_year - 4) % 60]
        da_yun = superLucks[(age // 10) % 10] if age >= 10 else "童限"

        score = (
            base_score
            + calc_superluck_bonus(da_yun)
            + calc_year_bonus(gan_zhi)
            + calc_age_bonus(age)
            + random.uniform(-2, 2)
        )

        score = max(10, min(90, score))

        open_val = chart_data[-1].close if chart_data else score
        close_val = score
        high_val = max(open_val, close_val) + 2
        low_val = min(open_val, close_val) - 2

        chart_data.append(
            KLinePoint(
                age=age,
                year=current_year,
                ganZhi=gan_zhi,
                superLuck=da_yun,
                open=round(open_val, 1),
                close=round(close_val, 1),
                high=round(high_val, 1),
                low=round(low_val, 1),
                score=round(score, 1),
                reason="运势由命局、大运、流年与人生阶段综合决定"
            )
        )

        current_year += 1
        s = int(base_score // 10)

        analysis = AnalysisData(
            bazi=[
                input_data.yearPillar,
                input_data.monthPillar,
                input_data.dayPillar,
                input_data.hourPillar,
            ],
            summary="命局稳定，中年运势最佳，晚年趋于平顺。",
            summaryScore=s,

            personality="性格积极主动，有进取心。",
            personalityScore=min(9, s + 1),

            industry="适合技术、金融、管理类行业。",
            industryScore=s,

            geomancy="宜南方或东南方发展。",
            geomancyScore=s,

            wealth="财运循序渐进，中年见成。",
            wealthScore=min(9, s + 1),

            marriage="婚姻整体平稳，重在沟通。",
            marriageScore=max(5, s - 1),

            health="注意心血管与作息规律。",
            healthScore=max(5, s - 1),

            family="家庭关系整体和谐。",
            familyScore=s,

            crypto="偏向长期价值投资。",
            cryptoScore=s,
            cryptoYear="2025 (乙巳)",
            cryptoStyle="现货定投 + 低频波段"
        )

        return LifeDestinyResult(chartData=chart_data, analysis=analysis)


def generate_random_life_result(input_data: UIType) -> LifeDestinyResult:
    if not isinstance(input_data, UIType):
        raise TypeError("generate_random_life_result 的参数必须是 UserInput 类型。")

    try:
        start_year = int(input_data.birthYear)
    except (ValueError, TypeError):
        start_year = 2024

    try:
        start_age = int(input_data.startAge)
    except (ValueError, TypeError):
        start_age = 1
    
    chart_data = []
    current_year = start_year
    
    gan_zhis = [
        "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
        "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
        "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
        "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
        "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
        "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
    ]
    
    da_yuns = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉"]
    
    reasons = [
        "今年运势平稳，适合积累。", "财星高照，有意外之喜。", "注意身体健康，避免过度劳累。",
        "事业上有贵人相助，进展顺利。", "感情生活丰富，但需注意沟通。", "投资需谨慎，避免高风险操作。",
        "学业进步明显，考试运佳。", "家庭和睦，幸福美满。", "可能会有变动，需做好心理准备。",
        "虽然有压力，但也是成长的机会。"
    ]

    for age in range(start_age, 101):
        open_val = chart_data[-1].close if chart_data else 50.0
        change = random.uniform(-15, 15)
        close_val = max(10, min(90, open_val + change))
        high_val = max(open_val, close_val) + random.uniform(0, 5)
        low_val = min(open_val, close_val) - random.uniform(0, 5)
        score_val = close_val 
        gan_zhi = gan_zhis[(current_year - 4) % 60]
        da_yun_idx = (age // 10) % len(da_yuns)
        da_yun = da_yuns[da_yun_idx] if age >= 10 else "童限"

        point = KLinePoint(
            age=age,
            year=current_year,
            ganZhi=gan_zhi,
            superLuck=da_yun,
            open=round(open_val, 1),
            close=round(close_val, 1),
            high=round(high_val, 1),
            low=round(low_val, 1),
            score=round(score_val, 1),
            reason=random.choice(reasons)
        )
        chart_data.append(point)
        current_year += 1

    analysis = AnalysisData(
        bazi=["甲子", "丙寅", "戊辰", "壬戌"],
        summary="这是一个随机生成的命理摘要。命主性格坚韧，财运起伏较大，晚年运势平稳。",
        summaryScore=random.randint(6, 9),
        personality="性格开朗，善于交际，但有时过于急躁。",
        personalityScore=random.randint(6, 9),
        industry="适合从事金融、科技或创意类工作。",
        industryScore=random.randint(6, 9),
        geomancy="宜居南方，喜火土，家中可摆放红色饰品。",
        geomancyScore=random.randint(6, 9),
        wealth="财运中等偏上，中年有大财。",
        wealthScore=random.randint(6, 9),
        marriage="婚姻美满，配偶得力。",
        marriageScore=random.randint(6, 9),
        health="注意心血管健康，多运动。",
        healthScore=random.randint(6, 9),
        family="家庭关系和谐，子女孝顺。",
        familyScore=random.randint(6, 9),
        crypto="适合长线持有 BTC/ETH，避免高频合约。",
        cryptoScore=random.randint(6, 9),
        cryptoYear="2025 (乙巳)",
        cryptoStyle="现货定投 + 少量波段"
    )

    return LifeDestinyResult(
        chartData=chart_data,
        analysis=analysis
    )
