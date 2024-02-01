import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, MSG_ALRT, MAIN_CHANNEL
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection
import re
import json
import base64
logger = logging.getLogger(__name__)

BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('🤖 𝐍𝐨𝐮𝐯𝐞𝐥𝐥𝐞𝐬 🤖', url="https://t.me/flaurabelle")
            ],
            [
                InlineKeyboardButton('📚 Aiɗes', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton(' 👨‍👩‍👦‍👦 — 𝐑𝐞𝐣𝐨𝐢𝐠𝐧𝐞𝐳-𝐍𝐨𝐮𝐬 — 👨‍👩‍👦‍👦 ', url=f'https://t.me/showgroup3')
                  ],[
                    InlineKeyboardButton('👩‍🦰 ᴍᴀ ᴄᴏᴘɪɴᴇ', url='https://t.me/flaurabelle'),
                    InlineKeyboardButton('👩‍🎤 ᴍᴏɴ ᴄᴀɴᴀʟ 👩‍🎤', url='https://t.me/netflixshoww')
                  ],[
                    InlineKeyboardButton('📚 Aiɗes', callback_data="spu"),
                    InlineKeyboardButton('📋 Iɴғoѕ', callback_data='about'),
                  ],[
                    InlineKeyboardButton('🦋 Voιr Mᥱs Noᥙvᥱᥣᥣᥱs Cᥲρᥲᥴιtᥱ́s 🦋', callback_data='help') 
                    ],[
                    InlineKeyboardButton('🔒 Ferмer ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Assurez-vous que le bot est administrateur dans le canal Forcesub")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "🤖 Rᴇᴊᴏɪɢɴᴇᴢ ᴍᴏɴ Cᴀɴᴀʟ", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton(" 🔄 Ꭱꭼ́ꭼꮪꮪꭺꭹꭼꮓ", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(" 🔄 Ꭱꭼ́ꭼꮪꮪꭺꭹꭼꮓ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**Désolé😉 vous n'êtes pɑs membre de mon Cɑnɑl pour recevoir ce fichier....\n\nPour ɑvoir votre fichier, Cliquez sur le bouton '👉 🤖 Rᴇᴊᴏɪɢɴᴇᴢ ᴍᴏɴ Cᴀɴᴀʟ' ci-dessous et rejoignez-le, puis revenez cliquez sur le boutons    '🔄 Rᴇ́ᴇssᴀʏᴇᴢ' en bɑs...\n\nEnfin Prenez plɑisir ɑvec vos fichiers Video...!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('sᴜʀᴘʀɪsᴇ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.SUR_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("Vᥱᥙιᥣᥣᥱz ρᥲtιᥱᥒtᥱr..")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "ɪᴍᴘᴏssɪʙʟᴇ ᴅ·ᴏᴜᴠʀɪᴇʀ ʟᴇ ғɪᴄʜɪᴇʀ.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("Please wait")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()
        

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("utf-8")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                )
            filetype = msg.media
            file = getattr(msg, filetype)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('Cᴇ ғɪᴄʜɪᴇʀ ɴ·ᴇxɪsᴛᴇ ᴘᴀs')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_markup=InlineKeyboardMarkup( [ [ InlineKeyboardButton('❤️‍🔥 Rᴇᴊᴏɪɴᴅʀᴇ ᴍᴏɴ Cᴀɴᴀʟ ❤️‍🔥', url=(MAIN_CHANNEL)) ] ] ),
        protect_content=True if pre == 'filep' else False,
        )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Cαnαux/Groupes ındexés**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Trɑitement...⏳", quote=True)
    else:
        await message.reply('Répondre au fichier avec /delete ce que vous souhaitez supprimer', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Ce format de fichier n’est pas pris en charge')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Le fichier est supprimé de la base de données avec succès')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Le fichier est supprimé de la base de données avec succès')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Le fichier est supprimé de la base de données avec succès')
            else:
                await msg.edit('Fichier introuvable dans la base de données')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'Cela supprimera tous les fichiers indexés.\nVoulez-vous continuer??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="OUI", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="ANNULER", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer(MSG_ALRT)
    await message.message.edit('Suppression réussie de tous les fichiers indexés.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vᴏᴜs ᴇ̂ᴛᴇs ᴜɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴇᴜʀ ᴀɴᴏɴʏᴍᴇ. ᴜᴛɪʟɪsᴇʀ /connect {message.chat.id} en ᴘᴍ")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Assuɾez-νσus que je sσis pɾéseƞte ɗɑƞs νσtɾe gɾσupe!!", quote=True)
                return
        else:
            await message.reply_text("Je ne suis connecté ɑ̀ ɑucun groupe", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)
    try:
        if settings['auto_delete']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'auto_delete', True)
        settings = await get_settings(grp_id)
    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Bᴏᴜᴛᴏɴ ғɪʟᴛʀᴇ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'sɪᴍᴘʟᴇ' if settings["button"] else 'ᴅᴏᴜʙʟᴇ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ᴍᴏᴅᴇ ᴅ·ᴇɴᴠᴏɪ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'ʙᴏᴛ ᴘᴍ' if settings["botpm"] else 'ᴍᴀɴᴜᴇʟ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ʙʟᴏϙᴜᴇʀ ᴄᴏɴᴛᴇɴᴜ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Oᴜɪ' if settings["file_secure"] else '❌ Nᴏɴ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Oᴜɪ' if settings["imdb"] else '❌ Nᴏɴ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'sᴜɢɢᴇsᴛ ᴏʀᴛʜᴏ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Oᴜɪ' if settings["spell_check"] else '❌ Nᴏɴ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Bɪᴇɴᴠᴇɴᴜᴇ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Oᴜɪ' if settings["welcome"] else '❌ Nᴏɴ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ᴀᴜᴛᴏᴅᴇsᴛʀᴜᴄᴛɪᴏɴ',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10 ᴍɪɴ' if settings["auto_delete"] else 'ᴅᴇ́sᴀᴄᴛɪᴠᴇ́',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ʟɪᴇɴ ᴄᴏᴜʀᴛ',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ ᴀᴄᴛɪᴠᴇ́' if settings["is_shortlink"] else '❌ ᴅᴇ́sᴀᴄᴛɪᴠᴇ́',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Modifiez vos pɑɾɑmètɾes pouɾ {title} Comme tu veux ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Checking template")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vᴏᴜs ᴇ̂ᴛᴇs ᴜɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴇᴜʀ ᴀɴᴏɴʏᴍᴇ. ᴜᴛɪʟɪsᴇʀ /connect {message.chat.id} en ᴘᴍ")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("𝖠𝗌𝗌𝗎𝗋𝖾𝗓-𝗏𝗈𝗎𝗌 𝗊𝗎𝖾 𝗃𝖾 𝗌𝗎𝗂𝗌 𝗉𝗋𝖾́𝗌𝖾𝗇𝗍 𝖽𝖺𝗇𝗌 𝗏𝗈𝗍𝗋𝖾 𝗀𝗋𝗈𝗎𝗉𝖾!!", quote=True)
                return
        else:
            await message.reply_text("𝖩𝖾 𝗇𝖾 𝗌𝗎𝗂𝗌 𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝖾́ 𝖺̀ 𝖺𝗎𝖼𝗎𝗇 𝗀𝗋𝗈𝗎𝗉𝖾!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Modèle modifié avec succès pour {title} to\n\n{template}")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    btn = [[
            InlineKeyboardButton("Suppɾimeɾ PɾeDVDs", callback_data="predvd"),
            InlineKeyboardButton("Suppɾimeɾ PɾeDVDs", callback_data="camrip")
          ]]
    await message.reply_text(
        text="<b>Sélectionnez le type de fichiers que vous souhɑitez supprimer !\n\nCelɑ supprimerɑ 100 fichiers de lɑ bɑse de données pour le type sélectionné.</b>",
        reply_markup=InlineKeyboardMarkup(btn)
    )


@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Users Saved In DB Are:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Votre messɑge ɑ été envoyé ɑvec succès ɑ̀ {user.mention}.</b>")
            else:
                await message.reply_text("<b>Cet utilisateur n'a pas encore démarré ce bot !</b>")
        except Exception as e:
            await message.reply_text(f"<b>Error: {e}</b>")
    else:
        await message.reply_text("<b>Utilisez cette commɑnde comme réponse ɑ̀ n’importe quel messɑge utilisɑnt l’identifiɑnt de discussion cible. Pɑr ex: /send ID de l'utilisɑteur</b>")

@Client.on_message(filters.command("shortlink") & filters.user(ADMINS))
async def shortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, Cette commɑnde ne fonctionne que dɑns les groupes !</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>Vous n'ɑvez pɑs ɑccès pour utiliser cette commɑnde !</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>Commɑnde incomplète :(\n\nDonnez-moi un lien court et une API ɑvec lɑ commɑnde!\n\nFormat: <code>/shortlink shorturllink.in 95a8195c40d31e0c3b6baa68813fcecb1239f2e9</code></b>")
    reply = await message.reply_text("<b>Veuillez pɑtienter...</b>")
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>Ajout réussi de l’API Shortlink pour {title}.\n\nSite Web ɑctuel de Shortlink : <code>{shortlink_url}</code>\nAPI actuelle: <code>{api}</code></b>")
