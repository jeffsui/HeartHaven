"""
实际问卷数据与数据工具

`data/sample_data.csv` 为实际问卷数据，字段固定为：
    性别,睡眠时长,压力指数1,压力指数2,压力指数3,平均值,情绪波动原因
本模块只读取该文件并做类型规范化，不再生成或覆盖模拟数据。
"""

import json
import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SAMPLE_CSV = os.path.join(DATA_DIR, "sample_data.csv")
DIARY_JSON = os.path.join(DATA_DIR, "diary.json")

COL_GENDER = "性别"
COL_SLEEP = "睡眠时长"
INDEX_COLS = ["压力指数1", "压力指数2", "压力指数3"]
COL_AVG = "平均值"
COL_REASON = "情绪波动原因"
COL_SLEEP_HOURS = "睡眠小时数"  # 派生列：从 "7 hours" 中解析出的数值

RAW_COLUMNS = [COL_GENDER, COL_SLEEP, *INDEX_COLS, COL_AVG, COL_REASON]


def split_reasons(value) -> list:
    """把 "grade, family" 之类的单元格拆成原因标签列表。"""
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def reason_options(df: pd.DataFrame) -> list:
    """按出现频次返回数据中全部原因标签，供录入表单使用。"""
    counts = {}
    for value in df.get(COL_REASON, pd.Series(dtype=str)):
        for reason in split_reasons(value):
            counts[reason] = counts.get(reason, 0) + 1
    return sorted(counts, key=lambda r: (-counts[r], r))


def load_sample_data() -> pd.DataFrame:
    """加载实际问卷数据（只读，不生成/覆盖 CSV）。

    返回保留原始 7 列的数据框，并附加数值列 `睡眠小时数`；
    三次压力指数与平均值统一转为 float，便于统计和绘图。
    文件缺失时返回空数据框，由调用方给出提示。
    """
    if not os.path.exists(SAMPLE_CSV):
        return pd.DataFrame(columns=[*RAW_COLUMNS, COL_SLEEP_HOURS])

    df = pd.read_csv(SAMPLE_CSV, encoding="utf-8-sig")

    missing = [c for c in RAW_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{SAMPLE_CSV} 缺少字段：{', '.join(missing)}")

    for col in [*INDEX_COLS, COL_AVG]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 平均值缺失时用三次压力指数的平均回填
    df[COL_AVG] = df[COL_AVG].fillna(df[INDEX_COLS].mean(axis=1)).round(1)

    df[COL_SLEEP_HOURS] = (
        df[COL_SLEEP]
        .astype(str)
        .str.extract(r"(\d+(?:\.\d+)?)", expand=False)
        .astype(float)
    )
    return df


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
