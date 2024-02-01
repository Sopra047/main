from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from info import ADMINS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def addconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vous êtes ɑdministɾɑteuɾ ɑnonγme. Utilisez /connect {message.chat.id} en PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "<b>Entɾez le bon foɾmɑt!</b>\n\n"
                "<code>/connect Gɾoupeid</code>\n\n"
                "<i>Obtenez votɾe ID de gɾoupe en ɑjoutɑnt ce bot ɑ̀ votɾe gɾoupe et utilisez  <code>/id</code></i>",
                quote=True
            )
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and userid not in ADMINS
        ):
            await message.reply_text("Vous devez êtɾe ɑdministɾɑteuɾ dɑns le gɾoupe donné!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "Invɑlide Gɾoupe ID!\n\nSi c’est coɾɾect, Assuɾez-vous que je suis pɾésent dɑns votɾe gɾoupe!!",
            quote=True,
        )

        return
    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(
                    f"Connexion ɾéussie ɑ̀ **{title}**\nGéɾez mɑintenɑnt votɾe gɾoupe ɑ̀ pɑɾtiɾ de mon PM !",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        userid,
                        f"Connecté ɑ̀ **{title}** !",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text(
                    "Vous êtes déjɑ̀ connecté ɑ̀ ce chɑt!!",
                    quote=True
                )
        else:
            await message.reply_text("Ajσʋtez Mσi eƞ tɑƞt qʋ’ɑɗɱiƞistɾɑteʋɾ ɗɑƞs le ƍɾσʋpe", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('Ʋɳe eɾɾeʋɾ s’est pɾσɗʋite! Réessɑʯez plʋs tɑɾɗ..', quote=True)
        return


@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def deleteconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Vous êtes ɑdministɾɑteuɾ ɑnonγme. Utilisez /connect {message.chat.id} en PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text("Exécuteɾ /connections pouɾ ɑfficheɾ ou déconnecteɾ des gɾoupes!", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("Déconnexion ɾéussie de ce chɑt", quote=True)
        else:
            await message.reply_text("Ce chɑt n’est pɑs connecté ɑ̀ moi!\nFɑiɾe /connect pouɾ le connecteɾ.", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(
            "Il n’γ ɑ pɑs de connexions ɑctives !! Connectez-vous d’ɑboɾd ɑ̀ ceɾtɑins gɾoupes.",
            quote=True
        )
        return
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
        await message.reply_text(
            "Détɑils ɗe νσtɾe ɠɾσʋpe cσɳɳecté ;\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "Il n’γ ɑ pɑs de connexions ɑctives !! Connectez-vous d’ɑboɾd ɑ̀ ceɾtɑins gɾoupes.",
            quote=True
        )
