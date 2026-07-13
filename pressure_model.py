"""
压力指数计算模型
将抽象压力转化为可量化指标，三大维度加权计算
"""


def calculate_pressure_score(
    # 学习压力参数
    homework_hours: float = 2.0,      # 作业时长（小时/天）
    exam_frequency: float = 2.0,      # 考试频率（次/周）
    grade_variance: float = 3.0,      # 成绩波动（标准差，1-10）
    tutoring_count: float = 1.0,      # 课外班数量
    # 生理状态参数
    sleep_hours: float = 7.0,         # 睡眠时长（小时/天）
    sleep_quality: float = 6.0,       # 睡眠质量（1-10分）
    exercise_freq: float = 2.0,       # 运动频率（次/周）
    # 社交反馈参数
    conflict_count: float = 1.0,      # 同伴冲突次数
    parent_criticism: float = 2.0,    # 家长批评频率（1-5）
    social_media_hours: float = 2.0,  # 社交媒体使用时长（小时/天）
    loneliness_score: float = 3.0,    # 孤独感评分（1-10）
) -> dict:
    """
    计算综合压力指数，返回分值和各维度详情
    """
    # 学习压力权重 40%
    study_pressure = (
        homework_hours * 2 +
        exam_frequency * 3 +
        grade_variance * 4 +
        tutoring_count * 1.5
    ) * 0.4

    # 生理状态权重 30%（反向指标：睡眠越少/质量越差，压力越大）
    physical_state = (
        max(0, 8 - sleep_hours) * 4 +
        max(0, 10 - sleep_quality) * 2.5 +
        max(0, 5 - exercise_freq) * 2
    ) * 0.3

    # 社交反馈权重 30%
    social_feedback = (
        conflict_count * 3 +
        parent_criticism * 3 +
        social_media_hours * 1.5 +
        loneliness_score * 2.5
    ) * 0.3

    total_pressure = study_pressure + physical_state + social_feedback

    # 归一化到 0-100
    max_possible = (
        (4 * 2 + 5 * 3 + 10 * 4 + 4 * 1.5) * 0.4 +
        (8 * 4 + 10 * 2.5 + 5 * 2) * 0.3 +
        (5 * 3 + 5 * 3 + 6 * 1.5 + 10 * 2.5) * 0.3
    )
    normalized = min(100, max(0, (total_pressure / max_possible) * 100))

    return {
        "total_score": round(normalized, 1),
        "study_pressure": round(min(100, (study_pressure / ((4 * 2 + 5 * 3 + 10 * 4 + 4 * 1.5) * 0.4)) * 100), 1),
        "physical_state": round(min(100, (physical_state / ((8 * 4 + 10 * 2.5 + 5 * 2) * 0.3)) * 100), 1),
        "social_feedback": round(min(100, (social_feedback / ((5 * 3 + 5 * 3 + 6 * 1.5 + 10 * 2.5) * 0.3)) * 100), 1),
        "breakdown": {
            "homework_hours": homework_hours,
            "exam_frequency": exam_frequency,
            "grade_variance": grade_variance,
            "tutoring_count": tutoring_count,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "exercise_freq": exercise_freq,
            "conflict_count": conflict_count,
            "parent_criticism": parent_criticism,
            "social_media_hours": social_media_hours,
            "loneliness_score": loneliness_score,
        }
    }


def get_pressure_level(score: float) -> dict:
    """根据压力分值返回等级信息"""
    if score <= 30:
        return {
            "level": "轻松状态",
            "color": "#4ECDC4",
            "emoji": "🟢",
            "audio": "轻快钢琴曲、Lo-fi音乐",
            "activity": "散步、阅读、享受当下",
            "description": "你的状态很棒！保持积极的生活方式。"
        }
    elif score <= 60:
        return {
            "level": "适度压力",
            "color": "#FFE66D",
            "emoji": "🟡",
            "audio": "自然白噪音、轻音乐",
            "activity": "深呼吸、冥想、听音乐",
            "description": "有一些压力，但在可管理范围内。试试放松活动~"
        }
    elif score <= 85:
        return {
            "level": "高压力",
            "color": "#FF6B6B",
            "emoji": "🟠",
            "audio": "舒缓大提琴、自然音景",
            "activity": "运动、倾诉、户外活动",
            "description": "压力较大，建议主动采取减压措施。"
        }
    else:
        return {
            "level": "超负荷",
            "color": "#9B59B6",
            "emoji": "🔴",
            "audio": "双耳节拍（Binaural Beats）",
            "activity": "休息、专业咨询、与信任的人深谈",
            "description": "压力已超出正常范围，请务必休息！必要时寻求专业帮助。"
        }


# 快速测评版（简化输入）
def quick_pressure_score(
    sleep: float = 7.0,
    mood: float = 5.0,
    stress: float = 5.0,
) -> dict:
    """
    快速压力测评，3个核心指标
    - sleep: 昨晚睡眠时长（0-12小时）
    - mood: 当前心情（1-10分）
    - stress: 当前压力感（1-10分）
    """
    score = (10 - mood) * 5 + max(0, 8 - sleep) * 4 + stress * 5
    score = min(100, max(0, score))
    result = get_pressure_level(score)
    result["total_score"] = round(score, 1)
    return result
