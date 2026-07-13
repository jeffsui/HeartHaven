"""
压力-色彩映射系统
将压力指数转化为视觉色彩和感官体验
"""

# 压力等级到色彩的完整映射
PRESSURE_COLOR_MAP = {
    "低频压力（0-30）": {
        "color": "#6FCFC4",
        "color_name": "柔青色",
        "emotion": "平静",
        "audio": "轻快钢琴曲",
        "audio_url": "https://music.163.com/#/playlist?id=806941556",
        "activity": "散步、阅读",
        "breath_pattern": "4-7-8呼吸法（吸气4秒-屏息7秒-呼气8秒）",
    },
    "中频压力（31-60）": {
        "color": "#E0C068",
        "color_name": "柔黄色",
        "emotion": "温暖",
        "audio": "自然白噪音",
        "audio_url": "https://music.163.com/#/playlist?id=53453271",
        "activity": "深呼吸、冥想",
        "breath_pattern": "腹式呼吸（吸气4秒-呼气6秒）",
    },
    "高频压力（61-85）": {
        "color": "#E8928C",
        "color_name": "柔珊瑚",
        "emotion": "警示",
        "audio": "舒缓大提琴",
        "audio_url": "https://music.163.com/#/playlist?id=713945846",
        "activity": "运动、倾诉",
        "breath_pattern": "方框呼吸（吸气4秒-屏息4秒-呼气4秒-屏息4秒）",
    },
    "超高频压力（86-100）": {
        "color": "#B18BC9",
        "color_name": "柔紫色",
        "emotion": "深度疗愈",
        "audio": "双耳节拍（Binaural Beats）",
        "audio_url": "https://music.163.com/#/playlist?id=601946963",
        "activity": "专业咨询、休息",
        "breath_pattern": "延长呼气（吸气3秒-呼气6秒）",
    },
}


def get_color_for_score(score: float) -> str:
    """根据压力分值返回对应颜色"""
    if score <= 30:
        return PRESSURE_COLOR_MAP["低频压力（0-30）"]["color"]
    elif score <= 60:
        return PRESSURE_COLOR_MAP["中频压力（31-60）"]["color"]
    elif score <= 85:
        return PRESSURE_COLOR_MAP["高频压力（61-85）"]["color"]
    else:
        return PRESSURE_COLOR_MAP["超高频压力（86-100）"]["color"]


def get_gradient_colors(score: float) -> list:
    """生成从绿色到当前压力色的渐变色列表"""
    base_color = (111, 207, 196)  # #6FCFC4
    if score <= 30:
        target = base_color
    elif score <= 60:
        target = (224, 192, 104)  # #E0C068
    elif score <= 85:
        target = (232, 146, 140)  # #E8928C
    else:
        target = (177, 139, 201)   # #B18BC9

    colors = []
    steps = 10
    for i in range(steps):
        ratio = i / (steps - 1)
        r = int(base_color[0] + (target[0] - base_color[0]) * ratio)
        g = int(base_color[1] + (target[1] - base_color[1]) * ratio)
        b = int(base_color[2] + (target[2] - base_color[2]) * ratio)
        colors.append(f"rgb({r},{g},{b})")
    return colors


def get_breath_animation_params(score: float) -> dict:
    """根据压力等级返回呼吸引导动画参数"""
    if score <= 30:
        return {"inhale": 4, "hold": 7, "exhale": 8, "cycles": 3}
    elif score <= 60:
        return {"inhale": 4, "hold": 0, "exhale": 6, "cycles": 5}
    elif score <= 85:
        return {"inhale": 4, "hold": 4, "exhale": 4, "hold2": 4, "cycles": 5}
    else:
        return {"inhale": 3, "hold": 0, "exhale": 6, "cycles": 8}
