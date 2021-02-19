# NE_auditor v.01
# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
# Да и может он не много (пока).
import os
import shutil
import datetime
import getpass


v_login = input("Введите логин аудитора: ")
try:
    v_pass = getpass.getpass("Введите пароль аудитора: ")
except Exception as err:
    print('Ошибка: ', err)
else:
    pass

v_date_time: str = str(datetime.date.today())
v_ip_list_file: str = 'ne_list.txt'
v_commands_file: str = 'ne_commands.txt'
v_commands_file_exist = v_ip_list_file_exist = False
v_path: str = './audit_result_' + v_date_time
v_coms = v_nes = ()  # определяем список команд и список NE

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

try:
    open(v_commands_file_exist, 'r')
    v_commands_file_exist = True
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_commands_file}, содержащий построчный спи6сок команд, не найден.")

v_counter: int = 0
if v_commands_file_exist:
    # print(f"\nСписок импортирован из файла {v_commands_file}:")
    with open(v_commands_file, 'r') as v_commreader:
        v_line: str = v_commreader.readline()
        while v_line:
            v_counter += 1
            v_coms = v_coms + (v_line.rstrip(),)
            # print(f"Команда {v_counter}: {v_line}", end='')
            v_line = v_commreader.readline()
else:
    pass


v_counter: int = 0
if v_ip_list_file_exist:
    # print(f"\n\nСписок импортирован из файла {v_ip_list_file}:")
    with open(v_ip_list_file, 'r') as v_ipreader:
        v_line: str = v_ipreader.readline()
        while v_line:
            v_counter += 1
            v_nes = v_nes + (v_line.rstrip(),)
            # print(f"NE-{v_counter}: {v_line}", end='')
            v_line = v_ipreader.readline()
else:
    pass

v_counter: int = 1
for x in v_nes:
    try:
        os.mkdir(v_path + '\\' + f"NE-{v_counter} (" + x + ")")
    except OSError:
        print(f"Создать директорию не удалось")
    else:
        v_nedir = v_path + '\\' + f"NE-{v_counter} (" + x + ")"
        v_counter += 1
        for v_comanda in v_coms:
            v_filename: str = v_nedir + "\\" + "(" + x + ")_" + v_comanda + ".log"
            with open(v_filename, 'w') as f:
                f.write('new test')
                f.close()
print('\n\n', v_nes)
print('\n\n', v_coms)
