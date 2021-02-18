# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
# Да и может он не много (пока).
ne_counter = 0
ip_list_file = 'ne_list.txt'
ip_list_file_exist = False

try:
    open(ip_list_file, 'r')
    ip_list_file_exist = True
except FileNotFoundError:
    print("Ошибка: файл", ip_list_file, "не найден.")

if ip_list_file_exist:
    with open(ip_list_file, 'r') as reader:
        line = reader.readline()
        while line != '':
            ne_counter += 1
            print('NE', ne_counter, ':', line, end='')
            line = reader.readline()
    print("\n\nГотово. Всего обработано NE:", ne_counter)
else:
    pass

input()
