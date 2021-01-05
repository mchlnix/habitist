#!/usr/bin/python -u

from __future__ import print_function
import todoist 
import helpers
import item
import time
import sys

import itemmanager

time_to_sleep = 30

def print_help():
    print( "habitist.py -ta TODOIST_API_KEY -hu HABITRPG_API_USER -hk HABITRPG_API_KEY" )

if '-h' in sys.argv or '--help' in sys.argv:
    print_help()
    sys.exit(0)

skip_next=True

try:
    for index,arg in enumerate(sys.argv):
        if skip_next:
            skip_next = False
            continue

        if arg in ["-ta", "--tapi"]:
            todoist_api_key = sys.argv[index+1]
            skip_next = True

        if arg in ["-hu", "--huser"]:
            habit_api_user = sys.argv[index+1]
            skip_next = True

        if arg in ["-hk", "--nkey"]:
            habit_api_key = sys.argv[index+1]
            skip_next = True
except:
    print_help()
    sys.exit(1)

manager = itemmanager.ItemManager( habit_api_user, habit_api_key, todoist_api_key )

if not ( todoist_api_key and habit_api_user and habit_api_key ):
    print_help()
    sys.exit(2)

while True:
    print( "Syncing with habitrpg" )

    manager.upload_to_habit()

    print("Syncing complete" )

    for seconds in range(time_to_sleep):
        print( "\rSleeping %i seconds" % (time_to_sleep - seconds), end="")
        time.sleep(1)
    print( "\rSlept for %i seconds", seconds)

    print( "Updating" )

    manager.update()
