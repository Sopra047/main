from googletrans import Translator
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from plugins.helpers.list import list

@Client.on_message(filters.command(["tr"]))
async def left(client,message):
	if (message.reply_to_message):
		try:
			lgcd = message.text.split("/tr")
			lg_cd = lgcd[1].lower().replace(" ", "")
			tr_text = message.reply_to_message.text
			translator = Translator()
			translation = translator.translate(tr_text,dest = lg_cd)
			hehek = InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            text=f"Lᴇs ᴄᴏᴅᴇs Lᴀɴɢᴜᴇs", url="https://cloud.google.com/translate/docs/languages"
                                        )
                                    ],
				    [
                                        InlineKeyboardButton(
                                            "Fᴇʀᴍᴇʀ", callback_data="close_data"
                                        )
                                    ],
                                ]
                            )
			try:
				for i in list:
					if list[i]==translation.src:
						fromt = i
					if list[i] == translation.dest:
						to = i 
				await message.reply_text(f"Trᥲdᥙιt dᥱ {fromt.capitalize()} ɑ̀ {to.capitalize()}\n\n```{translation.text}```", reply_markup=hehek, quote=True)
			except:
			   	await message.reply_text(f"Trɑduit de **{translation.src}** ɑ̀ **{translation.dest}**\n\n```{translation.text}```", reply_markup=hehek, quote=True)
			

		except :
			print("error")
	else:
			 ms = await message.reply_text("𝖴𝗍𝗂𝗅𝗂𝗌𝖾𝗋 𝖼𝖾𝗍𝗍𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝖾 𝖾𝗇 𝖱𝖾́𝗉𝗈𝗇𝖽𝗋𝖾 𝖺̀ 𝗎𝗇 𝗆𝖾𝗌𝗌𝖺𝗀𝖾")
			 await ms.delete()
