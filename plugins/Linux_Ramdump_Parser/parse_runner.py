"""Runs ramparse in its own console; holds a lock while running and writes the exit code when done."""
import msvcrt
import os
import subprocess


def main():
    lock_file = os.environ['ONEMORE_PARSE_LOCK']
    done_file = os.environ['ONEMORE_PARSE_DONE']
    command = os.environ['ONEMORE_PARSE_CMD']
    print(command)
    lock = open(lock_file, 'w')
    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)

    rc = subprocess.call(command)

    tmp = done_file + '.tmp'
    with open(tmp, 'w') as f:
        f.write(str(rc))
    os.replace(tmp, done_file)

    print("\n解析结束 (exit code {})，按回车关闭窗口".format(rc))
    try:
        input()
    except EOFError:
        pass


if __name__ == '__main__':
    main()
