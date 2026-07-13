"""
主题管理模块

定义深色 / 浅色两套主题（dataclass），并提供：
- get_theme()       : 从 session_state 读取当前主题对象
- toggle_theme()    : 切换主题并刷新页面
- render_theme_style(): 注入主题 CSS，使原生组件跟随切换
"""

from dataclasses import dataclass

import streamlit as st


@dataclass
class Theme:
    name: str

    bg: str
    card: str

    text: str
    title: str
    sub: str

    accent: str

    border: str

    footer: str

    plotly_template: str

    paper_bg: str
    plot_bg: str

    # 高压警示框配色（暖色警告调）
    hot_bg: str
    hot_border: str
    hot_fg: str


DARK = Theme(
    name="dark",

    bg="#14141A",
    card="#23232C",

    text="#E6E6EA",
    title="#F2F2F5",
    sub="#B8B8C4",

    accent="#6FCFC4",

    border="#444444",

    footer="#999999",

    plotly_template="plotly_dark",

    paper_bg="rgba(0,0,0,0)",

    plot_bg="rgba(0,0,0,0)",

    hot_bg="#2E2A1E",
    hot_border="#E0C068",
    hot_fg="#E6E6EA",
)

LIGHT = Theme(
    name="light",

    bg="#F7F8FA",
    card="#FFFFFF",

    text="#2C2C34",
    title="#111111",
    sub="#666666",

    accent="#4ECDC4",

    border="#DDDDDD",

    footer="#777777",

    plotly_template="plotly_white",

    paper_bg="rgba(255,255,255,0)",

    plot_bg="rgba(255,255,255,0)",

    hot_bg="#FFF8E6",
    hot_border="#E0A800",
    hot_fg="#5A4B00",
)


def get_theme() -> Theme:
    """根据 session_state 返回当前主题对象（默认深色）。"""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    return DARK if st.session_state.theme == "dark" else LIGHT


def toggle_theme():
    """在深色 / 浅色之间切换并刷新页面。"""
    st.session_state.theme = (
        "light" if st.session_state.theme == "dark" else "dark"
    )
    st.rerun()


def render_theme_style(theme: Theme):
    """
    注入主题 CSS。

    关键点：重写 Streamlit 的主题 CSS 变量（--default-background-color 等），
    这样原生组件（Tab / 表格 / Expander / 按钮 / 提示框 / 文字）都会跟随主题切换；
    同时强制覆盖主区域所有层级的容器背景（含 stMainBlockContainer / .block-container），
    解决中间区域不跟随的问题。
    """
    st.markdown(
        f"""
<style>
    :root, html, .stApp {{
        --default-background-color: {theme.bg} !important;
        --default-text-color: {theme.text} !important;
        --secondary-background-color: {theme.card} !important;
        --text-color: {theme.text} !important;
        --background-color: {theme.bg} !important;
        --default-primary-color: {theme.accent} !important;
    }}
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .main .block-container,
    .block-container,
    [data-testid="stHeader"] {{
        background-color: {theme.bg} !important;
        background: {theme.bg} !important;
        color: {theme.text} !important;
    }}
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div {{
        background-color: {theme.bg} !important;
        background: {theme.bg} !important;
    }}
    .stMarkdown, p, label, span, div {{ color: {theme.text}; }}
    h1, h2, h3, h4, h5, h6 {{ color: {theme.title}; }}
    /* Tab 标签 */
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent !important; }}
    .stTabs [data-baseweb="tab"] {{ color: {theme.text} !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: {theme.accent} !important;
        border-bottom-color: {theme.accent} !important;
    }}
    /* 数据表 */
    .stDataFrame, [data-testid="stDataFrame"] {{ background-color: {theme.card} !important; }}
    .stDataFrame table, .stDataFrame th, .stDataFrame td {{
        background-color: {theme.card} !important;
        color: {theme.text} !important;
        border-color: {theme.sub} !important;
    }}
    /* Expander */
    [data-testid="stExpander"] {{
        background-color: {theme.card} !important;
        border-color: {theme.sub} !important;
    }}
    [data-testid="stExpander"] summary {{ color: {theme.text} !important; }}
    /* 按钮 */
    .stButton > button {{
        background-color: {theme.card} !important;
        color: {theme.text} !important;
        border-color: {theme.sub} !important;
    }}
    .stButton > button:hover {{
        border-color: {theme.accent} !important;
        color: {theme.accent} !important;
    }}
    /* 提示框 info / success / warning / error */
    [data-testid="stAlert"], .stAlert {{
        background-color: {theme.card} !important;
        color: {theme.text} !important;
        border-color: {theme.sub} !important;
    }}
    /* 输入控件 */
    .stTextInput input, .stDateInput input, .stSelectbox select,
    input, textarea, select {{
        background-color: {theme.card} !important;
        color: {theme.text} !important;
    }}
    .stSlider label, .stSlider [data-testid="stTickBar"] {{ color: {theme.text} !important; }}
    /* 自定义类 */
    .main-title {{
        text-align: center; font-size: 2.5rem; font-weight: 800;
        color: {theme.title}; margin-bottom: 0.3rem;
    }}
    .subtitle {{
        text-align: center; font-size: 1.1rem;
        color: {theme.sub}; margin-bottom: 1.5rem;
    }}
    .score-display {{
        text-align: center; padding: 25px; border-radius: 15px; margin: 10px 0;
    }}
    .metric-card {{
        background: {theme.card}; border-radius: 10px; padding: 15px;
        text-align: center; margin: 5px 0;
    }}
    .breath-circle {{
        width: 120px; height: 120px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 20px auto; font-size: 1.2rem; font-weight: bold;
        transition: all 4s ease;
    }}
    .hotline-box {{
        background: {theme.hot_bg}; border-left: 4px solid {theme.hot_border};
        color: {theme.hot_fg}; padding: 12px 15px; border-radius: 5px; margin: 10px 0;
    }}
</style>
""",
        unsafe_allow_html=True,
    )
