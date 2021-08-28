import os, pytesseract, uuid, json
from PIL import Image
from pyrogram import Client, filters, idle
from datetime import datetime

empty_chat_data = {
    "blocked_words": [],
    "whitelist": []
}

with open("config.json", "r") as f:
    config = json.loads(f.read())

def dump_config():
    with open("config.json", "w") as f:
        f.write(json.dumps(config, indent=4))

app = Client("antimusk", config["api_id"], config["api_hash"], bot_token=config["bot_token"]).start()
me = app.get_me()

def split_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def check_protected_filter(_, client, message):
    if config["chats"].get(str(message.chat.id)):
        return True

async def check_authorized_filter(_, client, message):
    if message.from_user.id in config["authorized_users"] or message.from_user.username in config["authorized_users"]:
        return True

async def check_not_whitelisted_filter(_, client, message):
    if str(message.from_user.id) not in config["chats"].get(str(message.chat.id), empty_chat_data)["whitelist"]:
        return True

async def check_not_edited_filter(_, client, message):
    if not message.edit_date:
        return True

check_protected = filters.create(check_protected_filter)
check_authorized = filters.create(check_authorized_filter)
check_not_whitelisted = filters.create(check_not_whitelisted_filter)
check_not_edited = filters.create(check_not_edited_filter)

# Special filter for unprotected chats
async def unprotected_chat(message):
    if message.chat.type == "private":
        return True

    if not config["chats"].get(str(message.chat.id)):
        await message.reply("This chat is not protected, ask bot admins to add it to protected chats.")
        return True
    else:
        return False

# Special filter for handling admin commands
# Its not a direct filter because it relies on client.get_chat_member() which can cause FloodWait error if overused
async def not_admin(client, message):
    if message.chat.type == "private":
        return True

    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "administrator" or user.status == "creator":
        return False
    else:
        return True

@app.on_message(check_not_edited & filters.command(["start", f"start@{me.username}"]))
async def start(client, message):
    if message.chat.type == "private":
        buffer = "Hello, if you would like to add your chat to protected chats, you can ask any one of these bot admins:\n"

        try:
            users = await client.get_users(config["authorized_users"])
        except:
            return await message.reply("Something went wrong while trying to get authorized users, this can happen if you added an ID to your authorized users, tell the user with that ID to interact with the bot, if problem persists check the configuration file")

        for user in users:
            if user.username:
                buffer += f"• @{user.username}\n"
            else:
                buffer += f"• [{user.first_name}](tg://user?id={user.id})\n"

        return await message.reply(buffer)

@app.on_message(check_not_whitelisted & check_protected & check_not_edited & filters.photo)
async def ocr_search(client, message):
    request_uuid = str(uuid.uuid4())
    target = "data/" + request_uuid + ".jpg"

    await message.download(target)
    im = Image.open(target)

    tessract_data = pytesseract.image_to_string(im).lower()
    tessract_data_split = tessract_data.split(" ")

    for word in config["chats"][str(message.chat.id)]["blocked_words"]:
        if word in tessract_data_split:
            await message.reply(f"Found blocked word: `{word}`\nRequest UUID: {request_uuid}")

            try:
                await message.delete()
            except:
                await message.reply("Unfortunately i cant delete this message for some reason")

            with open("log.txt", "a") as f:
                f.write(
                    "Date: {}\n".format(datetime.now().strftime("%d.%m.%Y %H:%M:%S")) +
                    f"Match: {word}\n"
                    f"UUID: {request_uuid}\n"
                    f"Chat: {message.chat.id} ({message.chat.username})\n"
                    "=== Tesseract data ===\n" +
                    tessract_data +
                    "\n======================\n\n\n\n"
                )

            im.close()
            return

    im.close()
    os.remove(target)

@app.on_message(check_authorized & check_not_edited & filters.command(["reload", f"reload@{me.username}"]))
async def reload(client, message):
    with open("config.json", "r") as f:
        config = json.loads(f.read())

    await message.reply("Config successfully reloaded")

@app.on_message(check_authorized & check_not_edited & filters.command(["protect", f"protect@{me.username}"]))
async def protect(client, message):
    if message.chat.type == "private":
        args = message.text.split(" ")

        if len(args) < 2:
            return await message.reply("You need to provide chat username or ID")

        try:
            chat = await client.get_chat(args[1])
        except:
            return await message.reply("Chat not found, you need to add the bot in the chat")

        chat_id = str(chat.id)
    else:
        chat_id = str(message.chat.id)

    if chat_id in config["chats"]:
        return await message.reply("This chat is already protected")

    config["chats"][chat_id] = empty_chat_data

    dump_config()

    await message.reply("Added to protected chats")

