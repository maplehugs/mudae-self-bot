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
