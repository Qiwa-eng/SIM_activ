from ..loader import bot, CHANNEL_ID

BOT_NAME = ""

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status != "left"
    except Exception:
        return False

def main_menu_text(user_name: str) -> str:
    return f"<b>👋 {user_name}</b>, добро пожаловать в <b>«{BOT_NAME}»</b>"

async def fetch_bot_name() -> None:
    global BOT_NAME
    me = await bot.get_me()
    BOT_NAME = me.first_name
