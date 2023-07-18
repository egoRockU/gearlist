import json 
from main.models import Item

with open('items.json') as f:
    item_json=json.load(f)

for item in item_json:
    item = Item(name=item['name'], category=item['category'], brand=item['brand'], description=item['description'], added_by_id=item['added_by'])
    item.save()