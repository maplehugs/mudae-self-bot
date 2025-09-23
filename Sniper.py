import threading
import requests
import discum
import Vars
import time
import re

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
        # Remove trailing Discord emoji mentions like <:male:123456789>
        card_series = re.sub(r'<:[^:]+:\d+>$', '', card_series).strip()

        try:
            card_power = int(description.split('**')[1])
        except (IndexError, ValueError):
            card_power = 0

        # Claimed/unclaimed status
        footer = embeds[0].get('footer', {})
        status_emoji = claimed if footer.get('icon_url') else unclaimed

        # Log
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
                components = message.get("components", [])
                if components and components[0].get("components"):
                    btn = components[0]["components"][0]  # first button
                    btn_label = btn.get("label")
                    btn_emoji = btn.get("emoji", {}).get("name")
                    btn_id = btn.get("custom_id")

                    print(f"{timestamp} - Found button: label='{btn_label}', emoji='{btn_emoji}', id='{btn_id}'")

                    bot.click(
                        applicationID=message["author"]["id"],  # Mudae bot ID
                        channelID=message["channel_id"],
                        guildID=message.get("guild_id"),
                        messageID=message["id"],
                        messageFlags=message["flags"],
                        data={'component_type': 2, 'custom_id': btn_id},
                        sessionID=bot.gateway.session_id
                    )

                    print(f"{timestamp} - Clicked {btn_emoji or btn_label} for {card_name}")

                else:
                    # fallback to reaction
                    time.sleep(0.1)
                    requests.put(
                        f"https://discord.com/api/v8/channels/{channelID}/messages/{message['id']}/reactions/{emoji}/%40me",
                        headers=auth
                    )
                    print(f"{timestamp} - Reacted to {card_name} with {emoji}")

            except Exception as e:
                print(f"{timestamp} - Failed to snipe {card_name}: {e}")

        # Check all buttons (claim + kakera)
        components = message.get("components", [])
        if components and components[0].get("components"):
            inner_components = components[0]["components"]
            for comp in inner_components:
                try:
                    btn_emoji = comp.get("emoji", {}).get("name")
                    btn_label = comp.get("label")
                    btn_id = comp.get("custom_id")

                    # Debug log
                    print(f"{timestamp} - Found button: label='{btn_label}', emoji='{btn_emoji}', id='{btn_id}'")

                    # If this button matches desired Kakera emojis, click it
                    if btn_emoji in Vars.desiredKakeras:
                        print(f"{timestamp} - Found Kakera {btn_emoji} for {card_name}, claiming...")
                        bot.click(
                            applicationID=message['author']['id'],
                            channelID=message['channel_id'],
                            guildID=Vars.serverId,
                            messageID=message['id'],
                            messageFlags=message['flags'],
                            data={'component_type': 2, 'custom_id': btn_id},
                            sessionID=bot.gateway.session_id
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
