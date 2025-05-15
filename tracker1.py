import os
import time
import csv
import pytz
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline

load_dotenv(".env1")  

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
username = os.getenv("USERNAME")

kyiv_tz = pytz.timezone("Europe/Kyiv")
today = datetime.now(kyiv_tz).strftime("%Y-%m-%d")
log_file = f"logs/log_{username.strip('@')}_{today}.csv"

if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "status"])

session_file = f"sessions/session_{username.strip('@')}"

last_seen_time = None
sleep_mode = False
sleep_start = None
last_recorded_offline = None

with TelegramClient(session_file, api_id, api_hash) as client:
    print(f"✅ Вхід успішний як {username}")
    print("▶️ Старт відстеження онлайн-статусу...")

    last_status = None
    last_activity_time = None

    while True:
        try:
            user = client.get_entity(username)
            status = user.status
            now_dt = datetime.now(kyiv_tz)
            now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
            hour_now = now_dt.hour

            if isinstance(status, UserStatusOnline):
                current = "online"
                interval = 5
                
                # Вихід з режиму сну
                if sleep_mode:
                    duration = now_dt - sleep_start
                    log_msg = f"Пробудження після {duration.seconds // 3600}г {(duration.seconds % 3600) // 60}хв, з останньою активністю о {last_seen_time.strftime('%H:%M')}"
                    with open(log_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([now, log_msg])
                        writer.writerow([now, f"Початок активності о {now_dt.strftime('%H:%M')}"])
                    print(f"[{now}] {log_msg}")
                    sleep_mode = False
                    sleep_start = None

                last_seen_time = now_dt
                last_activity_time = now_dt

            elif isinstance(status, UserStatusOffline):
                current = "offline"

                # Визначення часу останньої активності
                if status.was_online:
                    last_seen_time = status.was_online.astimezone(kyiv_tz)

                # Якщо статус не змінився, але остання активність змінилася
                if last_status == "offline" and last_seen_time and last_recorded_offline != last_seen_time:
                    with open(log_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([now, f"Активність 5 сек о {last_seen_time.strftime('%H:%M')}"])
                    print(f"[{now}] Активність 5 сек о {last_seen_time.strftime('%H:%M')}")
                    last_recorded_offline = last_seen_time

                # Режим сну після 22:00 і понад 2 год офлайн
                if hour_now >= 22 and last_seen_time and (now_dt - last_seen_time > timedelta(hours=2)):
                    interval = 300  # 5 хв
                    if not sleep_mode:
                        sleep_mode = True
                        sleep_start = now_dt
                else:
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
