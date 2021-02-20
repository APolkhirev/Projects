"""
NE_auditor v.01
Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
Да и может он не много (пока).
"""
import datetime
import getpass
import os
import shutil
import ff_ipchecker
import ff_access_to_ne

v_date_time: str = str(datetime.date.today())
v_ip_list_file: str = 'ne_list.txt'
v_commands_file: str = 'ne_commands.txt'
v_path: str = './audit_result_' + v_date_time
v_coms = ()  # определяем список команд
v_nes = ()   # определяем список NE

try:
    shutil.rmtree(v_path, ignore_errors=False, onerror=None)
except OSError:
    print("Удалить директорию result не удалось")

try:
    os.mkdir(v_path)
except OSError:
    print("Создать директорию result не удалось")

try:
    """ Считывание IP-адресов из файла в кортеж """
    with open(v_ip_list_file, 'r') as v_ipreader:
        v_readedip: str = v_ipreader.readline()
        v_counter = 1
        while v_readedip:
            v_counter += 1
            if ff_ipchecker.f_checkip(v_readedip.rstrip())[0]:
                v_nes = v_nes + (v_readedip.rstrip(),)
            else:
                print(f"Ошибка в строке [{v_counter}] "
                      f"{v_readedip.rstrip()}: "
                      f"{ff_ipchecker.f_checkip(v_readedip.rstrip())[1]}")
            v_readedip = v_ipreader.readline()
        v_nes = sorted(tuple(set(v_nes)))  # сортируем и убираем дублирующиеся IP'шники
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_ip_list_file}, "
          f"содержащий построчный список IP-адресов сетевых элементов, не найден.")

try:
    """ Считывание списка команд из файла в кортеж """
    with open(v_commands_file, 'r') as v_commreader:
        v_line: str = v_commreader.readline()
        while v_line:
            v_coms = v_coms + (v_line.rstrip(),)
            v_line = v_commreader.readline()
        v_coms = tuple(set(v_coms))  # убираем дублирующиеся команды
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_commands_file}, содержащий построчный список команд, не найден.")

v_login = input("Введите логин: ")
v_pass: str = ''
try:
    v_pass = getpass.getpass("Введите пароль: ")
except Exception as err:
    print('Ошибка: ', err)

v_counter: int = 1
v_access_via: str = ''
for x in v_nes:
    try:
        os.mkdir(v_path + '\\' + f"NE-{v_counter} (" + x + ")")
    except OSError:
        print(f"Создать директорию не удалось")
    else:
        v_nedir = v_path + '\\' + f"NE-{v_counter} (" + x + ")"
        v_access_via = ff_access_to_ne.f_ne_access(v_nes[v_counter-1], v_login, v_pass, "huawei", v_coms, v_nedir)
        v_counter += 1
        print(v_access_via)
print('\n\n', v_nes)
print('\n', v_coms, '\n')
