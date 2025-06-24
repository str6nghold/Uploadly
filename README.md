# 💌 Uploadly

a suite of scripts to automate roblox decal management: fetch, modify, upload, and notify via discord.

## 🔧 features

- fetch user's decal inventory
- check for approved assets using roblox cloud api
- send discord notifications for approved assets
- batch-modify images by injecting random pixels
- upload images (decals) with fallback support
- randomized naming via a `names` file
- cookie persistence and csrf handling

## 📁 project structure

.
├── main_fetch_and_notify.py # check user decals + notify discord
├── image_editor.py # random pixel editor for decals/models
├── roblox_asset_manager.py # asset api wrapper + discord notifier
├── uploader.py # upload images via roblox api
├── webhook.txt # saved discord webhook
├── previous_cookie # saved .ROBLOSECURITY cookie
├── names # list of possible asset display names
├── output/ # output folder for modified images
├── requirements.txt
└── README.md




## ✅ prerequisites

- python 3.8+
- roblox creator access and valid `.ROBLOSECURITY` cookie
- discord webhook url for notifications
- roblox api key in `.env` file:

ROBLOX_API_KEY=apikey

## 📦 install

pip install -r requirements.txt
🧪 usage
1. check decals & notify if approved


python check.py
prompts for:

- roblox user id
- discord webhook

sends a discord embed if any decal is approved.

2. edit and generate glitched decal variants

python dupe.py
choose folder with images

configure mode (decal/model), pixel count, and generation amount

output saved in output/ within the selected folder.

3. upload to roblox

python upload.py
supports batching and fallback endpoint

uses random names from names file

requires .ROBLOSECURITY cookie (saved after first input)

📝 notes
max 7 concurrent uploads recommended due to rate limits

image editor injects random RGB pixels for subtle obfuscation

discord webhook notification is optional but helpful for alerting

⚠️ disclaimer
this code interfaces with roblox's private/internal apis and may break without notice. use at your own risk.

✨ todo
proper gui for image editing

automatic asset approval check after upload

parallel asset approval scanning
