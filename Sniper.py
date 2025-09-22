import threading
import requests
import discum
import Vars
import time
import re

from Vars import power_threshold

auth = {'authorization': Vars.token}
channelID = Vars.channelId
emoji = '💕'

bot = discum.Client(token=Vars.token, log=False)

claimed = '❤️'
unclaimed = '💔'
kakera_emoji = '💎'
power_threshold = Vars.power_threshold

def react_to_card(message):
    embeds = message.get('embeds', [])
    if not embeds:
        return

    try:
        card_name = embeds[0]['author']['name']
        description = embeds[0]['description']
        card_series = description.replace('\n', '**').split('**')[0].strip()
        # Remove any trailing Discord emoji mentions like <:male:123456789>
        card_series = re.sub(r'<:[^:]+:\d+>$', '', card_series).strip()

        try:
            card_power = int(description.split('**')[1])
        except (IndexError, ValueError):
            card_power = 0

        # Determine claimed/unclaimed status
        footer = embeds[0].get('footer', {})
        status_emoji = claimed if footer.get('icon_url') else unclaimed

        # General log
        timestamp = time.strftime("%H:%M - %d/%m/%y", time.localtime())
        print(f"{timestamp} - {status_emoji} ---- {card_power} - {card_name} - {card_series}")

        chosen = None

        if Vars.catch_from_characters and card_name in getattr(Vars, "desiredCharacters", []):
            chosen = message
        elif Vars.catch_from_series and card_series in Vars.desiredSeries:
            chosen = message
        elif Vars.catch_from_power and card_power >= power_threshold:
            chosen = message

        if chosen:

            RED = "\033[91m"
            RESET = "\033[0m"

            print(f"{RED}⚠️ {timestamp} - Sniping {card_name} from {card_series} (Power {card_power}) ⚠️{RESET}")

            try:

                time.sleep(0.1)
                requests.put(
                    f'https://discord.com/api/v8/channels/{channelID}/messages/{message["id"]}/reactions/{emoji}/%40me',
                    headers=auth
                )
            except Exception as e:
                print(f"{timestamp} - Failed to react to {card_name}: {e}")

        # Kakera logic: always check for any card
        components = message.get("components", [])
        if components and "components" in components[0]:
            inner_components = components[0]["components"]
            for comp in inner_components:
                try:
                    cardsKakera = comp["emoji"]["name"]
                    if cardsKakera in Vars.desiredKakeras:
                        print(f"{timestamp} - Found Kakera {cardsKakera} for {card_name}, claiming...")
                        bot.click(
                            message['author']['id'],
                            channelID=message['channel_id'],
                            guildID=Vars.serverId,
                            messageID=message['id'],
                            messageFlags=message['flags'],
                            data={'component_type': 2, 'custom_id': comp['custom_id']}
                        )
                        time.sleep(0.5)
                except (KeyError, IndexError):
                    continue

    except (KeyError, IndexError):
        return

@bot.gateway.command
def on_message(resp):
    if resp.event.message:
        message = resp.parsed.auto()
        if message['channel_id'] == channelID:
            react_to_card(message)

def start_gateway():
    bot.gateway.run(auto_reconnect=True)

def start_watcher():
    print("Starting sniper...")
    threading.Thread(target=start_gateway, daemon=True).start()
