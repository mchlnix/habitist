import item
import helpers

import todoist

import json
import sys
import os

PATH=os.path.expanduser("~/.config")

if not PATH:
    print("How come you have no .config directory in your USER directory?")
    print(PATH)
    sys.exit(1)
else:
    PATH+="/habitist.data"

class ItemManager:
    def __init__( self, h_api_user, h_api_key, t_api ):
        self.item_list = {}

        self.api = todoist.TodoistAPI( t_api )

        self.habit = helpers.HabiticaHelper( h_api_user, h_api_key )

        self.update()

    def update( self ):
        self.api.sync()

        temp = self._load_config()
        for _item in self.api.items.all():
            if _item['due']:
                if str(_item["id"]) in temp.keys():
                    self.item_list[_item["id"]] = item.Item( self.api, self.habit, _item["id"], temp[str(_item["id"])] )
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
            try:
                _item.sync_to_habitrpg()
            except Exception as e:
                print('error')
                print(e)

                print( "Failed syncing item: %s" % _item.content)
                
                print( "completed: %s" % _item.completed)
                return

        for _item in self.item_list.values():
            if _item.indent == 1:
                continue
            try:
                if not self.habit.checklist_item_is_uploaded( _item.habit_id, self.item_list[_item.parent].habit_id ):
                    _item.habit_id = self.habit.upload_checklist_item( {"text": _item.content }, self.item_list[_item.parent].habit_id )
            except Exception as e:
                print( str(e))
                print( "Failed uploading checklist item: %s" % _item.content)

            if _item.completed != self.habit.checklist_item_is_completed( _item.habit_id, self.item_list[_item.parent].habit_id): #no support for repeating subtasks
                self.habit.score_checklist_item( _item.habit_id, self.item_list[_item.parent].habit_id )

        self._save_config()

    def delete_all( self ):
        for _item in self.item_list.values():
            if _item.is_checklist_item:
                continue

            _item.delete_from_habitrpg()

        self._save_config()


