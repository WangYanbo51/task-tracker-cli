# ----------------------------------------------------------
# Title: task-cli.py
# Author: WYB51
# Version: 1.0
# Date: 2026-01-01
# Description: This is a simple Python task manager.
# ----------------------------------------------------------

import json
import sys
from datetime import datetime
import os
import re
from prettytable import PrettyTable

filename = "task.json"
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
is_json_exist = os.path.exists
task_standard = ['pid', 'description', 'status', 'createAt', 'updateAt']
status_standard = ['todo', 'done', 'in-progress']

def check_int(s):
    return re.match(r'^[+-]?[0-9]+$', s)

def write_json(full_task_data):
    global filename
    full_dict = {}
    full_dict['task'] = full_task_data
    with open(filename, "w") as f:
        f.write(json.dumps(full_dict, indent=4))
    return 0

def _fix_pid(data: list):
    IsEdited = False
    for index in range(len(data)):
        if isinstance(data[index], dict):
            if data[index].get('pid') is None:
                tmp_dict = {'pid': index}
                tmp_dict.update(data[index])
                data[index] = tmp_dict
                IsEdited = True
            elif data[index]['pid'] != index:
                data[index]['pid'] = index
                IsEdited = True
    return IsEdited

def _check_task_dict(data):
    if not isinstance(data, dict):
        return False
    for item in task_standard:
        if data.get(item) is None:
            return False
    if data['status'] not in status_standard:
        return False
    return True

def read_json():
    global filename
    file_dict = {}
    if not is_json_exist(filename):
        print_log(f"{filename} not exists, creating it.")
        write_json([])

    with open(filename, "r") as f:
        try:
            file_dict = json.loads(f.read())
        except json.decoder.JSONDecodeError:
            print_log(f"{filename} is invalid, creating new.")
            write_json([])
            return []

    if not isinstance(file_dict, dict) or file_dict.get('task') is None or not isinstance(file_dict['task'], list):
        print_log(f"{filename} is invalid, creating new.")
        write_json([])
        return []

    if _fix_pid(file_dict['task']):
        print_log("PID was somehow broken, fixing it.")
        write_json(file_dict['task'])

    return file_dict['task']

def print_error(message, ending = ""):
    print("\033[1;31mError: \033[0m" + message + ending)

def print_log(message):
    print("\033[1;33mInfo: \033[0m" + message)


def add_task(*args):    # parameter: task_description
    if len(args) < 1:
        print_error("No description for task!")
        return 1
    if len(args) > 1:
        print_error("Too many arguments!")
        return 1

    content = args[0]
    full_task_data = read_json()
    task_dict = {'pid': None,
                 'description': content,
                 'status': 'todo',
                 'createAt': now,
                 'updateAt': now,}

    for i in range(len(full_task_data)):
        if full_task_data[i] is None:
            task_dict['pid'] = i
            full_task_data[i] = task_dict
            break
    else:
        task_dict['pid'] = len(full_task_data)
        full_task_data.append(task_dict)

    for task in full_task_data:
        if task is not None and not _check_task_dict(task):
            print_log(f"Some unexpected change has been in your {filename}, you can add task if you like, but the file will be invalid.")
            print_log(f"You can view {filename} to see what was wrong and type \033[1mdelete\033[0m to delete it, or type \033[1mclean\033[0m to create new.")

    write_json(full_task_data)
    print(f"Task added successfully (PID: {task_dict['pid']})")

def delete_task(*args):   # parameter: pid
    if len(args) < 1:
        print_error("PID not given!")
        return 1
    if len(args) > 1:
        print_error("Too many arguments!")
        return 1

    full_task_data = read_json()
    pid = args[0]

    if not check_int(pid):
        print_error(f"'{pid}' is not a valid number!")
        return 1

    pid = int(pid)
    if len(full_task_data) == 0 or pid >= len(full_task_data) or pid < 0 or full_task_data[pid] is None:
        print_error("Task not found!")
        return 1

    full_task_data[pid] = None
    while len(full_task_data) != 0 and full_task_data[-1] is None:
        full_task_data.pop()

    write_json(full_task_data)

    print(f"Task deleted successfully (PID: {pid})")

