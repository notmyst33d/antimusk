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

    await message.download(target)

    im = Image.open(target)

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
                    "=== Tesseract data ===\n" +
                    tessract_data +
                    "\n======================\n\n\n\n"
                )

            break

    im.close()

app.run()