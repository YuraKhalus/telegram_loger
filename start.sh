#!/bin/bash
echo "▶️ Старт трекінгу акаунтів..."

python tracker1.py &
python tracker2.py &

wait
