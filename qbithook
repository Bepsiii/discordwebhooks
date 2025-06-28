# To use this script please link *this* file to qbit by going to tools > downloads > run when torrent finished > this script
# also get your own webhook for any server you are an administrator of by going to server settings > integrations > webhooks > create new webhook
# Cheers!


import sys
import requests
import json
import datetime

# --- CONFIGURATION ---
# Paste your Discord Webhook URL here 
WEBHOOK_URL = "WEBHOOK HERE"
# --- END CONFIGURATION ---

def send_discord_notification(torrent_name):
    """
    Sends a notification to the configured Discord webhook using an embed.
    """
    if not WEBHOOK_URL.startswith("https://discord.com/api/webhooks/"):
        print("Error: Please provide a valid Discord Webhook URL.")
        return

    headers = {"Content-Type": "application/json"}

    # This is the embed object that creates the rich message
    data = {
        "username": "qBittorrent Notifier",
        "avatar_url": "https://i.imgur.com/gJtA4gT.png",  # qBittorrent icon
        "embeds": [
            {
                "title": "✅ Download Complete",
                "color": 5763719,  # A nice green color
                "fields": [
                    {
                        "name": "Torrent Name",
                        "value": torrent_name,
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Powered by Python & qBittorrent"
                },
                "timestamp": str(datetime.datetime.utcnow().isoformat())
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Successfully sent notification for: {torrent_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord notification: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # The torrent name is passed as a command-line argument from qBittorrent
        torrent_name_arg = ' '.join(sys.argv[1:])
        send_discord_notification(torrent_name_arg)
    else:
        print("This script is intended to be run by qBittorrent.")
        # You can add a test message here if you run the script directly
        # send_discord_notification("Test Torrent: The Big Lebowski (1998)")
