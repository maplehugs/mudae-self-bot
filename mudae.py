"""Mudae self-bot core: config, gateway sniper, roller, card history and Discord/Telegram alerts."""
import collections
import datetime
import json
import re
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import discum
import requests
from discum.utils.slash import SlashCommander

MUDAE_ID = '432610292342587392'
API = 'https://discord.com/api/v9'
HERE = Path(__file__).parent
CONFIG_FILE = HERE / 'config.json'

DEFAULTS = {
    'token': '',
    'channelId': '',
    'serverId': '',
    'rollCommand': 'wx',
    'autoRoll': True,
    'repeatMinute': 25,
    'pokeRoll': True,
    'dailyKakera': True,
    'catchFromCharacters': True,
    'catchFromSeries': True,
    'catchFromPower': True,
    'minPower': 500,
    'claimDelayMs': 100,  # Mudae ignores claims that land too fast
    'desiredCharacters': [],
    'desiredSeries': [],
    'desiredKakeras': ['kakeraP', 'kakeraY', 'kakeraO', 'kakeraR', 'kakeraW', 'kakeraL'],
    'discordWebhook': '',
    'telegramToken': '',
    'telegramChatId': '',
}

cfg = dict(DEFAULTS)
if CONFIG_FILE.exists():
    cfg.update(json.loads(CONFIG_FILE.read_text(encoding='utf-8')))


def save_config(new):
    """Merge known keys with the right type into cfg and persist it."""
    if not isinstance(new, dict):
        return
    for k, v in new.items():
        if k in DEFAULTS and type(v) is type(DEFAULTS[k]):
            cfg[k] = v
    tmp = CONFIG_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(CONFIG_FILE)
    log('💾 Configuración guardada')


logs = collections.deque(maxlen=300)


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line)
    logs.append(line)


# ---------- history ----------
db = sqlite3.connect(HERE / 'mudae.db', check_same_thread=False)
db.row_factory = sqlite3.Row
db_lock = threading.Lock()
db.execute('''CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY, ts REAL, msg_id TEXT, name TEXT, series TEXT,
    power INTEGER, image TEXT, owned INTEGER, action TEXT DEFAULT 'seen', kakera TEXT)''')


def q(sql, *args):
    with db_lock, db:
        return [dict(r) for r in db.execute(sql, args).fetchall()]


# ---------- alerts ----------
def alert(text, image=None):
    threading.Thread(target=_send_alert, args=(text, image), daemon=True).start()


def _send_alert(text, image):
    if cfg['discordWebhook']:
        try:
            embeds = [{'image': {'url': image}}] if image else []
            requests.post(cfg['discordWebhook'], json={'content': text, 'embeds': embeds}, timeout=10).raise_for_status()
        except requests.RequestException as e:
            log(f'⚠️ Alerta Discord falló: {e}')
    if cfg['telegramToken'] and cfg['telegramChatId']:
        tg = f"https://api.telegram.org/bot{cfg['telegramToken']}/"
        chat = {'chat_id': cfg['telegramChatId']}
        try:
            r = image and requests.post(tg + 'sendPhoto', data={**chat, 'photo': image, 'caption': text}, timeout=10)
            if not (r and r.ok):  # Telegram can't fetch some image hosts; send the link instead
                requests.post(tg + 'sendMessage', data={**chat, 'text': f"{text}\n{image or ''}"}, timeout=10).raise_for_status()
        except requests.RequestException as e:
            log(f'⚠️ Alerta Telegram falló: {type(e).__name__}')  # str(e) would leak the bot token


# ---------- cards ----------
def parse_card(msg):
    """Return the card shown in a Mudae roll embed, or None if the message isn't a card."""
    embeds = msg.get('embeds') or []
    if not embeds or 'author' not in embeds[0] or 'image' not in embeds[0]:
        return None
    e = embeds[0]
    desc = e.get('description', '')
    power = re.search(r'\*\*([\d,]+)\*\*', desc)
    return {
        'msg_id': msg['id'],
        'name': e['author'].get('name', '?'),
        'series': re.sub(r'<a?:\w+:\d+>', '', re.split(r'\n|\*\*', desc)[0]).strip(),
        'power': int(power.group(1).replace(',', '')) if power else 0,
        'image': e['image'].get('url', ''),
        'owned': bool(e.get('footer', {}).get('icon_url')),
    }


def wanted(card, c=cfg):
    """Why we want this card (character > series > power), or None. Case-insensitive."""
    low = lambda xs: {x.strip().lower() for x in xs}
    if c['catchFromCharacters'] and card['name'].lower() in low(c['desiredCharacters']):
        return 'personaje'
    if c['catchFromSeries'] and card['series'].lower() in low(c['desiredSeries']):
        return 'serie'
    if c['catchFromPower'] and card['power'] >= c['minPower']:
        return f"poder ≥ {c['minPower']}"
    return None


