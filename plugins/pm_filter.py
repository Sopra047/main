# Kanged From @TroJanZheX
import asyncio
import asyncio
import re
import ast
import math
import random
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, FILE_CHANNEL, AUTH_USERS, NOR_IMG, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, SPELL_IMG, MSG_ALRT, FILE_FORWARD, MAIN_CHANNEL, LOG_CHANNEL, PICS, SUPPORT_CHAT_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
FILTER_MODE = {}
LANGUAGES = ["english", "French", "malayalam", "hindi"]


@Client.on_message(filters.command('autofilter') & filters.user(ADMINS))
async def fil_mod(client, message):
    mode_on = ["yes", "on", "true"]
    mode_of = ["no", "off", "false"]

    try:
        args = message.text.split(None, 1)[1].lower()
    except:
        return await message.reply("**𝙸𝙽𝙲𝙾𝙼𝙿𝙴𝚃𝙴𝙽𝚃 𝙲𝙾𝙼𝙼𝙰𝙳...**")

    m = await message.reply("**𝚂𝙴𝚃𝚃𝙸𝙽𝙶.../**")

    if args in mode_on:
        FILTER_MODE[str(message.chat.id)] = "True"
        await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙴𝙽𝙰𝙱𝙻𝙴𝙳**")

    elif args in mode_of:
        FILTER_MODE[str(message.chat.id)] = "False"
        await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙳𝙸𝚂𝙰𝙱𝙻𝙴𝙳**")
    else:
        await m.edit("𝚄𝚂𝙴 :- /autofilter on 𝙾𝚁 /autofilter off")


@Client.on_message((filters.group) & filters.text & filters.incoming)
async def give_filter(client, message):
    await global_filters(client, message)
    group_id = message.chat.id
    name = message.text

    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await message.reply_text(reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await message.reply_text(
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                    elif btn == "[]":
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or ""
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button)
                        )
                except Exception as e:
                    print(e)
                break

    else:
        if FILTER_MODE.get(str(message.chat.id)) == "False":
            return
        else:
            await auto_filter(client, message)


