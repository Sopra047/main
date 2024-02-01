import os
import pyrogram
import PyPDF2
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import User, Message, Document 
from gtts import gTTS
from info import DOWNLOAD_LOCATION
  
Thanks = """ 𝖢’𝖾𝗌𝗍 𝗅𝖺 𝖿𝗂𝗇 𝖽𝖾 𝗏𝗈𝗍𝗋𝖾 𝗅𝗂𝗏𝗋𝖾 𝖺𝗎𝖽𝗂𝗈, 𝖤𝗍 𝗆𝖾𝗋𝖼𝗂 𝖽’𝗎𝗍𝗂𝗅𝗂𝗌𝖾𝗋 𝖼𝖾 𝗌𝖾𝗋𝗏𝗂𝖼𝖾"""

@Client.on_message(filters.command(["audiobook"])) # PdfToText 
async def pdf_to_text(bot, message):
 try:
           if message.reply_to_message:
                pdf_path = DOWNLOAD_LOCATION + f"{message.chat.id}.pdf" #pdfFileObject
                txt = await message.reply("𝖳𝖾́𝗅𝖾́𝖼𝗁𝖺𝗋𝗀𝖾𝗆𝖾𝗇𝗍.....")
                await message.reply_to_message.download(pdf_path)  
                await txt.edit("Downloaded File")
                pdf = open(pdf_path,'rb')
                pdf_reader = PyPDF2.PdfFileReader(pdf) #pdfReaderObject
                await txt.edit("𝖮𝖻𝗍𝖾𝗇𝗍𝗂𝗈𝗇 𝖽𝗎 𝗇𝗈𝗆𝖻𝗋𝖾 𝖽𝖾 𝗉𝖺𝗀𝖾𝗌....")
                num_of_pages = pdf_reader.getNumPages() # Number of Pages               
                await txt.edit(f"Found {num_of_pages} Page")
                page_no = pdf_reader.getPage(0) # pageObject
                await txt.edit("𝖱𝖾𝖼𝗁𝖾𝗋𝖼𝗁𝖾 𝖽𝖾 𝗍𝖾𝗑𝗍𝖾 𝖺̀ 𝗉𝖺𝗋𝗍𝗂𝗋 𝖽𝗎 𝖿𝗂𝖼𝗁𝗂𝖾𝗋 𝖯𝖣𝖥... ")
                page_content = """ """ # EmptyString   
                chat_id = message.chat.id
                with open(f'{message.chat.id}.txt', 'a+') as text_path:   
                  for page in range (0,num_of_pages):              
                      page_no = pdf_reader.getPage(page) # Iteration of page number
                      page_content += page_no.extractText()
                await txt.edit(f"𝖢𝗋𝖾́𝖺𝗍𝗂𝗈𝗇 𝖽𝖾 𝗏𝗈𝗍𝗋𝖾 𝗅𝗂𝗏𝗋𝖾 𝖺𝗎𝖽𝗂𝗈...\n 𝖲’𝗂𝗅 𝗏𝗈𝗎𝗌 𝗉𝗅𝖺𝗂̂𝗍, 𝗇𝖾 𝖿𝖺𝗂𝗍𝖾𝗌 𝗉𝗅𝗎𝗌 𝗋𝗂𝖾𝗇")
                output_text = page_content + Thanks
              # Change Voice by editing the Language
                language = 'en-in'  # 'en': ['en-us', 'en-ca', 'en-uk', 'en-gb', 'en-au', 'en-gh', 'en-in',
                                    # 'en-ie', 'en-nz', 'en-ng', 'en-ph', 'en-za', 'en-tz'],
                tts_file = gTTS(text=output_text, lang=language, slow=False) 
                tts_file.save(f"{message.chat.id}.mp3")      
                with open(f"{message.chat.id}.mp3", "rb") as speech:
                      await bot.send_voice(chat_id, speech)   
                await txt.edit("Meɾci de m'ɑvoiɾ utiliseɾ...☺️\n©Sharing_Club")    
                os.remove(pdf_path)  
                
                
           else :
                await message.reply("𝖲’𝗂𝗅 𝗏𝗈𝗎𝗌 𝗉𝗅𝖺𝗂̂𝗍 𝗋𝖾́𝗉𝗈𝗇𝖽𝗋𝖾 𝖺𝗎 𝖿𝗂𝖼𝗁𝗂𝖾𝗋 𝖯𝖣𝖥")
 except Exception as error :
           print(error)
           await txt.delete()
           os.remove(pdf_path)
