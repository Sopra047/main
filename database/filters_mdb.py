import pymongo
from pyrogram import enums
from info import DATABASE_URI, DATABASE_NAME
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]



async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    # mycol.create_index([('text', 'text')])

    data = {
        'text':str(text),
        'reply':str(reply_text),
        'btn':str(btn),
        'file':str(file),
        'alert':str(alert)
    }

    try:
        mycol.update_one({'text': str(text)},  {"$set": data}, upsert=True)
    except:
        logger.exception('𝖴𝗇𝖾 𝖾𝗋𝗋𝖾𝗎𝗋 𝗌’𝖾𝗌𝗍 𝗉𝗋𝗈𝖽𝗎𝗂𝗍𝖾!', exc_info=True)
             
     
async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    
    query = mycol.find( {"text":name})
    # query = mycol.find( { "$text": {"$search": name}})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            try:
                alert = file['alert']
            except:
                alert = None
        return reply_text, btn, alert, fileid
    except:
        return None, None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file['text']
            texts.append(text)
    except:
        pass
    return texts


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    
    myquery = {'text':text }
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  𝖲𝗎𝗉𝗉𝗋𝗂𝗆𝖾́. 𝖩𝖾 𝗇𝖾 𝗋𝖾́𝗉𝗈𝗇𝖽𝗋𝖺𝗂 𝗉𝗅𝗎𝗌 𝖺̀ 𝖼𝖾 𝖿𝗂𝗅𝗍𝗋𝖾.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("𝖨𝗆𝗉𝗈𝗌𝗌𝗂𝖻𝗅𝖾 𝖽𝖾 𝗍𝗋𝗈𝗎𝗏𝖾𝗋 𝖼𝖾 𝖿𝗂𝗅𝗍𝗋𝖾!", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"𝖱𝗂𝖾𝗇 𝖺̀ 𝗌𝗎𝗉𝗉𝗋𝗂𝗆𝖾𝗋 𝖽𝖺𝗇𝗌 {title}!")
        return

    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"Tous les filtres de {title} 𝗈𝗇𝗍 𝖾́𝗍𝖾́ 𝗌𝗎𝗉𝗉𝗋𝗂𝗆𝖾́")
    except:
        await message.edit_text("𝖨𝗆𝗉𝗈𝗌𝗌𝗂𝖻𝗅𝖾 𝖽𝖾 𝗌𝗎𝗉𝗉𝗋𝗂𝗆𝖾𝗋 𝗍𝗈𝗎𝗌 𝗅𝖾𝗌 𝖿𝗂𝗅𝗍𝗋𝖾𝗌 𝖽𝗎 𝗀𝗋𝗈𝗎𝗉𝖾!")
        return


async def count_filters(group_id):
    mycol = mydb[str(group_id)]

    count = mycol.count()
    return False if count == 0 else count


async def filter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count()
        totalcount += count

    totalcollections = len(collections)

    return totalcollections, totalcount