@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    await message.reply_text("<b>Votɾe messɑge ɑ été envoγé ɑ̀ mon modéɾɑteuɾ !</b>",
                             reply_markup=InlineKeyboardMarkup(
                                 [[
                                     InlineKeyboardButton('📍 Lᴇ ғɪʟᴍ ᴇsᴛ ɪᴄɪ 📍', url='https://t.me/netflixshoww')
                                 ]]
                             )
                             )
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#PM_MSG\n\nNOM : {user}\n\nID : {user_id}\n\nMessɑge : {content}</b>"
    )


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(query.message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    if ENABLE_SHORTLINK == True:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}",
                        url=await get_shortlink(query.message.chat.id,
                                                f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id,
                                                                          f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id,
                                                f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'files_#{file.file_id}',
                    ),
                ]
                for file in files
            ]
    btn.insert(0,
               [
                   InlineKeyboardButton(f'⭕ ʀᴇᴊᴏɪɴs ᴘᴏᴜʀ ᴅᴇ ɴᴏᴜᴠᴇᴀᴜx ғɪʟᴍs ⭕', url='https://t.me/showgroup3'),
               ]
               )
    btn.insert(1,
               [
                   InlineKeyboardButton(f'Fɪʟᴍ / Sᴇ́ʀɪᴇ', url='https://t.me/netflixshoww'),
                   InlineKeyboardButton("🌐 Lᴀɴɢᴜᴇs 🌏", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
               ]
              )
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪𝐑𝐞𝐭𝐨𝐮𝐫", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📄𝐏𝐚𝐠𝐞𝐬 {math.ceil(int(offset) / 7) + 1} / {math.ceil(total / 7)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"📄𝐏𝐚𝐠𝐞𝐬 {math.ceil(int(offset) / 7) + 1} / {math.ceil(total / 7)}", callback_data="pages"),
             InlineKeyboardButton("𝐒𝐮𝐢𝐯𝐚𝐧𝐭⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪𝐑𝐞𝐭𝐨𝐮𝐫", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📄𝐏𝐚𝐠𝐞𝐬 {math.ceil(int(offset) / 7) + 1} / {math.ceil(total / 7)}",
                                     callback_data="pages"),
                InlineKeyboardButton("𝐒𝐮𝐢𝐯𝐚𝐧𝐭⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


# Language Code Temp


@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
        return await query.answer(
            f"⚠️ Sᥲᥣᥙt {query.from_user.first_name},\nCe n’est pɑs votre requête 😤,\nEffectuez ɑussi votre demɑnde...",
            show_alert=True,
        )

    _, search, key = query.data.split("#")

    btn = [
        [
            InlineKeyboardButton(
                text=lang.title(),
                callback_data=f"fl#{lang.lower()}#{search}#{key}"
            ),
        ]
        for lang in LANGUAGES
    ]

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="☟  Sélectionnez votɾe lɑngue  ☟", callback_data="selectlang"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↺ Rᴇᴛᴏᴜʀ ᴀᴜx ғɪᴄʜɪᴇʀs ​↻", callback_data=f"next_{req}_{key}_{offset}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, search, key = query.data.split("#")

    search = search.replace("_", " ")
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
        return await query.answer(
            f"⚠️ Sᥲᥣᥙt {query.from_user.first_name},\nCe n’est pɑs votre requête 😤,\nEffectuez ɑussi votre demɑnde...",
            show_alert=True,
        )

    search = f"{search} {lang}"

    files, offset, _ = await get_search_results(search, max_results=10)
    files = [file for file in files if re.search(lang, file.file_name, re.IGNORECASE)]
    if not files:
        await query.answer("🚫 𝗔𝘂𝗰𝘂𝗻 𝗳𝗶𝗰𝗵𝗶𝗲𝗿 𝗻’𝗮 𝗲́𝘁𝗲́ 𝘁𝗿𝗼𝘂𝘃𝗲́ 🚫", show_alert=1)
        return

    settings = await get_settings(message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK == True:
        btn = (
            [
                [
                    InlineKeyboardButton(
                        text=f"📂 {get_size(file.file_size)} ⊳ {file.file_name}",
                        url=await get_shortlink(
                            message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                ]
                for file in files
            ]
            if settings["button"]
            else [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(
                            message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(
                            message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                ]
                for file in files
            ]
        )
    elif settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📂 {get_size(file.file_size)} ⊳ {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            for file in files
        ]
     

    btn.insert(0, [InlineKeyboardButton("! Envoyer tous les fichiers en PM !", callback_data=f"send_fall#files#{key}#{offset}")])
    offset = 0

    btn.append([
        InlineKeyboardButton(
            text="↺ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ​↻",
            callback_data=f"next_{req}_{key}_{offset}"
        ),
    ])

    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))


# spellcheck error fixing
@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')

    movies = SPELL_CHECK.get(query.message.reply_to_message.id)

    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[int(movie_)]  # Fixed int(movie_) instead of movies[(int(movie_))]

    await query.answer(script.TOP_ALRT_MSG)

    k = await manual_filters(bot, query.message, text=movie)

    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("𝖠𝗌𝗌𝗎𝗋𝖾𝗓-𝗏𝗈𝗎𝗌 𝗊𝗎𝖾 𝗃𝖾 𝗌𝗎𝗂𝗌 𝗉𝗋𝖾́𝗌𝖾𝗇𝗍𝖾 𝖽𝖺𝗇𝗌 𝗏𝗈𝗍𝗋𝖾 𝗀𝗋𝗈𝗎𝗉𝖾!!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "𝖩𝖾 𝗇𝖾 𝗌𝗎𝗂𝗌 𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝖾́ 𝖺̀ 𝖺𝗎𝖼𝗎𝗇 𝗀𝗋𝗈𝗎𝗉𝖾!\n𝖵𝖾́𝗋𝗂𝖿𝗂𝖾𝗋 /connections 𝗈𝗎 𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝖾𝗓-𝗆𝗈𝗂 𝖺̀ 𝗇’𝗂𝗆𝗉𝗈𝗋𝗍𝖾 𝗊𝗎𝖾𝗅 𝗀𝗋𝗈𝗎𝗉𝖾",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("Vous devez être propriétɑire du groupe ou utilisɑteur Authentifié pour le fɑire. -_- !", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "ᴄᴏɴɴᴇᴄᴛᴇʀ"
            cb = "connectcb"
        else:
            stat = "ᴅᴇ́ᴄᴏɴɴᴇᴄᴛᴇʀ"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("sᴜᴘᴘʀɪᴍᴇʀ", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("ʀᴇᴛᴏᴜʀ", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Nᴏᴍ ᴅᴜ ɢʀᴏᴜᴘᴇ : **{title}**\nID ᴅᴜ ɢʀᴏᴜᴘᴇ : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"𝖢𝗈𝗇𝗇𝖾𝖼𝗍𝖾́ 𝖺̀ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('𝖴𝗇𝖾 𝖾𝗋𝗋𝖾𝗎𝗋 𝗌’𝖾𝗌𝗍 𝗉𝗋𝗈𝖽𝗎𝗂𝗍𝖾!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"𝖣𝖾́𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝖾𝗋 𝖽𝖾 **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"𝖴𝗇𝖾 𝖾𝗋𝗋𝖾𝗎𝗋 𝗌’𝖾𝗌𝗍 𝗉𝗋𝗈𝖽𝗎𝗂𝗍𝖾!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Connexion supprimée avec succès"
            )
        else:
            await query.message.edit_text(
                f"𝖴𝗇𝖾 𝖾𝗋𝗋𝖾𝗎𝗋 𝗌’𝖾𝗌𝗍 𝗉𝗋𝗈𝖽𝗎𝗂𝗍𝖾!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "Il n’y a pas de connexions actives !! Connectez-ᴍᴏɪ d’abord à certains groupes.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Détails de votre groupe connecté ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        clicked = query.from_user.id  # fetching the ID of the user who clicked the button
        try:
            typed = query.message.reply_to_message.from_user.id  # fetching user ID of the user who sent the movie request
        except:
            typed = clicked  # if failed, uses the clicked user's ID as requested user ID
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('🚫 𝗳𝗶𝗰𝗵𝗶𝗲𝗿 𝗻𝗼𝗻 𝘁𝗿𝗼𝘂𝘃𝗲́ 🚫')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(
                        f"HEY {query.from_user.first_name}, Ce n’est pɑs votre requête, Effectuez ɑussi votre pɾopɾe demɑnde !",
                        show_alert=True)
            elif settings['botpm']:
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(
                        f"HEY {query.from_user.first_name}, Ce n’est pɑs votre requête, Effectuez ɑussi votre pɾopɾe demɑnde !",
                        show_alert=True)
            else:
                if clicked == typed:
                    file_send = await client.send_cached_media(
                        chat_id=FILE_CHANNEL,
                        file_id=file_id,
                        caption=script.CHANNEL_CAP.format(query.from_user.mention, title, query.message.chat.title),
                        protect_content=True if ident == "filep" else False,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(f'🇮🇳 Mᴀʟ', 'fmal'),
                                    InlineKeyboardButton(f'🇮🇳 Tᴀᴍ', 'ftam'),
                                    InlineKeyboardButton(f'🇮🇳 Hɪɴ', 'fhin')
                                ], [
                                InlineKeyboardButton("📍 𝙲𝙰𝙽𝙰𝙻 📍", url=(MAIN_CHANNEL))
                            ]
                            ]
                        )
                    )
                    Joel_tgx = await query.message.reply_text(
                        script.FILE_MSG.format(query.from_user.mention, title, size),
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton('📥 Lɪᴇɴ ᴛᴇ́ʟᴇ́ᴄʜᴀʀɢᴇᴍᴇɴᴛ 📥 ', url=file_send.link)
                                ], [
                                InlineKeyboardButton("⚠️ 𝖠𝖼𝖼𝖾̀𝗌 𝖨𝗆𝗉𝗈𝗌𝗌𝗂𝖻𝗅𝖾❓ 𝖢𝗅𝗂𝗊𝗎𝖾𝗓-𝗂𝖼𝗂 ⚠️", url=(FILE_FORWARD))
                            ]
                            ]
                        )
                    )
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await Joel_tgx.delete()
                        await file_send.delete()
                else:
                    await query.answer(
                        f"Hᴇʏ {query.from_user.first_name}, Ce n’est pɑs votre requête, Effectuez ɑussi votre pɾopɾe demɑnde !",
                        show_alert=True)
                await query.answer('Vérifiez PM, j’ɑi envoyé les fichiers en PM', show_alert=True)
        except UserIsBlocked:
            await query.answer('𝖣𝖾́𝖻𝗅𝗈𝗊𝗎𝖾𝗋 𝗅𝖾 𝖻𝗈𝗍 𝖲𝗎𝗉𝖾𝗋 𝖬𝖺𝗇 😑 !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
            await query.answer(
                "J’ɑime votre intelligence, mɑis ne soyez pɑs trop intelligent 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('🚫 𝗳𝗶𝗰𝗵𝗶𝗲𝗿 𝗻𝗼𝗻 𝘁𝗿𝗼𝘂𝘃𝗲́')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "predvd":
        k = await client.send_message(chat_id=query.message.chat.id, text="<b>𝖲𝗎𝗉𝗉𝗋𝖾𝗌𝗌𝗂𝗈𝗇 𝖯𝗋𝖾𝖣𝖵𝖣𝗌... 𝖵𝖾𝗎𝗂𝗅𝗅𝖾𝗓 𝗉𝖺𝗍𝗂𝖾𝗇𝗍𝖾𝗋...</b>")
        files, next_offset, total = await get_bad_files(
            'predvd',
            offset=0)
        deleted = 0
        for file in files:
            file_ids = file.file_id
            result = await Media.collection.delete_one({
                '_id': file_ids,
            })
            if result.deleted_count:
                logger.info('𝖥𝗂𝖼𝗁𝗂𝖾𝗋 𝖯𝗋𝖾𝖣𝖵𝖣 𝗍𝗋𝗈𝗎𝗏𝖾́ ! 𝖲𝗎𝗉𝗉𝗋𝗂𝗆𝖾́ 𝖺𝗏𝖾𝖼 𝗌𝗎𝖼𝖼𝖾̀𝗌 𝖽𝖾 𝗅𝖺 𝖻𝖺𝗌𝖾 𝖽𝖾 𝖽𝗈𝗇𝗇𝖾́𝖾𝗌.')
            deleted += 1
        deleted = str(deleted)
        await k.edit_text(text=f"<b>𝖲𝗎𝗉𝗉𝗋𝗂𝗆𝖾́ 𝖺𝗏𝖾𝖼 𝗌𝗎𝖼𝖼𝖾̀𝗌 {deleted} PreDVD 𝖥𝗂𝖼𝗁𝗂𝖾𝗋𝗌.</b>")

    elif query.data == "camrip":
        k = await client.send_message(chat_id=query.message.chat.id, text="<b>𝖲𝗎𝗉𝗉𝗋𝖾𝗌𝗌𝗂𝗈𝗇 𝖽𝖾 𝖢𝖺𝗆𝖱𝗂𝗉𝗌... 𝖵𝖾𝗎𝗂𝗅𝗅𝖾𝗓 𝗉𝖺𝗍𝗂𝖾𝗇𝗍𝖾𝗋...</b>")
        files, next_offset, total = await get_bad_files(
            'camrip',
            offset=0)
        deleted = 0
        for file in files:
            file_ids = file.file_id
            result = await Media.collection.delete_one({
                '_id': file_ids,
            })
            if result.deleted_count:
                logger.info('𝖥𝗂𝖼𝗁𝗂𝖾𝗋 𝖢𝖺𝗆𝖱𝗂𝗉 𝗍𝗋𝗈𝗎𝗏𝖾́ ! ! 𝖲𝗎𝗉𝗉𝗋𝗂𝗆𝖾́ 𝖺𝗏𝖾𝖼 𝗌𝗎𝖼𝖼𝖾̀𝗌 𝖽𝖾 𝗅𝖺 𝖻𝖺𝗌𝖾 𝖽𝖾 𝖽𝗈𝗇𝗇𝖾́𝖾𝗌..')
            deleted += 1
        deleted = str(deleted)
        await k.edit_text(text=f"<b>𝖲𝗎𝗉𝗉𝗋𝗂𝗆𝖾́ 𝖺𝗏𝖾𝖼 𝗌𝗎𝖼𝖼𝖾̀𝗌 {deleted} CamRip 𝖥𝗂𝖼𝗁𝗂𝖾𝗋𝗌.</b>")

    elif query.data == "pages":
        await query.answer()

    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = BUTTONS.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
            return
        files, n_offset, total = await get_search_results(search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident)
        await query.answer( f"HEY {query.from_user.first_name}, Tous les fichiers de cette pɑge ont été envoyés ɑvec succès ɑ̀ votre PM !", show_alert=True)

    elif query.data == "reqinfo":
        await query.answer(
            "⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nAprès 10 minutes, ce messɑge serɑ ɑutomɑtiquement supprimé\n\nSi vous ne voyez pɑs le fichier de film / série demɑndé, regɑrdez lɑ pɑge suivɑnte\n\n❣ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Filmserieshoww",
            show_alert=True)

    elif query.data == "minfo":
        await query.answer(
            "⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nFᴏʀᴍᴀᴛ ᴅᴇ ᴅᴇᴍᴀɴᴅᴇ ᴅᴇ ғɪʟᴍ\n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nAʟʟᴇᴢ sᴜʀ Gᴏᴏɢʟᴇ ➠ Tᴀᴘᴇᴢ ʟᴇ ɴᴏᴍ ᴅᴜ ғɪʟᴍ ➠ Cᴏᴘɪᴇᴢ ʟᴇ ɴᴏᴍ ᴄᴏʀʀᴇᴄᴛ ➠ Cᴏʟʟᴇᴢ ᴅᴀɴs ᴄᴇ Gʀᴏᴜᴘᴇ\n\nExemple : Avɑtɑr\n\n🚯 N’utiliser pɑs ➠ ':(!,./)\n\n @Filmserieshoww",
            show_alert=True)

    elif query.data == "sinfo":
        await query.answer(
            "⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nFᴏʀᴍᴀᴛ ᴅᴇ ᴅᴇᴍᴀɴᴅᴇ sᴇ́ʀɪᴇ \n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nAʟʟᴇᴢ sᴜʀ Gᴏᴏɢʟᴇ ➠ Tᴀᴘᴇᴢ ʟᴇ ɴᴏᴍ ᴅᴇ sᴇ́ʀɪᴇ ➠ Cᴏᴘɪᴇᴢ ʟᴇ ɴᴏᴍ ᴄᴏʀʀᴇᴄᴛ ➠ Cᴏʟʟᴇᴢ ᴅᴀɴs ᴄᴇ Gʀᴏᴜᴘᴇ\n\nExemple : Arrow S01\n\n🚯 N’utiliser pɑs ➠ ':(!,./)\n\n @Filmserieshoww",
            show_alert=True)

    elif query.data == "tinfo":
        await query.answer(
            "▣Iɴғᴏ▣\n\n★ Tᥲρᥱz ᥣ’orthogrᥲρhᥱ ᥴorrᥱᥴtᥱ (ɢᴏᴏɢʟᴇ)\n\n★ Sι voᥙs ᥒ’obtᥱᥒᥱz ρᥲs votrᥱ fιᥴhιᥱr dᥲᥒs ᥣᥲ ρᥲgᥱ, ᥣ’ᥱ́tᥲρᥱ sᥙιvᥲᥒtᥱ ᥴoᥒsιstᥱ ᥲ̀ ᥴᥣιqᥙᥱr sᥙr ᥣᥱ boᥙtoᥒ sᥙιvᥲᥒt.\n\n★ Coᥒtιᥒᥙᥱz ᥴᥱttᥱ mᥱ́thodᥱ ρoᥙr obtᥱᥒιr votrᥱ fιᥴhιᥱr\n\n❣ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Filmserieshoww",
            show_alert=True)

    elif query.data == "fmal":
        await query.answer(
            "En raison des droits d'auteur, le fichier sera supprimé d'ici dans 10 minutes, alors téléchargez-le après avoir été déplacé d'ici vers un autre endroit !"
                      
        )                    
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton(' 👨‍👩‍👦‍👦 — 𝐑𝐞𝐣𝐨𝐢𝐠𝐧𝐞𝐳-𝐍𝐨𝐮𝐬 — 👨‍👩‍👦‍👦 ', url=f'https://t.me/showgroup3')
                  ],[
                    InlineKeyboardButton('👩‍🦰 ᴍᴀ ᴄᴏᴘɪɴᴇ', url='https://t.me/flaurabelle'),
                    InlineKeyboardButton('👩‍🎤 ᴍᴏɴ ᴄᴀɴᴀʟ 👩‍🎤', url='https://t.me/netflixshoww')
                  ],[
                    InlineKeyboardButton('📚 Aiɗes', callback_data="spu"),
                    InlineKeyboardButton('📋 Iɴғoѕ', callback_data='about'),
                  ],[
                    InlineKeyboardButton('🦋 Voiɾ Mes Nouvelles Cɑpɑcités 🦋', callback_data='help') 
                    ],[
                    InlineKeyboardButton('🔒 Fermer Menu', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)
    elif query.data == "help":
        buttons = [[  
            InlineKeyboardButton('🗣 Iɴᴛᴇʟʟɪɢᴇɴᴄᴇ Aʀᴛɪғɪᴄɪᴇʟʟᴇ 👩‍💻', callback_data='opnai'),
        ], [
            InlineKeyboardButton('🎼 ᴄʜᴀɴsᴏɴ 🎧', callback_data='song'),
            InlineKeyboardButton('🎬 ᴠɪᴅᴇᴏ 🎞', callback_data='video')
        ], [
            InlineKeyboardButton('🎚 ᴛᴛs ᴠᴏᴄᴀʟ 🎛', callback_data='tts'),
            InlineKeyboardButton('🖼 ᴛɢʀᴀᴘʜ ☁️', callback_data='tele')
        ], [
            InlineKeyboardButton('⚽️ ɢᴀᴍᴇs 🎲', callback_data='fun')
        ], [
            InlineKeyboardButton('📟 ᴊsᴏɴᴇ 🕹', callback_data='json'),
            InlineKeyboardButton('☃️ sᴛɪᴄᴋɪᴅ 🦄', callback_data='sticker')
        ], [
            InlineKeyboardButton('🛅 ᴘᴏʟɪᴄᴇ 🖊', callback_data='font'),
            InlineKeyboardButton('🔠 ɢᴛʀᴀɴs 📚', callback_data='gtrans')
        ], [
            InlineKeyboardButton('📒 ᴄɪᴛᴀᴛɪᴏɴs 📇', callback_data='autofilter')
        ], [
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "spc":
        buttons = [[
            InlineKeyboardButton('Log', url="https://t.me/flaurabelle"),
            ], [
                InlineKeyboardButton('👨‍👩‍👦Gʀᴏᴜᴘᴇ ᴅ’ᴀɪᴅᴇ', url='https://t.me/showgroup3'),
                InlineKeyboardButton('👥 Gɾσʋpe Visiσɳ', url='https://t.me/showgroup'),
            ], [
                InlineKeyboardButton('🖼 Pσsteɾs Séɾies', url='https://t.me/netflixshoww'),
                InlineKeyboardButton('🎬 Pσsteɾs Filɱs', url='https://t.me/filmserieshoww'),
            ], [
                InlineKeyboardButton('↪️ Vσs Reqʋête Filɱ & Séɾie ↩️', url='https://t.me/showgroup3'),    
            ], [
                InlineKeyboardButton('📺 Pσsteɾs Sɑɠɑ', url='https://t.me/filmserieshowsss2'),
                InlineKeyboardButton('🗂 Mєѕ Ƈнαι̂ηєѕ', url='https://t.me/flaurabelle'),
        
            ], [
                InlineKeyboardButton('🆘 Adмιɴ', callback_data='extra'),
                InlineKeyboardButton('📨Cσƞtɑctez-ƞσʋs', url='https://t.me/soprasoppy'),
            ], [
                InlineKeyboardButton('🏠 𝐀𝐜𝐜𝐮𝐞𝐢𝐥', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.KD_CNL,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('🔮 Stɑtistique', callback_data='stats'),
            InlineKeyboardButton('🔎 Recɦeɾcɦe', switch_inline_query_current_chat='')
        ], [
            InlineKeyboardButton('🧑‍💻 ɪηғᴏ ɗєᴠ', callback_data='source'),
            InlineKeyboardButton('💝 𝖥𝖺𝗂𝗋𝖾 𝗎𝗇 𝖣𝗈𝗇 💝', callback_data='manuelfilter')
        ], [
            InlineKeyboardButton('🏠 Accυeιl', callback_data='start'),
            InlineKeyboardButton('🔐 Ferмer', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "spu":
        buttons = [[
                InlineKeyboardButton('👨‍👩‍👦Gʀᴏᴜᴘᴇ ᴅ’ᴀɪᴅᴇ', url='https://t.me/showgroup3'),
                InlineKeyboardButton('👥 Gɾσʋpe Visiσɳ', url='https://t.me/showgroup'),
            ], [
                InlineKeyboardButton('🖼 Pσsteɾs Séɾies', url='https://t.me/netflixshoww'),
                InlineKeyboardButton('🎬 Pσsteɾs Filɱs', url='https://t.me/filmserieshoww'),
            ],  [
                InlineKeyboardButton('↪️ Vσs Reqʋête Filɱ & Séɾie ↩️', url='https://t.me/showgroup3'),    
            ],  [
                InlineKeyboardButton('📺 Pσsteɾs Sɑɠɑ', url='https://t.me/filmserieshowsss2'),
                InlineKeyboardButton('🗂 Mєѕ Ƈнαι̂ηєѕ', url='https://t.me/flaurabelle'),
        
            ], [
                InlineKeyboardButton('🆘 Adмιɴ', callback_data='extra'),
                InlineKeyboardButton('📨Cσƞtɑctez-ƞσʋs', url='https://t.me/soprasoppy'),
            ], [
                InlineKeyboardButton('⏮ RETOUR', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.KD_CNL,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "disc":
        buttons = [[
            InlineKeyboardButton('RETOUR', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DISC_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('⏮ RETOUR', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('⏮ RETOUR', callback_data='about'),
            InlineKeyboardButton('💝 Doɴ ❤️‍🩹', url='https://t.me/soprasoppy')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('⏮ RETOUR', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 RETOUR', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('⏮ RETOUR', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('⏮ RETOUR', callback_data='spu'),
            InlineKeyboardButton('👮‍♂ ꮓꮻɴꭼ ꭺꭰꮇꮖɴ 👨‍💻', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('⏮RETOUR', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        reply_markup = InlineKeyboardMarkup(buttons)
        if query.from_user.id in ADMINS:
            await query.message.edit_text(text=script.ADMIN_TXT, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        else:
            await query.answer("👊⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nC'est uniquement pouɾ mes ɑdministɾɑteuɾs👊", show_alert=True)
                    
    elif query.data == "song":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SONG_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "video":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.VIDEO_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tts":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TTS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "gtrans":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help'),
            InlineKeyboardButton('𝙻𝙰𝙽𝙶 𝙲𝙾𝙳𝙴𝚂', url='https://cloud.google.com/translate/docs/languages')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GTRANS_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "country":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CON_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tele":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TELE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "corona":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CORONA_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "abook":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOOK_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "opnai":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.OPNAI_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "sticker":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.STICKER_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "pings":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PINGS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "json":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.JSON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "urlshort":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.URLSHORT_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "whois":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.WHOIS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "font":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FONT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "carb":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CARB_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "fun":
        buttons = [[
            InlineKeyboardButton('ꭱꭼꭲꮻꮜꭱ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FUN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('⏮ RETOUR', callback_data='about'),
            InlineKeyboardButton('♻️AᥴtᥙᥲꙆɩ⳽ᥱɾ', callback_data='rfrsh')
        ]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Actualisation...")
        buttons = [[
            InlineKeyboardButton('⏮ RETOUR', callback_data='stats'),
            InlineKeyboardButton('♻️AᥴtᥙᥲꙆɩ⳽ᥱɾ', callback_data='rfrsh')
        ]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Votre connexion ɑctive ɑ été modifiée. Aller ɑ̀ /settings.")
            return await query.answer(MSG_ALRT)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)
        try:
            if settings['auto_delete']:
                settings = await get_settings(grp_id)
        except KeyError:
            await save_group_settings(grp_id, 'auto_delete', True)
            settings = await get_settings(grp_id)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Bᴏᴜᴛᴏɴ ғɪʟᴛʀᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('sɪᴍᴘʟᴇ' if settings["button"] else 'ᴅᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴍᴏᴅᴇ ᴅ·ᴇɴᴠᴏɪ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ʙᴏᴛ ᴘᴍ' if settings["botpm"] else 'ᴍᴀɴᴜᴇʟ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ʙʟᴏϙᴜᴇʀ ᴄᴏɴᴛᴇɴᴜ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Oᴜɪ' if settings["file_secure"] else '❌ Nᴏɴ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Oᴜɪ' if settings["imdb"] else '❌ Nᴏɴ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('sᴜɢɢᴇsᴛ ᴏʀᴛʜᴏ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Oᴜɪ' if settings["spell_check"] else '❌ Nᴏɴ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bɪᴇɴᴠᴇɴᴜᴇ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Oᴜɪ' if settings["welcome"] else '❌ Nᴏɴ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏᴅᴇsᴛʀᴜᴄᴛɪᴏɴ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 ᴍɪɴ' if settings["auto_delete"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇ́',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ʟɪᴇɴ ᴄᴏᴜʀᴛ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ ᴀᴄᴛɪᴠᴇ́' if settings["is_shortlink"] else '❌ ᴅᴇ́sᴀᴄᴛɪᴠᴇ́',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton("𝗙𝗲𝗿𝗺𝗲𝗿", callback_data="close_data")
                ]

            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)


async def auto_filter(client, msg, spoll=False):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, msg)
                else:
                    await client.send_message(chat_id=LOG_CHANNEL,
                                              text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK == True:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"📂[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(message.chat.id,
                                                                                                       f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"📂{file.file_name}",
                        url=await get_shortlink(message.chat.id,
                                                f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"📂{get_size(file.file_size)}",
                        url=await get_shortlink(message.chat.id,
                                                f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"📂[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"📂{file.file_name}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                    InlineKeyboardButton(
                        text=f"📂{get_size(file.file_size)}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                ]
                for file in files
            ]

    key = f"{message.chat.id}-{message.id}"
    btn.insert(0,
               [
                   InlineKeyboardButton(f'⭕ ʀᴇᴊᴏɪɴs ᴘᴏᴜʀ ᴅᴇ ɴᴏᴜᴠᴇᴀᴜx ғɪʟᴍs ⭕', url='https://t.me/netflixshoww'),
               ]
               )
    btn.insert(1,
               [
                   InlineKeyboardButton(f'Fɪʟᴍ / Sᴇ́ʀɪᴇ', url='https://t.me/filmserieshoww'),
                   InlineKeyboardButton("🌐 Lᴀɴɢᴜᴇs 🌏​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
               ]
              )
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"📄𝐏𝐚𝐠𝐞 1/{math.ceil(int(total_results) / 7)}", callback_data="pages"),
             InlineKeyboardButton(text="𝐒𝐮𝐢𝐯𝐚𝐧𝐭⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="PAS DE PAGE SUPPLEMENTAIRE", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b><i>Voici ce que j'ɑi tɾouvé ɑ̀ pɾopos de votɾe ɾequête:\n {search}\n👤Demɑndé pɑɾ : {message.from_user.mention}\n👥Gɾoupe : {message.chat.title}</i></b>"
    if imdb and imdb.get('poster'):
        try:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(
                    text=f"<b>HEY {message.from_user.mention}, {str(total_results)} Rᴇ́sᴜʟᴛᴀᴛs ᴛʀᴏᴜᴠᴇ́ ᴅᴀɴs ᴍᴀ ʙᴀsᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇs ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {search}. Vᴇᴜɪʟʟᴇᴢ ᴜᴛɪʟɪsᴇʀ ʟ’ᴜɴ ᴅᴇ ᴍᴇs Gʀᴏᴜᴘᴇ ᴅᴇ ʀᴇᴄʜᴇʀᴄʜᴇ ᴏᴜ ᴄʀᴇ́ᴇʀ ᴜɴ ɢʀᴏᴜᴘᴇ ᴇᴛ ᴍ’ᴀᴊᴏᴜᴛᴇʀ ᴇɴ ᴛᴀɴᴛ ϙᴜ’ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴇᴜʀ ᴘᴏᴜʀ ᴏʙᴛᴇɴɪʀ ᴅᴇs ғɪᴄʜɪᴇʀs ᴠɪᴅᴇ́ᴏ. Cᴇᴄɪ ᴇsᴛ ᴜɴ ɢʀᴏᴜᴘᴇ ᴅᴇ sᴜᴘᴘᴏʀᴛ. Rᴀɪsᴏɴ ᴘᴏᴜʀ ʟᴀϙᴜᴇʟʟᴇ ᴠᴏᴜs ɴᴇ ᴘᴏᴜʀʀᴇᴢ ᴘᴀs ᴏʙᴛᴇɴɪʀ ᴅᴇ ғɪᴄʜɪᴇʀs ᴅ’ɪᴄɪ...</b>",
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton('Dᴇᴍᴀɴᴅᴇᴢ-ɪᴄɪ 🚀', url='https://t.me/showgroup3')
                        ]]
                    )
                )
            else:
                hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                                 reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(
                    text=f"<b>HEY {message.from_user.mention}, {str(total_results)} Rᴇ́sᴜʟᴛᴀᴛs ᴛʀᴏᴜᴠᴇ́ ᴅᴀɴs ᴍᴀ ʙᴀsᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇs ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {search}. Rᴇ́sᴜʟᴛᴀᴛs ᴏɴᴛ ᴇ́ᴛᴇ́s ᴛʀᴏᴜᴠᴇ́ ᴅᴀɴs ᴍᴀ ʙᴀsᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇs ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {search}. Vᴇᴜɪʟʟᴇᴢ ᴜᴛɪʟɪsᴇʀ ʟ’ᴜɴ ᴅᴇ ᴍᴇs Gʀᴏᴜᴘᴇ ᴅᴇ ʀᴇᴄʜᴇʀᴄʜᴇ ᴏᴜ ᴄʀᴇ́ᴇʀ ᴜɴ ɢʀᴏᴜᴘᴇ ᴇᴛ ᴍ’ᴀᴊᴏᴜᴛᴇʀ ᴇɴ ᴛᴀɴᴛ ϙᴜ’ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴇᴜʀ ᴘᴏᴜʀ ᴏʙᴛᴇɴɪʀ ᴅᴇs ғɪᴄʜɪᴇʀs ᴠɪᴅᴇ́ᴏ. Cᴇᴄɪ ᴇsᴛ ᴜɴ ɢʀᴏᴜᴘᴇ ᴅᴇ sᴜᴘᴘᴏʀᴛ. Rᴀɪsᴏɴ ᴘᴏᴜʀ ʟᴀϙᴜᴇʟʟᴇ ᴠᴏᴜs ɴᴇ ᴘᴏᴜʀʀᴇᴢ ᴘᴀs ᴏʙᴛᴇɴɪʀ ᴅᴇ ғɪᴄʜɪᴇʀs ᴅ’ɪᴄɪ...</b>",
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton('Dᴇᴍᴀɴᴅᴇᴢ-ɪᴄɪ 🚀', url='https://t.me/showgroup3')
                        ]]
                    )
                )
            else:
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                hmm = await message.reply_photo(photo=poster, caption=cap[:1024],
                                                reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
        except Exception as e:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(
                    text=f"<b>HEY {message.from_user.mention}, {str(total_results)} Rᴇ́sᴜʟᴛᴀᴛs ᴛʀᴏᴜᴠᴇ́ ᴅᴀɴs ᴍᴀ ʙᴀsᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇs ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {search}. Vᴇᴜɪʟʟᴇᴢ ᴜᴛɪʟɪsᴇʀ ʟ’ᴜɴ ᴅᴇ ᴍᴇs Gʀᴏᴜᴘᴇ ᴅᴇ ʀᴇᴄʜᴇʀᴄʜᴇ ᴏᴜ ᴄʀᴇ́ᴇʀ ᴜɴ ɢʀᴏᴜᴘᴇ ᴇᴛ ᴍ’ᴀᴊᴏᴜᴛᴇʀ ᴇɴ ᴛᴀɴᴛ ϙᴜ’ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴇᴜʀ ᴘᴏᴜʀ ᴏʙᴛᴇɴɪʀ ᴅᴇs ғɪᴄʜɪᴇʀs ᴠɪᴅᴇ́ᴏ. Cᴇᴄɪ ᴇsᴛ ᴜɴ ɢʀᴏᴜᴘᴇ ᴅᴇ sᴜᴘᴘᴏʀᴛ. Rᴀɪsᴏɴ ᴘᴏᴜʀ ʟᴀϙᴜᴇʟʟᴇ ᴠᴏᴜs ɴᴇ ᴘᴏᴜʀʀᴇᴢ ᴘᴀs ᴏʙᴛᴇɴɪʀ ᴅᴇ ғɪᴄʜɪᴇʀs ᴅ’ɪᴄɪ...</b>",
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton('Dᴇᴍᴀɴᴅᴇᴢ-ɪᴄɪ 🚀', url='https://t.me/showgroup3')
                        ]]
                    )
                )
            else:
                logger.exception(e)
                fek = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        await message.delete()
    else:
        if message.chat.id == SUPPORT_CHAT_ID:
            await message.reply_text(
                text=f"<b>HEY {message.from_user.mention}, {str(total_results)} Rᴇ́sᴜʟᴛᴀᴛs ᴛʀᴏᴜᴠᴇ́ ᴅᴀɴs ᴍᴀ ʙᴀsᴇ ᴅᴇ ᴅᴏɴɴᴇ́ᴇs ᴘᴏᴜʀ ᴠᴏᴛʀᴇ ʀᴇϙᴜᴇ̂ᴛᴇ {search}. Vᴇᴜɪʟʟᴇᴢ ᴜᴛɪʟɪsᴇʀ ʟ·ᴜɴ ᴅᴇ ᴍᴇs Gʀᴏᴜᴘᴇ ᴅᴇ ʀᴇᴄʜᴇʀᴄʜᴇ ᴏᴜ ᴄʀᴇ́ᴇʀ ᴜɴ ɢʀᴏᴜᴘᴇ ᴇᴛ ᴍ·ᴀᴊᴏᴜᴛᴇʀ ᴇɴ ᴛᴀɴᴛ ϙᴜ·ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴇᴜʀ ᴘᴏᴜʀ ᴏʙᴛᴇɴɪʀ ᴅᴇs ғɪᴄʜɪᴇʀs ᴠɪᴅᴇ́ᴏ. Cᴇᴄɪ ᴇsᴛ ᴜɴ ɢʀᴏᴜᴘᴇ ᴅᴇ sᴜᴘᴘᴏʀᴛ. Rᴀɪsᴏɴ ᴘᴏᴜʀ ʟᴀϙᴜᴇʟʟᴇ ᴠᴏᴜs ɴᴇ ᴘᴏᴜʀʀᴇᴢ ᴘᴀs ᴏʙᴛᴇɴɪʀ ᴅᴇ ғɪᴄʜɪᴇʀs ᴅ’ɪᴄɪ...</b>",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton('Dᴇᴍᴀɴᴅᴇᴢ-ɪᴄɪ 🚀', url='https://t.me/showgroup3')
                    ]]
                )
            )
        else:
            fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    await message.delete()
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    await message.delete()

    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    RQST = query.strip()
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply(script.I_CUDNT.format(reqstr.mention))
        await asyncio.sleep(8)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG,
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="𝗙𝗲𝗿𝗺𝗲𝗿", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    spell_check_del = await msg.reply_photo(
        photo=(SPELL_IMG),
        caption=(script.CUDNT_FND.format(reqstr.mention)),
        reply_markup=InlineKeyboardMarkup(btn)
    )

    try:
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
        grpid = await active_connection(str(message.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(message.chat.id)
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()


async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            elsa = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await elsa.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await elsa.delete()

                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await hmm.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await hmm.delete()

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await oto.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await oto.delete()

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await dlt.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await dlt.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False


async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )

                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

