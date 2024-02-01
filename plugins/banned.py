from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import SUPPORT_CHAT

async def banned_users(_, client, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)

async def disabled_chat(_, client, message: Message):
    return message.chat.id in temp.BANNED_CHATS

disabled_group=filters.create(disabled_chat)


@Client.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    ban = await db.get_ban_status(message.from_user.id)
    await message.reply(f'Désolé😥, Tu es interdit de m’utiliser. \nBan Reason: {ban["ban_reason"]}')

@Client.on_message(filters.group & disabled_group & filters.incoming)
async def grp_bd(bot, message):
    buttons = [[
        InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
    ]]
    reply_markup=InlineKeyboardMarkup(buttons)
    vazha = await db.get_chat(message.chat.id)
    k = await message.reply(
        text=f"CHAT NON AUTORISÉ 🐞 🐞\n\n𝖬𝗈𝗇 𝖺𝖽𝗆𝗂𝗇𝗂𝗌𝗍𝗋𝖺𝗍𝖾𝗎𝗋 𝗆’𝖺 𝗂𝗇𝗍𝖾𝗋𝖽𝗂𝗍 𝖽𝖾 𝗍𝗋𝖺𝗏𝖺𝗂𝗅𝗅𝖾𝗋 𝗂𝖼𝗂 ! 𝖲𝗂 𝗏𝗈𝗎𝗌 𝗏𝗈𝗎𝗅𝖾𝗓 𝖾𝗇 𝗌𝖺𝗏𝗈𝗂𝗋 𝗉𝗅𝗎𝗌, 𝖼𝗈𝗇𝗍𝖺𝖼𝗍𝖾𝗓 𝗅𝖾 𝗌𝗎𝗉𝗉𝗈𝗋𝗍...\nRaison : <code>{vazha['reason']}</code>.",
        reply_markup=reply_markup)
    try:
        await k.pin()
    except:
        pass
    await bot.leave_chat(message.chat.id)
