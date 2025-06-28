# WiFi Speed to Discord Webhook Script (Updating Embed)
#
# Description:
# This script measures internet speed hourly and sends the results to Discord.
# It posts a single message and continuously updates it with the latest results.
# The embed also maintains a view of the last x amount speed tests for historical context.
#
#
# Setup:
# 1. Install necessary libraries:
#    pip install speedtest-cli requests ********
#
# 2. Get your Discord Webhook URL from Server Settings -> Integrations -> Webhooks.
#
# 3. Paste the URL into the `DISCORD_WEBHOOK_URL` variable below.
#
# How to Run:
# - Execute from your terminal: python your_script_name.py
# - It will run and post/update a message, then wait an hour.
# - To stop the script, press Ctrl+C.

import speedtest
import requests
from datetime import datetime, timedelta
import time
from collections import deque
import json

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
# You can change the number of historical results to keep
HISTORY_LENGTH = 5

# --- GLOBAL VARIABLES ---
# This will store the ID of the Discord message to be edited.
message_id = None
# A deque is a list-like container with fast appends and pops from either end.
# We use it to efficiently store the last N speed test results.
speed_history = deque(maxlen=HISTORY_LENGTH)

def get_internet_speed():
    """Measures download, upload, and ping. Returns a dict."""
    print("Running speed test... This may take a moment.")
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()
        results_dict = st.results.dict()
        ping = results_dict['ping']
        
        download_mbps = round(download_speed / 1_000_000, 2)
        upload_mbps = round(upload_speed / 1_000_000, 2)
        
        print(f"Speed test complete: ↓{download_mbps} Mbps, ↑{upload_mbps} Mbps, {ping}ms")
        
        return {
            "download": download_mbps,
            "upload": upload_mbps,
            "ping": round(ping, 2),
            "timestamp": datetime.now()
        }
    except Exception as e:
        print(f"An error occurred during the speed test: {e}")
        return None

def format_history_string():
    """Creates a formatted string from the speed history."""
    if not speed_history:
        return "No historical data yet."
    
    # We build the string line by line from our history
    history_lines = []
    # We reverse the deque for display so the newest is at the top
    for entry in reversed(speed_history):
        ts = entry['timestamp'].strftime("%H:%M")
        line = f"`{ts}` - **↓** {entry['download']} Mbps, **↑** {entry['upload']} Mbps, **Ping:** {entry['ping']} ms"
        history_lines.append(line)
        
    return "\n".join(history_lines)

def send_or_edit_discord_message(latest_speed):
    """
    Sends a new message or edits an existing one with the latest speed data.
    """
    global message_id
    if "YOUR_WEBHOOK_URL_HERE" in DISCORD_WEBHOOK_URL:
        print("ERROR: Please replace 'YOUR_WEBHOOK_URL_HERE' with your actual Discord webhook URL.")
        return

    # Build the embed
    embed = {
        "author": {"name": "Live Internet Speed Report"},
        "title": f"Latest: {latest_speed['download']} Mbps Download / {latest_speed['upload']} Mbps Upload",
        "description": f"Last updated: **<t:{int(latest_speed['timestamp'].timestamp())}:F>**",
        "color": 0x3498db,  # A nice blue color
        "fields": [
            {"name": "Download Speed", "value": f"**{latest_speed['download']} Mbps**", "inline": True},
            {"name": "Upload Speed", "value": f"**{latest_speed['upload']} Mbps**", "inline": True},
            {"name": "Latency (Ping)", "value": f"**{latest_speed['ping']} ms**", "inline": True},
            {"name": "Recent History (Newest First)", "value": format_history_string(), "inline": False}
        ],
        "footer": {"text": f"Continuously monitoring every hour. History shows last {HISTORY_LENGTH} tests."}
    }
    
    data = {"embeds": [embed]}
    headers = {"Content-Type": "application/json"}
    
    try:
        if message_id is None:
            # First time running, so we POST to create the message.
            # The `?wait=true` is crucial for getting the message ID back.
            url = DISCORD_WEBHOOK_URL + "?wait=true"
            response = requests.post(url, data=json.dumps(data), headers=headers)
            
            if 200 <= response.status_code < 300:
                # Successfully created message, now save its ID
                message_id = response.json()['id']
                print(f"Successfully created initial message with ID: {message_id}")
            else:
                print(f"Failed to create message. Status: {response.status_code}, Response: {response.text}")

        else:
            # Message already exists, so we PATCH to edit it.
            url = f"{DISCORD_WEBHOOK_URL}/messages/{message_id}"
            response = requests.patch(url, data=json.dumps(data), headers=headers)
            
            if 200 <= response.status_code < 300:
                print(f"Successfully edited message with ID: {message_id}")
            elif response.status_code == 404:
                # The message was deleted in Discord. Reset and try again next cycle.
                print("Message not found (it was likely deleted). Will create a new one on the next run.")
                message_id = None
            else:
                print(f"Failed to edit message. Status: {response.status_code}, Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while communicating with Discord: {e}")

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    try:
        while True:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{current_time}] Starting new speed test cycle.")
            
            speed_results = get_internet_speed()
            
            if speed_results:
                # Add the latest results to our history *before* sending
                # so the update includes the most recent test in its history.
                speed_history.append(speed_results)
                send_or_edit_discord_message(speed_results)
            
            # Wait for 1 hour (3600 seconds) before the next run
            next_run_time = datetime.now() + timedelta(seconds=3600)
            print(f"Test complete. Waiting for 1 hour. Next test at {next_run_time.strftime('%H:%M:%S')}.")
            time.sleep(3600)
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user. Exiting.")