def update_task(*args): # parameter: pid, task_description
    if len(args) < 2:
        print_error("Too short arguments!")
        return 1
    if len(args) > 2:
        print_error("Too many arguments!")
        return 1

    pid = args[0]
    content = args[1]
    full_task_data = read_json()

    if not check_int(pid):
        print_error(f"'{pid}' is not a valid number!")
        return 1
    pid = int(pid)
    if len(full_task_data) == 0 or pid >= len(full_task_data) or pid < 0 or full_task_data[pid] is None:
        print_error("Task not found!")
        return 1

    if not _check_task_dict(full_task_data[pid]):
        print_error("Your file has been modified!", ending = " (Try \033[1mclean\033[0m to create new)")
        return 1

    full_task_data[pid]['description'] = content
    full_task_data[pid]['updateAt'] = now

    write_json(full_task_data)

    print(f"Task updated successfully (PID: {pid})")

def _mark_task(*args, status):  # internal marker, parameter: pid, status
    if len(args) < 1:
        print_error("PID not given!")
        return 1
    if len(args) > 1:
        print_error("Too many arguments!")
        return 1

    full_task_data = read_json()

    pid = args[0]
    if not check_int(pid):
        print_error(f"'{pid}' is not a valid number!")
        return 1
    pid = int(pid)
    if len(full_task_data) == 0 or pid >= len(full_task_data) or pid < 0 or full_task_data[pid] is None:
        print_error("Task not found!")
        return 1

    if not _check_task_dict(full_task_data[pid]):
        print_error("Your file has been modified!", ending = " (Try \033[1mclean\033[0m to create new)")
        return 1

    full_task_data[pid]['status'] = status
    full_task_data[pid]['updateAt'] = now

    write_json(full_task_data)

    print(f"Task status updated successfully! (PID: {pid}, status: {status})")

def mark_task_done(*args): # parameter: pid
    _mark_task(*args, status = 'done')

def mark_task_in_progress(*args): # parameter: pid
    _mark_task(*args, status = 'in-progress')

def list_task(*args):  # parameter: status = all
    if len(args) > 1:
        print_error("Too many arguments!")
        return 1
    if len(args) == 0:
        status = 'all'
    elif args[0] in status_standard:
        status = args[0]
    else:
        print_error(f"No status named '{args[0]}'")
        return 1

    full_task_data = read_json()

    table = PrettyTable(['PID', 'description', 'status', 'create_time', 'update_time'])
    if status == 'all':
        for task in full_task_data:
            if task is not None:
                if _check_task_dict(task):
                    table.add_row([task[item] for item in task_standard])
                else:
                    print_error("Your file has been modified!", ending = " (Try \033[1mclean\033[0m to create new)")
                    return 1

    else:
        for task in full_task_data:
            if task is not None:
                if _check_task_dict(task) and task['status'] == status:
                    table.add_row([task[item] for item in task_standard])
                else:
                    print_error("Your file has been modified!", ending = " (Try \033[1mclean\033[0m to create new)")
                    return 1
    print(table)

def clean_task():
    global filename
    if not is_json_exist(filename):
        print_log(f"{filename} not found, creating it.")
    write_json([])
    print(f"{filename} cleaned!")

def print_help():
    print("Usage: ")
    path = os.path.relpath(sys.argv[0])
    if 'py' in path:
        prefix = f"\tpython {path}"
    else:
        prefix = f"\t./{path}"
    print(prefix + " <operation> [...]")
    print()
    print("Operations:")
    print(prefix + " help")
    print(prefix + " version")
    print(prefix + " add [task_description]")
    print(prefix + " update [task_id] [new_task_description]")
    print(prefix + " delete [task_id]")
    print(prefix + " mark-in-progress [task_id]")
    print(prefix + " mark-done [task_id]")
    print(prefix + " list [in-progress/todo/done/all]")
    print(prefix + " clean")

def print_version():
    print("Author: WYB51")
    print("Version: 1.0")


operation_dict = {
    'add': add_task,
    'update': update_task,
    'delete': delete_task,
    'mark-in-progress': mark_task_in_progress,
    'mark-done': mark_task_done,
    'list': list_task,
    'clean': clean_task,
    'help': print_help,
    'version': print_version,
}


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print_error("You haven't given an operation!", " (Try \033[1mhelp\033[0m to get help)")
        sys.exit(1)

    op = operation_dict.get(sys.argv[1])

    if op is None:
        print_error("No operation specified!", " (Try \033[1mhelp\033[0m to get help)")
        sys.exit(1)
    else:
        sys.exit(op(*sys.argv[2:]))