@app.on_message(check_authorized & check_not_edited & filters.command(["unprotect", f"unprotect@{me.username}"]))
async def unprotect(client, message):
    if message.chat.type == "private":
        args = message.text.split(" ")

        if len(args) < 2:
            return await message.reply("You need to provide chat username or ID")

        try:
            chat = await client.get_chat(args[1])
        except:
            return await message.reply("Chat not found, you need to add the bot in the chat")

        chat_id = str(chat.id)
    else:
        chat_id = str(message.chat.id)

    if chat_id not in config["chats"]:
        return await message.reply("This chat is not protected")

    del config["chats"][chat_id]

    dump_config()

    await message.reply("Removed from protected chats")

@app.on_message(check_not_edited & filters.command(["blockword", f"blockword@{me.username}"]))
async def blockword(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    args = message.text.split(" ")

    if len(args) < 2:
        return await message.reply("Please provide a word or a list of words")

    args.pop(0)

    for word in args:
        if word.lower() not in config["chats"][str(message.chat.id)]["blocked_words"]:
            config["chats"][str(message.chat.id)]["blocked_words"].append(word.lower())

    dump_config()

    await message.reply("Added to blocked words")

@app.on_message(check_not_edited & filters.command(["unblockword", f"unblockword@{me.username}"]))
async def unblockword(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    args = message.text.split(" ")

    if len(args) < 2:
        return await message.reply("Please provide a word or a list of words")

    args.pop(0)

    for word in args:
        if word.lower() in config["chats"][str(message.chat.id)]["blocked_words"]:
            config["chats"][str(message.chat.id)]["blocked_words"].remove(word.lower())

    dump_config()

    await message.reply("Removed from blocked words")

@app.on_message(check_not_edited & filters.command(["listblockedwords", f"listblockedwords@{me.username}"]))
async def listblockedwords(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    buffer = "Blocked words:\n"

    for word in config["chats"][str(message.chat.id)]["blocked_words"]:
        buffer += f"• `{word}`\n"

    await message.reply(buffer)

@app.on_message(check_not_edited & filters.command(["listwhitelist", f"listwhitelist@{me.username}"]))
async def listwhitelist(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    buffer = "Whitelisted users:\n"

    user_lists = split_list(config["chats"][str(message.chat.id)]["whitelist"], 200)

    for user_list in user_lists:
        try:
            users = await client.get_users(user_list)
            for user in users:
                buffer += f"• `{user.id} ({user.first_name})`\n"
        except Exception as e:
            buffer += str(e)

    await message.reply(buffer)

@app.on_message(check_not_edited & filters.command(["whitelist", f"whitelist@{me.username}"]))
async def whitelist(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    args = message.text.split(" ")

    if len(args) < 2:
        return await message.reply("Please provide a username or ID")

    try:
        user = await client.get_users(args[1])
    except:
        return await message.reply("User not found")

    if user.id == me.id:
        return await message.reply("I cant whitelist myself")

    if str(user.id) in config["chats"][str(message.chat.id)]["whitelist"]:
        return await message.reply("This user is already whilelisted")

    config["chats"][str(message.chat.id)]["whitelist"].append(str(user.id))

    dump_config()

    await message.reply("User whitelisted")

@app.on_message(check_not_edited & filters.command(["unwhitelist", f"unwhitelist@{me.username}"]))
async def unwhitelist(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    args = message.text.split(" ")

    if len(args) < 2:
        return await message.reply("Please provide a username or ID")

    try:
        user = await client.get_users(args[1])
    except:
        return await message.reply("User not found")

    if str(user.id) not in config["chats"][str(message.chat.id)]["whitelist"]:
        return await message.reply("This user is not whilelisted")

    config["chats"][str(message.chat.id)]["whitelist"].remove(str(user.id))

    dump_config()

    await message.reply("User unwhitelisted")

@app.on_message(check_not_edited & filters.command(["clearblockedwords", f"clearblockedwords@{me.username}"]))
async def clearblockedwords(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    config["chats"][str(message.chat.id)]["blocked_words"] = []

    dump_config()

    await message.reply("Blocked words cleared")

@app.on_message(check_not_edited & filters.command(["clearwhitelist", f"clearwhitelist@{me.username}"]))
async def clearwhitelist(client, message):
    if await unprotected_chat(message) or await not_admin(client, message): return

    config["chats"][str(message.chat.id)]["whitelist"] = []

    dump_config()

    await message.reply("Whitelist cleared")

print("AntiMusk started")
idle()