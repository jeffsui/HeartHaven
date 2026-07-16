"""
AI 情绪陪伴调用层

支持 智谱 GLM / Kimi / Gemini 三家（均兼容 OpenAI 协议，统一用 openai 客户端）。
API Key 优先从 session_state 读取（用户在 UI 输入），其次环境变量。
无 Key 或调用失败时，降级到本地关键词方案（solutions 模块），保证页面不崩。
"""

import json
import os

import streamlit as st

try:
    from openai import OpenAI
except Exception:  # 未安装时也能导入本模块（降级路径不依赖）
    OpenAI = None

from music_library import get_music_list

PROVIDERS = {
    "智谱 GLM": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-4-flash",
    },
    "Kimi": {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
    },
    "Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-1.5-flash",
    },
}

_MUSIC_TEXT = "\n".join(f"- {m['name']} — {m['artist']}" for m in get_music_list())

SYSTEM_PROMPT = f"""你是一个温柔、支持性、非评判的青少年情绪陪伴助手。
用户会分享今天发生的事情或情绪。请你：
1. 识别用户的核心情绪（emotion，中文词，如 焦虑/孤独/委屈/开心/希望）。
2. 给出一句共情安慰（comfort，2-4 句，温柔、不评判，不要声称能诊断或治疗）。
3. 从给定曲库中选择一首最合适的歌（必须来自曲库，返回 name/artist/reason）。
4. 给出一个适合该情绪氛围的颜色（color，十六进制，如 #758AA2）。
5. 给出一个情绪强度分数（emotion_score，0-100 整数）。
6. 给出呼吸训练模式（breathing，如 "478" 表示吸气4屏息7呼气8）和冥想建议（meditation，如 "3分钟正念呼吸"）。

只输出如下 JSON，不要任何额外文字：
{{
  "emotion": "焦虑",
  "emotion_score": 82,
  "comfort": "……",
  "music": {{"name": "……", "artist": "……", "reason": "……"}},
  "color": "#758AA2",
  "breathing": "478",
  "meditation": "3分钟正念呼吸"
}}

曲库（music.name 只能从中选择）：
{_MUSIC_TEXT}
"""


def get_api_key(provider: str) -> str:
    """优先 session_state（UI 输入），其次环境变量。"""
    ss_key = f"api_key_{provider}"
    if ss_key in st.session_state and st.session_state[ss_key]:
        return st.session_state[ss_key]
    env_map = {
        "智谱 GLM": "ZHIPU_API_KEY",
        "Kimi": "KIMI_API_KEY",
        "Gemini": "GEMINI_API_KEY",
    }
    return os.getenv(env_map.get(provider, ""), "")


def _fallback(user_text: str) -> dict:
    """本地降级：无 AI 时给一个稳妥结果。"""
    from solutions import recommend_solutions

    sols = recommend_solutions(user_text)
    return {
        "emotion": "未知",
        "emotion_score": 50,
        "comfort": "我听到了你的分享。无论今天发生了什么，你的感受都是真实且重要的。"
        "先给自己一点时间，慢慢来，好吗？",
        "music": {
            "name": "Weightless",
            "artist": "Marconi Union",
            "reason": "一首常被提及能帮助放松的器乐，希望陪你安静下来。",
        },
        "color": "#6FCFC4",
        "breathing": "478",
        "meditation": "3分钟正念呼吸",
        "fallback": True,
        "solutions": sols,
    }


def generate_companion(user_text: str, provider: str = "智谱 GLM") -> dict:
    """调用 AI 生成情绪陪伴结果；失败或缺失 Key 时降级到本地方案。"""
    if not user_text or not user_text.strip():
        return _fallback(user_text or "")

    api_key = get_api_key(provider)
    if not api_key or OpenAI is None:
        return _fallback(user_text)

    try:
        client = OpenAI(api_key=api_key, base_url=PROVIDERS[provider]["base_url"])
        resp = client.chat.completions.create(
            model=PROVIDERS[provider]["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.8,
            response_format={"type": "json_object"},
            timeout=30,
        )
        data = json.loads(resp.choices[0].message.content)
        if not data.get("music", {}).get("name"):
            return _fallback(user_text)
        data.setdefault("color", "#6FCFC4")
        data.setdefault("breathing", "478")
        data.setdefault("meditation", "3分钟正念呼吸")
        return data
    except Exception:
        return _fallback(user_text)
