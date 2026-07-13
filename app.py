"""
🌈 情绪避风港 — 青少年情绪可视化实验室
Streamlit 主应用
"""

import numpy as np
import pandas as pd
import streamlit as st
from color_mapping import (
    PRESSURE_COLOR_MAP,
    get_breath_animation_params,
    get_color_for_score,
    get_gradient_colors,
)
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
from visualization import (
    generate_sample_weekly_data,
    plot_group_comparison,
    plot_pressure_source_pie,
    plot_pressure_trend,
    plot_pressure_wave,
    plot_sankey,
)

# ============ 页面配置 ============
st.set_page_config(
    page_title="情绪避风港",
    page_icon="🌈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ 自定义样式 ============
st.markdown(
    """
<style>
    /* ===== 暗黑模式基底 ===== */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #14141A;
        color: #E6E6EA;
    }
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: #F2F2F5;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #B8B8C4;
        margin-bottom: 1.5rem;
    }
    .score-display {
        text-align: center;
        padding: 25px;
        border-radius: 15px;
        margin: 10px 0;
    }
    .metric-card {
        background: #23232C;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px 0;
    }
    .breath-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        font-size: 1.2rem;
        font-weight: bold;
        transition: all 4s ease;
    }
    .hotline-box {
        background: #2E2A1E;
        border-left: 4px solid #E0C068;
        color: #E6E6EA;
        padding: 12px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============ 侧边栏：压力自测 ============
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
    score = result["total_score"]
    level_info = get_pressure_level(score)
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
    social_media = st.sidebar.slider("社交媒体使用时长（小时/天）", 0.0, 8.0, 2.0, 0.5)
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

color = level_info["color"]


# ============ 主页面 ============
st.markdown('<div class="main-title">🌈 情绪避风港</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">让看不见的压力，变成看得见的色彩</div>',
    unsafe_allow_html=True,
)

# 压力指数展示卡片
st.markdown(
    f"""
<div class="score-display" style="background: linear-gradient(135deg, {color}33, {color}66); border: 2px solid {color};">
    <h1 style="color: {color}; margin:0;">{level_info["emoji"]} 你的压力指数</h1>
    <h1 style="color: {color}; font-size: 3rem; margin:5px 0;">{score:.0f} / 100</h1>
    <h3 style="color: {color}; margin:0;">{level_info["level"]}</h3>
    <p style="color: #555; font-size: 16px; margin-top:8px;">{level_info["description"]}</p>
</div>
""",
    unsafe_allow_html=True,
)

# 高压警示 + 求助热线
if score > 85:
    st.markdown(
        """
    <div class="hotline-box">
        ⚠️ <strong>你的压力已超出正常范围</strong><br>
        📞 24小时心理援助热线：<strong>400-161-9995</strong><br>
        📞 北京心理危机研究与干预中心：<strong>010-82951332</strong><br>
        💚 请务必休息，必要时寻求专业帮助。
    </div>
    """,
        unsafe_allow_html=True,
    )


# ============ Tab 页 ============
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏠 仪表盘", "📊 数据分析", "📖 情绪日记", "💡 减压推荐"]
)

# ---------- Tab 1: 仪表盘 ----------
with tab1:
    st.subheader("🏠 压力仪表盘")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
        <div class="metric-card" style="border-left: 4px solid {color};">
            <h4>学习压力</h4>
            <h2 style="color: #FF6B6B;">{result.get("study_pressure", "N/A")}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="metric-card" style="border-left: 4px solid {color};">
            <h4>生理状态</h4>
            <h2 style="color: #4ECDC4;">{result.get("physical_state", "N/A")}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-card" style="border-left: 4px solid {color};">
            <h4>社交反馈</h4>
            <h2 style="color: #FFE66D;">{result.get("social_feedback", "N/A")}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # 压力波段曲线
    st.markdown("#### 📈 一周压力波动预测")
    weekly_data = generate_sample_weekly_data(score)
    fig_wave = plot_pressure_wave(weekly_data, color=color)
    st.pyplot(fig_wave)

    # 压力来源饼图
    st.markdown("#### 🎯 压力来源分布")
    study_val = result.get("study_pressure", 30)
    phys_val = result.get("physical_state", 25)
    social_val = result.get("social_feedback", 25)
    fig_pie = plot_pressure_source_pie(study_val, phys_val, social_val)
    st.plotly_chart(fig_pie, use_container_width=True)


# ---------- Tab 2: 数据分析 ----------
with tab2:
    st.subheader("📊 群体数据分析")

    df = load_sample_data()
    st.markdown(f"当前使用 **模拟数据**（{len(df)} 位同学），可替换为实际问卷数据。")

    # 群体对比
    st.markdown("#### 不同年级压力对比")
    from pressure_model import calculate_pressure_score as cps

    group_data = []
    for grade in ["初一", "初二", "初三"]:
        subset = df[df["grade"] == grade]
        scores = []
        for _, row in subset.iterrows():
            r = cps(
                homework_hours=row["homework_hours"],
                exam_frequency=row["exam_frequency"],
                grade_variance=row["grade_variance"],
                tutoring_count=row["tutoring_count"],
                sleep_hours=row["sleep_hours"],
                sleep_quality=row["sleep_quality"],
                exercise_freq=row["exercise_freq"],
                conflict_count=row["conflict_count"],
                parent_criticism=row["parent_criticism"],
                social_media_hours=row["social_media_hours"],
                loneliness_score=row["loneliness_score"],
            )
            scores.append(r)
        if scores:
            avg_study = np.mean([s["study_pressure"] for s in scores])
            avg_phys = np.mean([s["physical_state"] for s in scores])
            avg_social = np.mean([s["social_feedback"] for s in scores])
            group_data.append(
                {
                    "group": grade,
                    "study": avg_study,
                    "physical": avg_phys,
                    "social": avg_social,
                }
            )

    group_df = pd.DataFrame(group_data)
    fig_group = plot_group_comparison(group_df)
    st.plotly_chart(fig_group, use_container_width=True)

    # 性别对比
    st.markdown("#### 不同性别压力对比")
    gender_data = []
    for gender in ["男", "女"]:
        subset = df[df["gender"] == gender]
        scores = []
        for _, row in subset.iterrows():
            r = cps(
                homework_hours=row["homework_hours"],
                exam_frequency=row["exam_frequency"],
                grade_variance=row["grade_variance"],
                tutoring_count=row["tutoring_count"],
                sleep_hours=row["sleep_hours"],
                sleep_quality=row["sleep_quality"],
                exercise_freq=row["exercise_freq"],
                conflict_count=row["conflict_count"],
                parent_criticism=row["parent_criticism"],
                social_media_hours=row["social_media_hours"],
                loneliness_score=row["loneliness_score"],
            )
            scores.append(r)
        if scores:
            avg_study = np.mean([s["study_pressure"] for s in scores])
            avg_phys = np.mean([s["physical_state"] for s in scores])
            avg_social = np.mean([s["social_feedback"] for s in scores])
            gender_data.append(
                {
                    "group": gender,
                    "study": avg_study,
                    "physical": avg_phys,
                    "social": avg_social,
                }
            )

    gender_df = pd.DataFrame(gender_data)
    fig_gender = plot_group_comparison(gender_df)
    st.plotly_chart(fig_gender, use_container_width=True)

    # 桑基图
    st.markdown("#### 🔄 压力能量流向图")
    avg_study = np.mean(
        [
            s["study_pressure"]
            for s in [
                cps(**{k: v for k, v in row.items() if k not in ["grade", "gender"]})
                for _, row in df.iterrows()
            ]
        ]
    )
    avg_phys = np.mean(
        [
            s["physical_state"]
            for s in [
                cps(**{k: v for k, v in row.items() if k not in ["grade", "gender"]})
                for _, row in df.iterrows()
            ]
        ]
    )
    avg_social = np.mean(
        [
            s["social_feedback"]
            for s in [
                cps(**{k: v for k, v in row.items() if k not in ["grade", "gender"]})
                for _, row in df.iterrows()
            ]
        ]
    )

    fig_sankey = plot_sankey(
        avg_study, avg_phys, avg_social, avg_study + avg_phys + avg_social
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    # 原始数据
    with st.expander("📋 查看原始数据"):
        st.dataframe(df.round(2), use_container_width=True)


# ---------- Tab 3: 情绪日记 ----------
with tab3:
    st.subheader("📖 情绪日记")

    st.markdown("记录你每天的压力值，追踪情绪变化趋势。")

    if st.button("✨ 载入示例日记（演示用）"):
        seeded = seed_sample_diary()
        if seeded:
            st.success("✅ 已载入两周示例日记！")
        else:
            st.info("示例日记已存在，未重复载入。")
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
        fig_diary = plot_pressure_trend(diary)
        if fig_diary:
            st.plotly_chart(fig_diary, use_container_width=True)

        with st.expander("📋 查看所有记录"):
            for entry in reversed(diary):
                level = get_pressure_level(entry["score"])
                st.markdown(
                    f"- **{entry['date']}** | 压力指数: **{entry['score']}** {level['emoji']} {level['level']} | {entry.get('note', '')}"
                )

        if st.button("🗑️ 清空所有记录"):
            clear_diary()
            st.rerun()
    else:
        st.info("还没有记录，快来写第一条吧！")


# ---------- Tab 4: 减压推荐 ----------
with tab4:
    st.subheader("💡 个性化减压方案")

    st.markdown(
        f"""
    <div style="background: {color}22; border-radius: 15px; padding: 25px; border: 2px solid {color};">
        <h3 style="color: {color};">🎵 推荐音乐</h3>
        <p style="font-size: 16px;">{level_info["audio"]}</p>

        <h3 style="color: {color}; margin-top: 15px;">🧘 推荐活动</h3>
        <p style="font-size: 16px;">{level_info["activity"]}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 呼吸引导
    st.markdown("#### 🫁 呼吸引导")
    breath = get_breath_animation_params(score)
    st.markdown(
        f"""
    <div style="background: #23232C; border-radius: 15px; padding: 25px; text-align: center;">
        <div class="breath-circle" style="background: {color}; color: white; margin: 10px auto;">
            🫁
        </div>
        <p style="font-size: 18px; font-weight: bold;">
            {"吸气 " + str(breath["inhale"]) + "秒 → 屏息 " + str(breath.get("hold", 0)) + "秒 → 呼气 " + str(breath["exhale"]) + "秒" if breath.get("hold", 0) > 0 else "吸气 " + str(breath["inhale"]) + "秒 → 呼气 " + str(breath["exhale"]) + "秒"}
        </p>
        <p>重复 {breath["cycles"]} 个循环</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 色彩心理学
    st.markdown("#### 🎨 色彩心理学解读")
    for level_name, info in PRESSURE_COLOR_MAP.items():
        st.markdown(
            f"""
        <div style="background: {info["color"]}15; border-left: 4px solid {info["color"]}; padding: 10px 15px; margin: 5px 0; border-radius: 5px;">
            <strong style="color: {info["color"]};">{level_name}</strong> —
            <span style="color: {info["color"]};">■</span> {info["color_name"]}（{info["emotion"]}）
            <br>🎵 {info["audio"]} | 🏃 {info["activity"]} | 🫁 {info["breath_pattern"]}
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("""
    > 💚 **温馨提示**：本工具仅用于压力自测和情绪记录，**不能替代专业心理诊断**。
    > 如果您感到持续痛苦，请务必寻求专业心理咨询师的帮助。
    """)


# ============ 页脚 ============
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #B8B8C4; font-size: 0.85rem; padding: 10px;">
    🌈 情绪避风港 — 青少年情绪可视化实验室<br>
    压力不是弱点，而是需要被理解的信号
</div>
""",
    unsafe_allow_html=True,
)
