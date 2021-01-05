import re

class Item:
    def __init__( self, api, h_helper, t_id, h_id=0 ):
        self.is_repeating = False
        self.is_checklist = False
        self.is_checklist_item = False

        self.indent = 1
        self.parent = t_id

        self.h_helper = h_helper
        self.api = api

        self.todoist_id = t_id
        self.habit_id = h_id

        self.task = {}
        self.type = "todo"
        self.repeats_on = {}

        self._update_from_todoist()

    def _update_from_todoist( self ):
        _item = self.api.items.get_by_id(self.todoist_id)

        self.content       = _item["content"]
        self.creation_date = _item["date_added"]
        self.due_date      = _item["due"]
        self.collapsed     = _item["collapsed"]
        self.priority      = _item["priority"]
        self.completed     = _item["checked"] == 1
        if 'date_string' in _item:
            if _item["date_string"]:
                self.date_string   = _item["date_string"].lower()
            else:
                self.date_string = ""
        else:
            self.date_string = ""


        self.tags = []

        try:
            self.tags = [ self.h_helper.get_tag_id_by_name( "p:" + self.api.projects.get_by_id(_item["project_id"])["name"]) ]
        except AttributeError:
            print( "Old project was found and skipped, %s" % _item["project_id"] )

        for label in _item["labels"]:
            try:
                self.tags += [ self.h_helper.get_tag_id_by_name( self.api.labels.get_by_id(label)["name"] ) ]
            except AttributeError: # issue #10
                print( "Old label was found, %i" % label )

        # self.notes = ""

        # for note in _notes:
        #     self.notes += note["content"]
        #     self.notes += "\n\n"

        self.repeats_on = {}

        self._check_for_repeating()

        #collapse 4 levels of indentation into 2
        if 'indent' in _item:
            if _item["indent"] > 1 and _item["parent_id"]:
                self.indent = _item["indent"]

                self.is_checklist_item = True

                parent = self.api.items.get_by_id( _item["parent_id"] )

                while parent["indent"] > 1:
                    parent = self.api.items.get_by_id( parent["parent_id"] )

                self.parent = parent["id"]

        self._update_task()

    def _update_task( self ):
        self.task["text"] = self.content
        self.task["date"] = self.h_helper.date_t_to_h( self.due_date )
        self.task["startDate"] = self.h_helper.date_t_to_h( self.due_date )
        self.task["tags"] = self.tags
        self.task["completed"] = self.completed
        self.task["type"] = self.type
        self.task["dateCreated"] = self.creation_date
        self.task["repeat"] = self.repeats_on

    def sync_with_habitrpg( self ):
        if habitrpg == 0:
            return

        self.task = self.h_helper.download_task( self.habit_id )

    def sync_to_habitrpg( self ):
        self._update_from_todoist()
        print(self.habit_id)
        if self.habit_id == 0:
            self.habit_id = self.h_helper.upload_task( self.task )
            return

        habit_task = self.h_helper.download_task( self.habit_id )
        print(habit_task)
        if habit_task["completed"]:
            if not self.task["completed"]: # was uncompleted on todoist?
                if not self.type == "daily": # see issue #1
                    self.h_helper.score_task( self.habit_id, direction="down" )
                else:
                    self.task.pop( "startDate" )

            self.h_helper.update_task( self.habit_id, self.task )

            return

        if not habit_task["completed"]:
            if self.task["completed" ]: # normal todo was completed
                self.h_helper.score_task( self.habit_id )
            elif self.is_repeating:
                if self.type == "daily":
                    date_key = "startDate"
                else:
                    date_key = "date"

                if self.task["date"] != habit_task[date_key]: # TODO actually compare them with >
                    self.h_helper.score_task( self.habit_id )

                    if self.task["type"] == "todo": # dailies renew on their own
                        self.habit_id = self.h_helper.upload_task( self.task ) # make new task and associate it

            # update every time
            self.h_helper.update_task( self.habit_id, self.task ) # just update the task

    def delete_from_habitrpg( self ):
        if self.habit_id == 0:
            return

        self.h_helper.delete_task( self.habit_id )
        self.habit_id = 0

    def _check_for_repeating( self ):
        self.type = "todo"
        self.repeats_on = {}

        year_strings  = ["yearly", "every year"]
        month_strings = ["monthly", "every month"]
        day_strings   = ["daily", "every day", "ev day" ]

        if not self.date_string:
            self.is_repeating = False
            return

        for word, num in zip(
                ["first", "second", "third", "fourth", "fifth",
                 "sixth", "seventh", "eighth", "ninth", "tenth"],
                ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"] ):
            self.date_string = self.date_string.replace( word, num )

        self.repeats_on = {}

        # build the regex for yearly tasks
        ev_yrly  = "(yearly|ev(ery)?( year)?)"
        ev_mthly = "(monthly|ev(ery)?( month)?)"
        ev_daily = "(daily|(ev(ery)?( day)?))"
        on       = "( on)?"
        the_xth  = "(( the)? \\d+(st|nd|rd|th)?)"
        of       = "( of)?"
        month    = "( (jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?" + \
        "|jul(y)?|aug(ust)?|sep(t)?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?))"
        monday   = "mon(day)?"
        tuesday  = "tue(s(day)?)?"
        wednesday = "wed(nesday)?"
        thursday = "thu(r(s(day)?)?)?"
        friday   = "fri(day)?"
        saturday = "sat(urday)?"
        sunday   = "sun(day)?"
        day      = "(%s|%s|%s|%s|%s|%s|%s)" % (monday, tuesday, wednesday, thursday, friday, saturday, sunday)
        re_or    = "|"
        decimals = " \d+"
        stop     = "$"

        yrly_re = re.compile(ev_yrly + on + the_xth + "?" + of + month + the_xth + "?" + re_or + ev_yrly + decimals + stop, re.IGNORECASE ) # https://regex101.com/r/xUnNAT/10

        # build the regex for monthly tasks
        mthly_re = re.compile( ev_mthly + "(" + on + the_xth + day + "?" + re_or + day + "?" + the_xth+ ")"); # https://regex101.com/r/UoiLVm/5

        daily_re = re.compile( ev_daily + " (" + day + re_or + "weekday|weekend|day" + ")" )

        # get yearlies
        if self.date_string in year_strings or re.match( yrly_re, self.date_string ):
            self.is_repeating = True
            return

        # get monthlies
        if self.date_string in month_strings or re.match(mthly_re, self.date_string ):
            self.is_repeating = True
            return

        # get dailies TODO  renew!
        if self.date_string in day_strings or re.match(daily_re, self.date_string ):
            self.is_repeating = True
            self.type = "daily"
            everyday = self.date_string in day_strings
            weekend = re.match( ev_daily + " weekend", self.date_string )
            weekday = re.match( ev_daily + " weekday", self.date_string )
            self.repeats_on = {
                "su": bool( everyday or weekend or re.search(sunday, self.date_string, re.IGNORECASE )),
                "s":  bool( everyday or weekend or re.search(saturday, self.date_string, re.IGNORECASE)),
                "f":  bool( everyday or weekday or re.search(friday, self.date_string, re.IGNORECASE)),
                "th": bool( everyday or weekday or re.search(thursday, self.date_string, re.IGNORECASE)),
                "w":  bool( everyday or weekday or re.search(wednesday, self.date_string, re.IGNORECASE)),
                "t":  bool( everyday or weekday or re.search(tuesday, self.date_string, re.IGNORECASE)),
                "m":  bool( everyday or weekday or re.search(monday, self.date_string, re.IGNORECASE))
            }
            return

