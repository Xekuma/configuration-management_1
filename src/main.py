import os
import sys
import argparse
import json
import base64
import calendar
from datetime import datetime

VFS_NAME = "vfs"

config = {
    'vfs_path': None,
    'script_path': None
}

vfs_data = {}
current_path = "/"


def load_vfs(vfs_path):
    global vfs_data, current_path
    current_path = "/"
    if not vfs_path or not os.path.exists(vfs_path):
        print(f"Внимание: файл VFS '{vfs_path}' не найден."
              + " Будет создана пустая VFS в памяти.")
        vfs_data = {"/": {}}
        return
    
    try:
        with open(vfs_path, 'r', encoding='utf-8') as f:
            vfs_data = json.load(f)
    except Exception as e:
        print(f"Ошибка чтения VFS: {e}")
        vfs_data = {"/": {}}


def cmd_vfs_init():
    global vfs_data, current_path
    current_path = "/"
    vfs_data = {"/": {}}
    
    vfs_path = config.get('vfs_path')
    if vfs_path:
        try:
            with open(vfs_path, 'w', encoding='utf-8') as f:
                json.dump(vfs_data, f, ensure_ascii=False, indent=4)
            print(f"VFS инициализирована (очищена) и сохранена в {vfs_path}")
        except Exception as e:
            print(f"Ошибка записи VFS: {e}")
    else:
        print("Ошибка: параметр --vfs не был передан при запуске эмулятора.")


def resolve_path(target_path):
    global current_path
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


def cmd_conf_dump():
    print(f"vfs_path={config['vfs_path']}")
    print(f"script_path={config['script_path']}")


def cmd_ls(args):
    targets = args if args else ["."]
    for target in targets:
        path = resolve_path(target)
        node = get_vfs_node(path)
        
        if node is None:
            print(f"ls: невозможно получить доступ к " 
                  + f"'{target}': Нет такого файла или каталога")
        elif isinstance(node, str):
            print(os.path.basename(path))
        elif isinstance(node, dict):
            if len(targets) > 1:
                print(f"{target}:")
            if node:
                print("  ".join(node.keys()))


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


def cmd_head(args):
    if not args:
        print("head: пропущен операнд, задающий файл")
        return

    lines_count = 10
    target = args[0]

    if args[0] == '-n':
        if len(args) < 3:
            print("head: после '-n' требуется указать количество строк и имя файла")
            return
        try:
            lines_count = int(args[1])
            if lines_count < 0:
                raise ValueError
        except ValueError:
            print(f"head: неверное количество строк: '{args[1]}'")
            return
        target = args[2]

    path = resolve_path(target)
    node = get_vfs_node(path)
    
    if node is None:
        print(f"head: невозможно открыть '{target}' " 
              + "для чтения: Нет такого файла или каталога")
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
            month = int(args[0])
            year = int(args[1])
            if not (1 <= month <= 12) or not (1 <= year <= 9999):
                raise ValueError
            print(calendar.month(year, month))
        else:
            print("cal: слишком много аргументов")
    except ValueError:
        print("cal: некорректные аргументы месяца или года")


def execute_command(cmd, args_list):
    if cmd == 'exit':
        sys.exit(0)
    elif cmd == 'ls':
        cmd_ls(args_list)
    elif cmd == 'cd':
        cmd_cd(args_list)
    elif cmd == 'find':
        cmd_find(args_list)
    elif cmd == 'head':
        cmd_head(args_list)
    elif cmd == 'cal':
        cmd_cal(args_list)
    elif cmd == 'conf-dump':
        cmd_conf_dump()
    elif cmd == 'vfs-init':
        cmd_vfs_init()
    else:
        print(f"{cmd}: команда не найдена")
    return True


def run_script(script_path):
    if not os.path.exists(script_path):
        print(f"Ошибка: стартовый скрипт '{script_path}' не найден.")
        return

    with open (script_path, 'r', encoding='utf-8-sig') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            print(f"{VFS_NAME}:~$ {line}")

            cmd, args_list = parse_input(line)
            if cmd:
                if not execute_command(cmd, args_list):
                    break


def print_args():
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки ОС"
    )
        
    parser.add_argument(
        '--vfs', type=str, help='Путь к физическому расположению VFS'
    )
    
    parser.add_argument(
        '--script', type=str, help='Путь к стартовому скрипту'
    )
    
    args = parser.parse_args()
    
    config['vfs_path'] = args.vfs
    config['script_path'] = args.script
    
    load_vfs(config['vfs_path'])
    
    text = ("\n--- Параметры запуска ---\n"
        + f"Путь к VFS: {args.vfs}\n" 
        + f"Путь к скрипту: {args.script}\n"
    + "-------------------------------------------\n")
    print(text)
    
    if args.script:
        run_script(args.script)


def main():
    print_args()
    
    while True:
        try:
            prompt = f"{VFS_NAME}:{current_path}$ "
            user_input = input(prompt)
            
            cmd, args_list = parse_input(user_input)
            
            if not cmd:
                continue

            if not execute_command(cmd, args_list):
                break
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except Exception as e:
            print(f"Ошибка эмулятора: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()