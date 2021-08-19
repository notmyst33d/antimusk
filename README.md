# antimusk
Simple userbot for deleting crypto scam messages

## Installing
1. `git clone https://github.com/notmyst33d/antimusk`
2. `cd antimusk`
3. Replace api_id and api_hash in `config.ini` with your api_id and api_hash from [my.telegram.org](https://my.telegram.org)
4. `pip install -r requirements.txt`
5. Install Tesseract (i recommend you to use Tesseract 5 since its faster and more accurate)
6. Add your chat ID or username to `protected_chats` and optionally add more banned words to `banned_words`
7. `python antimusk.py`

After you started the userbot it should start waiting for photos in your chat, every photo that has a banned word is saved on your disk and logged to `log.txt`
