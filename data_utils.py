"""
示例数据与数据工具
"""

import pandas as pd
import numpy as np
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SAMPLE_CSV = os.path.join(DATA_DIR, "sample_data.csv")
DIARY_JSON = os.path.join(DATA_DIR, "diary.json")


def generate_sample_data(n: int = 80, seed: int = 42) -> pd.DataFrame:
    """
    生成模拟问卷数据（n位同学）。
    刻意覆盖四种压力等级，并形成清晰的年级/性别梯度，便于展示对比。
    注意：本数据由随机数生成，仅用于演示，不代表真实群体。
    """
    np.random.seed(seed)
    df = pd.DataFrame({
        "grade": np.random.choice(["初一", "初二", "初三"], n, p=[0.3, 0.35, 0.35]),
        "gender": np.random.choice(["男", "女"], n, p=[0.5, 0.5]),
        "homework_hours": np.random.normal(2.5, 1.0, n),
        "exam_frequency": np.random.normal(2.5, 1.2, n),
        "grade_variance": np.random.normal(4, 2, n),
        "tutoring_count": np.random.poisson(1.5, n).astype(float),
        "sleep_hours": np.random.normal(7, 1.2, n),
        "sleep_quality": np.random.normal(6, 2, n),
        "exercise_freq": np.random.poisson(2, n).astype(float),
        "conflict_count": np.random.poisson(1, n).astype(float),
        "parent_criticism": np.random.normal(2.5, 1, n),
        "social_media_hours": np.random.normal(2, 1.5, n),
        "loneliness_score": np.random.normal(4, 2, n),
    })

    # 年级梯度：初三学生压力更大
    m9 = df["grade"] == "初三"
    df.loc[m9, "homework_hours"] += 1.0
    df.loc[m9, "exam_frequency"] += 1.0
    df.loc[m9, "sleep_hours"] -= 0.8
    df.loc[m9, "loneliness_score"] += 0.8

    # 性别梯度（展示差异，非定论）
    mf = df["gender"] == "女"
    df.loc[mf, "loneliness_score"] += 0.5
    df.loc[mf, "parent_criticism"] += 0.3

    # 裁剪到合理范围
    clip = {
        "homework_hours": (0.5, 5), "exam_frequency": (0, 6), "grade_variance": (1, 10),
        "tutoring_count": (0, 5), "sleep_hours": (4, 11), "sleep_quality": (1, 10),
        "exercise_freq": (0, 7), "conflict_count": (0, 5), "parent_criticism": (1, 5),
        "social_media_hours": (0, 8), "loneliness_score": (1, 10),
    }
    for c, (lo, hi) in clip.items():
        df[c] = df[c].clip(lo, hi)

    # 注入少量极端样本，保证四档色彩都有展示
    extras = pd.DataFrame([
        # 轻松型（低频压力 0-30）
        {"grade": "初一", "gender": "男", "homework_hours": 1, "exam_frequency": 0.5,
         "grade_variance": 1.5, "tutoring_count": 0, "sleep_hours": 9, "sleep_quality": 9,
         "exercise_freq": 5, "conflict_count": 0, "parent_criticism": 1,
         "social_media_hours": 1, "loneliness_score": 1.5},
        # 高压力型（高频压力 61-85）
        {"grade": "初二", "gender": "女", "homework_hours": 4.5, "exam_frequency": 5,
         "grade_variance": 8, "tutoring_count": 3, "sleep_hours": 5, "sleep_quality": 3,
         "exercise_freq": 0, "conflict_count": 3, "parent_criticism": 4,
         "social_media_hours": 4, "loneliness_score": 7},
        # 超负荷型（超高频压力 86-100）
        {"grade": "初三", "gender": "女", "homework_hours": 5, "exam_frequency": 6,
         "grade_variance": 9, "tutoring_count": 4, "sleep_hours": 4.5, "sleep_quality": 2,
         "exercise_freq": 0, "conflict_count": 4, "parent_criticism": 5,
         "social_media_hours": 6, "loneliness_score": 9},
    ])
    df = pd.concat([df, extras], ignore_index=True)
    return df


def save_sample_data():
    """保存示例数据到CSV"""
    df = generate_sample_data()
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(SAMPLE_CSV, index=False, encoding="utf-8-sig")
    return SAMPLE_CSV


def load_sample_data() -> pd.DataFrame:
    """加载示例数据"""
    if not os.path.exists(SAMPLE_CSV):
        save_sample_data()
    return pd.read_csv(SAMPLE_CSV, encoding="utf-8-sig")


# 情绪日记工具
def load_diary() -> list:
    """加载情绪日记"""
    if os.path.exists(DIARY_JSON):
        with open(DIARY_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_diary_entry(date: str, score: float, note: str = ""):
    """保存一条日记"""
    diary = load_diary()
    diary.append({"date": date, "score": score, "note": note})
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DIARY_JSON, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=2)


def clear_diary():
    """清空日记"""
    if os.path.exists(DIARY_JSON):
        os.remove(DIARY_JSON)


def seed_sample_diary():
    """
    预置两周示例情绪日记（仅在为空时调用），便于演示趋势图。
    返回 True 表示本次新写入，False 表示已存在未覆盖。
    """
    if os.path.exists(DIARY_JSON):
        return False
    import datetime

    base = datetime.date(2026, 6, 29)
    pattern = [40, 52, 60, 68, 82, 45, 38, 44, 55, 63, 71, 88, 50, 42]
    notes = [
        "考试周，有点累", "", "和爸妈吵架了", "运动完舒服多了", "周五巅峰…",
        "周末放松", "睡了个好觉", "", "小测还行", "作业有点多",
        "朋友聚会开心", "压力爆表的一天", "调整呼吸后好些", "新的一周",
    ]
    diary = [
        {"date": str(base + datetime.timedelta(days=i)), "score": s, "note": notes[i]}
        for i, s in enumerate(pattern)
    ]
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DIARY_JSON, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=2)
    return True
