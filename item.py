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

        self._update()

    def _update( self ):
        _item = self.api.items.get_by_id(self.todoist_id)

        self.content       = _item["content"]
        self.creation_date = _item["date_added"]
        self.due_date      = _item["due_date_utc"]
        self.collapsed     = _item["collapsed"]
        self.priority      = _item["priority"]
        self.completed     = _item["checked"] == 1
        self.date_string   = _item["date_string"].lower()

        self.tags = [ self.h_helper.get_tag_id_by_name( "p:" + self.api.projects.get_by_id(_item["project_id"])["name"]) ]

        for label in _item["labels"]:
            self.tags += [ self.h_helper.get_tag_by_id( self.api.labels.get_by_id(label) ) ]

        # self.notes = ""

        # for note in _notes:
        #     self.notes += note["content"]
        #     self.notes += "\n\n"

        self.repeats_on = {}

        self._check_for_repeating()

        self.indent = _item["indent"]

        #collapse 4 levels of indentation into 2

        if _item["indent"] > 1:
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


    def _check_for_repeating( self ):
        self.type = "todo"
        self.repeats_on = {}

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
        on       = "( on)?"
        the_xth  = "(( the)? \\d+(st|nd|rd|th)?)"
        of       = "( of)?"
        month    = "( (jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?" + \
        "|jul(y)?|aug(ust)?|sep(t)?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?))"
        day      = "( mon(day)?|tue(s(day)?)?|wed(nesday)?|thu(r(s(day)?)?)?" + \
                   "|fri(day)?|sat(urday)?|sun(day)?)"
        re_or    = "|"
        decimals = " \d+"
        stop     = "$"

        yrly_re = re.compile(ev_yrly + on + the_xth + "?" + of + month + the_xth + "?" + re_or + ev_yrly + decimals + stop, re.IGNORECASE ) # https://regex101.com/r/xUnNAT/10

        # build the regex for monthly tasks
        mthly_re = re.compile( ev_mthly + "(" + on + the_xth + day + "?" + re_or + day + the_xth+ ")"); # https://regex101.com/r/UoiLVm/5

        # get yearlies
        if self.date_string == "yearly" or self.date_string == "every year" or re.match( yrly_re, self.date_string ):
            print( self.content + " is yearly with " + self.date_string )
            self.is_repeating = True
            return

        # get monthlies
        if self.date_string == "monthly" or self.date_string == "every month" or re.match(mthly_re, self.date_string ):
            print( self.content + " is monthly with " + self.date_string )
            self.is_repeating = True
            return

        # get dailies TODO  renew!
        noStartDate = not re.match( "(after|starting|last|\d+(st|nd|rd|th)|(first|second|third))", self.date_string, re.IGNORECASE )

        needToParse = re.match( "^ev(ery)? [^\d]", self.date_string, re.IGNORECASE) or self.date_string == "daily"

        if needToParse and noStartDate:
            print( self.content + " is daily/weekly with " + self.date_string )

            self.type = 'daily'
            self.is_repeating = True

            everyday = bool( re.match("^ev(ery)? [^(week)]?(?:day|night)", self.date_string, re.IGNORECASE) or self.date_string == "daily")
            weekday = bool(re.match("^ev(ery)? (week)?day", self.date_string, re.IGNORECASE))
            weekend = bool(re.match("^ev(ery)? (week)?end", self.date_string, re.IGNORECASE))

            self.repeats_on = {
                "su": bool( everyday or weekend or re.search("\\bs($| |,|u)", self.date_string, re.IGNORECASE )),
                "s":  bool( everyday or weekend or re.search("\\bsa($| |,|t)", self.date_string, re.IGNORECASE)),
                "f":  bool( everyday or weekday or re.search("\\bf($| |,|r)", self.date_string, re.IGNORECASE)),
                "th": bool( everyday or weekday or re.search("\\bth($| |,|u)", self.date_string, re.IGNORECASE)),
                "w":  bool( everyday or weekday or (re.search("\\bw($| |,|e)", self.date_string, re.IGNORECASE) and not weekend)), # Otherwise also searches weekend
                "t":  bool( everyday or weekday or re.search("\\bt($| |,|u)", self.date_string, re.IGNORECASE)),
                "m":  bool( everyday or weekday or re.search("\\bm($| |,|o)", self.date_string, re.IGNORECASE))
            }

        if not self.is_repeating:
            print( self.content + " did not match anything with " + self.date_string )

    def sync_with_habitrpg( self ):
        if habitrpg == 0:
            return

        self.task = self.h_helper.download_task( self.habit_id )

    def sync_to_habitrpg( self ):
        self._update_task()
        if self.habit_id == 0:
            self.habit_id = self.h_helper.upload_task( self.task )
            return

        self._update()

        task = self.h_helper.download_task( self.habit_id )

        if self.task["completed"] and not task["completed"]: # normal todos completed
            self.h_helper.score_task( self.habit_id )
        elif self.is_repeating:
            if self.task["type"] == "daily": # dailies will renew themselves?
                pass
            #    self.h_helper.score_task( self.habit_id ) # score and mark it done
            elif self.task["date"] != task["date"]: # TODO actually compare them with >
                self.habit_id = self.h_helper.upload_task( self.task ) # make new task and associate it
                self.h_helper.score_task( self.habit_id ) # score and mark it done
            else:
                self.h_helper.update_task( self.habit_id, self.task ) # just update the task


        else:
            self.h_helper.update_task( self.habit_id, self.task ) # just update the task

    def delete_from_habitrpg( self ):
        if self.habit_id == 0:
            return

        self.h_helper.delete_task( self.habit_id )
        self.habit_id = 0

