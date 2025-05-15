import os
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline

load_dotenv(".env2")

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
username = os.getenv("USERNAME")

today = datetime.now().strftime("%Y-%m-%d")
log_file = f"log_{username.strip('@')}_{today}.csv"

if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "status"])

with TelegramClient("session_" + username.strip('@'), api_id, api_hash) as client:
    print(f"✅ Вхід успішний як {username}")
    print("▶️ Старт відстеження онлайн-статусу...")

    last_status = None
    while True:
        try:
            user = client.get_entity(username)
            status = user.status
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if isinstance(status, UserStatusOnline):
                current = "online"
                interval = 3
            elif isinstance(status, UserStatusOffline):
                current = "offline"
                interval = 30
            else:
                current = "unknown"
                interval = 60

            if current != last_status:
                with open(log_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([now, current])
                print(f"[{now}] Статус: {current}")
                last_status = current

            time.sleep(interval)

        except KeyboardInterrupt:
            print("⏹ Завершено вручну")
            break
        except Exception as e:
            print("⚠️ Помилка:", e)
            time.sleep(60)
