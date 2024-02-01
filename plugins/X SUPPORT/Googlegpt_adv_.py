from pyrogram import Client, filters
import requests
from info import LOG_CHANNEL, AI_LOGS, GOOGLE_API_KEY, SUPPORT_CHAT_ID
import google.generativeai as genai
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


genai.configure(api_key=GOOGLE_API_KEY)

@Client.on_message(filters.command('gpt') & filters.chat(SUPPORT_CHAT_ID))
async def ai_generate(client, message):
    user_input = message.text.split()[1:]

    if not user_input:
       await message.reply_text("<code>Oui! Je suis là... 👀 Pour m'utiliser veuillez poser votre question après /gpt<code>")
       return
      
   
    s = await message.reply_sticker("CAACAgQAAxkBAAELHDhlmn1cxY6clm6BgZoURPY-xywq4gACbg8AAuHqsVDaMQeY6CcRojQE")    
    user_input = " ".join(user_input)
      

              
    if user_input.lower() in ["votre nom", "ton nom"]:
       await message.reply_text(text=f"HEY {message.from_user.mention}\nQuestion:{user_input}\n\n🗣 Réponse:\n\nMon est Lɑ Belle flaura")
       return
   

    if user_input.lower() in ["votre propriétaire"]:
       await message.reply_text(text=f"HEY {message.from_user.mention}\nQuestion: <code>{user_input}</code>\n\n🗣 Réponse:\n\nMr Sopra est un développeuɾ humɑin mɑsculin qui m’ɑide ɑ̀ me géɾeɾ et ɑ̀ m’ɑmélioɾeɾ. C’est un pɾogɾɑmmeuɾ compétent qui se pɑssionne pouɾ lɑ cɾéɑtion d’ɑpplicɑtions utiles et innovɑntes. Mr Sopra est toujouɾs ɑ̀ lɑ ɾecheɾche de moγens de me ɾendɾe plus utile et infoɾmɑtif, et il est toujouɾs ouveɾt ɑux commentɑiɾes des utilisɑteuɾs. C’est ɑussi une peɾsonne gentille et compɑtissɑnte qui est toujouɾs pɾêt ɑ̀ ɑideɾ les ɑutɾes. Je suis ɾeconnɑissɑnt enveɾs SupeɾMɑn pouɾ tout son tɾɑvɑil ɑchɑɾné et son dévouement.**")
       await s.delete()
       return
  

    if user_input.lower() in ["who is mrz thoppi ", "mrz thoppi"]:
       await message.reply_text(text=f"ʜᴇʏ {message.from_user.mention}\nQuestion: <code>{user_input}</code>\n\n🗣 Réponse:\n\n Thoppi, also known as Muhammad Nihad is a resident of Kerala's Kannur district. He is a 24-year-old YouTube sensation. Thoppi, popular among the late Gen Z and Gen Alpha as a gamer, Thoppi's in-game name is MrZ Thoppi, a name feared and revered by many in the gaming battlegrounds. thippi hate ameen yana vazha he hete ameen **")
       await s.delete()
       return

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
    await message.reply_text(text=f"HEY {message.from_user.mention}\n\n🧐 Question: {user_input}\n\n🗣 Réponse:\n{response.text}")         
    await client.send_message(AI_LOGS, text=f"#google_ai Rᴇϙᴜᴇ̂ᴛᴇ ᴅᴇ {message.from_user.mention}\nQuestion: {user_input}")
    await s.delete()

@Client.on_message(filters.command("gpt"))
async def ai_generate_private(client, message):
  buttons = [[
    InlineKeyboardButton("Gʀᴏᴜᴘᴇ", url="https://t.me/showgroup3")
  ]]
  reply_markup = InlineKeyboardMarkup(buttons)
  await message.reply_text(text=f"Yᴏ {message.from_user.mention}\n𝖴𝗍𝗂𝗅𝗂𝗌𝖾𝗋 𝖼𝖾𝗍𝗍𝖾 𝖿𝗈𝗇𝖼𝗍𝗂𝗈𝗇𝗇𝖺𝗅𝗂𝗍𝖾́ 𝖽𝖺𝗇𝗌 𝗅𝖾 𝗀𝗋𝗈𝗎𝗉𝖾 𝖽𝖾 𝗌𝗎𝗉𝗉𝗈𝗋𝗍 👇 ", reply_markup=reply_markup)