# ---------- discord ----------
client = None
me = {}


def click(msg, custom_id):
    client.click(MUDAE_ID, channelID=msg['channel_id'], guildID=msg.get('guild_id'), messageID=msg['id'],
                 messageFlags=msg['flags'], data={'component_type': 2, 'custom_id': custom_id},
                 sessionID=client.gateway.session_id)


def handle(msg):
    card = parse_card(msg)
    if not card:
        return check_marriage(msg.get('content', ''))

    row = q('INSERT INTO cards (ts, msg_id, name, series, power, image, owned) VALUES (?,?,?,?,?,?,?) RETURNING id',
            time.time(), card['msg_id'], card['name'], card['series'], card['power'], card['image'], card['owned'])[0]['id']
    log(f"{'❤️' if card['owned'] else '💔'} {card['power']} - {card['name']} - {card['series']}")

    buttons = [b for r in msg.get('components', []) for b in r.get('components', []) if b.get('custom_id')]
    emoji = lambda b: (b.get('emoji') or {}).get('name') or ''

    reason = not card['owned'] and wanted(card)
    if reason:
        log(f"🎯 Snipeando {card['name']} ({reason})")
        time.sleep(cfg['claimDelayMs'] / 1000)
        heart = next((b for b in buttons if not emoji(b).startswith('kakera')), None)
        if heart:
            click(msg, heart['custom_id'])
        else:
            client.addReaction(msg['channel_id'], msg['id'], '💕')
        q("UPDATE cards SET action='claim' WHERE id=?", row)
        alert(f"🎯 Intentando reclamar **{card['name']}** — {card['series']} ({card['power']}) · {reason}", card['image'])

    for b in buttons:
        if emoji(b) in cfg['desiredKakeras']:
            click(msg, b['custom_id'])
            q('UPDATE cards SET kakera=? WHERE id=?', emoji(b), row)
            log(f"💎 {emoji(b)} en {card['name']}")
            alert(f"💎 Reclamado {emoji(b)} en {card['name']}", card['image'])
            time.sleep(0.5)


def check_marriage(content):
    """Confirm a pending claim when Mudae announces our marriage (any language: match our name + the card)."""
    text = content.lower()
    # ponytail: matches username/global name only; a server nickname won't confirm (the claim alert still fires)
    if not any(n and n.lower() in text for n in (me.get('username'), me.get('global_name'))):
        return
    for c in q("SELECT id, name, image FROM cards WHERE action='claim' AND ts > ?", time.time() - 120):
        if c['name'].lower() in text:
            q("UPDATE cards SET action='married' WHERE id=?", c['id'])
            log(f"💍 ¡Casado con {c['name']}!")
            alert(f"💍 ¡Te casaste con **{c['name']}**!", c['image'])


def on_gateway(resp):
    if resp.event.ready:
        log(f"✅ Conectado como {me.get('username')}")
    elif resp.event.message:
        msg = resp.parsed.auto()
        if msg['channel_id'] == cfg['channelId'] and msg['author']['id'] == MUDAE_ID:
            handle(msg)


def _run_gateway(c):
    try:
        c.gateway.run(auto_reconnect=True)
    except Exception as e:
        log(f'❌ Gateway: {e}')
    if client is c:  # died on its own, not via stop()
        log('⚠️ Bot desconectado')
        alert('⚠️ El bot de Mudae se desconectó')


def start():
    global client, me
    if client:
        return log('El bot ya está corriendo')
    if not (cfg['token'] and cfg['channelId'] and cfg['serverId']):
        return log('❌ Falta token, canal o servidor en la configuración')
    r = requests.get(API + '/users/@me', headers={'authorization': cfg['token']}, timeout=10)
    if not r.ok:
        return log(f'❌ Token inválido (HTTP {r.status_code})')
    me = r.json()
    client = discum.Client(token=cfg['token'], log=False)
    client.gateway.command(on_gateway)
    threading.Thread(target=_run_gateway, args=(client,), daemon=True).start()
    log(f"🚀 Iniciando como {me['username']}")


def stop():
    global client
    c, client = client, None
    if c:
        c.gateway.close()
        log('⏹️ Bot detenido')


def discord_get(path):
    while True:
        r = requests.get(API + path, headers={'authorization': cfg['token']}, timeout=10)
        if r.status_code != 429:
            return r
        time.sleep(r.json().get('retry_after', 1))


_guilds = {}  # token -> guild list, checking Mudae in every server is slow


