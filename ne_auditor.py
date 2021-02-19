# NE_auditor v.01
# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
# Да и может он не много (пока).
import os
import shutil
import datetime
from typing import Tuple

v_date_time: str = str(datetime.date.today())
v_ip_list_file: list = 'ne_list.txt'
v_ip_list_file_exist: bool = False
v_path: str = os.getcwd() + '\\audit_result_' + v_date_time
v_nes: tuple = ()

try:
    shutil.rmtree(v_path, ignore_errors=False, onerror=None)
except OSError:
    print (f"Удалить директорию result не удалось")
else:
    pass

try:
    os.mkdir(v_path)
except OSError:
    print (f"Создать директорию result не удалось")
else:
    pass

try:
    open(v_ip_list_file, 'r')
    v_ip_list_file_exist = True
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_ip_list_file}, содержащий построчный список IP-адресов сетевых элементов, не найден.")

v_ne_counter: int = 0
if v_ip_list_file_exist:
    print(f"Список импортирован из файла {v_ip_list_file}:")
    with open(v_ip_list_file, 'r') as v_ipreader:
        v_line: str = v_ipreader.readline()
        while v_line != '':
            v_ne_counter += 1
            v_nes = v_nes + (v_line.rstrip(),)
            print(f"NE-{v_ne_counter}: {v_line}", end='')
            v_line = v_ipreader.readline()
else:
    pass

v_ne_counter: int = 0
for x in v_nes:
    try:
        v_ne_counter += 1
        os.mkdir(v_path + '\\' + f"NE-{v_ne_counter} (" + x + ")")
    except OSError:
        print(f"Создать директорию не удалось")
    else:
        pass

print('\n\n', v_nes)

input()
