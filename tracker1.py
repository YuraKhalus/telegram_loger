import os
import time
import csv
import pytz
from datetime import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from datetime import datetime

load_dotenv(".env1")  

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
username = os.getenv("USERNAME")

today = datetime.now(pytz.timezone("Europe/Kyiv")).strftime("%Y-%m-%d")
log_file = f"logs/log_{username.strip('@')}_{today}.csv"

if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "status"])

session_file = f"sessions/session_{username.strip('@')}"
with TelegramClient(session_file, api_id, api_hash) as client:
    print(f"✅ Вхід успішний як {username}")
    print("▶️ Старт відстеження онлайн-статусу...")

    last_status = None
    while True:
        try:
            user = client.get_entity(username)
            status = user.status
            kyiv_tz = pytz.timezone("Europe/Kyiv")
            now = datetime.now(kyiv_tz).strftime("%Y-%m-%d %H:%M:%S")

            if isinstance(status, UserStatusOnline):
                current = "online"
                interval = 8
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
