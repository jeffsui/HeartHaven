"""
压力指数模型

实际问卷数据包含三次压力指数（压力指数1/2/3）与平均值，
综合压力指数取三次测量的平均值，与 CSV 的「平均值」列口径一致。
"""


def calculate_pressure_score(index1: float, index2: float, index3: float) -> dict:
    """由三次压力指数计算综合压力指数、各次明细与波动幅度。"""
    indices = [
        round(float(index1), 1),
        round(float(index2), 1),
        round(float(index3), 1),
    ]
    return {
        "total_score": round(sum(indices) / len(indices), 1),
        "indices": indices,
        "amplitude": round(max(indices) - min(indices), 1),
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
            "description": "你的状态很棒！保持积极的生活方式。",
        }
    elif score <= 60:
        return {
            "level": "适度压力",
            "color": "#FFE66D",
            "emoji": "🟡",
            "audio": "自然白噪音、轻音乐",
            "activity": "深呼吸、冥想、听音乐",
            "description": "有一些压力，但在可管理范围内。试试放松活动~",
        }
    elif score <= 85:
        return {
            "level": "高压力",
            "color": "#FF6B6B",
            "emoji": "🟠",
            "audio": "舒缓大提琴、自然音景",
            "activity": "运动、倾诉、户外活动",
            "description": "压力较大，建议主动采取减压措施。",
        }
    else:
        return {
            "level": "超负荷",
            "color": "#9B59B6",
            "emoji": "🔴",
            "audio": "双耳节拍（Binaural Beats）",
            "activity": "休息、专业咨询、与信任的人深谈",
            "description": "压力已超出正常范围，请务必休息！必要时寻求专业帮助。",
        }
