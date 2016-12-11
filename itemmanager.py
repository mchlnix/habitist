import item
import helpers

import todoist

class ItemManager:
    def __init__( self, h_api_user, h_api_key, t_api ):
        self.item_list = {}

        self.api = todoist.TodoistAPI( t_api )

        self.api.sync()

        self.habit = helpers.HabiticaHelper( h_api_user, h_api_key )

        for _item in self.api.items.all():
            self.item_list[_item["id"]] = item.Item( self.api, self.habit, _item["id"] )

    def _load_config( self ):
        pass

    def _save_config( self ):
        pass

    def upload_to_habit( self ):

        # upload todos and checklists first

        for _item in self.item_list.values():
            if _item.indent > 1:
                continue

            _item.sync_to_habitrpg()

        for _item in self.item_list.values():
            if _item.indent == 1:
                continue

            self.habit.upload_checklist_item( {"text": _item.content }, self.item_list[_item.parent].habit_id )

    def delete_all( self ):
        for _item in self.item_list.values():
            if _item.is_checklist_item:
                continue

            _item.delete_from_habitrpg()


