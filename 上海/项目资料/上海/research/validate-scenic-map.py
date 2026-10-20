"""Check the public map's route/shop separation and itinerary consistency."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent.parent
data = json.loads((root/'武康路轻松版/行程数据.json').read_text(encoding='utf-8'))
views = json.loads((root/'research/map-views.json').read_text(encoding='utf-8'))
pins = json.loads((root/'research/map-place-pins.json').read_text(encoding='utf-8'))
points = data['points']
by_id = {v['id']:v for v in views}
days = {d['id']:d for d in data['days']}

for day in range(1,6):
    route = by_id[day]['routes'][0]['route']
    assert route == by_id[day]['description']['route'] == days[day]['route'], day
    assert all(points[key].get('kind') == 'sight' for key in route), (day,route)
    assert all(key in by_id[day]['keys'] for key in route), day
assert by_id[9]['routes'] == [by_id[day]['routes'][0] for day in range(2,6)]
assert all(not any(day in pin['days'] for day in (3,4,5)) for pin in pins if pin['kind']=='shop')
assert len({pin['name'] for pin in pins}) == len(pins)
assert '12:05' in days[1]['mode'] and '15:00' in days[1]['pace']
assert '27日' in days[7]['mode'] or '早享' in days[7]['mode']
print(json.dumps({'scenic_days_checked':5,'unique_reference_pins':len(pins),
                  'city_routes':len(by_id[9]['routes'])},ensure_ascii=False))
