import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.sumanjay.cf/covid/?country="

BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton("Fᥱrmᥱr", callback_data='close_data')]])

@Client.on_message(filters.command("covid"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    await message.reply_photo(
        photo="https://telegra.ph/file/ba80a640f5f659aade51b.jpg",
        caption=covid_info(query),
        quote=True
    )


def covid_info(country_name):
    try:
        r = requests.get(API + requote_uri(country_name.lower()))
        info = r.json()
        country = info['country'].capitalize()
        active = info['active']
        confirmed = info['confirmed']
        deaths = info['deaths']
        info_id = info['id']
        last_update = info['last_update']
        latitude = info['latitude']
        longitude = info['longitude']
        recovered = info['recovered']
        covid_info = f"""--**𝙲𝙾𝚅𝙸𝙳 𝟷𝟿 𝙸𝙽𝙵𝙾𝚁𝙼𝙰𝚃𝙸𝙾𝙽**--
᚛› Ƥɑყs : `{country}`
᚛› Aᴄᴛɪғ : `{active}`
᚛› Cᴏɴғɪʀᴍᴇ́ : `{confirmed}`
᚛› Dᴇ́ᴄᴇ̀s : `{deaths}`
᚛› ID : `{info_id}`
᚛› Dᴇʀɴɪᴇ̀ʀᴇ ᴍɪsᴇ ᴀ̀ ᴊᴏᴜʀ : `{last_update}`
᚛› Latitude : `{latitude}`
᚛› Longitude : `{longitude}`
᚛› Rᴇ́ᴛᴀʙʟɪ : `{recovered}`"""
        return covid_info
    except Exception as error:
        return error
