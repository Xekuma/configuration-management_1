import os
import sys
import argparse
import json
import base64
import calendar
from datetime import datetime

VFS_NAME = "vfs"
config = {'vfs_path': None, 'script_path': None}
vfs_data = {}
current_path = "/"


def load_vfs(vfs_path):
    global vfs_data, current_path
    current_path = "/"
    if not vfs_path or not os.path.exists(vfs_path):
        msg = f"Внимание: VFS '{vfs_path}' не найден. Создана пустая VFS."
        print(msg)
        vfs_data = {"/": {}}
        return
    try:
        with open(vfs_path, 'r', encoding='utf-8') as f:
            vfs_data = json.load(f)
    except Exception as e:
        print(f"Ошибка чтения VFS: {e}")
        vfs_data = {"/": {}}


def cmd_vfs_init(args=None):
    global vfs_data, current_path
    current_path = "/"
    vfs_data = {"/": {}}
    vfs_path = config.get('vfs_path')
    if not vfs_path:
        print("Ошибка: параметр --vfs не был передан при запуске.")
        return
    try:
        with open(vfs_path, 'w', encoding='utf-8') as f:
            json.dump(vfs_data, f, ensure_ascii=False, indent=4)
        print(f"VFS инициализирована (очищена) и сохранена в {vfs_path}")
    except Exception as e:
        print(f"Ошибка записи VFS: {e}")


def resolve_path(target_path):
    if not target_path or target_path == '.':
        return current_path
    if target_path.startswith('/'):
        parts = target_path.split('/')
    else:
        parts = current_path.split('/') + target_path.split('/')
    resolved = []
    for p in parts:
        if not p or p == '.':
            continue
        if p == '..':
            if resolved:
                resolved.pop()
        else:
            resolved.append(p)
    return '/' + '/'.join(resolved) if resolved else '/'


def get_vfs_node(path):
    if path == '/':
        return vfs_data.get('/', {})
    parts = [p for p in path.split('/') if p]
    curr = vfs_data.get('/', {})
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return None
    return curr


def parse_input(user_input):
    expanded_input = os.path.expandvars(user_input)
    parts = expanded_input.split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def cmd_conf_dump(args=None):
    print(f"vfs_path={config['vfs_path']}")
    print(f"script_path={config['script_path']}")


def format_ls_item(name, node):
    if isinstance(node, dict):
        perms = "drwxr-xr-x"
        size = len(node)
    else:
        perms = "-rw-r--r--"
        try:
            size = len(base64.b64decode(node))
        except Exception:
            size = len(node)
    return f"{perms}\t{size}\t{name}"


def print_ls_dir(node, long_fmt, all_flag):
    items = list(node.keys())
    if all_flag:
        items = [".", ".."] + items
    else:
        items = [k for k in items if not k.startswith('.')]
    if not items:
        return
    if not long_fmt:
        print("  ".join(items))
        return
    for k in items:
        child = node if k in (".", "..") else node[k]
        print(format_ls_item(k, child))


def cmd_ls(args):
    flags = [a for a in args if a.startswith('-') and len(a) > 1]
    targets = [a for a in args if a not in flags] or ["."]
    long_fmt, all_flag = False, False
    for f in flags:
        for ch in f[1:]:
            if ch == 'l':
                long_fmt = True
            elif ch == 'a':
                all_flag = True
            else:
                print(f"ls: неверный ключ — «{ch}»")
                return
    for target in targets:
        path = resolve_path(target)
        node = get_vfs_node(path)
        if node is None:
            print(f"ls: нет доступа к '{target}': Нет такого файла/каталога")
        elif isinstance(node, str):
            name = os.path.basename(path)
            print(format_ls_item(name, node) if long_fmt else name)
        elif isinstance(node, dict):
            if len(targets) > 1:
                print(f"{target}:")
            print_ls_dir(node, long_fmt, all_flag)


def cmd_cd(args):
    global current_path
    if len(args) > 1:
        print("cd: слишком много аргументов")
        return
    target = args[0] if args else "/"
    new_path = resolve_path(target)
    node = get_vfs_node(new_path)
    if node is None:
        print(f"cd: {target}: Нет такого файла или каталога")
    elif not isinstance(node, dict):
        print(f"cd: {target}: Не является каталогом")
    else:
        current_path = new_path


def cmd_find(args):
    target = args[0] if args else "."
    name_filter = args[1] if len(args) > 1 else None
    start_path = resolve_path(target)
    start_node = get_vfs_node(start_path)
    if start_node is None:
        print(f"find: '{target}': Нет такого файла или каталога")
        return

    def walk(path, node):
        basename = os.path.basename(path) if path != '/' else '/'
        if name_filter is None or name_filter in basename:
            print(path)
        if isinstance(node, dict):
            for k, v in node.items():
                next_path = f"/{k}" if path == '/' else f"{path}/{k}"
                walk(next_path, v)

    walk(start_path, start_node)


def parse_head_args(args):
    if not args:
        print("head: пропущен операнд, задающий файл")
        return None, None
    if args[0] != '-n':
        return 10, args[0]
    if len(args) < 3:
        print("head: после '-n' укажите число строк и имя файла")
        return None, None
    try:
        count = int(args[1])
        if count < 0:
            raise ValueError
        return count, args[2]
    except ValueError:
        print(f"head: неверное количество строк: '{args[1]}'")
        return None, None


