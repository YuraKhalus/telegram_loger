import time
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline
import matplotlib.pyplot as plt



load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
username = os.getenv("USERNAME")

sessions = []
current_session_start = None

csv_file = "sessions_log.csv"
is_new_file = not os.path.exists(csv_file)

client = TelegramClient('online-tracker-session', api_id, api_hash)
client.start()

def get_status():
    user = client.get_entity(username)
    status = user.status
    return status

def log_to_csv(start, end, duration_sec):
    duration_min = round(duration_sec / 60, 2)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(['Start Time', 'End Time', 'Duration (sec)', 'Duration (min)'])
        writer.writerow([
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S"),
            int(duration_sec),
            duration_min
        ])

try:
    print("▶️ Старт відстеження онлайн-статусу...")
    while True:
        status = get_status()
        now = datetime.now()

        if isinstance(status, UserStatusOnline):
            if current_session_start is None:
                current_session_start = now
                print(f"[{now.strftime('%H:%M:%S')}] 🟢 ONLINE")
        else:
            if current_session_start is not None:
                session_end = now
                duration = (session_end - current_session_start).total_seconds()
                sessions.append((current_session_start, session_end, duration))
                log_to_csv(current_session_start, session_end, duration)
                print(f"[{now.strftime('%H:%M:%S')}] 🔴 OFFLINE – {int(duration)} сек.")
                current_session_start = None

        time.sleep(5)

except KeyboardInterrupt:
    print("\n⏹️ Завершено вручну. Створення графіку...")

    start_times = [s[0] for s in sessions]
    durations = [s[2] / 60 for s in sessions]

    plt.figure(figsize=(10, 6))
    plt.bar(start_times, durations, width=0.01, color='skyblue')
    plt.title('Telegram Активність за день')
    plt.xlabel('Час початку сесії')
    plt.ylabel('Тривалість (хв)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)

    today = datetime.now().strftime('%Y-%m-%d')
    plt.savefig(f"activity_{today}.png")
    plt.show()
