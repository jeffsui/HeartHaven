"""
UI 组件模块

所有自定义 HTML 卡片与区块都放在这里，返回字符串，
由 app.py 通过 st.markdown(..., unsafe_allow_html=True) 渲染。
这样 app.py 不再堆砌大段 HTML，整体更简洁、可复用。
"""

from music_library import search_url
from solutions import SOLUTION_LIBRARY
from theme import Theme

# 三大压力维度品牌色（与主题无关，恒定）
STUDY_COLOR = "#E8928C"  # 学习压力 · 柔珊瑚
PHYS_COLOR = "#6FCFC4"  # 生理状态 · 柔青
SOCIAL_COLOR = "#E0C068"  # 社交反馈 · 柔黄


def main_title() -> str:
    return '<div class="main-title">🌈 净化</div>'


def subtitle() -> str:
    return '<div class="subtitle">Turn invisible emotions into visible colors</div>'


def score_display(score: float, level_info: dict, color: str, theme: Theme) -> str:
    """顶部压力指数大卡片。"""
    return f"""
<div class="score-display" style="background: linear-gradient(135deg, {color}33, {color}66); border: 2px solid {color};">
    <h1 style="color: {color}; margin:0;">{level_info["emoji"]} 你的压力指数</h1>
    <h1 style="color: {color}; font-size: 3rem; margin:5px 0;">{score:.0f} / 100</h1>
    <h3 style="color: {color}; margin:0;">{level_info["level"]}</h3>
    <p style="color: {theme.sub}; font-size: 16px; margin-top:8px;">{level_info["description"]}</p>
</div>
"""


def hotline_box(theme: Theme) -> str:
    """高压警示 + 求助热线。"""
    return """
<div class="hotline-box">
    ⚠️ <strong>你的压力已超出正常范围</strong><br>
    📞 24小时心理援助热线：<strong>400-161-9995</strong><br>
    📞 北京心理危机研究与干预中心：<strong>010-82951332</strong><br>
    💚 请务必休息，必要时寻求专业帮助。
</div>
"""


def card(title: str, value, color: str, theme: Theme, value_color: str = None) -> str:
    """通用指标卡片（左侧色条 + 标题 + 数值）。"""
    value_color = value_color or color
    return f"""
<div class="metric-card" style="border-left: 4px solid {color};">
    <h4>{title}</h4>
    <h2 style="color: {value_color};">{value}</h2>
</div>
"""


def recommendation_box(level_info: dict, color: str, theme: Theme) -> str:
    """个性化减压方案：推荐音乐 / 活动。"""
    return f"""
<div style="background: {color}22; border-radius: 15px; padding: 25px; border: 2px solid {color};">
    <h3 style="color: {color};">🎵 推荐音乐</h3>
    <p style="font-size: 16px;">{level_info["audio"]}</p>

    <h3 style="color: {color}; margin-top: 15px;">🧘 推荐活动</h3>
    <p style="font-size: 16px;">{level_info["activity"]}</p>
</div>
"""


def breath_guide(breath: dict, color: str, theme: Theme) -> str:
    """呼吸引导区块。"""
    if breath.get("hold", 0) > 0:
        pattern = (
            f"吸气 {breath['inhale']}秒 → 屏息 {breath['hold']}秒 "
            f"→ 呼气 {breath['exhale']}秒"
        )
    else:
        pattern = f"吸气 {breath['inhale']}秒 → 呼气 {breath['exhale']}秒"
    return f"""
<div style="background: {theme.card}; border-radius: 15px; padding: 25px; text-align: center;">
    <div class="breath-circle" style="background: {color}; color: white; margin: 10px auto;">
        🫁
    </div>
    <p style="font-size: 18px; font-weight: bold;">{pattern}</p>
    <p>重复 {breath["cycles"]} 个循环</p>
</div>
"""


