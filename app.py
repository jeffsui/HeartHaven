"""
🌈 净化 — 青少年情绪可视化实验室
Streamlit 主应用（重构版）

结构：
    main()
      ├─ 主题切换 + 注入主题样式
      ├─ render_sidebar()        侧边栏压力自测
      ├─ render_dashboard()      仪表盘
      ├─ render_analysis()       群体数据分析
      ├─ render_diary()          情绪日记
      └─ render_recommendation() 个性化减压方案
"""

import time

import numpy as np
import pandas as pd
import streamlit as st
from ai_companion import PROVIDERS, generate_companion
from color_mapping import PRESSURE_COLOR_MAP, get_breath_animation_params
from data_utils import (
    clear_diary,
    load_diary,
    load_sample_data,
    save_diary_entry,
    seed_sample_diary,
)
from dotenv import load_dotenv
from music_library import search_url
from pressure_model import (
    calculate_pressure_score,
    get_pressure_level,
    quick_pressure_score,
)
from theme import get_theme, render_theme_style
from ui import (
    PHYS_COLOR,
    SOCIAL_COLOR,
    STUDY_COLOR,
    ai_comfort_box,
    breath_guide,
    card,
    color_psychology_item,
    emotion_gradient,
    footer,
    hotline_box,
    main_title,
    meditation_card,
    music_card,
    recommendation_box,
    score_display,
    solution_card,
    subtitle,
)
from visualization import (
    generate_sample_weekly_data,
    plot_group_comparison,
    plot_pressure_source_pie,
    plot_pressure_trend,
    plot_pressure_wave,
    plot_sankey,
)

load_dotenv()


# ============ 侧边栏：压力自测 ============
def render_sidebar():
    st.sidebar.title("🧪 压力测评")
    test_mode = st.sidebar.radio(
        "选择测评模式", ["快速测评（3题）", "详细测评（11题）"], index=0
    )

    if test_mode == "快速测评（3题）":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 快速压力测评")
        sleep = st.sidebar.slider("😴 昨晚睡了几小时？", 0.0, 12.0, 8.0, 0.5)
        mood = st.sidebar.slider("😊 当前心情（1-10分）", 1.0, 10.0, 5.0, 0.5)
        stress = st.sidebar.slider("😰 当前压力感（1-10分）", 1.0, 10.0, 5.0, 0.5)
        result = quick_pressure_score(sleep=sleep, mood=mood, stress=stress)
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 详细压力测评")

        st.sidebar.markdown("#### 📚 学习压力")
        homework = st.sidebar.slider("每天作业时长（小时）", 0.0, 5.0, 2.0, 0.5)
        exam_freq = st.sidebar.slider("每周考试/测验次数", 0.0, 6.0, 2.0, 0.5)
        grade_var = st.sidebar.slider("成绩波动程度（1-10）", 1.0, 10.0, 3.0, 0.5)
        tutoring = st.sidebar.slider("课外辅导班数量", 0.0, 5.0, 3.0, 0.5)

        st.sidebar.markdown("#### 💪 生理状态")
        sleep_h = st.sidebar.slider("每天睡眠时长（小时）", 0.0, 12.0, 8.0, 0.5)
        sleep_q = st.sidebar.slider("睡眠质量（1-10分）", 1.0, 10.0, 6.0, 0.5)
        exercise = st.sidebar.slider("每周运动次数", 0.0, 7.0, 2.0, 0.5)

        st.sidebar.markdown("#### 👥 社交反馈")
        conflict = st.sidebar.slider("同伴冲突次数", 0.0, 5.0, 1.0, 0.5)
        criticism = st.sidebar.slider("家长批评频率（1-5）", 1.0, 5.0, 2.0, 0.5)
        social_media = st.sidebar.slider(
            "社交媒体使用时长（小时/天）", 0.0, 8.0, 2.0, 0.5
        )
        loneliness = st.sidebar.slider("孤独感评分（1-10）", 1.0, 10.0, 3.0, 0.5)

        result = calculate_pressure_score(
            homework_hours=homework,
            exam_frequency=exam_freq,
            grade_variance=grade_var,
            tutoring_count=tutoring,
            sleep_hours=sleep_h,
            sleep_quality=sleep_q,
            exercise_freq=exercise,
            conflict_count=conflict,
            parent_criticism=criticism,
            social_media_hours=social_media,
            loneliness_score=loneliness,
        )

    score = result["total_score"]
    level_info = get_pressure_level(score)
    return result, score, level_info


