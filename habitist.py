#!/usr/bin/python3 -u

from __future__ import print_function

import sys
import time

import itemmanager

time_to_sleep = 120


def print_help(exit_code=None):
    print("habitist.py -ta TODOIST_API_KEY -hu HABITRPG_API_USER -hk HABITRPG_API_KEY")

    if exit_code is not None:
        sys.exit(exit_code)


if '-h' in sys.argv or '--help' in sys.argv:
    print_help(0)

skip_next = True

habit_api_user = habit_api_key = todoist_api_key = 0

try:
    for index, arg in enumerate(sys.argv):
        if skip_next:
            skip_next = False
            continue

        if arg in ["-ta", "--tapi"]:
            todoist_api_key = sys.argv[index + 1]
            skip_next = True

        if arg in ["-hu", "--huser"]:
            habit_api_user = sys.argv[index + 1]
            skip_next = True

        if arg in ["-hk", "--nkey"]:
            habit_api_key = sys.argv[index + 1]
            skip_next = True
except IndexError:
    print_help(1)


if not all([habit_api_user, habit_api_key, todoist_api_key]):
    print_help(2)

manager = itemmanager.ItemManager(habit_api_user, habit_api_key, todoist_api_key)

while True:
    print("Syncing with habitrpg")

    manager.upload_to_habit()

    print("Syncing complete")

    seconds = 0

    for seconds in range(time_to_sleep):
        print("\rSleeping %i seconds" % (time_to_sleep - seconds), end="")
        time.sleep(1)
    print("\rSlept for %i seconds", seconds)

    print("Updating")

    manager.update()
