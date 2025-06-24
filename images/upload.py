import os
import random
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
 
PRIMARY_API_URL = "https://apis.roblox.com/assets/user-auth/v1/assets"
FALLBACK_API_URL = "https://apis.roblox.com/v1/assets/upload"
FOLDER_NAME = "output"
COOKIE_FILE = "previous_cookie"
 
def format_cookie(raw_value):
    raw_value = raw_value.strip()
    return raw_value if raw_value.startswith(".ROBLOSECURITY=") else f".ROBLOSECURITY={raw_value}"
 
def get_cookie():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            previous = f.read().strip()
        use_prev = input("Use previous cookie? [Y/n] ").strip().lower()
        if use_prev in ("", "y", "yes"):
            return previous
 
    raw_value = ""
    while not raw_value.strip():
        raw_value = input("Enter your .ROBLOSECURITY cookie value only: ").strip()
    formatted = format_cookie(raw_value)
    with open(COOKIE_FILE, "w") as f:
        f.write(formatted)
    return formatted
 
def get_csrf_token(session, headers):
    resp = session.post(PRIMARY_API_URL, headers=headers)
    token = resp.headers.get("X-CSRF-TOKEN")
    if not token:
        raise RuntimeError("❌ Failed to fetch CSRF token. Check your cookie.")
    return token
 
def get_authenticated_user_id(headers):
    resp = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"❌ Failed to fetch authenticated user info: {resp.status_code} {resp.text}")
    return resp.json().get("id")
 
def get_random_name(names_list):
    return random.choice(names_list).strip()
 
def upload_image(filepath, headers, user_id, names_list):
    session = requests.Session()
    headers = headers.copy()
    display_name = get_random_name(names_list)
 
    def attempt(url):
        with open(filepath, "rb") as img:
            files = {"fileContent": (os.path.basename(filepath), img, "image/png")}
            data = {
                "request": (
                    '{"displayName":"' + display_name +
                    '","description":"Decal","assetType":"Decal",'
                    f'"creationContext":{{"creator":{{"userId":{user_id}}},"expectedPrice":0}}}}'
                )
            }
            return session.post(url, headers=headers, files=files, data=data)
 
    resp = attempt(PRIMARY_API_URL)
    if resp.status_code == 403:
        headers["X-CSRF-TOKEN"] = get_csrf_token(session, headers)
        resp = attempt(PRIMARY_API_URL)
 
    if resp.status_code == 200:
        return filepath, True, "primary", resp.text
 
    resp_fb = attempt(FALLBACK_API_URL)
    if resp_fb.status_code == 200:
        return filepath, True, "fallback", resp_fb.text
 
    return filepath, False, f"failed both (primary {resp.status_code}, fallback {resp_fb.status_code})", resp_fb.text
 
def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk
 
def send_images_in_batches(folder_path, headers, user_id):
    valid_ext = (".png", ".jpg")
    image_files = [fn for fn in os.listdir(folder_path) if fn.lower().endswith(valid_ext)]
    if not image_files:
        print("⚠️ No image files found.")
        return
 
    if not os.path.exists("names"):
        print("❌ 'names' file not found.")
        return
 
    with open("names", "r") as f:
        names_list = [line.strip() for line in f if line.strip()]
    if not names_list:
        print("❌ 'names' file is empty.")
        return
 
    while True:
        try:
            batch_size = int(input("How many images to upload at once? (max 7 recommended): ").strip())
            if batch_size < 1 or batch_size > 20:
                print("⚠️ Please enter a number between 1 and 20.")
            else:
                if batch_size > 7:
                    print("⚠️ Warning: uploading more than 7 concurrently may hit rate limits.")
                break
        except ValueError:
            print("⚠️ Invalid number. Please try again.")
 
    delay_between_uploads = 0
    if batch_size == 1:
        delay_input = input("Would you like to set a delay between uploads? [Y/n]: ").strip().lower()
        if delay_input in ("", "y", "yes"):
            delay_between_uploads = float(input("Enter delay time in seconds (e.g., 2.0): ").strip())
 
    for idx, batch in enumerate(chunked_iterable(image_files, batch_size), start=1):
        print(f"\n🔁 Uploading batch {idx} ({len(batch)} images)...")
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [
                executor.submit(upload_image, os.path.join(folder_path, fn), headers, user_id, names_list)
                for fn in batch
            ]
            for future in as_completed(futures):
                filepath, success, method, text = future.result()
                if success:
                    msg = "✅ Uploaded (fallback)" if method == "fallback" else "✅ Uploaded"
                    print(f"{msg} {filepath} via {method}")
                else:
                    print(f"❌ Error with {filepath}: {text}")
                if not success and "403" in text:
                    should_exit = input("❌ 403 error occurred. Would you like to exit? [Y/n]: ").strip().lower()
                    if should_exit in ("", "y", "yes"):
                        print("Exiting script...")
                        return
                if delay_between_uploads > 0:
                    print(f"⏳ Waiting for {delay_between_uploads} seconds before next upload...")
                    time.sleep(delay_between_uploads)
 
def main():
    os.makedirs(FOLDER_NAME, exist_ok=True)
    print(f"Using folder '{FOLDER_NAME}'")
 
    raw_cookie = get_cookie()
    headers = {"Cookie": format_cookie(raw_cookie)}
 
    session = requests.Session()
    headers["X-CSRF-TOKEN"] = get_csrf_token(session, headers)
 
    print("🔍 Fetching authenticated user ID...")
    user_id = get_authenticated_user_id(headers)
    print(f"👤 Authenticated as User ID: {user_id}")
 
    send_images_in_batches(FOLDER_NAME, headers, user_id)
 
if __name__ == "__main__":
    main()
