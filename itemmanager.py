import item
import helpers

import todoist

import json
import sys
import os

PATH=os.path.expanduser("~/.config")

if not PATH:
    print "How come you have no .config directory in your USER directory?"
    print PATH
    sys.exit(1)
else:
    PATH+="/habitist.data"

class ItemManager:
    def __init__( self, h_api_user, h_api_key, t_api ):
        self.item_list = {}

        self.api = todoist.TodoistAPI( t_api )

        self.api.sync()

        self.habit = helpers.HabiticaHelper( h_api_user, h_api_key )

        temp = self._load_config()

        for _item in self.api.items.all():
            if str(_item["id"]).decode("utf-8") in temp.keys():
                self.item_list[_item["id"]] = item.Item( self.api, self.habit, _item["id"], temp[str(_item["id"]).decode("utf-8")] )
            else:
                self.item_list[_item["id"]] = item.Item( self.api, self.habit, _item["id"] )

    def _load_config( self ):
        try:
            with open( PATH, "r" ) as save_file:
                temp = json.load( save_file )
        except IOError:
            temp = {}

        return temp

    def _save_config( self ):
        temp = {}

        for key in self.item_list.keys():
            temp[key] = self.item_list[key].habit_id

        with open( PATH, "w+" ) as save_file:
            json.dump( temp, save_file )

    def upload_to_habit( self ):

        # upload todos and checklists first

        for _item in self.item_list.values():
            if _item.indent > 1:
                continue

            _item.sync_to_habitrpg()

        for _item in self.item_list.values():
            if _item.indent == 1:
                continue

        self._save_config()

    def delete_all( self ):
        for _item in self.item_list.values():
            if _item.is_checklist_item:
                continue

            _item.delete_from_habitrpg()

        self._save_config()


