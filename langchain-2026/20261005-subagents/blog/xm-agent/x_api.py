"""数据源：twitterapi.io 的 /twitter/user/last_tweets 接口。

配了 `TWITTERAPI_IO_KEY` 就走真实 API，没配就走内置 mock —— demo 随时能跑起来。

这里刻意返回**未加工的原始 JSON**：一条推文十几个字段，几十条就是上万字符。
子代理的价值就是把这坨噪声压缩成一份摘要，主管的上下文里只留下摘要。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import requests

API_URL = "https://api.twitterapi.io/twitter/user/last_tweets"
TIMEOUT = 20

# X 的时间串形如 "Tue Dec 10 07:00:30 +0000 2024"。
# 不用 strftime 生成，避免系统 locale 把 %a/%b 输出成中文导致解析不一致。
_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _fmt_x_time(dt: datetime) -> str:
    return f"{_WEEKDAYS[dt.weekday()]} {_MONTHS[dt.month - 1]} {dt.day:02d} {dt:%H:%M:%S} +0000 {dt.year}"


def _parse_x_time(raw: str) -> datetime | None:
    try:
        return datetime.strptime(raw, "%a %b %d %H:%M:%S %z %Y")
    except (ValueError, TypeError):
        return None


# ===========================================================================
# 真实 API
# ===========================================================================


def _call_real_api(username: str) -> dict:
    """调 twitterapi.io，返回原始响应体（每页最多 20 条推文）。"""
    resp = requests.get(
        API_URL,
        params={"userName": username, "cursor": "", "includeReplies": "false"},
        headers={"X-API-Key": os.environ["TWITTERAPI_IO_KEY"]},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# ===========================================================================
# Mock 兜底 —— 结构、字段名与真实接口完全一致，只为让 demo 在没有 key 时也能跑
#    账号均为虚构，推文内容为演示数据，不代表任何真实人物或真实事件。
# ===========================================================================

_MOCK_ACCOUNTS: dict[str, dict] = {
    "nova_rocket": {
        "name": "Nova Rocket",
        "followers": 4_820_000,
        "bio": "可复用火箭 / 在轨制造，让上天变成日常通勤。",
        # (小时, 分钟, 正文, 点赞, 转发, 是否转推)
        "posts": [
            (9, 12, "第 12 次试飞定档本周五。这次要再抓一次助推器，目标复用第 3 回。", 41_200, 6_830, False),
            (11, 40, "猛禽 3 的室压又推高了一档，台架数据比预期干净。工程师们今天该加鸡腿。", 28_900, 4_120, False),
            (14, 5, "总有人问火星窗口期。答案是两年一次，但准备这件事一天都不能停。", 63_400, 11_500, False),
            (17, 33, "这个着陆段动画做得比我们官方的好，分享给大家。", 12_700, 3_040, True),
            (21, 48, "凌晨三点的控制室，比世界上任何地方都安静，也比任何地方都吵。", 88_100, 15_600, False),
            (10, 5, "昨天的回收船已经回到泊位，甲板上的灼痕就是最好的成绩单。", 33_500, 5_270, False),
            (19, 20, "招人：热防护、推进、飞控都在扩编，简历直接投。", 15_800, 2_310, False),
        ],
    },
    "quant_whale": {
        "name": "量化老鲸",
        "followers": 386_000,
        "bio": "只聊数据和概率，不聊信仰。所有内容不构成投资建议。",
        "posts": [
            (8, 5, "早盘：两市缩量高开，量能没跟上的高开基本都是陷阱，别追。", 9_450, 1_820, False),
            (10, 22, "上午的横盘是在等下午的会议纪要。两点半是分水岭，别提前站队。", 7_310, 1_260, False),
            (15, 40, "收盘复盘：指数微跌，但涨停家数比昨天多了 9 家，情绪其实在修复。", 11_200, 2_450, False),
            (18, 12, "今晚会写一篇关于仓位管理的长文，讲我为什么永远不满仓。", 6_820, 980, False),
            (22, 30, "今天最大的收获不是赚了多少，是又一次没在开盘十分钟里手痒。", 14_600, 2_110, False),
            (9, 30, "转发一份我认同的仓位表，原作者做了很扎实的回测。", 4_100, 890, True),
        ],
    },
}


def _mock_tweets(username: str) -> dict:
    """按账号名生成一份结构合法的假数据；未预置的账号走通用模板。"""
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    spec = _MOCK_ACCOUNTS.get(username.lower())
    if spec is None:
        spec = {
            "name": username,
            "followers": 12_400,
            "bio": "演示账号。",
            "posts": [
                (9, 5, f"这是 {username} 的演示推文，用来占位。", 320, 45, False),
                (13, 26, "第二条演示推文，结构与其他账号完全一致。", 180, 22, False),
                (20, 41, "第三条演示推文，方便观察汇总效果。", 96, 11, False),
                (11, 15, "这条是昨天的，应当被子代理过滤掉。", 240, 30, False),
            ],
        }

    tweets = []
    for idx, (hour, minute, text, likes, reposts, is_repost) in enumerate(spec["posts"]):
        # 最后一条故意放到昨天，用来验证「只取当天」这个要求真的被执行了
        day_offset = -1 if idx == len(spec["posts"]) - 1 else 0
        created = today + timedelta(days=day_offset, hours=hour, minutes=minute)
        tweet_id = f"{1_910_000_000_000_000_000 + idx * 7_919_311}"
        tweets.append(
            {
                "type": "tweet",
                "id": tweet_id,
                "url": f"https://x.com/{username}/status/{tweet_id}",
                "text": text,
                "source": "Twitter for iPhone",
                "retweetCount": reposts,
                "replyCount": likes // 37,
                "likeCount": likes,
                "quoteCount": reposts // 21,
                "viewCount": likes * 31,
                "bookmarkCount": likes // 12,
                "createdAt": _fmt_x_time(created),
                "lang": "zh",
                "isReply": False,
                "inReplyToId": "",
                "conversationId": tweet_id,
                "inReplyToUserId": "",
                "inReplyToUsername": "",
                "isLimitedReply": False,
                # 转推用 retweeted_tweet 非空表示，接口里没有 isRetweet 字段
                "retweeted_tweet": (
                    {
                        "type": "tweet",
                        "id": f"{tweet_id}0",
                        "text": "（被转推的原帖内容）",
                        "createdAt": _fmt_x_time(created - timedelta(hours=3)),
                        "likeCount": 2_100,
                        "retweetCount": 340,
                        "author": {"type": "user", "userName": "someone_else", "name": "Someone Else"},
                    }
                    if is_repost
                    else None
                ),
                "author": {
                    "type": "user",
                    "userName": username,
                    "name": spec["name"],
                    "id": "100000001",
                    "description": spec["bio"],
                    "followers": spec["followers"],
                    "following": 410,
                    "isBlueVerified": True,
                    "profilePicture": f"https://pbs.twimg.com/profile_images/{username}.jpg",
                },
            }
        )

    return {
        "tweets": tweets,
        "has_next_page": False,
        "next_cursor": "",
        "status": "success",
        "message": "",
    }


# ===========================================================================
# 工具入口
# ===========================================================================


def _normalize_username(raw: str) -> str:
    """把用户各种粘贴姿势归一成裸 handle。

    界面上看到的 "Serenity" 是昵称，接口只认 @ 后面那串，所以下面几种写法
    都要能认出来：
        @aleabitoreddit
        aleabitoreddit
        x.com/aleabitoreddit
        https://x.com/aleabitoreddit/status/1910...
    """
    name = (raw or "").strip()
    if "://" in name or name.startswith(("x.com/", "twitter.com/")):
        name = urlparse(name if "://" in name else "https://" + name).path
    name = name.strip("/")
    if "/" in name:
        name = name.split("/")[0]  # 状态链接 /handle/status/123 -> handle
    return name.lstrip("@").strip()


def fetch_user_tweets(username: str) -> str:
    """拉取某个 X 账号最近发布的推文，返回原始 JSON。

    Args:
        username: 账号的 handle，即 @ 后面那一串，例如 aleabitoreddit。
    """
    username = _normalize_username(username)
    if not username:
        return "[参数错误] 账号名不能为空"

    live = bool(os.environ.get("TWITTERAPI_IO_KEY"))
    try:
        payload = _call_real_api(username) if live else _mock_tweets(username)
    except Exception as exc:  # noqa: BLE001 —— 网络/额度问题不该让整个 demo 崩掉
        return f"[数据源异常] 拉取 {username} 失败：{type(exc).__name__}: {exc}"

    if payload.get("status") == "error":
        return f"[数据源错误] {payload.get('message', '未知错误')}"

    now_utc = datetime.now(timezone.utc)
    tweets = payload.get("tweets") or []
    # 给每条打上 is_today 标记，子代理就不必自己去算日期了
    for tweet in tweets:
        created = _parse_x_time(tweet.get("createdAt", ""))
        tweet["is_today"] = bool(created) and created.date() == now_utc.date()

    header = (
        f"[数据来源: {'twitterapi.io 实时接口' if live else 'mock 演示数据（未配置 TWITTERAPI_IO_KEY）'}]\n"
        f"[账号: @{username}] [今天(UTC): {now_utc.date().isoformat()}] [共返回 {len(tweets)} 条]\n"
    )
    return header + json.dumps(payload, ensure_ascii=False, indent=2)
