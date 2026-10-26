"""Run: python test_mudae.py"""
import mudae

roll = {
    'id': '1', 'content': 'Wished by @someone',
    'embeds': [{
        'author': {'name': 'Rio Futaba'},
        'description': 'Seishun Buta Yarou <:female:123>\n**1,234**<:kakera:456>\nReact with any emoji to claim!',
        'image': {'url': 'https://mudae.net/rio.png'},
    }],
}
card = mudae.parse_card(roll)
assert card == {'msg_id': '1', 'name': 'Rio Futaba', 'series': 'Seishun Buta Yarou', 'power': 1234,
                'image': 'https://mudae.net/rio.png', 'owned': False}, card
assert mudae.parse_card({'id': '2', 'content': 'out of rolls', 'embeds': []}) is None

claimed = {**roll, 'embeds': [{**roll['embeds'][0], 'footer': {'icon_url': 'https://cdn/x.png'}}]}
assert mudae.parse_card(claimed)['owned'] is True

c = {**mudae.DEFAULTS, 'desiredCharacters': ['rio futaba'], 'desiredSeries': ['Nekopara'], 'minPower': 2000}
assert mudae.wanted(card, c) == 'personaje'
assert mudae.wanted({**card, 'name': 'Mai', 'series': 'NEKOPARA'}, c) == 'serie'
assert mudae.wanted({**card, 'name': 'Mai'}, c) is None
assert mudae.wanted({**card, 'name': 'Mai', 'power': 2000}, c).startswith('poder')
assert mudae.wanted(card, {**c, 'catchFromCharacters': False}) is None
tu = """**onlymaple**, you __can__ claim right now! The next claim reset is in **1h 44** min.
You have **0** rolls left. Next rolls reset in **44** min.
$daily is available!
Stock: **1,342**<:kakera:469835869059153940>

Next $dk in **19h 52** min."""
assert mudae.parse_tu(tu) == {'rolls': 0, 'dk': False, 'daily': True, 'stock': 1342}, mudae.parse_tu(tu)
assert mudae.parse_tu('You have **10** rolls left.\n$dk is ready!') == {'rolls': 10, 'dk': True, 'daily': False, 'stock': None}
k = """You have **342**<:kakera:1>!
 **Bronze 0** · Next level: **1,000**<:kakera:1> +1 wishlist slot
 **Silver 0** · Next level: **2,000**<:kakera:1> +25% wishlist spawn
 **Gold 1** · Next level: **6,000**<:kakera:1> -10% kakera power usage ($ku)
??? · Prerequisites: Bronze I + Silver I + Gold I or 2 badges IV
 **Diamond 0** · Next level: **12,000**<:kakera:1> +1 $ouroharvest ($oh) per day"""
b = mudae.parse_badges(k)
assert b == {'bronze': (0, 1000), 'silver': (0, 2000), 'gold': (1, 6000), 'diamond': (0, 12000)}, b
assert mudae.pick_badge(b, 342) is None
assert mudae.pick_badge(b, 2500) == 'bronze'
assert mudae.pick_badge({**b, 'bronze': (1, 2000)}, 2000) in ('bronze', 'silver')

import datetime
J = datetime.timedelta(minutes=mudae.ROLL_JITTER_MIN)
for minute in (25, 55):
    mudae.cfg['repeatMinute'] = minute
    for h, m in ((14, 0), (14, 30), (14, 50), (23, 59)):
        now = datetime.datetime(2026, 1, 1, h, m)
        for _ in range(200):
            t = mudae.plan_roll(now)
            assert now < t <= now + datetime.timedelta(hours=1) + J, (minute, now, t)
            assert (t.minute - minute) % 60 < mudae.ROLL_JITTER_MIN, (minute, t)
            nxt = mudae.plan_roll(t + J)  # after rolling: next one is in the following hour's window
            assert datetime.timedelta(minutes=45) < nxt - t < datetime.timedelta(minutes=75), (t, nxt)
print('ok')