# ============ Tab 1: 仪表盘 ============
def render_dashboard(result, score, level_info, color, theme):
    st.subheader("🧪 压力测评")

    # AI 情绪陪伴（解决方法）与欢迎页保持一致：此前 AI 已给出的分析/音乐/呼吸/冥想
    companion = st.session_state.get("companion")
    if companion:
        st.markdown("#### 🤖 AI 情绪陪伴 · 你的解决方法")
        render_solution_section(companion, theme, with_gradient=False)
        st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            card(
                "学习压力",
                result.get("study_pressure", "N/A"),
                color,
                theme,
                STUDY_COLOR,
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            card(
                "生理状态",
                result.get("physical_state", "N/A"),
                color,
                theme,
                PHYS_COLOR,
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            card(
                "社交反馈",
                result.get("social_feedback", "N/A"),
                color,
                theme,
                SOCIAL_COLOR,
            ),
            unsafe_allow_html=True,
        )

    # 压力波段曲线
    st.markdown("#### 📈 一周压力波动预测")
    weekly_data = generate_sample_weekly_data(score)
    st.pyplot(plot_pressure_wave(weekly_data, color=color, theme=theme))

    # 压力来源饼图
    st.markdown("#### 🎯 压力来源分布")
    study_val = result.get("study_pressure", 30)
    phys_val = result.get("physical_state", 25)
    social_val = result.get("social_feedback", 25)
    st.plotly_chart(
        plot_pressure_source_pie(study_val, phys_val, social_val, theme=theme),
        use_container_width=True,
    )


# ============ Tab 2: 数据分析 ============
def _row_kwargs(row):
    """把数据行转为 calculate_pressure_score 的关键字参数（去掉分组列）。"""
    return {k: v for k, v in row.items() if k not in ("grade", "gender")}


def _avg_group(group, scores):
    return {
        "group": group,
        "study": np.mean([s["study_pressure"] for s in scores]),
        "physical": np.mean([s["physical_state"] for s in scores]),
        "social": np.mean([s["social_feedback"] for s in scores]),
    }


def render_analysis(theme):
    st.subheader("📊 群体数据分析")

    df = load_sample_data()
    st.markdown(f"当前使用 **模拟数据**（{len(df)} 位同学），可替换为实际问卷数据。")

    # 群体对比
    st.markdown("#### 不同年级压力对比")
    group_data = []
    for grade in ["初一", "初二", "初三"]:
        subset = df[df["grade"] == grade]
        scores = [
            calculate_pressure_score(**_row_kwargs(row)) for _, row in subset.iterrows()
        ]
        if scores:
            group_data.append(_avg_group(grade, scores))
    group_df = pd.DataFrame(group_data)
    st.plotly_chart(
        plot_group_comparison(group_df, theme=theme), use_container_width=True
    )

    # 性别对比
    st.markdown("#### 不同性别压力对比")
    gender_data = []
    for gender in ["男", "女"]:
        subset = df[df["gender"] == gender]
        scores = [
            calculate_pressure_score(**_row_kwargs(row)) for _, row in subset.iterrows()
        ]
        if scores:
            gender_data.append(_avg_group(gender, scores))
    gender_df = pd.DataFrame(gender_data)
    st.plotly_chart(
        plot_group_comparison(gender_df, theme=theme), use_container_width=True
    )

    # 桑基图
    # st.markdown("#### 🔄 压力能量流向图")
    # avg_study = np.mean(
    #     [
    #         calculate_pressure_score(**_row_kwargs(row))["study_pressure"]
    #         for _, row in df.iterrows()
    #     ]
    # )
    # avg_phys = np.mean(
    #     [
    #         calculate_pressure_score(**_row_kwargs(row))["physical_state"]
    #         for _, row in df.iterrows()
    #     ]
    # )
    # avg_social = np.mean(
    #     [
    #         calculate_pressure_score(**_row_kwargs(row))["social_feedback"]
    #         for _, row in df.iterrows()
    #     ]
    # )
    # st.plotly_chart(
    #     plot_sankey(
    #         avg_study,
    #         avg_phys,
    #         avg_social,
    #         avg_study + avg_phys + avg_social,
    #         theme=theme,
    #     ),
    #     use_container_width=True,
    # )

    # 原始数据
    with st.expander("📋 查看原始数据"):
        st.dataframe(df.round(2), use_container_width=True)


# ============ Tab 3: 情绪日记 ============
def render_diary(score, theme):
    st.subheader("📖 情绪日记")
    st.markdown("记录你每天的压力值，追踪情绪变化趋势。")

    if st.button("✨ 载入示例日记（演示用）"):
        seeded = seed_sample_diary()
        st.success(
            "✅ 已载入两周示例日记！" if seeded else "示例日记已存在，未重复载入。"
        )
        st.rerun()

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        diary_date = st.date_input("📅 日期")
    with col_b:
        diary_score = st.slider("压力指数", 0, 100, int(score))
    with col_c:
        diary_note = st.text_input("📝 今天的心情（选填）")

    if st.button("💾 保存今日记录", use_container_width=True):
        save_diary_entry(str(diary_date), diary_score, diary_note)
        st.success("✅ 已保存！")

    diary = load_diary()
    if diary:
        st.markdown("#### 📈 情绪趋势")
        fig_diary = plot_pressure_trend(diary, theme=theme)
        if fig_diary:
            st.plotly_chart(fig_diary, use_container_width=True)

        with st.expander("📋 查看所有记录"):
            for entry in reversed(diary):
                level = get_pressure_level(entry["score"])
                st.markdown(
                    f"- **{entry['date']}** | 压力指数: **{entry['score']}** "
                    f"{level['emoji']} {level['level']} | {entry.get('note', '')}"
                )

        if st.button("🗑️ 清空所有记录"):
            clear_diary()
            st.rerun()
    else:
        st.info("还没有记录，快来写第一条吧！")


# ============ Tab 4: 减压推荐 ============
def render_recommendation(score, level_info, color, theme):
    st.subheader("💡 个性化减压方案")

    # 与 AI 情绪陪伴（压力测评里的解决方法）保持一致：优先展示 AI 推荐的那首歌
    companion = st.session_state.get("companion")
    music = companion.get("music", {}) if companion else {}
    if music.get("name"):
        st.markdown("#### 🎵 为你推荐的音乐（与 AI 陪伴一致）")
        st.markdown(music_card(music, theme), unsafe_allow_html=True)
        st.link_button(
            "▶ 点击播放",
            search_url(music["name"], music.get("artist", "")),
            key="reco_play",
        )
        st.markdown("---")

    st.markdown(recommendation_box(level_info, color, theme), unsafe_allow_html=True)

    # 呼吸引导
    st.markdown("#### 🫁 呼吸引导")
    breath = get_breath_animation_params(score)
    st.markdown(breath_guide(breath, color, theme), unsafe_allow_html=True)

    # 色彩心理学
    st.markdown("#### 🎨 色彩心理学解读")
    for level_name, info in PRESSURE_COLOR_MAP.items():
        st.markdown(
            color_psychology_item(level_name, info, theme), unsafe_allow_html=True
        )

    st.markdown("""
> 💚 **温馨提示**：本工具仅用于压力自测和情绪记录，**不能替代专业心理诊断**。
> 如果您感到持续痛苦，请务必寻求专业心理咨询师的帮助。
""")


def _parse_breathing(s: str) -> dict:
    """把 '478' 之类解析为呼吸参数；不足补默认。"""
    nums = [int(c) for c in str(s) if c.isdigit()]
    if len(nums) >= 3:
        inhale, hold, exhale = nums[0], nums[1], nums[2]
    elif len(nums) == 2:
        inhale, hold, exhale = nums[0], 0, nums[1]
    else:
        inhale, hold, exhale = 4, 7, 8
    return {"inhale": inhale, "hold": hold, "exhale": exhale, "cycles": 4}


def render_solution_section(result: dict, theme, with_gradient: bool = False):
    """渲染 AI 解决方法：共情 → 音乐 → 呼吸 → 冥想。

    可在欢迎页（带情绪渐变）与『压力测评』Tab（不带渐变，避免污染整个仪表盘主题）复用。
    """
    color = result.get("color", "#6FCFC4")

    # 情绪渐变：首次播放动画，之后静态着色（避免交互重播闪烁）
    if with_gradient:
        if st.session_state.get("companion_color") != color:
            st.markdown(
                emotion_gradient(color, theme, animate=True), unsafe_allow_html=True
            )
            st.session_state.companion_color = color
        else:
            st.markdown(
                emotion_gradient(color, theme, animate=False), unsafe_allow_html=True
            )

    # AI 共情
    st.markdown(
        ai_comfort_box(result.get("comfort", ""), color, theme),
        unsafe_allow_html=True,
    )

    # 音乐疗愈
    st.markdown(music_card(result.get("music", {}), theme), unsafe_allow_html=True)
    music = result.get("music", {})
    if music.get("name"):
        st.link_button(
            "▶ 点击播放",
            search_url(music["name"], music.get("artist", "")),
            key="solution_play",
        )

    # 呼吸训练
    st.markdown("#### 🌬 接下来做一次呼吸训练")
    breath = _parse_breathing(result.get("breathing", "478"))
    st.markdown(breath_guide(breath, color, theme), unsafe_allow_html=True)

    # 冥想
    st.markdown("#### 🧘 最后做一次冥想")
    st.markdown(
        meditation_card(result.get("meditation", "3分钟正念呼吸"), theme),
        unsafe_allow_html=True,
    )
    if st.button("🧘 开始冥想", use_container_width=True, key="solution_meditation"):
        st.info(
            "找一个舒服的姿势，闭上眼睛，跟随上面的呼吸节奏，"
            "把注意力放在每一次吸气与呼气上……"
        )

    # 降级提示
    if result.get("fallback"):
        st.caption("ℹ️ 当前未接入 AI（未提供 Key 或调用失败），已使用本地陪伴建议。")


# ============ 欢迎页（AI 情绪陪伴入口） ============
def render_welcome(theme):
    st.markdown(main_title(), unsafe_allow_html=True)
    st.markdown(subtitle(), unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="text-align:center; margin: 30px 0;">
            <h1>👋 Hi！</h1>
            <h2>今天过得怎么样？</h2>
            <p style="color:{theme.sub}; font-size:1.1rem;">有什么想分享的吗？</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.text_area(
        "情绪表达",
        placeholder="请输入今天发生的事情……",
        height=180,
        key="welcome_text",
        label_visibility="collapsed",
    )

    # AI 设置（可选）：选择 provider 并粘贴 key
    with st.expander("⚙️ AI 设置（可选，不填则使用本地陪伴）"):
        provider = st.radio(
            "选择 AI 模型", list(PROVIDERS.keys()), index=0, horizontal=True
        )
        st.session_state[f"api_key_{provider}"] = st.text_input(
            f"{provider} API Key",
            type="password",
            value=st.session_state.get(f"api_key_{provider}", ""),
        )
        st.caption(
            "Key 仅保存在本次会话，不会写入磁盘。也可通过环境变量 "
            "ZHIPU_API_KEY / KIMI_API_KEY / GEMINI_API_KEY 提供。"
        )

    if st.button("💡 解决方法", use_container_width=True):
        placeholder = st.empty()
        steps = [
            "🤖 AI正在倾听你的故事……",
            "正在分析情绪……",
            "正在寻找最适合你的音乐……",
            "正在生成疗愈建议……",
        ]
        for s in steps:
            placeholder.markdown(
                f"<div style='text-align:center; color:{theme.sub}; "
                f"font-size:1.05rem; margin:10px 0;'>{s}</div>",
                unsafe_allow_html=True,
            )
            time.sleep(0.7)
        placeholder.empty()

        result = generate_companion(st.session_state.get("welcome_text", ""), provider)
        st.session_state.companion = result
        st.session_state.show_solution = True
        st.rerun()

    # 点击「解决方法」后，AI 结果不在欢迎页展示，而是进入 Dashboard 的「压力测评」后再显示
    if st.session_state.get("show_solution", False) and st.session_state.get(
        "companion"
    ):
        # 保留情绪渐变作为情感反馈（不展示文字结果）
        color = st.session_state.companion.get("color", "#6FCFC4")
        if st.session_state.get("companion_color") != color:
            st.markdown(
                emotion_gradient(color, theme, animate=True), unsafe_allow_html=True
            )
            st.session_state.companion_color = color
        else:
            st.markdown(
                emotion_gradient(color, theme, animate=False), unsafe_allow_html=True
            )

        st.success(
            "✅ AI 已为你生成专属建议（音乐 / 呼吸 / 冥想），"
            "进入「压力测评」即可查看。"
        )
        if st.button(
            "📊 进入压力分析 Dashboard",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.entered_app = True
            st.rerun()
    else:
        # 未使用 AI 陪伴时，仍可跳过直接进入 Dashboard
        if st.button(
            "📊 直接进入压力分析 Dashboard（跳过 AI 陪伴）",
            use_container_width=True,
        ):
            st.session_state.entered_app = True
            st.rerun()


# ============ 主程序 ============
def main():
    st.set_page_config(
        page_title="净化",
        page_icon="🌈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 主题切换（侧边栏最上方）
    _choice = st.sidebar.radio(
        "🎨 界面主题",
        ["🌙 深色", "☀️ 浅色"],
        index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
        horizontal=True,
    )
    st.session_state.theme = "dark" if _choice.startswith("🌙") else "light"
    theme = get_theme()
    render_theme_style(theme)

    # 情绪引导：欢迎页优先；未进入前侧边栏只保留主题切换
    if not st.session_state.get("entered_app", False):
        render_welcome(theme)
        return

    # 侧边栏自测
    result, score, level_info = render_sidebar()
    color = level_info["color"]

    # 主标题 + 压力指数卡片
    st.markdown(main_title(), unsafe_allow_html=True)
    st.markdown(subtitle(), unsafe_allow_html=True)
    st.markdown(score_display(score, level_info, color, theme), unsafe_allow_html=True)
    if score > 85:
        st.markdown(hotline_box(theme), unsafe_allow_html=True)

    # 四个 Tab
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🧪 压力测评", "📊 数据分析", "📖 情绪日记", "💡 减压推荐"]
    )
    with tab1:
        render_dashboard(result, score, level_info, color, theme)
    with tab2:
        render_analysis(theme)
    with tab3:
        render_diary(score, theme)
    with tab4:
        render_recommendation(score, level_info, color, theme)

    # 页脚
    st.markdown("---")
    st.markdown(footer(theme), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
