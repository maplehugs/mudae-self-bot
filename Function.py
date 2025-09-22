import discum
import json
import time
import requests
import Vars
from discum.utils.slash import SlashCommander

botID = '432610292342587392' 
auth = {'authorization' : Vars.token}
bot = discum.Client(token = Vars.token, log=False)
url = (f'https://discord.com/api/v8/channels/{Vars.channelId}/messages')

def send_daily(bot, botID):
    try:
        daily_command = SlashCommander(bot.getSlashCommands(botID).json()).get(['daily'])
        bot.sendCommand(daily_command)
        print("[+] /daily command sent successfully!")
    except Exception as e:
        print(f"[!] Failed to send /daily command: {e}")

def simpleRoll():
    print("Trying to do Daily Kakera")
    send_daily(bot, botID)
    print(time.strftime("Rolling at %H:%M - %d/%m/%y", time.localtime()))
    i = 1
    x = 0
    claimed = '❤️'
    unclaimed = '🤍'
    kakera = '💎'
    emoji = '🐿️'
    rollCommand = SlashCommander(bot.getSlashCommands(botID).json()).get([Vars.rollCommand])
    continueRolling = True

    rolled_cards = []  # store card info for later evaluation

    while continueRolling == True or x < 4:

        bot.triggerSlashCommand(botID, Vars.channelId, Vars.serverId, data=rollCommand)
        time.sleep(1.8)
        r = requests.get(url, headers=auth)
        jsonCard = json.loads(r.text)

        if (len(jsonCard[0]['content']) != 0):
            x += 1
            continueRolling = False
            continue

        idMessage = (jsonCard[0]['id'])
        try:
            cardName = (jsonCard[0]['embeds'][0]['author']['name'])
            cardSeries = (jsonCard[0]['embeds'][0]['description']).replace('\n', '**').split('**')[0]
            cardPower = int((jsonCard[0]['embeds'][0]['description']).split('**')[1])
        except (IndexError, KeyError, ValueError):
            cardName = 'null'
            cardSeries = 'null'
            cardPower = 0

        rolled_cards.append({
            "id": idMessage,
            "name": cardName,
            "series": cardSeries,
            "power": cardPower
        })

        if not 'footer' in jsonCard[0]['embeds'][0] or not 'icon_url' in jsonCard[0]['embeds'][0]['footer']:
            print(i, ' - ' + unclaimed + ' ---- ', cardPower, ' - ' + cardName + ' - ' + cardSeries)
        else:
            print(i, ' - ' + claimed + ' ---- ', cardPower, ' - ' + cardName + ' - ' + cardSeries)

        components = jsonCard[0].get("components", [])

        if components and "components" in components[0]:
            inner_components = components[0]["components"]
            for comp in inner_components:
                try:
                    cardsKakera = comp["emoji"]["name"]
                    if cardsKakera in Vars.desiredKakeras:
                        x -= 1
                        print(kakera + ' - ' + kakera + ' - Trying to react to ' + cardsKakera + ' of ' + cardName)
                        bot.click(
                            jsonCard[0]['author']['id'],
                            channelID=jsonCard[0]['channel_id'],
                            guildID=Vars.serverId,
                            messageID=jsonCard[0]['id'],
                            messageFlags=jsonCard[0]['flags'],
                            data={'component_type': 2, 'custom_id': comp['custom_id']}
                        )
                        time.sleep(0.5)
                except (KeyError, IndexError):
                    continue

        i += 1

    # --- Selection logic after all rolls ---
    chosen_card = None

    # 1. Desired characters
    for card in rolled_cards:
        if card["name"] in getattr(Vars, "desiredCharacters", []):
            chosen_card = card
            break

    # 2. Desired series
    if not chosen_card:
        for card in rolled_cards:
            if card["series"] in Vars.desiredSeries:
                chosen_card = card
                break

    # 3. Power threshold
    if not chosen_card:
        best_card = None
        for card in rolled_cards:
            if card["power"] >= 500:
                if not best_card or card["power"] > best_card["power"]:
                    best_card = card
        chosen_card = best_card

    if chosen_card:
        print(f"Trying to claim {chosen_card['name']} from {chosen_card['series']} (Power {chosen_card['power']})")
        requests.put(
            f'https://discord.com/api/v8/channels/{Vars.channelId}/messages/{chosen_card["id"]}/reactions/{emoji}/%40me',
            headers=auth
        )
    else:
        print("No desirable card found this round.")

    print('Rolling ended')

    if Vars.pokeRoll:
        print('\nTrying to roll Pokeslot')
        requests.post(url=url, headers=auth, data={'content': '$p'})
