import os
import sys

VFS_NAME = "vfs"

def parse_input(user_input):
    input = os.path.expandvars(user_input)
    parts = input.split()

    if not parts:
        return None, []
    
    return parts[0], parts[1:]

def cmd_ls(args):
    print(f"ls, Аргументы: {args}")


def cmd_cd(args):
    print(f"cd Аргументы: {args}")


def main():
    while True:
        try:
            prompt = f"{VFS_NAME}:~$ "
            user_input = input(prompt)
            
            cmd, args = parse_input(user_input)
            
            if not cmd:
                continue
                
            if cmd == 'exit':
                break
            elif cmd == 'ls':
                cmd_ls(args)
            elif cmd == 'cd':
                cmd_cd(args)
            else:
                print(f"{cmd}: команда не найдена")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except Exception as e:
            print(f"Ошибка эмулятора: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()




