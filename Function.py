import discum
import json
import time
import requests
import Vars
from discum.utils.slash import SlashCommander

botID = '432610292342587392' 
auth = {'authorization' : Vars.token}
bot = discum.Client(token=Vars.token, log=False)
url = f'https://discord.com/api/v8/channels/{Vars.channelId}/messages'

def send_daily(bot, botID):
    try:
        daily_command = SlashCommander(bot.getSlashCommands(botID).json()).get(['dk'])
        bot.triggerSlashCommand(botID, Vars.channelId, Vars.serverId, data=daily_command)
    except Exception:
        pass  # silently ignore errors

def simpleRoll():

    if Vars.daily_kakera:
        send_daily(bot, botID)

    rollCommand = SlashCommander(bot.getSlashCommands(botID).json()).get([Vars.rollCommand])
    continueRolling = True
    x = 0

    while continueRolling or x < 4:
        bot.triggerSlashCommand(botID, Vars.channelId, Vars.serverId, data=rollCommand)
        time.sleep(1.8)

        r = requests.get(url, headers=auth)
        jsonCard = json.loads(r.text)

        if len(jsonCard[0]['content']) != 0:
            x += 1
            continueRolling = False
            continue

    if Vars.pokeRoll:
        requests.post(url=url, headers=auth, data={'content': '$p'})
