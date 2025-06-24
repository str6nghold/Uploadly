# roblox_asset_manager.py
import os, requests
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed

load_dotenv()

class RobloxAssetManager:
    ASSETS_BASE = "https://apis.roblox.com/assets/v1"
    ASSET_IMG_URL = "https://www.roblox.com/asset-thumbnail/image?assetId={id}&width=420&height=420"

    def __init__(self):
        self.api_key = os.getenv("ROBLOX_API_KEY")
        if not self.api_key:
            raise ValueError("missing ROBLOX_API_KEY")
        self.headers = {"x-api-key": self.api_key}

    def get_asset(self, asset_id: int) -> dict:
        url = f"{self.ASSETS_BASE}/assets/{asset_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def check_approved(self, asset_id: int, webhook_url: str = None) -> bool:
        data = self.get_asset(asset_id)
        state = data.get("moderationResult", {}).get("moderationState", "")
        approved = bool(state and state.lower() == "approved")
        if approved and webhook_url:
            self._send_discord_notification(data, webhook_url)
        return approved

    def _send_discord_notification(self, data: dict, webhook_url: str):
        asset_id = data["assetId"]
        name = data.get("displayName", "unknown")
        image_url = self.ASSET_IMG_URL.format(id=asset_id)

        webhook = DiscordWebhook(url=webhook_url)
        embed = DiscordEmbed(
            title=f"asset approved 🎉",
            description=f"**{name}** (id: {asset_id}) is now approved.",
            color=0x00ff00
        )
        webhook.add_embed(embed)
        webhook.execute()
