# habitist

`habitist.py -ta TODOIST_API_KEY -hu HABITRPG_API_USER -hk HABITRPG_API_KEY`

Syncs your todoist tasks to HabitRPG

----------------

Supports:

- Simple Todos as simple Todos
- Repeating tasks as simple Todos, that renew themselves
- Daily and weekly tasks as dailies with streak support
- Labels as tags
- Projects as special `p:project_name` tags
- Subtasks as checklist items

On the short list:
- Bug Fixes?

Sometime, maybe:
- Check if it works with Windows
- Notes into comments
- Special labels for attributes
- Priorities as difficulty?

##INSTALL

Only tested on Linux.

You'll need:
- Python
- [The Python requests library](https://pypi.python.org/pypi/requests) `pip install requests`
- [The Todoist Python API](https://developer.todoist.com/#client-libraries) `pip install todoist-python`

Just drop the files in a directory of your choice, change the testing API keys to your own and run it.

It runs in a continuous loop with a 30 second break. Cancel by Ctrl+C.
