# 🌈 净化 — 青少年情绪可视化实验室

> Turn invisible emotions into visible colors

## 🎯 项目简介

将无形的压力转化为可视化的数据和艺术表达，帮助青少年认识、理解和管理自己的压力。

项目以 **AI 情绪陪伴** 作为系统入口：先倾听青少年的情绪表达，再由 AI 共情、推荐音乐与呼吸冥想，最后进入压力分析 Dashboard。

## 📁 项目结构

```
emotion-lab/
├── app.py                  # Streamlit 主应用（启动入口 + 欢迎页门禁）
├── pressure_model.py       # 压力指数计算模型（三维度加权）
├── visualization.py        # 图表生成（曲线/饼图/柱状图/桑基图）
├── color_mapping.py        # 压力-色彩映射系统
├── data_utils.py           # 示例数据生成与情绪日记工具
├── theme.py                # 深色/浅色主题管理
├── ui.py                   # 自定义 HTML 卡片与组件
├── solutions.py            # 本地关键词降级推荐引擎
├── ai_companion.py         # AI 情绪陪伴调用层（智谱 GLM / Kimi / Gemini）
├── music_library.py        # 固定音乐曲库
├── data/
│   ├── sample_data.csv     # 模拟问卷数据（运行后自动生成）
│   └── diary.json          # 情绪日记（运行后自动生成）
├── requirements.txt        # Python 依赖清单
└── README.md               # 本文件
```

> 说明：`recode.md`、`welcome_page_req.md` 为开发规划文档，不纳入运行结构。

## 🚀 快速开始

### 环境准备

```bash
# 1. 创建并激活虚拟环境（可选但推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
streamlit run app.py
```

浏览器访问 http://localhost:8501

### 配置 AI（可选）

AI 调用支持通过 **环境变量** 或 **`.env` 文件**（依赖 `python-dotenv`）注入 Key，也可在应用内 `⚙️ AI 设置` 中临时粘贴：

```bash
# .env 示例
ZHIPU_API_KEY=你的智谱Key
KIMI_API_KEY=你的KimiKey
GEMINI_API_KEY=你的GeminiKey
```

未配置 Key 时，系统自动降级为本地关键词陪伴方案，功能仍可正常使用。

## 🧪 功能模块

| 模块 | 功能 |
|------|------|
| 🌈 欢迎页 | AI 情绪陪伴：表达→共情→音乐→呼吸/冥想→情绪渐变 |
| 🏠 仪表盘 | 压力指数展示、一周波动预测、来源分布 |
| 📊 数据分析 | 年级/性别对比、桑基图能量流向 |
| 📖 情绪日记 | 记录每日压力值、趋势追踪 |
| 💡 减压推荐 | 个性化音乐/活动推荐、呼吸引导、心理援助热线 |

## 🤖 AI 情绪陪伴（系统入口）

打开应用首先进入 **AI 情绪陪伴** 欢迎页，遵循心理咨询的"表达→共情→干预→评估"流程：

> 表达情绪 → AI 共情 → 音乐疗愈 → 呼吸/冥想 → 压力分析

- 💬 **表达**：写下今天发生的事情或情绪
- 💙 **AI 共情**：模型识别情绪并生成温柔、非评判的安慰话语
- 🎵 **音乐疗愈**：从固定曲库（父母冲突 / 挫折 / 孤独 / 焦虑 / 伤心 / 开心）中匹配最合适的歌曲
- 🌬 **呼吸 & 🧘 冥想**：跟随 AI 建议的呼吸节奏放松
- 🎨 **情绪渐变**：AI 为情绪生成专属颜色，整页背景与呼吸圆圈缓慢过渡到该色
- 📊 完成后进入压力分析 Dashboard

### 接入 AI（可选）

支持 **智谱 GLM / Kimi / Gemini**（均兼容 OpenAI 协议），三选一：

1. **运行时 UI 输入**：欢迎页底部 `⚙️ AI 设置` → 选择模型 → 粘贴 API Key（仅存于当前会话，不写入磁盘）
2. **环境变量 / `.env` 文件**：`ZHIPU_API_KEY` / `KIMI_API_KEY` / `GEMINI_API_KEY`
3. **未配置时**：自动降级为本地关键词陪伴方案，功能仍可正常使用

> 所有推荐均为情绪陪伴建议，不构成心理诊断或治疗承诺。

## 📊 压力测评

支持两种模式：
- **快速测评**（3题）：睡眠、心情、压力感
- **详细测评**（11题）：学习压力、生理状态、社交反馈三维度

## 🎨 压力色彩映射

| 压力等级 | 分值范围 | 色彩 | 含义 |
|----------|----------|------|------|
| 轻松状态 | 0-30 | 🟢 青绿色 | 平静 |
| 适度压力 | 31-60 | 🟡 明黄色 | 温暖 |
| 高压力 | 61-85 | 🟠 珊瑚红 | 警示 |
| 超负荷 | 86-100 | 🔴 紫色 | 深度疗愈 |

## 🛠 主要依赖

- `streamlit` — Web 应用框架
- `plotly` / `matplotlib` — 数据可视化
- `pandas` / `numpy` — 数据处理
- `openai` — AI 情绪陪伴调用（智谱/Kimi/Gemini 统一协议）
- `python-dotenv` — 读取 `.env` 中的 API Key

## ⚠️ 免责声明

本工具仅用于压力自测和情绪记录，**不能替代专业心理诊断或治疗**。如果您或身边的人感到持续痛苦，请务必寻求专业心理咨询师或拨打心理援助热线的帮助。
