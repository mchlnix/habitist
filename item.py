

class Item:
    def __init__( self, api, h_helper, item_id ):
        self.is_repeating = False
        self.is_checklist = False
        self.is_checklist_item = False
        self.h_helper = h_helper
        self.api = api

        self.todoist_id = item_id
        self.habit_id = 0

        self._update()

    def _update( self ):
        _item = self.api.items.get_by_id(self.todoist_id)

        self.content       = _item["content"]
        self.creation_date = _item["date_added"]
        self.due_date      = _item["due_date_utc"]
        self.collapsed     = _item["collapsed"]
        self.priority      = _item["priority"]
        self.completed     = _item["checked"] == 1

        self.tags = [ self.h_helper.get_tag_id_by_name( "p:" + self.api.projects.get_by_id(_item["project_id"])["name"]) ]

        for label in _item["labels"]:
            self.tags += [ self.h_helper.get_tag_by_id( self.api.labels.get_by_id(label) ) ]

        # self.notes = ""

        # for note in _notes:
        #     self.notes += note["content"]
        #     self.notes += "\n\n"

        self.task = {}

        self.task["text"] = self.content
        self.task["date"] = self.h_helper.date_t_to_h( self.due_date )
        self.task["tags"] = self.tags
        self.task["completed"] = self.completed
        self.task["type"] = "todo"
        self.task["dateCreated"] = self.creation_date

    def _check_for_repeating( self ):
        pass

    def sync_with_habitrpg( self ):
        if habitrpg == 0:
            return

        self.task = self.h_helper.download_task( self.habit_id )

    def sync_to_habitrpg( self ):
        if self.habit_id == 0:
            self.habit_id = self.h_helper.upload_task( self.task )
        else:
            self._update()

            self.h_helper.update_task( self.habit_id, self.task )

    def delete_from_habitrpg( self ):
        if self.habit_id == 0: 
            return

        self.h_helper.delete_task( self.habit_id )