def color_psychology_item(level_name: str, info: dict, theme: Theme) -> str:
    """色彩心理学解读中的单条。"""
    return f"""
<div style="background: {info["color"]}15; border-left: 4px solid {info["color"]}; padding: 10px 15px; margin: 5px 0; border-radius: 5px;">
    <strong style="color: {info["color"]};">{level_name}</strong> —
    <span style="color: {info["color"]};">■</span> {info["color_name"]}（{info["emotion"]}）
    <br>🎵 {info["audio"]} | 🏃 {info["activity"]} | 🫁 {info["breath_pattern"]}
</div>
"""


def footer(theme: Theme) -> str:
    """页脚。"""
    return f"""
<div style="text-align: center; color: {theme.footer}; font-size: 0.85rem; padding: 10px;">
    🌈 净化 — 青少年情绪可视化实验室<br>
    压力不是弱点，而是需要被理解的信号
</div>
"""


def solution_card(sol_key: str, theme: Theme) -> str:
    """欢迎页推荐解法卡片（emoji + 标题 + 描述 + 顶部色条），深浅模式自适应。"""
    info = SOLUTION_LIBRARY.get(
        sol_key, {"emoji": "💡", "title": sol_key, "desc": "", "color": "#6FCFC4"}
    )
    color = info["color"]
    return f"""
<div style="background:{theme.card}; border:1px solid {theme.border}; border-top:4px solid {color};
            border-radius:12px; padding:18px; text-align:center; height:100%;">
    <div style="font-size:2rem;">{info["emoji"]}</div>
    <div style="font-weight:700; color:{theme.title}; margin:6px 0;">{info["title"]}</div>
    <div style="font-size:0.85rem; color:{theme.sub};">{info["desc"]}</div>
</div>
"""


def ai_comfort_box(comfort: str, color: str, theme: Theme) -> str:
    """AI 想对你说：共情安慰框，左侧用 AI 生成的情绪色。"""
    return f"""
<div style="background: {color}1A; border-left: 4px solid {color}; border-radius: 12px; padding: 20px; margin: 10px 0;">
    <div style="font-size: 1.05rem; font-weight: 700; color: {color}; margin-bottom: 8px;">💙 AI想对你说</div>
    <p style="color: {theme.text}; font-size: 1rem; line-height: 1.8; white-space: pre-line; margin: 0;">{comfort}</p>
</div>
"""


def music_card(music: dict, theme: Theme) -> str:
    """推荐歌曲卡片（歌名 / 歌手 / 推荐原因）。"""
    return f"""
<div style="background: {theme.card}; border: 1px solid {theme.border}; border-radius: 12px; padding: 18px;">
    <div style="font-weight: 700; color: {theme.title}; font-size: 1.05rem; margin-bottom: 6px;">🎵 推荐歌曲</div>
    <div style="margin: 6px 0;">
        <strong style="color: {theme.title}; font-size: 1.15rem;">{music.get("name", "")}</strong>
        <span style="color: {theme.sub};"> — {music.get("artist", "")}</span>
    </div>
    <div style="font-size: 0.9rem; color: {theme.sub};">推荐原因：{music.get("reason", "")}</div>
</div>
"""


def meditation_card(text: str, theme: Theme) -> str:
    """冥想引导卡片。"""
    return f"""
<div style="background: {theme.card}; border: 1px solid {theme.border}; border-radius: 12px; padding: 18px; margin: 10px 0;">
    <div style="font-weight: 700; color: {theme.title}; font-size: 1.05rem; margin-bottom: 6px;">🧘 冥想</div>
    <p style="color: {theme.sub}; font-size: 0.95rem; margin: 0;">{text}</p>
</div>
"""