def cmd_head(args):
    lines_count, target = parse_head_args(args)
    if target is None:
        return
    path = resolve_path(target)
    node = get_vfs_node(path)
    if node is None:
        print(f"head: '{target}': Нет такого файла или каталога")
    elif isinstance(node, dict):
        print(f"head: ошибка чтения '{target}': Это каталог")
    else:
        try:
            content = base64.b64decode(node).decode('utf-8')
            for line in content.splitlines()[:lines_count]:
                print(line)
        except Exception as e:
            print(f"head: ошибка декодирования файла: {e}")


def cmd_cal(args):
    now = datetime.now()
    try:
        if len(args) == 0:
            print(calendar.month(now.year, now.month))
        elif len(args) == 1:
            year = int(args[0])
            if not (1 <= year <= 9999):
                raise ValueError
            print(calendar.calendar(year))
        elif len(args) == 2:
            month, year = int(args[0]), int(args[1])
            if not (1 <= month <= 12 and 1 <= year <= 9999):
                raise ValueError
            print(calendar.month(year, month))
        else:
            print("cal: слишком много аргументов")
    except ValueError:
        print("cal: некорректные аргументы месяца или года")


def mkdir_parents(parts, target):
    curr = vfs_data.get('/', {})
    for p in parts:
        if p not in curr:
            curr[p] = {}
        elif not isinstance(curr[p], dict):
            print(f"mkdir: '{target}': '{p}' не является каталогом")
            return
        curr = curr[p]


def mkdir_one(target, parents_flag):
    path = resolve_path(target)
    if path == '/':
        if not parents_flag:
            print(f"mkdir: '{target}': Файл существует")
        return
    parts = [p for p in path.split('/') if p]
    if parents_flag:
        mkdir_parents(parts, target)
        return
    parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
    dir_name = parts[-1]
    parent = get_vfs_node(parent_path)
    if parent is None:
        print(f"mkdir: '{target}': Нет такого файла или каталога")
    elif not isinstance(parent, dict):
        print(f"mkdir: '{target}': Не является каталогом")
    elif dir_name in parent:
        print(f"mkdir: '{target}': Файл существует")
    else:
        parent[dir_name] = {}


def cmd_mkdir(args):
    parents_flag = '-p' in args
    targets = [a for a in args if a != '-p']
    if not targets:
        print("mkdir: пропущен операнд")
        return
    for target in targets:
        mkdir_one(target, parents_flag)


def remove_single_dir(path, name):
    if path == '/':
        print(f"rmdir: '{name}': Нельзя удалить корневой каталог")
        return False
    if current_path == path or current_path.startswith(path + '/'):
        print(f"rmdir: '{name}': Каталог используется")
        return False
    parts = [p for p in path.split('/') if p]
    parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
    parent = get_vfs_node(parent_path)
    if not isinstance(parent, dict) or parts[-1] not in parent:
        print(f"rmdir: '{name}': Нет такого файла или каталога")
        return False
    node = parent[parts[-1]]
    if not isinstance(node, dict):
        print(f"rmdir: '{name}': Не является каталогом")
        return False
    if len(node) > 0:
        print(f"rmdir: '{name}': Каталог не пуст")
        return False
    del parent[parts[-1]]
    return True


def rmdir_parents(target):
    curr_path = resolve_path(target)
    steps = len([p for p in target.split('/') if p and p != '.'])
    for _ in range(steps):
        if curr_path == '/' or not remove_single_dir(curr_path, curr_path):
            break
        parts = [p for p in curr_path.split('/') if p]
        curr_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'


def cmd_rmdir(args):
    parents_flag = '-p' in args
    targets = [a for a in args if a != '-p']
    if not targets:
        print("rmdir: пропущен операнд")
        return
    for target in targets:
        if parents_flag:
            rmdir_parents(target)
        else:
            remove_single_dir(resolve_path(target), target)


def execute_command(cmd, args_list):
    if cmd == 'exit':
        sys.exit(0)
    commands = {
        'ls': cmd_ls,
        'cd': cmd_cd,
        'find': cmd_find,
        'head': cmd_head,
        'cal': cmd_cal,
        'mkdir': cmd_mkdir,
        'rmdir': cmd_rmdir,
        'conf-dump': cmd_conf_dump,
        'vfs-init': cmd_vfs_init,
    }
    if cmd in commands:
        commands[cmd](args_list)
    else:
        print(f"{cmd}: команда не найдена")
    return True


def run_script(script_path):
    if not os.path.exists(script_path):
        print(f"Ошибка: стартовый скрипт '{script_path}' не найден.")
        return
    with open(script_path, 'r', encoding='utf-8-sig') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            print(f"{VFS_NAME}:{current_path}$ {line}")
            cmd, args_list = parse_input(line)
            if cmd and not execute_command(cmd, args_list):
                break


def print_args():
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки ОС"
    )
    parser.add_argument('--vfs', type=str, help='Путь к VFS')
    parser.add_argument('--script', type=str, help='Путь к скрипту')
    args = parser.parse_args()
    config['vfs_path'] = args.vfs
    config['script_path'] = args.script
    load_vfs(config['vfs_path'])
    print("\n--- Параметры запуска ---")
    print(f"Путь к VFS: {args.vfs}")
    print(f"Путь к скрипту: {args.script}")
    print("-------------------------------------------\n")
    if args.script:
        run_script(args.script)


def main():
    print_args()
    while True:
        try:
            user_input = input(f"{VFS_NAME}:{current_path}$ ")
            cmd, args_list = parse_input(user_input)
            if cmd and not execute_command(cmd, args_list):
                break
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except Exception as e:
            print(f"Ошибка эмулятора: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()