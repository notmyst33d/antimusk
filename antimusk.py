import os, pytesseract, uuid
from PIL import Image
from pyrogram import Client, filters
from datetime import datetime

app = Client("antimusk")

banned_words = [
    "elon",
    "musk",
    "elonmusk",
    "tweet",
    "twitter",
    "crypto",
    "blockchain",
    "bitcoin"
]

protected_chats = [
    "me"
]

@app.on_message(filters.chat(protected_chats) & filters.photo)
async def search(client, message):
    request_uuid = str(uuid.uuid4())
    target = "data/" + request_uuid + ".jpg"

    tries = 0
    while True:
        try:
            await message.download(target)
            im = Image.open(target)
            break
        except:
            print(f"[{request_uuid}] Download failed, retrying...")

            message = await app.get_messages(message.chat.id, message.message_id)
            if message.empty:
                print(f"[{request_uuid}] Message was removed before the bot had a chance to download it, thats weird...")
                return

            tries += 1

            if tries == 5:
                print(f"[{request_uuid}] Reached retry limit")
                return

    tessract_data = pytesseract.image_to_string(im).lower()

    for word in banned_words:
        if word in tessract_data:
            await message.reply(f"Found banned word:\n```{word} ({request_uuid})```")

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

app.run()
