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
print('ok')
