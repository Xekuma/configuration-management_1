import os
import sys
import argparse
import json

VFS_NAME = "vfs"

config = {
    'vfs_path': None,
    'script_path': None
}

vfs_data = {}


def load_vfs(vfs_path):
    global vfs_data
    if not vfs_path or not os.path.exists(vfs_path):
        print(f"Внимание: файл VFS '{vfs_path}' не найден. Будет создана пустая VFS в памяти.")
        vfs_data = {"/": {}}
        return
    
    try:
        with open(vfs_path, 'r', encoding='utf-8') as f:
            vfs_data = json.load(f)
    except Exception as e:
        print(f"Ошибка чтения VFS: {e}")
        vfs_data = {"/": {}}


def cmd_vfs_init():
    global vfs_data
    vfs_data = {"/": {}}
    
    vfs_path = config.get('vfs_path')
    if vfs_path:
        try:
            # Очищаем физическое представление (перезаписываем JSON-файл)
            with open(vfs_path, 'w', encoding='utf-8') as f:
                json.dump(vfs_data, f, ensure_ascii=False, indent=4)
            print(f"VFS инициализирована (очищена) и сохранена в {vfs_path}")
        except Exception as e:
            print(f"Ошибка записи VFS: {e}")
    else:
        print("Ошибка: параметр --vfs не был передан при запуске эмулятора.")


def parse_input(user_input):
    input = os.path.expandvars(user_input)
    parts = input.split()

    if not parts:
        return None, []
    
    return parts[0], parts[1:]

def cmd_conf_dump():
    print(f"vfs_path={config['vfs_path']}")
    print(f"script_path={config['script_path']}")


def cmd_ls(args):
    print(f"ls, Аргументы: {args}")


def cmd_cd(args):
    print(f"cd Аргументы: {args}")


def execute_command(cmd, args_list):
    if cmd == 'exit':
        sys.exit(0)
    elif cmd == 'ls':
        cmd_ls(args_list)
    elif cmd == 'cd':
        cmd_cd(args_list)
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


def main():
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
    
    while True:
        try:
            prompt = f"{VFS_NAME}:~$ "
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