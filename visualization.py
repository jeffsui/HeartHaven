"""
数据可视化模块（重构版）

所有图表统一通过 apply_plotly_theme() / apply_matplotlib_theme() 应用主题，
绘图函数只接收 Theme 对象，不再各自判断 dark / light，整体减少大量重复代码。
"""

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from data_utils import (
    COL_AVG,
    COL_GENDER,
    COL_REASON,
    COL_SLEEP_HOURS,
    INDEX_COLS,
    split_reasons,
)
from theme import DARK, Theme

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 主题应用 ============
def apply_plotly_theme(fig, theme: Theme):
    """统一应用 Plotly 主题。"""
    fig.update_layout(
        template=theme.plotly_template,
        paper_bgcolor=theme.paper_bg,
        plot_bgcolor=theme.plot_bg,
        font=dict(color=theme.text),
    )
    return fig


def apply_matplotlib_theme(fig, ax, theme: Theme):
    """
    统一应用 Matplotlib 主题，返回文字相关颜色元组：
    (title, label, tick, grid, spine, leg_fg, leg_ec, leg_lc)
    """
    if theme.name == "dark":
        fig_bg, ax_bg = theme.bg, "#1C1C24"
        colors = (
            "#F2F2F5",
            "#E6E6EA",
            "#E6E6EA",
            "#555",
            "#444",
            "#1C1C24",
            "#444",
            "#E6E6EA",
        )
    else:
        fig_bg, ax_bg = theme.bg, "#F7F8FA"
        colors = (
            "#1A1A1F",
            "#2C2C34",
            "#2C2C34",
            "#CCCCCC",
            "#DDDDDD",
            "#F7F8FA",
            "#DDDDDD",
            "#2C2C34",
        )
    fig.patch.set_facecolor(fig_bg)
    ax.set_facecolor(ax_bg)
    return colors


# ============ 各图表 ============
def plot_pressure_wave(
    pressure_values: list,
    days: list = None,
    color: str = "#E8928C",
    theme: Theme = DARK,
    title: str = "📊 压力波段曲线",
    x_title: str = "测量次序",
):
    """生成压力波段曲线图（Plotly），可复用于一周数据或三次测量。"""
    if days is None:
        days = ["第1次", "第2次", "第3次"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=days,
            y=pressure_values,
            mode="lines+markers+text",
            line=dict(color=color, width=3),
            marker=dict(size=10, color=color),
            text=[f"{v:.0f}" for v in pressure_values],
            textposition="top center",
            fill="tozeroy",
            fillcolor="rgba(232, 146, 140, 0.25)",
            hovertemplate="%{x}<br>压力指数: %{y:.0f}<extra></extra>",
            name="压力指数",
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18), x=0.5, xanchor="center"),
        title_x=0.5,
        xaxis=dict(title=x_title, tickmode="array", tickvals=days),
        yaxis=dict(title="压力指数", range=[0, 105]),
        shapes=[
            dict(
                type="rect",
                xref="paper",
                x0=0,
                x1=1,
                yref="y",
                y0=0,
                y1=30,
                fillcolor="#6FCFC4",
                opacity=0.10,
                line_width=0,
            ),
            dict(
                type="rect",
                xref="paper",
                x0=0,
                x1=1,
                yref="y",
                y0=30,
                y1=60,
                fillcolor="#E0C068",
                opacity=0.10,
                line_width=0,
            ),
            dict(
                type="rect",
                xref="paper",
                x0=0,
                x1=1,
                yref="y",
                y0=60,
                y1=85,
                fillcolor="#E8928C",
                opacity=0.10,
                line_width=0,
            ),
            dict(
                type="rect",
                xref="paper",
                x0=0,
                x1=1,
                yref="y",
                y0=85,
                y1=100,
                fillcolor="#B18BC9",
                opacity=0.10,
                line_width=0,
            ),
        ],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=30, t=70, b=40),
        height=420,
    )

    return apply_plotly_theme(fig, theme)


def plot_pressure_source_pie(
    study: float, physical: float, social: float, theme: Theme = DARK
):
    """生成压力来源饼图（Plotly 交互式）。"""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["学习压力", "生理状态", "社交反馈"],
                values=[study, physical, social],
                marker=dict(colors=["#E8928C", "#6FCFC4", "#E0C068"]),
                hole=0.45,
                textinfo="label+percent",
                textfont=dict(size=14),
                hovertemplate="%{label}<br>压力值: %{value:.1f}<br>占比: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=dict(text="🎯 压力来源分布", font=dict(size=18)),
        showlegend=True,
        height=400,
    )
    return apply_plotly_theme(fig, theme)


def plot_group_comparison(data: pd.DataFrame, theme: Theme = DARK):
    """生成群体对比柱状图。data 需包含列: group, study, physical, social。"""
    fig = go.Figure()
    categories = ["学习压力", "生理状态", "社交反馈"]
    colors = ["#E8928C", "#6FCFC4", "#E0C068"]

    for i, (cat, col) in enumerate(zip(categories, ["study", "physical", "social"])):
        fig.add_trace(
            go.Bar(
                name=cat,
                x=data["group"],
                y=data[col],
                marker_color=colors[i],
                text=data[col].round(1),
                textposition="outside",
            )
        )

    fig.update_layout(
        barmode="group",
        title=dict(text="📊 不同群体压力对比", font=dict(size=18)),
        yaxis=dict(title="压力指数", range=[0, 100]),
        height=400,
    )
    return apply_plotly_theme(fig, theme)


