#https://github.com/Joelkb/DQ-the-file-donor

import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS
from database.ia_filterdb import Media, unpack_new_file_id

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    """Suppɾimeɾ plusieuɾs fichieɾs de lɑ bɑse de données"""

    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        logger.info('𝖫𝖾 𝖿𝗂𝖼𝗁𝗂𝖾𝗋 𝖺 𝖾́𝗍𝖾́ 𝗌𝗎𝗉𝗉𝗋𝗂𝗆𝖾́ 𝖺𝗏𝖾𝖼 𝗌𝗎𝖼𝖼𝖾̀𝗌 𝖽𝖾 𝗅𝖺 𝖻𝖺𝗌𝖾 𝖽𝖾 𝖽𝗈𝗇𝗇𝖾́𝖾𝗌.')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            logger.info('𝖫𝖾 𝖿𝗂𝖼𝗁𝗂𝖾𝗋 𝖺 𝖾́𝗍𝖾́ 𝗌𝗎𝗉𝗉𝗋𝗂𝗆𝖾́ 𝖺𝗏𝖾𝖼 𝗌𝗎𝖼𝖼𝖾̀𝗌 𝖽𝖾 𝗅𝖺 𝖻𝖺𝗌𝖾 𝖽𝖾 𝖽𝗈𝗇𝗇𝖾́𝖾𝗌..')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                logger.info('𝖫𝖾 𝖿𝗂𝖼𝗁𝗂𝖾𝗋 𝖺 𝖾́𝗍𝖾́ 𝗌𝗎𝗉𝗉𝗋𝗂𝗆𝖾́ 𝖺𝗏𝖾𝖼 𝗌𝗎𝖼𝖼𝖾̀𝗌 𝖽𝖾 𝗅𝖺 𝖻𝖺𝗌𝖾 𝖽𝖾 𝖽𝗈𝗇𝗇𝖾́𝖾𝗌..')
            else:
                logger.info('𝖥𝗂𝖼𝗁𝗂𝖾𝗋 𝗂𝗇𝗍𝗋𝗈𝗎𝗏𝖺𝖻𝗅𝖾 𝖽𝖺𝗇𝗌 𝗅𝖺 𝖻𝖺𝗌𝖾 𝖽𝖾 𝖽𝗈𝗇𝗇𝖾́𝖾𝗌.')
