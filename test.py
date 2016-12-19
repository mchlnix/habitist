#!/usr/bin/python -u

from __future__ import print_function
import todoist 
import helpers
import item
import time

import itemmanager

# All test accounts

todoist_api_key = "842a5fd93a077424ae29e681fb90551653bd8129"
habit_api_user  = "4cd37e0d-e73b-4bd9-b203-38b0eeace872"
habit_api_key   = "cddfbde9-5e50-407f-baa9-8c2ccb8e7506"

manager = itemmanager.ItemManager( habit_api_user, habit_api_key, todoist_api_key )

print( "Syncing with habitrpg" )

manager.upload_to_habit()

print("\rSyncing complete      " )

print( "" )
raw_input( "Check HabitRPG, then press Enter: " )
print( "" )

print( "Deleting items.", end="" )

manager.delete_all()

print( "\rDeleted items  " )

