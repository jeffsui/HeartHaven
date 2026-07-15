"""
解法推荐引擎（无 AI 版 · 本地降级用）

把用户在欢迎页表达的情绪文字，通过关键词匹配映射到一组减压解法。
当未接入 AI（无 Key 或调用失败）时，作为本地陪伴降级方案使用。
"""

# 解法库：每个解法含展示用 emoji / 标题 / 描述 / 主题色
# 颜色复用三大压力维度品牌色，保证视觉统一
SOLUTION_LIBRARY = {
    "深呼吸": {"emoji": "🌬", "title": "深呼吸", "desc": "缓解焦虑与紧张", "color": "#6FCFC4"},
    "冥想": {"emoji": "🧘", "title": "冥想", "desc": "平静心绪", "color": "#B18BC9"},
    "听音乐": {"emoji": "🎵", "title": "听音乐", "desc": "Lo-fi 放松", "color": "#E0C068"},
    "写日记": {"emoji": "📖", "title": "写日记", "desc": "梳理情绪", "color": "#E8928C"},
    "散步": {"emoji": "🚶", "title": "散步", "desc": "换个环境", "color": "#7FB069"},
    "制定学习计划": {"emoji": "📚", "title": "制定计划", "desc": "分解考试压力", "color": "#E8928C"},
    "番茄钟": {"emoji": "⏰", "title": "番茄钟", "desc": "专注写作业", "color": "#E0C068"},
    "呼吸训练": {"emoji": "🌬", "title": "呼吸训练", "desc": "4-7-8 呼吸法", "color": "#6FCFC4"},
    "白噪音": {"emoji": "😴", "title": "白噪音", "desc": "助眠", "color": "#9AA0A8"},
    "睡眠音乐": {"emoji": "🎵", "title": "睡眠音乐", "desc": "睡前放松", "color": "#9AA0A8"},
    "情绪记录": {"emoji": "❤️", "title": "情绪记录", "desc": "看见情绪", "color": "#E8928C"},
    "找人聊聊": {"emoji": "💬", "title": "找人聊聊", "desc": "倾诉支持", "color": "#6FCFC4"},
}

# 关键词 → 解法列表
KEYWORDS = {
    "考试": ["深呼吸", "制定学习计划", "听音乐"],
    "作业": ["番茄钟", "听音乐"],
    "焦虑": ["冥想", "呼吸训练"],
    "失眠": ["白噪音", "睡眠音乐"],
    "吵架": ["情绪记录", "散步"],
    "孤独": ["写日记", "散步", "找人聊聊"],
    "压力": ["深呼吸", "冥想", "散步"],
    "烦": ["听音乐", "散步"],
    "哭": ["找人聊聊", "写日记"],
    "累": ["散步", "听音乐"],
}

# 无匹配时的兜底推荐
DEFAULT_SOLUTIONS = ["深呼吸", "冥想", "听音乐", "写日记"]


def recommend_solutions(text: str) -> list:
    """
    根据用户输入文字返回推荐解法 key 列表（去重、保序）。
    无命中关键词时返回 DEFAULT_SOLUTIONS。
    """
    if not text:
        return list(DEFAULT_SOLUTIONS)

    lowered = text.lower()
    matched = []
    for key, sols in KEYWORDS.items():
        if key in lowered:
            for s in sols:
                if s not in matched:
                    matched.append(s)

    return matched if matched else list(DEFAULT_SOLUTIONS)