def emotion_gradient(color: str, theme: Theme, animate: bool = True) -> str:
    """注入情绪渐变 CSS：背景过渡到 AI 生成的情绪色，呼吸圆圈也跟随。

    animate=True 时播放 2.5s 渐变动画（首次进入陪伴页）；
    animate=False 时直接静态着色（避免后续交互重播闪烁）。
    """

    # 计算颜色明度并选择合适的前景色（深色或白色）以保证对比度
    def _hex_to_rgb(h: str):
        h = h.lstrip("#")
        if len(h) == 3:
            h = "".join([c * 2 for c in h])
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return r, g, b

    def _relative_luminance(r, g, b):
        # sRGB -> linear
        def _f(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        R = _f(r)
        G = _f(g)
        B = _f(b)
        return 0.2126 * R + 0.7152 * G + 0.0722 * B

    try:
        r, g, b = _hex_to_rgb(color)
        lum = _relative_luminance(r, g, b)
    except Exception:
        # 解析失败时回退到主题文本色
        lum = 0.0
        r, g, b = (0, 0, 0)

    # 阈值选择，亮色背景需暗色前景（contrast-friendly）
    fg = "#111111" if lum > 0.5 else "#FFFFFF"
    fg_rgba = f"rgba({r}, {g}, {b}, 0.12)"
    fg_border = f"rgba({r}, {g}, {b}, 0.22)"

    # 注入更有侵略性的覆盖，包含文字、按钮、链接等元素
    if animate:
        body = f"""
@keyframes emotionFade {{
    0% {{ background-color: {theme.bg} !important; color: {theme.text} !important; }}
    100% {{ background-color: {color} !important; color: {fg} !important; }}
}}
* {{
    animation: emotionFade 2.5s ease forwards !important;
}}
html, body {{
    background-color: {color} !important;
    background: {color} !important;
    color: {fg} !important;
}}
section[data-testid="stAppViewContainer"] {{
    background-color: {color} !important;
    background: {color} !important;
    color: {fg} !important;
}}
div[data-testid="stMain"] {{
    background-color: {color} !important;
    background: {color} !important;
    color: {fg} !important;
}}
div[class*="block-container"] {{
    background-color: {color} !important;
    background: {color} !important;
    color: {fg} !important;
}}
.stApp {{
    background-color: {color} !important;
    background: {color} !important;
    color: {fg} !important;
}}

/* 按钮与链接 */
button, .stButton>button, a, .stButton button {{
    color: {fg} !important;
    background-color: {fg_rgba} !important;
    border-color: {fg_border} !important;
}}

/* Streamlit 组件的文本覆盖 */
.stMarkdown, .stText, .main-title, .subtitle, .score-display, .metric-card, .hotline-box {{
    color: {fg} !important;
}}
"""
    else:
        body = f"""
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
div[class*="block-container"] {{
    background-color: {color} !important;
    background: {color} !important;
    color: {fg} !important;
}}

button, .stButton>button, a, .stButton button {{
    color: {fg} !important;
    background-color: {fg_rgba} !important;
    border-color: {fg_border} !important;
}}
"""
    # 额外覆盖：增强边框可见性（特别是在亮色背景下）
    extra = f"""
/* 边框与输入可见性增强 */
.metric-card, .score-display, .hotline-box, .stCard, .stMarkdown, .stText, .stHeader, .stSidebar, .block-container {{
    border-color: {fg_border} !important;
    box-shadow: 0 0 0 1px {fg_border} inset !important;
}}

input, textarea, select, .stTextInput>div, .stTextArea>div, .stNumberInput>div, .stSelectbox>div {{
    border-color: {fg_border} !important;
    box-shadow: 0 0 0 1px {fg_border} inset !important;
    background-clip: padding-box !important;
}}

/* 保持按钮边界清晰 */
.stButton>button, button, .stButton button {{
    border: 1px solid {fg_border} !important;
    box-shadow: 0 1px 0 0 rgba(0,0,0,0.06) !important;
}}
"""

    return f"""
<style>
{body}
.breath-circle {{
    background: {color} !important;
    transition: background 2.5s ease !important;
}}
{extra}
</style>
"""
