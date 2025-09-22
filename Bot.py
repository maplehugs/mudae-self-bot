# main.py
import schedule
import time
from Function import simpleRoll
import Vars
from Sniper import start_watcher

print("Starting bot...")

# Start the real-time watcher
start_watcher()

# First roll on start
# simpleRoll()

# Schedule future rolls
timeString = ':' + Vars.repeatMinute
schedule.every().hour.at(timeString).do(simpleRoll)

while True:
    schedule.run_pending()
    time.sleep(1)