def plot_sankey(
    study: float, physical: float, social: float, total: float, theme: Theme = DARK
):
    """生成能量消耗桑基图（Sankey Diagram）。"""
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=20,
                    thickness=25,
                    line=dict(color="#666666", width=0.5),
                    label=[
                        "总压力",
                        "学习压力",
                        "生理状态",
                        "社交反馈",
                        "作业负担",
                        "考试焦虑",
                        "成绩波动",
                        "睡眠不足",
                        "缺乏运动",
                        "人际冲突",
                        "孤独感",
                    ],
                    color=[
                        "#9AA0A8",
                        "#E8928C",
                        "#6FCFC4",
                        "#E0C068",
                        "#E8A8A4",
                        "#E08C88",
                        "#D97873",
                        "#6FCFC4",
                        "#5BBDB2",
                        "#E0C068",
                        "#C9A84E",
                    ],
                ),
                link=dict(
                    source=[0, 0, 0, 1, 1, 1, 2, 2, 3, 3],
                    target=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    value=[
                        study,
                        physical,
                        social,
                        study * 0.4,
                        study * 0.35,
                        study * 0.25,
                        physical * 0.6,
                        physical * 0.4,
                        social * 0.5,
                        social * 0.5,
                    ],
                    color=[
                        "rgba(232,146,140,0.3)",
                        "rgba(111,207,196,0.3)",
                        "rgba(224,192,104,0.3)",
                        "rgba(232,168,164,0.4)",
                        "rgba(224,140,136,0.4)",
                        "rgba(217,120,115,0.4)",
                        "rgba(111,207,196,0.4)",
                        "rgba(91,189,178,0.4)",
                        "rgba(224,192,104,0.4)",
                        "rgba(201,168,78,0.4)",
                    ],
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(text="🔄 压力能量流向图", font=dict(size=18)),
        height=450,
    )
    return apply_plotly_theme(fig, theme)


def plot_pressure_trend(diary_data: list, theme: Theme = DARK):
    """生成情绪日记趋势图。diary_data: [{"date": "7/1", "score": 65}, ...]"""
    if not diary_data:
        return None

    df = pd.DataFrame(diary_data)
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["score"],
            mode="lines+markers",
            line=dict(width=3, color="#E8928C"),
            marker=dict(size=10),
            fill="tozeroy",
            fillcolor="rgba(232,146,140,0.15)",
            name="压力指数",
        )
    )

    # 添加阈值线
    fig.add_hline(y=30, line_dash="dash", line_color="#6FCFC4", annotation_text="轻松")
    fig.add_hline(y=60, line_dash="dash", line_color="#E0C068", annotation_text="适度")
    fig.add_hline(y=85, line_dash="dash", line_color="#B18BC9", annotation_text="高压")

    fig.update_layout(
        title=dict(text="📅 情绪日记趋势", font=dict(size=18)),
        yaxis=dict(title="压力指数", range=[0, 100]),
        height=350,
    )
    return apply_plotly_theme(fig, theme)


# ============ 实际问卷数据图表 ============
_PALETTE = ["#E8928C", "#6FCFC4", "#E0C068", "#B18BC9"]


def plot_gender_pressure(df: pd.DataFrame, theme: Theme = DARK):
    """按性别统计平均压力指数（标注各组样本数）。"""
    grouped = (
        df.groupby(COL_GENDER, dropna=True)[COL_AVG]
        .agg(["mean", "count"])
        .reset_index()
    )
    fig = go.Figure(
        go.Bar(
            x=grouped[COL_GENDER],
            y=grouped["mean"].round(1),
            marker_color=[_PALETTE[i % len(_PALETTE)] for i in range(len(grouped))],
            text=[
                f"{v:.1f}（n={int(n)}）"
                for v, n in zip(grouped["mean"], grouped["count"])
            ],
            textposition="outside",
            hovertemplate="性别: %{x}<br>平均压力指数: %{y:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="📊 不同性别平均压力对比", font=dict(size=18)),
        xaxis=dict(title="性别"),
        yaxis=dict(title="平均压力指数", range=[0, 100]),
        height=400,
    )
    return apply_plotly_theme(fig, theme)


def plot_sleep_vs_pressure(df: pd.DataFrame, theme: Theme = DARK):
    """睡眠时长与平均压力指数散点图（按性别着色，叠加线性趋势线）。"""
    fig = go.Figure()
    gender_colors = {"female": "#E8928C", "male": "#6FCFC4"}
    for gender, subset in df.groupby(COL_GENDER, dropna=True):
        label = str(gender)
        fig.add_trace(
            go.Scatter(
                x=subset[COL_SLEEP_HOURS],
                y=subset[COL_AVG],
                mode="markers",
                name=label,
                marker=dict(
                    size=11,
                    color=gender_colors.get(label, "#E0C068"),
                    opacity=0.85,
                    line=dict(width=1, color=theme.text),
                ),
                hovertemplate=(
                    f"性别: {label}<br>睡眠: %{{x:.1f}} 小时"
                    "<br>平均压力指数: %{y:.1f}<extra></extra>"
                ),
            )
        )

    valid = df[[COL_SLEEP_HOURS, COL_AVG]].dropna()
    if len(valid) >= 2 and valid[COL_SLEEP_HOURS].nunique() > 1:
        slope, intercept = np.polyfit(valid[COL_SLEEP_HOURS], valid[COL_AVG], 1)
        xs = np.linspace(
            valid[COL_SLEEP_HOURS].min(), valid[COL_SLEEP_HOURS].max(), 50
        )
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=slope * xs + intercept,
                mode="lines",
                name="整体趋势",
                line=dict(color="#E0C068", width=2, dash="dash"),
                hovertemplate="睡眠: %{x:.1f} 小时<br>趋势值: %{y:.1f}<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(text="😴 睡眠时长与压力指数关系", font=dict(size=18)),
        xaxis=dict(title="睡眠时长（小时）"),
        yaxis=dict(title="平均压力指数", range=[0, 100]),
        height=420,
    )
    return apply_plotly_theme(fig, theme)


