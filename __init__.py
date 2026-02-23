import random
import aiohttp
from pathlib import Path
from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.bot import Bot
from gsuid_core.logger import logger

VOICE_ROOT = Path(__file__).parent / "resources" / "record"
VOICE_ROOT.mkdir(parents=True, exist_ok=True)

sv = SV("全局语音")

@sv.on_message()
async def voice_reply_handler(bot: Bot, event: Event):
    msg = event.text.strip()
    if not msg:
        return

    target_dir = VOICE_ROOT / msg
    if not target_dir.exists() or not target_dir.is_dir():
        return

    files = [f for f in target_dir.iterdir() if f.is_file()]
    if not files:
        return

    chosen = random.choice(files)

    voice_seg = {
        "type": "record",
        "data": {"file": chosen.absolute().as_uri()}
    }

    logger.info(f"[DEBUG] 准备发送语音，文件URI: {chosen.absolute().as_uri()}")

    # 直接调用 NapCat HTTP API
    api_url = "http://127.0.0.1:5700/send_private_msg" if event.user_type == "direct" else "http://127.0.0.1:5700/send_group_msg"
    params = {
        "user_id": event.user_id if event.user_type == "direct" else None,
        "group_id": event.group_id if event.user_type != "direct" else None,
        "message": [voice_seg]
    }
    params = {k: v for k, v in params.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=params) as resp:
            if resp.status == 200:
                result = await resp.json()
                if result.get("status") == "ok":
                    logger.info("[DEBUG] 语音发送成功")
                else:
                    logger.error(f"[DEBUG] 语音发送失败，API返回: {result}")
            else:
                logger.error(f"[DEBUG] 语音发送失败，HTTP状态码: {resp.status}")