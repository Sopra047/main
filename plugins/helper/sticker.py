#Made
#by
#Don_Sflix

from pyrogram import Client, filters

@Client.on_message(filters.command(["stickerid"]))
async def stickerid(bot, message):   
    if message.reply_to_message.sticker:
       await message.reply(f"**L’ID de l’ɑutocollɑnt est**  \n `{message.reply_to_message.sticker.file_id}` \n \n ** L’identifiɑnt unique est ** \n\n`{message.reply_to_message.sticker.file_unique_id}`", quote=True)
    else: 
       await message.reply("<b>Oups!! Il ne s’ɑgit pɑs d’un fichieɾ d’ɑutocollɑnts</b>")
