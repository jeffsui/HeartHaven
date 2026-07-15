"""
固定音乐曲库（情绪陪伴用）

AI 从本库中选择最适合用户当前情绪的歌曲，避免随意推荐。
注意：这些推荐仅作为情绪陪伴建议，不构成任何治疗或医学效果承诺。
"""

MUSIC_LIBRARY = {
    "与父母冲突": [
        {
            "name": "Mockingbird",
            "artist": "Eminem",
            "reason": "歌曲讲述父母与孩子之间复杂而真实的情感，很多人在这里找到共鸣。",
        }
    ],
    "遭遇挫折迷茫": [
        {
            "name": "Lose Yourself",
            "artist": "Eminem",
            "reason": "面对压力时不要放弃、抓住每一次机会，适合在低谷时给自己力量。",
        }
    ],
    "孤独": [
        {
            "name": "Fix You",
            "artist": "Coldplay",
            "reason": "温柔的旋律像在说“我会接住你”，适合感到孤单时被默默陪伴。",
        }
    ],
    "焦虑": [
        {
            "name": "Weightless",
            "artist": "Marconi Union",
            "reason": "常被提及具有舒缓放松效果的器乐，帮助平复紧绷的神经。",
        }
    ],
    "伤心": [
        {
            "name": "River Flows in You",
            "artist": "Yiruma",
            "reason": "纯净的钢琴曲，像安静的陪伴，适合难过时慢慢平复心情。",
        }
    ],
    "开心": [
        {
            "name": "Happy",
            "artist": "Pharrell Williams",
            "reason": "轻快明亮的节奏和好心情很搭，让快乐再多停留一会儿。",
        }
    ],
}


def get_music_list() -> list:
    """展平为列表，供 AI 选择（只暴露 name/artist/reason）。"""
    items = []
    for _cat, songs in MUSIC_LIBRARY.items():
        for s in songs:
            items.append(s)
    return items


def search_url(name: str, artist: str) -> str:
    """构造跳转到音乐平台搜索的链接（避免托管音频的版权问题）。"""
    from urllib.parse import quote

    q = quote(f"{artist} {name}")
    return f"https://music.163.com/#/search/m/?s={q}"
