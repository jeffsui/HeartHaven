"""
🌈 情绪避风港 — 青少年情绪可视化实验室
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

import numpy as np
import pandas as pd
import streamlit as st
from color_mapping import PRESSURE_COLOR_MAP, get_breath_animation_params
from data_utils import (
    clear_diary,
    load_diary,
    load_sample_data,
    save_diary_entry,
    seed_sample_diary,
)
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
    breath_guide,
    card,
    color_psychology_item,
    footer,
    hotline_box,
    main_title,
    recommendation_box,
    score_display,
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


# ============ 侧边栏：压力自测 ============
def render_sidebar():
    st.sidebar.title("🧪 压力测评")
    test_mode = st.sidebar.radio(
        "选择测评模式", ["快速测评（3题）", "详细测评（11题）"], index=0
    )

    if test_mode == "快速测评（3题）":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 快速压力测评")
        sleep = st.sidebar.slider("😴 昨晚睡了几小时？", 0.0, 12.0, 7.0, 0.5)
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
        tutoring = st.sidebar.slider("课外辅导班数量", 0.0, 5.0, 1.0, 0.5)

        st.sidebar.markdown("#### 💪 生理状态")
        sleep_h = st.sidebar.slider("每天睡眠时长（小时）", 0.0, 12.0, 7.0, 0.5)
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
    st.subheader("🏠 压力仪表盘")

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
    st.markdown("#### 🔄 压力能量流向图")
    avg_study = np.mean(
        [
            calculate_pressure_score(**_row_kwargs(row))["study_pressure"]
            for _, row in df.iterrows()
        ]
    )
    avg_phys = np.mean(
        [
            calculate_pressure_score(**_row_kwargs(row))["physical_state"]
            for _, row in df.iterrows()
        ]
    )
    avg_social = np.mean(
        [
            calculate_pressure_score(**_row_kwargs(row))["social_feedback"]
            for _, row in df.iterrows()
        ]
    )
    st.plotly_chart(
        plot_sankey(
            avg_study,
            avg_phys,
            avg_social,
            avg_study + avg_phys + avg_social,
            theme=theme,
        ),
        use_container_width=True,
    )

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
        ["🏠 仪表盘", "📊 数据分析", "📖 情绪日记", "💡 减压推荐"]
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
