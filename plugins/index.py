import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Aʀʀᴇ̂ᴛ ᴅᴇ ʟ’ɪɴᴅᴇxᴀᴛɪᴏɴ😉")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Nᥱ trᥲᥒsfᥱ́rᥱr ρᥣᥙs dᥱ fιᥴhιᥱrs 📂 vᥱᥒᥲᥒt dᥱ {chat} ou de n*ımporte quel répertoıre sous peıne d*être bαnnı.\nMeѕѕαɢe de Mr Sopra',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Attendez, laissez-moi terminer le premier', show_alert=True)
    msg = query.message

    await query.answer('Traitement...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Votre soumission pour indexation {chat} a été accepté par nos modérateurs😀 et sera bientôt ajouté.✔️',
                               reply_to_message_id=int(lst_msg_id))
    await msg.edit(
        "Indexation démarrée🤖",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('ANNULER', callback_data='index_cancel')]]
        )
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Lien non valide')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('Il peut s’agir d’un canal / groupe privé😔. Faites de moi un administratrice là-bas pour indexer les fichiers.😀\nBesoins de fichiers Contactez ShowTeam Support\n@showgroup')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Lien spécifié non vɑlide.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Assurez-vous que je suıs αdmınıstrαtrıce dαns le cαnαl, sı le cαnαl est prıvé')
    if k.empty:
        return await message.reply('𝖨𝗅 𝗉𝖾𝗎𝗍 𝗌’𝖺𝗀𝗂𝗋 𝖽’𝗎𝗇 𝗀𝗋𝗈𝗎𝗉𝖾 𝖾𝗍 𝗃𝖾 𝗇𝖾 𝗌𝗎𝗂𝗌 𝗉𝖺𝗌 𝗎𝗇 𝖺𝖽𝗆𝗂𝗇𝗂𝗌𝗍𝗋𝖺𝗍𝖾𝗎𝗋 𝖽𝗎 𝗀𝗋𝗈𝗎𝗉𝖾.')

    if message.from_user.id in ADMINS:
        buttons = [
            [
                InlineKeyboardButton('✔️Ꭺꮯꮯꭼꮲꭲꭼꭱ✔️',
                                     callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
            ],
            [
                InlineKeyboardButton('❌Aɴɴυler❌', callback_data='close_data'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f'Voulez-vous indexeɾ ce Cɑnɑl / Gɾoupe ?\n\nChᥲt ID/ Usᥱrᥒᥲmᥱ: <code>{chat_id}</code>\nDᴇʀɴɪᴇʀ ᴍᴇssᴀɢᴇ ID: <code>{last_msg_id}</code>',
            reply_markup=reply_markup)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Assʋɾez-νσʋs ʠʋe je sʋis ʋɳ ɑɗɱiɳistɾɑteʋɾ ɗɑɳs le cɧɑt et ɑνec l’ɑʋtσɾisɑtiσɳ ɗ’iɳνiteɾ ɗes ʋtilisɑteʋɾs.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [
            InlineKeyboardButton('Accepteɾ l*iɳɗexɑtiσɳ ✔️',
                                 callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ],
        [
            InlineKeyboardButton('Reʄʋseɾ l*iɳɗexɑtiσɳ ❌',
                                 callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(LOG_CHANNEL,
                           f'#IndexRequest\n\nPar : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username - <code> {chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
                           reply_markup=reply_markup)
    await message.reply('ᒍᥱ ᥒᥱ ⳽ᥙɩ⳽ ρᥲ⳽ ʋotɾᥱ ρoᥙᑲᥱꙆꙆᥱ 🚮, ❌Evıter ὰ l*αvenır de me trαnsférer des fıchıers 📂.\nFɑite pɑr @filmserieshoww')


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("Le numéro de saut doit être un nombre entier.")
        await message.reply(f"Définissez avec succès le numéro de saut comme {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Donnez-moi un numéro de saut")


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    await msg.edit(f"Annuler avec succès!!\n\nEnregistré <code>{total_files}</code> fichiers dans la base de données!\nFichiers en double ignorés: <code>{duplicate}</code>\nMessages supprimés ignorés: <code>{deleted}</code>\nMessages non multimédias ignorés: <code>{no_media + unsupported}</code>(Médias non pris en charge - `{unsupported}` )\nLes erreurs qui se sont produites: <code>{errors}</code>")
                    break
                current += 1
                if current % 20 == 0:
                    can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)
                    await msg.edit_text(
                        text=f"Nombre total de messages récupérés: <code>{current}</code>\nNombre total de messages enregistrés: <code>{total_files}</code>\nFichiers en double ignorés: <code>{duplicate}</code>\nMessages supprimés ignorés: <code>{deleted}</code>\nMessages non multimédias ignorés: <code>{no_media + unsupported}</code>(Médias non pris en charge - `{unsupported}` )\nLes erreurs qui se sont produites: <code>{errors}</code>",
                        reply_markup=reply)
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                media.caption = message.caption
                aynav, vnay = await save_file(media)
                if aynav:
                    total_files += 1
                elif vnay == 0:
                    duplicate += 1
                elif vnay == 2:
                    errors += 1
        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
        else:
            await msg.edit(f'Enregistré avec succès <code>{total_files}</code> vers la base de données!\nFichiers en double ignorés: <code>{duplicate}</code>\nMessages supprimés ignorés: <code>{deleted}</code>\nMessages non multimédias ignorés: <code>{no_media + unsupported}</code>(Médias non pris en charge - `{unsupported}` )\nLes erreurs qui se sont produites: <code>{errors}</code>')
