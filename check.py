import os
import requests
from ram import RobloxAssetManager  # ensure this import matches your file structure

def get_user_decals(user_id):
    url = f"https://apis.roblox.com/cloud/v2/users/{user_id}/inventory-items"
    headers = {"x-api-key": os.getenv("ROBLOX_API_KEY")}
    decals = []
    cursor = None

    while True:
        params = {"filter": "inventoryItemAssetTypes=DECAL", "maxPageSize": 100, "pageToken": cursor}
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("inventoryItems", [])
        decals.extend(items)
        cursor = data.get("nextPageToken")
        if not cursor:
            break

    return decals

def get_webhook_url():
    webhook_file = "webhook.txt"
    if os.path.exists(webhook_file):
        with open(webhook_file, "r") as f:
            saved_webhook = f.read().strip()
        reuse = input(f"Found saved webhook: {saved_webhook}\nDo you want to reuse this webhook? (y/n): ").strip().lower()
        if reuse == "y":
            return saved_webhook
    # If not reusing, prompt for new webhook and save it
    new_webhook = input("Enter your Discord webhook URL: ").strip()
    with open(webhook_file, "w") as f:
        f.write(new_webhook)
    return new_webhook

def main():
    manager = RobloxAssetManager()
    user_id = input("enter roblox user id: ").strip()
    decals = get_user_decals(user_id)

    if not decals:
        print("no decals found for user")
        return

    print(f"checking {len(decals)} decals...")

    DISCORD_WEBHOOK_URL = get_webhook_url()

    for decal in decals:
        assetId = decal.get("assetDetails", {}).get("assetId")
        if not assetId:
            continue
        try:
            asset_info = manager.get_asset(assetId)
            moderation_state = asset_info.get("moderationResult", {}).get("moderationState")
            if asset_info and moderation_state == "Approved":
                print(f"approved decal found: id {assetId}, name: {asset_info.get('displayName')}")
                manager._send_discord_notification(asset_info, DISCORD_WEBHOOK_URL)
                break
        except Exception as e:
            print("User has a private inventory")
            break
    else:
        print("no approved decals found")

if __name__ == "__main__":
    main()
