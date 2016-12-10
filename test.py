#!/usr/bin/python -u

from __future__ import print_function
import todoist 
import helpers
import item
import time

# All test accounts

todoist_api_key = "842a5fd93a077424ae29e681fb90551653bd8129"
habit_api_user  = "4cd37e0d-e73b-4bd9-b203-38b0eeace872"
habit_api_key   = "cddfbde9-5e50-407f-baa9-8c2ccb8e7506"

api = todoist.TodoistAPI( todoist_api_key )

api.sync()

habit = helpers.HabiticaHelper( habit_api_user, habit_api_key )

items = []

for _item in api.items.all():
    items += [ item.Item( api, habit, _item["id"] ) ]

print( "Syncing with habitrpg", end="" )

for _item in items:
    _item.sync_to_habitrpg()

print("\rSyncing complete      " )

print( "" )
raw_input( "Check HabitRPG, then press Enter: " )
print( "" )

print( "Deleting items.", end="" )

for _item in items:
    _item.delete_from_habitrpg()

print( "\rDeleted items  " )

