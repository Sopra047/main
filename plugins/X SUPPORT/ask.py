from pyrogram import Client, filters
import requests
from info import LOG_CHANNEL, AI_LOGS, GOOGLE_API_KEY, SUPPORT_CHAT_ID
import google.generativeai as genai
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

genai.configure(api_key=GOOGLE_API_KEY)

@Client.on_message(filters.command('ask') & filters.chat(SUPPORT_CHAT_ID))
async def ai_generate(client, message):
   user_input = message.text.split()[1:]

   if not user_input:
       await message.reply_text("Commɑnde incomplète /ask Sɑlut")
       return

   user_input = " ".join(user_input)

   generation_config = {
       "temperature": 0.9,
       "top_p": 1,
       "top_k": 1,
       "max_output_tokens": 2048,
   }

   safety_settings = [
       {
           "category": "HARM_CATEGORY_HARASSMENT",
           "threshold": "BLOCK_MEDIUM_AND_ABOVE"
       },
       {
           "category": "HARM_CATEGORY_HATE_SPEECH",
           "threshold": "BLOCK_MEDIUM_AND_ABOVE"
       },
       {
           "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
           "threshold": "BLOCK_MEDIUM_AND_ABOVE"
       },
       {
           "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
           "threshold": "BLOCK_MEDIUM_AND_ABOVE"
       },
   ]

   model = genai.GenerativeModel(
       model_name="gemini-pro",
       generation_config=generation_config,
       safety_settings=safety_settings
   )

   prompt_parts = [user_input]
   response = model.generate_content(prompt_parts)
   await message.reply_text(text=f"🙋 Demandeur: {message.from_user.mention}\n\n🤦 Question: {user_input}\n\n📝 Réponse:\n\n{response.text}\n\n🤗𝑁.𝐵 : 𝐿’𝐼𝐴 𝑝𝑒𝑢𝑥 𝑐𝑜𝑚𝑚𝑒𝑡𝑡𝑟𝑒 𝑑𝑒𝑠 𝑒𝑟𝑟𝑒𝑢𝑟𝑠. 𝑃𝑒𝑛𝑠𝑒𝑧 à 𝑣é𝑟𝑖𝑓𝑖𝑒𝑟 𝑙𝑒𝑠 𝑖𝑛𝑓𝑜𝑟𝑚𝑎𝑡𝑖𝑜𝑛𝑠 𝑖𝑚𝑝𝑜𝑟𝑡𝑎𝑛𝑡𝑒𝑠.")         
   await client.send_message(AI_LOGS, text=f"#ask Rᴇϙᴜᴇ̂ᴛᴇ ᴅᴇ {message.from_user.mention}\nQuestion: {user_input}")

@Client.on_message(filters.command("ask"))
async def ai_generate_private(client, message):
  buttons = [[
    InlineKeyboardButton("Support", url="https://t.me/Showgroup3")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"HEY {message.from_user.mention}\n𝖴𝗍𝗂𝗅𝗂𝗌𝖾𝗋 𝖼𝖾𝗍𝗍𝖾 𝖿𝗈𝗇𝖼𝗍𝗂𝗈𝗇𝗇𝖺𝗅𝗂𝗍𝖾́ 𝖽𝖺𝗇𝗌 𝗅𝖾 𝗀𝗋𝗈𝗎𝗉𝖾 𝖽𝖾 𝗌𝗎𝗉𝗉𝗈𝗋𝗍 👇", reply_markup=reply_markup)
