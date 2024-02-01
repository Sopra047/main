import re, asyncio, os, sys
from pyrogram import Client, filters, enums
from pyrogram.types import *
from info import ADMINS

    
@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**🔄 Lᴇs ᴘʀᴏᴄᴇssᴜs sᴇ sᴏɴᴛ ᴀʀʀᴇ̂ᴛᴇ́s. Lᴇ ʀᴏʙᴏᴛ ʀᴇᴅᴇ́ᴍᴀʀʀᴇ...**", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("**✅️ ʟᴇ ʙᴏᴛ ᴇsᴛ ʀᴇᴅᴇ́ᴍᴀʀʀᴇ́. ᴍᴀɪɴᴛᴇɴᴀɴᴛ, ᴠᴏᴜs ᴘᴏᴜᴠᴇᴢ ᴍ’ᴜᴛɪʟɪsᴇʀ**")
    os.execl(sys.executable, sys.executable, *sys.argv)