def guilds(refresh=False):
    """The user's servers, flagged by whether Mudae's slash commands are available there."""
    if refresh or cfg['token'] not in _guilds:
        r = discord_get('/users/@me/guilds')
        if not r.ok:
            raise ValueError(f'Token inválido (HTTP {r.status_code})')

        def info(g):
            idx = discord_get(f"/guilds/{g['id']}/application-command-index")
            apps = idx.json().get('applications', []) if idx.ok else []
            icon = f"https://cdn.discordapp.com/icons/{g['id']}/{g['icon']}.png?size=64" if g.get('icon') else ''
            return {'id': g['id'], 'name': g['name'], 'icon': icon, 'mudae': any(a['id'] == MUDAE_ID for a in apps)}

        with ThreadPoolExecutor(4) as pool:
            _guilds[cfg['token']] = sorted(pool.map(info, r.json()), key=lambda g: (not g['mudae'], g['name'].lower()))
    return _guilds[cfg['token']]


def channels(guild_id):
    """Text channels of a server, in Discord's order, labelled with their category."""
    r = discord_get(f'/guilds/{guild_id}/channels')
    if not r.ok:
        raise ValueError(f'No pude leer los canales (HTTP {r.status_code})')
    chans = r.json()
    cats = {c['id']: c for c in chans if c['type'] == 4}
    # ponytail: no permission math, channels you can't see may be listed too
    text = [c for c in chans if c['type'] in (0, 5)]
    order = lambda c: (cats[c['parent_id']]['position'] if c.get('parent_id') in cats else -1, c['position'])
    return [{'id': c['id'], 'name': c['name'], 'category': cats.get(c.get('parent_id'), {}).get('name', '')}
            for c in sorted(text, key=order)]


def last_reply():
    """Mudae's latest answer to one of *our* slash commands."""
    msgs = client.getMessages(cfg['channelId'], 10).json()
    for m in msgs if isinstance(msgs, list) else []:
        meta = m.get('interaction_metadata') or m.get('interaction') or {}
        if m['author']['id'] == MUDAE_ID and meta.get('user', {}).get('id') == me.get('id'):
            return m


def roll():
    if not client:
        return log('▶️ Inicia el bot antes de rolear')
    ch, guild = cfg['channelId'], cfg['serverId']
    cmds = SlashCommander(client.getSlashCommands(MUDAE_ID).json())
    if cfg['dailyKakera']:
        client.triggerSlashCommand(MUDAE_ID, ch, guild, data=cmds.get(['dk']))
        time.sleep(2)
    log(f"🎲 Roleando /{cfg['rollCommand']}")
    cmd = cmds.get([cfg['rollCommand']])
    for _ in range(30):  # ponytail: hard cap in case "out of rolls" is never detected
        client.triggerSlashCommand(MUDAE_ID, ch, guild, data=cmd)
        time.sleep(2)
        reply = last_reply()
        if reply and not reply.get('embeds'):  # text answer = no rolls left ("Wished by" cards still have embeds)
            log(f"🛑 {reply['content'][:100]}")
            break
    if cfg['pokeRoll']:
        client.sendMessage(ch, '$p')


def run_bg(fn):
    def safe():
        try:
            fn()
        except Exception as e:
            log(f'❌ {fn.__name__}: {e}')
    threading.Thread(target=safe, daemon=True).start()


def next_roll():
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    t = now.replace(minute=cfg['repeatMinute'] % 60)
    return t if t > now else t + datetime.timedelta(hours=1)


def start_scheduler():
    def loop():
        last = None
        while True:
            now = datetime.datetime.now()
            slot = now.strftime('%Y%m%d%H')
            if cfg['autoRoll'] and client and now.minute == cfg['repeatMinute'] and last != slot:
                last = slot
                run_bg(roll)
            time.sleep(10)
    threading.Thread(target=loop, daemon=True).start()


def names():
    """Characters and series seen so far, most frequent first, for autocomplete."""
    pick = lambda col: [r[col] for r in q(f"SELECT {col} FROM cards WHERE {col} != '' GROUP BY {col} ORDER BY count(*) DESC LIMIT 3000")]
    return {'name': pick('name'), 'series': pick('series')}


def state():
    since = time.time() - 86400
    stats = q("""SELECT count(*) seen, sum(action='claim') claims, sum(action='married') married,
                 sum(kakera IS NOT NULL) kakera FROM cards WHERE ts > ?""", since)[0]
    return {
        'running': client is not None,
        'connected': bool(client and client.gateway.READY),
        'user': me.get('username'),
        'nextRoll': next_roll().strftime('%H:%M') if cfg['autoRoll'] else None,
        'stats': {k: v or 0 for k, v in stats.items()},
        'feed': q('SELECT * FROM cards ORDER BY id DESC LIMIT 60'),
        'history': q("SELECT * FROM cards WHERE action != 'seen' OR kakera IS NOT NULL ORDER BY id DESC LIMIT 300"),
        'log': list(logs)[-150:],
    }
