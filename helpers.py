import requests as r

class HabiticaHelper:

    def __init__( self, user_id, api_key ):
        self.headers={"x-api-user": user_id,
                      "x-api-key":  api_key }
        self.tag_cache={}

    '''
    Gets the ID for a label in habitrpg.
    
    label_name      the name to search for
    create          whether or not to create a label,
                    if it can't be found
    use_cache       if false a new request will be made

    Returns the tag id.
    '''
    def get_tag_id_by_name( self, tag_name, create=True, use_cache=True ):
        if not self.tag_cache or not use_cache:
            resp = r.get( "https://habitica.com/api/v3/tags", headers=self.headers )
            self.tag_cache = resp.json()["data"]

        for tag in self.tag_cache:
            if tag["name"] == tag_name:
                return tag["id"]
        else:
            resp = r.post( "https://habitica.com/api/v3/tags", headers=self.headers, json={"name": tag_name} )
            return self.get_tag_id_by_name( tag_name, use_cache=False )
        
    '''
    Creates a task.
    
    task        a dictionary with:  text        -   The name of the task
                                    date        -   When is it due, if ever.
                                    tags        -   A list of ids (of habitrpg)
                                    completed   -   boolean
                                    type        -   "todo" or "daily"
                                    dateCreated -   Like 2020-12-06T22:59:59.000Z
    
    Returns the task id.
    '''
    def upload_task( self, task ):
        print(task)
        print(self.headers)
        resp = r.post( "https://habitica.com/api/v3/tasks/user", headers=self.headers, json=task )
        print(resp.__dict__) 
        return resp.json()["data"]["id"]

    '''
    Transforms a todoist date string to a habitrpg date string.

    Returns string.
    '''
    def date_t_to_h( self, date_string ):
        if not date_string:
            return ""

        _months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                   "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                   "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
        _l = date_string['date'].split("-")

        year  = _l[0]
        day   = _l[2]
        month = _l[1]
        time  = '23:00:00'

        return "{}-{}-{}T{}.000Z".format( year, month, day, time)

    '''
    Uploads a task object to habitrpg to update the task with id habit_id.

    Returns response as json.
    '''
    def update_task( self, habit_id, task ):
        resp = r.put( "https://habitica.com/api/v3/tasks/" + str(habit_id), headers=self.headers, json=task )

        return resp.json()["data"]

    def download_task( self, habit_id ):
        resp = r.get( "https://habitica.com/api/v3/tasks/" + str(habit_id), headers=self.headers )

        return resp.json()["data"]

    def delete_task( self, habit_id ):
        resp = r.delete( "https://habitica.com/api/v3/tasks/" + str(habit_id), headers=self.headers )

        return 

    def upload_checklist_item( self, task, checklist_id ):
        resp = r.post("https://habitica.com/api/v3/tasks/%s/checklist" % checklist_id, headers=self.headers, json=task )

        try:
           return resp.json()["data"]["checklist"][-1]["id"]
        except KeyError:
            print(resp.json())

        return "0"

    def score_task( self, habit_id, direction="up" ):
        resp = r.post("https://habitica.com/api/v3/tasks/%s/score/%s" % (habit_id, direction), headers=self.headers )


    def checklist_item_is_uploaded( self, item_id, parent_id ):
        if parent_id == "0" or item_id == "0":
            return False

        task = self.download_task( parent_id )

        try:
            if task:
                for child in reversed(task["checklist"]):
                    if child["id"] == item_id:
                        return True
        except KeyError:
            print(task)

        return False



    '''
    Checks if a task is uploaded as a task. Note: check does not work for 
    checklist items. Use checklist_item_is_uploaded, instead.

    Returns boolean. True if it is uploaded.
    '''
    def task_is_uploaded( self, habit_id ):
        return bool( self.download_task( habit_id ) )

    def score_checklist_item( self, item_id, parent_id ):
        resp = r.post( "https://habitica.com/api/v3/tasks/%s/checklist/%s/score" % (parent_id, item_id), headers=self.headers )

    def checklist_item_is_completed( self, item_id, parent_id ):
        if parent_id == "0" or item_id == "0":
            return False

        task = self.download_task( parent_id )

        try:
            if task:
                for child in reversed(task["checklist"]):
                    if child["id"] == item_id:
                        return child["completed"]
        except KeyError:
            print(task)


        return False
