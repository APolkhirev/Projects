# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
# Да и может он не много (пока).

ip_list_file = 'ne_list.txt'
ip_list_file_exist = False

try:
    open(ip_list_file, 'r')
    ip_list_file_exist = True
except FileNotFoundError:
    print(f"Ошибка: файл ./{ip_list_file}, содержащий список IP-адресов сетевых элементов, не найден.")

ne_counter = 0
if ip_list_file_exist:
    print(f"Список импортирован из файла {ip_list_file}:")
    with open(ip_list_file, 'r') as reader:
        line = reader.readline()
        while line != '':
            ne_counter += 1
            print(f"NE-{ne_counter}: {line}", end='')
            line = reader.readline()
    print(f"\n\nГотово. Всего было обработано NE: {ne_counter}")
else:
    pass

input()
