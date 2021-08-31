# AntiMusk
Simple bot for deleting crypto scam messages

## How it works
It uses Tesseract OCR to scan photos for blocked words, its primarily used to detect and delete photos like this:
<img src="https://i.imgur.com/dRxf1RU.jpg" width="400">

## Installing
1. `git clone https://github.com/notmyst33d/antimusk`
2. `cd antimusk`
3. Create a copy of `config_template.json` and rename it to `config.json`
4. Replace `api_id` and `api_hash` in `config.json` with your api_id and api_hash from [my.telegram.org](https://my.telegram.org)
5. Get your bot token from [@BotFather](https://t.me/BotFather) and replace `bot_token` in `config.json` with that token
6. `pip install -r requirements.txt`
7. Install Tesseract (i recommend you to use Tesseract 5 since its faster and more accurate)
8. Add your username or ID to `authorized_users` in `config.json`
9. `python antimusk.py`
10. Add protected chats using `/protect` command

After you started the bot it should start waiting for photos in your protected chats, every photo that has a blocked word is saved on your disk and logged to `log.txt`

## Commands
All commands only respond to chat admins, except for `/start`, `/protect`, `/unprotect` and `/reload`
```
/start - Get start message (only PM)
/protect - Add chat to protected chats (only for bot admins)
/unprotect - Remove chat from protected chats (only for bot admins)
/reload - Reload configuration file (only for bot admins)
/blockword - Block a word or a list of words
/unblockword - Unblock a word or a list of words
/whitelist - Add a user to a whitelist
/unwhitelist - Remove a user from a whitelist
/listblockedwords - Get a list of blocked words
/listwhitelist - Get a list of whitelisted users
/clearblockedwords - Clear a list of blocked words
/clearwhitelist - Clear a list of whitelisted users
/silentmode - Toggle silent mode
```