def plot_index_fluctuation(df: pd.DataFrame, theme: Theme = DARK):
    """三次压力指数波动：每位样本一条淡线，叠加全体均值曲线。"""
    fig = go.Figure()
    for _, row in df.iterrows():
        values = [row[c] for c in INDEX_COLS]
        if any(pd.isna(v) for v in values):
            continue
        fig.add_trace(
            go.Scatter(
                x=INDEX_COLS,
                y=values,
                mode="lines+markers",
                line=dict(color="rgba(232,146,140,0.25)", width=1.5),
                marker=dict(size=4, color="rgba(232,146,140,0.35)"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    means = [df[c].mean() for c in INDEX_COLS]
    fig.add_trace(
        go.Scatter(
            x=INDEX_COLS,
            y=means,
            mode="lines+markers+text",
            line=dict(color="#6FCFC4", width=4),
            marker=dict(size=12, color="#6FCFC4"),
            text=[f"{v:.1f}" for v in means],
            textposition="top center",
            name="全体均值",
            hovertemplate="%{x}<br>全体均值: %{y:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="📈 三次压力指数波动", font=dict(size=18)),
        xaxis=dict(title="测量次序", tickmode="array", tickvals=INDEX_COLS),
        yaxis=dict(title="压力指数", range=[0, 105]),
        height=420,
    )
    return apply_plotly_theme(fig, theme)


def plot_reason_distribution(df: pd.DataFrame, theme: Theme = DARK):
    """情绪波动原因分布：拆分逗号分隔的多标签后按出现次数统计。"""
    counts = {}
    for value in df.get(COL_REASON, pd.Series(dtype=str)):
        for reason in split_reasons(value):
            counts[reason] = counts.get(reason, 0) + 1

    items = sorted(counts.items(), key=lambda kv: kv[1])
    fig = go.Figure(
        go.Bar(
            x=[c for _, c in items],
            y=[r for r, _ in items],
            orientation="h",
            marker_color="#E0C068",
            text=[c for _, c in items],
            textposition="outside",
            hovertemplate="%{y}<br>出现次数: %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="🎯 情绪波动原因分布", font=dict(size=18)),
        xaxis=dict(
            title="出现次数（一条记录可含多个原因）",
            range=[0, max(counts.values()) * 1.2 if counts else 1],
        ),
        yaxis=dict(title="原因标签"),
        height=420,
    )
    return apply_plotly_theme(fig, theme)


def plot_compare_with_samples(result: dict, df: pd.DataFrame, theme: Theme = DARK):
    """个人三次压力指数与综合值 vs 全体样本均值。"""
    labels = [*INDEX_COLS, "综合平均"]
    my_values = [*result["indices"], result["total_score"]]
    sample_values = (
        [df[c].mean() for c in INDEX_COLS] + [df[COL_AVG].mean()]
        if not df.empty
        else []
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="你的测评",
            x=labels,
            y=[round(v, 1) for v in my_values],
            marker_color="#E8928C",
            text=[f"{v:.1f}" for v in my_values],
            textposition="outside",
        )
    )
    if sample_values:
        fig.add_trace(
            go.Bar(
                name="样本均值",
                x=labels,
                y=[round(v, 1) for v in sample_values],
                marker_color="#6FCFC4",
                text=[f"{v:.1f}" for v in sample_values],
                textposition="outside",
            )
        )
    fig.update_layout(
        barmode="group",
        title=dict(text="🎯 你的压力指数 vs 样本均值", font=dict(size=18)),
        yaxis=dict(title="压力指数", range=[0, 105]),
        height=400,
    )
    return apply_plotly_theme(fig, theme)
